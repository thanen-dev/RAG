# ── core/document.py ───────────────────────────────────────
# PDF loading (with OCR fallback), chunking, embedding, and persistence.
# No UI code lives here.

import io
import os
import hashlib
import logging
from typing import List, Optional, Tuple

import fitz  # PyMuPDF — far superior to pypdf for mixed text/image PDFs

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from config import (
    CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, VECTORSTORE_DIR,
    OCR_ENABLED, MIN_TEXT_PER_PAGE,
)

logger = logging.getLogger(__name__)

# ── Optional OCR ────────────────────────────────────────────
# Gracefully degrade if Tesseract is not installed on the system.
_OCR_READY = False
try:
    from PIL import Image
    import pytesseract
    pytesseract.get_tesseract_version()  # raises if tesseract binary not found
    _OCR_READY = True
    logger.info("Tesseract OCR is available — image pages will be processed.")
except Exception:
    logger.warning(
        "Tesseract OCR not found. Image-only PDF pages will be skipped.\n"
        "  macOS : brew install tesseract\n"
        "  Linux : sudo apt install tesseract-ocr\n"
        "  Windows: https://github.com/UB-Mannheim/tesseract/wiki"
    )

# ── File size limits ────────────────────────────────────────
_MAX_FILE_BYTES  = 80 * 1024 * 1024   # 80 MB per file
_MAX_TOTAL_BYTES = 300 * 1024 * 1024  # 300 MB total session


# ──────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────

def _sha256(data: bytes, length: int = 20) -> str:
    return hashlib.sha256(data).hexdigest()[:length]


def _collection_id(file_hashes: List[str]) -> str:
    """Deterministic ID for a set of files — used as the persist folder name."""
    combined = "|".join(sorted(file_hashes))
    return hashlib.sha256(combined.encode()).hexdigest()[:24]


def _extract_page_text(page: "fitz.Page") -> Tuple[str, bool]:
    """
    Extract text from one PDF page.

    Strategy:
      1. Native text via PyMuPDF  (fast, handles most PDFs)
      2. OCR fallback              (for scanned / image-only pages)

    Returns (text, ocr_was_used).
    """
    # --- Step 1: native extraction ------------------------------------------
    # "text" mode with sort=True respects reading order.
    # "blocks" can also work but "text" is simpler and good enough.
    text = page.get_text("text", sort=True).strip()

    if len(text) >= MIN_TEXT_PER_PAGE:
        return text, False

    # --- Step 2: OCR fallback ------------------------------------------------
    if not (OCR_ENABLED and _OCR_READY):
        return text, False  # no OCR available, return whatever native gave us

    try:
        # Render at 2.5× zoom (≈ 225 DPI) for good OCR accuracy
        mat = fitz.Matrix(2.5, 2.5)
        pix = page.get_pixmap(matrix=mat, alpha=False, colorspace=fitz.csGRAY)
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        # psm 3 = auto layout detection; oem 3 = best available LSTM engine
        ocr_text = pytesseract.image_to_string(img, config="--psm 3 --oem 3").strip()
        return ocr_text, True

    except Exception as exc:
        logger.warning(f"OCR failed on page {page.number}: {exc}")
        return text, False


def _load_single_pdf(file_bytes: bytes, filename: str) -> List[Document]:
    """
    Parse one PDF into a list of LangChain Documents (one per page).
    Uses native PyMuPDF extraction with OCR fallback per page.
    """
    docs: List[Document] = []
    ocr_count = 0
    skip_count = 0

    try:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        logger.error(f"Cannot open {filename}: {exc}")
        return docs

    total_pages = len(pdf)
    for page_num in range(total_pages):
        try:
            page = pdf[page_num]
            text, ocr_used = _extract_page_text(page)

            if not text:
                skip_count += 1
                continue

            if ocr_used:
                ocr_count += 1

            docs.append(Document(
                page_content=text,
                metadata={
                    "source": filename,
                    "page": page_num,          # 0-indexed
                    "page_display": page_num + 1,  # 1-indexed for UI
                    "ocr": ocr_used,
                    "total_pages": total_pages,
                }
            ))
        except Exception as exc:
            logger.warning(f"Skipping page {page_num} of {filename}: {exc}")
            skip_count += 1

    pdf.close()
    logger.info(
        f"{filename}: {len(docs)}/{total_pages} pages loaded "
        f"({ocr_count} OCR, {skip_count} skipped)"
    )
    return docs


