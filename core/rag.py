# ── core/rag.py ────────────────────────────────────────────
# RAG logic — search + prompt + AI call. Pure logic, no UI.

from typing import Any, Dict, Iterable, List, Tuple
import time
import logging

from groq import Groq, GroqError

from config import GROQ_API_KEY, LLM_MODEL, TOP_K_RESULTS
from core.prompts import (
    base_rag_prompt,
    explain_mode_prompt,
    summarize_mode_prompt,
    quiz_mode_prompt,
)
from utils.cache import get_cached_result, cache_result

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is required.")

client = Groq(api_key=GROQ_API_KEY)

# Maps mode key → prompt builder function
PROMPT_MAP = {
    "base":      base_rag_prompt,
    "explain":   explain_mode_prompt,
    "summarize": summarize_mode_prompt,
    "quiz":      quiz_mode_prompt,
}


def _normalize_query(question: str) -> str:
    return " ".join(question.strip().split())


def search_documents(vectorstore: Any, question: str) -> list:
    try:
        normalized = _normalize_query(question)
        if not normalized:
            return []
        result = vectorstore.similarity_search(normalized, k=TOP_K_RESULTS)
        logger.info(f"Retrieved {len(result)} chunks for: {question[:50]}...")
        return result
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []


def _build_context(relevant_docs: Iterable[Any]) -> str:
    parts = []
    for doc in relevant_docs:
        source = doc.metadata.get("source", "unknown") if doc.metadata else "unknown"
        page = doc.metadata.get("page") if doc.metadata else None
        label = f"[{source}" + (f", p.{int(page)+1}" if page is not None else "") + "]"
        parts.append(f"{label}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def _build_messages(
    context: str,
    question: str,
    mode: str,
    chat_history: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """
    Build the full messages list for the Groq API call.
    Includes a system prompt, recent conversation history, and the current question.
    """
    # System message — strict document-only instruction
    system = (
        "You are a precise document assistant. "
        "You ONLY answer based on the document excerpts provided to you. "
        "Never use outside knowledge. "
        "If the answer is not in the documents, say exactly: "
        "'The documents do not contain information about this.' "
        "Always cite which document and page your answer comes from when possible."
    )

    messages = [{"role": "system", "content": system}]

    # Include last 6 exchanges (3 user + 3 assistant) for context
    # This gives the AI memory of the recent conversation
    recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
    for entry in recent_history:
        if entry["role"] in ("user", "assistant"):
            messages.append({"role": entry["role"], "content": entry["content"]})

    # Build the current turn prompt using the selected mode
    prompt_fn = PROMPT_MAP.get(mode, base_rag_prompt)

    if mode == "quiz":
        # Quiz mode doesn't need the question, just the context
        user_content = prompt_fn(context=context)
    elif mode == "summarize":
        user_content = prompt_fn(context=context, question=question)
    else:
        user_content = prompt_fn(context=context, question=question)

    messages.append({"role": "user", "content": user_content})
    return messages


def get_answer(
    vectorstore: Any,
    question: str,
    doc_names: Tuple[str, ...] = (),
    mode: str = "base",
    chat_history: List[Dict[str, str]] = None,
) -> Tuple[str, list, Dict[str, Any]]:
    """
    Full RAG pipeline:
      1. Validate inputs
      2. Check cache
      3. Retrieve relevant document chunks
      4. Build prompt using selected mode
      5. Call LLM with conversation history
      6. Cache and return result

    Returns (answer_text, relevant_docs, debug_info).
    """
    if chat_history is None:
        chat_history = []

    debug: Dict[str, Any] = {"question": question, "mode": mode}
    t_start = time.perf_counter()

    # ── Input validation ──
    if not question or not question.strip():
        return "Please enter a question.", [], {
            **debug, "reason": "empty_question",
            "total_ms": (time.perf_counter() - t_start) * 1000
        }

    if not vectorstore:
        return "No documents loaded. Upload PDFs to begin.", [], {
            **debug, "reason": "no_vectorstore",
            "total_ms": (time.perf_counter() - t_start) * 1000
        }

    # ── Cache check (only for non-quiz, non-summarize modes) ──
    if mode in ("base", "explain"):
        cached = get_cached_result(question, doc_names)
        if cached:
            debug.update(cached["debug_info"])
            debug["cached"] = True
            debug["total_ms"] = (time.perf_counter() - t_start) * 1000
            return cached["answer"], cached["relevant_docs"], debug

    debug["cached"] = False

    # ── Retrieval ──
    t0 = time.perf_counter()
    try:
        relevant_docs = search_documents(vectorstore, question)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return "Error searching documents. Please try again.", [], {
            **debug, "reason": "search_error", "error": str(e),
            "total_ms": (time.perf_counter() - t_start) * 1000
        }

    debug["num_docs_retrieved"] = len(relevant_docs)
    debug["retrieval_ms"] = (time.perf_counter() - t0) * 1000

    if not relevant_docs:
        return (
            "I couldn't find relevant content in your documents for this question. "
            "Try rephrasing, or check that you've uploaded the right files.",
            [],
            {**debug, "reason": "no_relevant_docs",
             "total_ms": (time.perf_counter() - t_start) * 1000}
        )

    # ── Build context + messages ──
    try:
        context = _build_context(relevant_docs)
        messages = _build_messages(context, question, mode, chat_history)
        debug["prompt_chars"] = sum(len(m["content"]) for m in messages)
    except Exception as e:
        logger.error(f"Prompt build failed: {e}")
        return "Error building prompt. Please try again.", relevant_docs, {
            **debug, "reason": "prompt_error", "error": str(e),
            "total_ms": (time.perf_counter() - t_start) * 1000
        }

    # ── LLM call ──
    try:
        t_llm = time.perf_counter()
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=2048,
            temperature=0.3,   # Lower = more factual, less creative
        )

        if not response.choices or not response.choices[0].message:
            raise ValueError("Empty LLM response")

        answer = response.choices[0].message.content
        if not answer or not answer.strip():
            raise ValueError("Empty answer content")

        debug["llm_ms"] = (time.perf_counter() - t_llm) * 1000
        debug["total_ms"] = (time.perf_counter() - t_start) * 1000
        logger.info(f"Answer generated in {debug['total_ms']:.0f}ms [{mode} mode]")

        # Cache base/explain mode results
        if mode in ("base", "explain"):
            cache_result(question, doc_names, answer, relevant_docs, debug)

    except GroqError as e:
        logger.error(f"Groq API error: {e}")
        return (
            "The AI service is temporarily unavailable. Check your API key or try again.",
            [],
            {**debug, "error": str(e), "total_ms": (time.perf_counter() - t_start) * 1000}
        )
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return (
            "Something went wrong. Please try again.",
            [],
            {**debug, "error": str(e), "total_ms": (time.perf_counter() - t_start) * 1000}
        )

    return answer, list(relevant_docs), debug