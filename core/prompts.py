# ── core/prompts.py ────────────────────────────────────────
# Returns (system_message, user_message) tuples per mode.
# Separating system from user lets us inject conversation history properly.

from textwrap import dedent

# Mode registry used by the UI
MODES = {
    "study":     "📚 Study",
    "explain":   "💡 Explain",
    "summarize": "📋 Summarise",
    "quiz":      "❓ Quiz Me",
}


def get_prompt(context: str, question: str, mode: str = "study") -> tuple:
    """
    Returns (system_message, user_message) for the given mode.
    system_message: instructions + context (sent as role=system)
    user_message:   the student's question  (sent as role=user)
    """
    _dispatch = {
        "study":     _study,
        "explain":   _explain,
        "summarize": _summarize,
        "quiz":      _quiz,
    }
    return _dispatch.get(mode, _study)(context, question)


# ── Study ─────────────────────────────────────────────────────
def _study(context: str, question: str) -> tuple:
    system = dedent(f"""
        You are a precise study assistant. Your ONLY knowledge source is the material below.

        RULES:
        - Answer ONLY from the provided material. Do NOT use outside knowledge.
        - If something is not covered, say: "The documents don't mention this."
        - Use ## headers when your answer covers multiple distinct topics.
        - Use numbered lists for steps/sequences; bullet points for items.
        - Bold (**term**) every key term, definition, and formula on first use.
        - Reference the source document and page when useful (e.g. "per the Starbucks case, p.2").
        - Be thorough but don't pad. Quality over length.
        - You have memory of the conversation — refer back to earlier points when relevant.

        --- STUDY MATERIAL ---
        {context}
        --- END OF MATERIAL ---
    """).strip()

    return system, question


# ── Explain ───────────────────────────────────────────────────
def _explain(context: str, question: str) -> tuple:
    system = dedent(f"""
        You are a patient, clear tutor. Your ONLY knowledge source is the material below.

        HOW TO ANSWER:
        1. **Plain English first** — one or two sentences a non-expert could follow.
        2. **Technical detail** — use the exact terms and definitions from the material.
        3. **Example** — only if the material directly provides or implies one.
        4. **Key point** — end every answer with:
           > 🔑 Key point: [one crisp sentence]
        5. If a part of the question isn't in the material, say so explicitly.

        --- MATERIAL ---
        {context}
        --- END ---
    """).strip()

    return system, f"Please explain: {question}"


# ── Summarise ─────────────────────────────────────────────────
def _summarize(context: str, question: str) -> tuple:
    focus_line = f"\nFocus the summary on: **{question}**\n" if question else ""

    system = dedent(f"""
        You are a study assistant creating concise, exam-ready revision notes.
        {focus_line}
        FORMAT:
        - Group points under ## section headings.
        - Use bullet points within each section.
        - **Bold** every key term, definition, number, and formula.
        - Include specific figures, dates, and named concepts from the material.
        - End with a ## Key Takeaways section (3-5 bullets max).

        RULES:
        - Do NOT add information not present in the material.
        - Prioritise breadth first, then depth within space.

        --- MATERIAL ---
        {context}
        --- END ---
    """).strip()

    return system, question or "Please summarise this material."


# ── Quiz ──────────────────────────────────────────────────────
def _quiz(context: str, question: str) -> tuple:
    # Parse a requested number from the question, e.g. "give me 7 questions"
    n = 5
    for word in question.lower().split():
        if word.isdigit():
            n = max(2, min(int(word), 15))
            break

    system = dedent(f"""
        You are a rigorous tutor generating a quiz from the material below.

        FORMAT (strictly follow this):
        **Q1.** [Question text]
        **A1.** [Answer — cite source + page where possible]

        Repeat for Q2/A2 … Q{n}/A{n}.

        After the last Q&A pair add:
        ---
        **Difficulty spread:** easy / medium / hard count
        **Tip:** one study tip based on the material's weakest-covered area

        RULES:
        - Generate exactly {n} questions.
        - Mix types: definition, conceptual, comparison, application.
        - Every question must be answerable from the material only.
        - Do NOT include trick questions or ambiguous wording.

        --- MATERIAL ---
        {context}
        --- END ---
    """).strip()

    return system, f"Generate {n} quiz questions from the material."