def _load_all_pdfs(uploaded_files) -> Tuple[List[Document], List[str], List[str]]:
    """
    Validate and load all uploaded files.
    Returns (all_documents, filenames, per_file_sha256_hashes).
    """
    all_docs:   List[Document] = []
    names:      List[str]      = []
    hashes:     List[str]      = []
    total_size: int            = 0

    for uf in uploaded_files:
        # Only accept PDFs
        if not uf.name.lower().endswith(".pdf"):
            logger.warning(f"Skipping non-PDF: {uf.name}")
            continue

        # Read bytes
        try:
            uf.seek(0)
            file_bytes = uf.read()
        except Exception as exc:
            logger.error(f"Cannot read {uf.name}: {exc}")
            continue

        size = len(file_bytes)

        # Per-file size guard
        if size > _MAX_FILE_BYTES:
            logger.warning(
                f"Skipping {uf.name}: {size/1024/1024:.1f} MB > "
                f"{_MAX_FILE_BYTES/1024/1024:.0f} MB limit"
            )
            continue

        # Total size guard
        total_size += size
        if total_size > _MAX_TOTAL_BYTES:
            logger.warning("Total upload limit reached — remaining files skipped.")
            break

        # Process
        docs = _load_single_pdf(file_bytes, uf.name)
        if docs:
            all_docs.extend(docs)
            names.append(uf.name)
            hashes.append(_sha256(file_bytes))
        else:
            logger.warning(f"No extractable content in {uf.name}")

    return all_docs, names, hashes


def _split_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into retrieval-sized chunks with meaningful overlap.
    Filters out noise chunks shorter than 60 characters.
    """
    if not documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        # Try to split at natural paragraph / sentence boundaries first
        separators=["\n\n\n", "\n\n", "\n", ". ", "! ", "? ", "; ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    # Drop near-empty chunks that add noise to retrieval
    chunks = [c for c in chunks if len(c.page_content.strip()) > 60]
    logger.info(f"Split {len(documents)} pages → {len(chunks)} chunks")
    return chunks


def _make_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},  # cosine similarity
    )


# ──────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────

def load_vectorstore_from_disk(collection_id: str) -> Optional[Chroma]:
    """
    Attempt to load a previously persisted vectorstore.
    Returns None if not found or on any error.
    """
    if not PERSIST_VECTORSTORE or not collection_id:
        return None

    persist_dir = os.path.join(VECTORSTORE_DIR, collection_id)
    if not os.path.isdir(persist_dir):
        return None

    try:
        embeddings = _make_embeddings()
        vs = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        count = vs._collection.count()
        if count == 0:
            logger.warning(f"Persisted store at {persist_dir} is empty — ignoring.")
            return None
        logger.info(f"Restored vectorstore from disk: {count} chunks ({persist_dir})")
        return vs
    except Exception as exc:
        logger.warning(f"Could not load persisted vectorstore: {exc}")
        return None


def build_vectorstore(uploaded_files) -> Tuple[Optional[Chroma], List[str], str]:
    """
    Full pipeline: validate → load PDFs (with OCR) → chunk → embed → store.

    Returns:
        vectorstore   : Chroma instance (or None on failure)
        names         : list of successfully processed filenames
        collection_id : opaque ID; pass to load_vectorstore_from_disk() later
    """
    # ── 1. Load ──────────────────────────────────────────────
    documents, names, hashes = _load_all_pdfs(uploaded_files)

    if not documents:
        return None, names, ""

    collection_id = _collection_id(hashes)

    # ── 2. Check if already persisted ────────────────────────
    if PERSIST_VECTORSTORE:
        existing = load_vectorstore_from_disk(collection_id)
        if existing:
            logger.info("Re-using persisted vectorstore — skipping re-embedding.")
            return existing, names, collection_id

    # ── 3. Chunk ─────────────────────────────────────────────
    chunks = _split_documents(documents)
    if not chunks:
        return None, names, ""

    # ── 4. Embed ─────────────────────────────────────────────
    try:
        embeddings = _make_embeddings()
        logger.info(f"Embedding model loaded: {EMBEDDING_MODEL}")
    except Exception as exc:
        raise ValueError(f"Failed to load embedding model: {exc}")

    # ── 5. Build vectorstore ─────────────────────────────────
    try:
        if PERSIST_VECTORSTORE:
            persist_dir = os.path.join(VECTORSTORE_DIR, collection_id)
            os.makedirs(persist_dir, exist_ok=True)
            vs = Chroma.from_documents(
                chunks, embeddings, persist_directory=persist_dir
            )
            logger.info(f"Vectorstore saved to {persist_dir} ({len(chunks)} chunks)")
        else:
            vs = Chroma.from_documents(chunks, embeddings)
            logger.info(f"In-memory vectorstore created ({len(chunks)} chunks)")

        return vs, names, collection_id

    except Exception as exc:
        raise ValueError(f"Failed to create vectorstore: {exc}")
