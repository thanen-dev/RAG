"""
Lightweight evaluation harness for the RAG pipeline.

Run this locally to sanity‑check retrieval quality against a few
hand‑crafted questions and expected answer snippets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.document import build_vectorstore
from core.rag import get_answer


@dataclass
class EvalCase:
    question: str
    expected_snippet: str


def run_eval(uploaded_files, cases: List[EvalCase]) -> None:
    """
    uploaded_files: list of Streamlit UploadedFile‑like objects or file wrappers.
    cases: small list of EvalCase items to test.
    """
    vectorstore, _ = build_vectorstore(uploaded_files)

    for i, case in enumerate(cases, start=1):
        print(f"\n=== Case {i} ===")
        print("Q:", case.question)
        answer, relevant_docs, debug = get_answer(vectorstore, case.question)
        print("Answer:", answer[:400].replace("\n", " ") + "...")

        # Check whether expected snippet appears in any retrieved chunk.
        in_chunks = any(
            case.expected_snippet.lower() in doc.page_content.lower()
            for doc in relevant_docs
        )
        print("Expected snippet in retrieved chunks:", in_chunks)
        print("Retrieved docs:", debug.get("num_docs_retrieved"))


if __name__ == "__main__":
    print(
        "This script is intended to be imported and used from a notebook or "
        "from within Streamlit, where you can supply UploadedFile objects."
    )

