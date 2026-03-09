# RAG Upgrade — What Changed & How to Set Up

## New Dependencies

```bash
pip install -r requirements.txt
```

**Tesseract OCR** must also be installed at the OS level:
- macOS:   `brew install tesseract`
- Linux:   `sudo apt install tesseract-ocr`
- Windows: https://github.com/UB-Mannheim/tesseract/wiki

---

## What Was Fixed & Added

### 1. OCR for Image-Based PDFs (the big fix)
`core/document.py` now uses **PyMuPDF** instead of pypdf.
- Every page tries native text extraction first (fast)
- If a page has < 100 chars of text, it falls back to **Tesseract OCR**
- Your `Exploring_Management.pdf` with 533 pages will now extract content
- The file size bug is also fixed — oversized files are properly skipped

### 2. Vectorstore Persistence
Your document embeddings are now **saved to disk** in `vectorstores/`.
- After the first upload, you never need to re-upload the same PDFs again
- Page refresh / app restart will automatically reload your documents
- Look for the ♻️ icon next to the doc count in the sidebar

### 3. Conversation History
The LLM now receives the last **3 exchanges** as context.
- Follow-up questions like "tell me more about point 2" now work properly
- Short follow-up queries are also contextualised before retrieval

### 4. MMR Retrieval
Switched from plain similarity search to **Maximal Marginal Relevance**.
- Retrieves diverse chunks instead of 8 near-identical ones
- Configurable via `MMR_LAMBDA` in `.env` (0=diverse, 1=relevant, default 0.6)

### 5. Four Answer Modes (now wired up)
Select from the sidebar:
- 📚 **Study** — strict, citation-aware answers from your material
- 💡 **Explain** — plain English first, then technical depth
- 📋 **Summarise** — bullet-point revision notes with key terms bolded
- ❓ **Quiz Me** — generates Q&A pairs (say "give me 7 questions" etc.)

---

## Files Changed

| File | Change |
|------|--------|
| `requirements.txt` | Added pymupdf, pytesseract, Pillow |
| `config.py` | Added OCR, persistence, MMR, conversation settings |
| `core/document.py` | Full rewrite: PyMuPDF + OCR + disk persistence |
| `core/rag.py` | MMR retrieval + conversation history + mode support |
| `core/prompts.py` | Restructured to system/user format; all 4 modes |
| `utils/session.py` | Saves/loads `collection_id` for vectorstore restoration |
| `components/sidebar.py` | Mode selector added |
| `app.py` | Wires up modes, conversation history, vectorstore restoration |

## Files Unchanged
`components/styles.py`, `components/chat.py`, `utils/cache.py`, `utils/logger.py`
