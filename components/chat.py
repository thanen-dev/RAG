# ── components/chat.py ─────────────────────────────────────
# Chat UI — mode tabs, hero, document context, messages, sources panel.

import streamlit as st
import os

# Mode definitions
MODES = {
    "base":    {"label": "Base Mode",        "icon": "⊡", "desc": "Quickly access facts from your content"},
    "explain": {"label": "Explanatory Mode", "icon": "💡", "desc": "Get detailed context and insights"},
    "summarize": {"label": "Summarize Mode", "icon": "⇥⇤", "desc": "Condense documents into key takeaways"},
    "quiz":    {"label": "Quiz Mode",        "icon": "✓?", "desc": "Test your understanding with auto-generated quizzes"},
}


def render_mode_tabs():
    """Top pill-style mode selector — matches the design reference."""
    if "active_mode" not in st.session_state:
        st.session_state.active_mode = "base"

    st.markdown('<div class="mode-tabs-bar"><div class="mode-tabs-pill-group">', unsafe_allow_html=True)

    cols = st.columns(len(MODES))
    for i, (mode_key, mode_data) in enumerate(MODES.items()):
        with cols[i]:
            is_active = st.session_state.active_mode == mode_key
            btn_style = (
                "background:#0071e3;color:#fff;border:none;border-radius:999px;"
                "padding:0.38rem 1rem;font-size:0.8rem;font-weight:600;cursor:pointer;width:100%;"
                "box-shadow:0 1px 6px rgba(0,113,227,0.3);"
                if is_active else
                "background:transparent;color:rgba(0,0,0,0.5);border:none;border-radius:999px;"
                "padding:0.38rem 1rem;font-size:0.8rem;font-weight:400;cursor:pointer;width:100%;"
            )
            if st.button(mode_data["label"], key=f"mode_btn_{mode_key}", use_container_width=True):
                st.session_state.active_mode = mode_key
                st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

    # Status bar showing active mode
    if st.session_state.get("vectorstore") and st.session_state.chat_history:
        active = MODES[st.session_state.active_mode]
        doc_count = len(st.session_state.doc_names)
        st.markdown(
            f'<div class="mode-status-bar">Using <strong>{active["label"]}</strong> · Responding based on {doc_count} source{"s" if doc_count != 1 else ""}</div>',
            unsafe_allow_html=True,
        )


def render_hero():
    """Empty state hero — Apple-inspired large typography + mode cards."""
    st.markdown("""
    <div class="hero">
        <div class="hero-title">Welcome,<br>Ask your knowledge base</div>
        <div class="hero-subtitle">
            Upload your lecture slides, readings, or PDFs.<br>
            Ask questions — get answers from your actual material.
        </div>
        <div class="mode-cards-grid">
            <div class="mode-card">
                <span class="mode-card-icon">⊡</span>
                <div class="mode-card-title">Base Mode</div>
                <div class="mode-card-desc">Quickly access facts and information from your content</div>
            </div>
            <div class="mode-card">
                <span class="mode-card-icon">💡</span>
                <div class="mode-card-title">Explanatory Mode</div>
                <div class="mode-card-desc">Get detailed context and insights on complex topics</div>
            </div>
            <div class="mode-card">
                <span class="mode-card-icon">⇥⇤</span>
                <div class="mode-card-title">Summarize Mode</div>
                <div class="mode-card-desc">Condense long documents into key takeaways</div>
            </div>
            <div class="mode-card">
                <span class="mode-card-icon">✓?</span>
                <div class="mode-card-title">Quiz Mode</div>
                <div class="mode-card-desc">Test your understanding with auto-generated quizzes</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_document_context():
    """Document context banner shown above chat."""
    if not st.session_state.doc_names:
        return

    pills = ""
    for name in st.session_state.doc_names:
        short = os.path.splitext(name)[0]
        short = short[:22] + "..." if len(short) > 22 else short
        pills += f'<span class="doc-context-pill">📄 {short}</span> '

    st.markdown(f"""
    <div class="doc-context-bar">
        <span class="doc-context-label">Active Sources</span>
        {pills}
    </div>
    """, unsafe_allow_html=True)


def render_chat_history():
    """Render all messages in the chat history."""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])


def render_sources(relevant_docs):
    """Collapsible source viewer shown below each assistant response."""
    if not relevant_docs:
        return

    with st.expander(f"📎 {len(relevant_docs)} sources used"):
        for i, doc in enumerate(relevant_docs):
            meta = getattr(doc, "metadata", {}) or {}
            source = meta.get("source", "")
            page = meta.get("page")

            if source:
                source = os.path.basename(source)
                source = os.path.splitext(source)[0]
            else:
                source = f"Document {i + 1}"

            label = f"{source}" + (f" — p. {int(page) + 1}" if page is not None else "")

            st.caption(label)
            preview = doc.page_content.strip()[:500]
            st.markdown(
                f'<div style="font-size:0.78rem;color:rgba(0,0,0,0.45);line-height:1.65;'
                f'padding:0.4rem 0;border-left:2px solid rgba(0,113,227,0.2);padding-left:0.7rem;">'
                f'{preview}</div>',
                unsafe_allow_html=True,
            )
            if i < len(relevant_docs) - 1:
                st.divider()


def render_sources_panel(relevant_docs=None):
    """Right-panel Knowledge Base sources (shown when docs are loaded)."""
    st.markdown("""
    <div class="sources-panel">
        <div class="sources-panel-title">Knowledge Base (RAG)</div>
        <div class="sources-panel-sub">Contextual Sources:</div>
    """, unsafe_allow_html=True)

    if relevant_docs:
        for i, doc in enumerate(relevant_docs, start=1):
            meta = getattr(doc, "metadata", {}) or {}
            source = meta.get("source", "")
            page = meta.get("page")
            if source:
                source = os.path.basename(source)
                source = os.path.splitext(source)[0]
            else:
                source = f"Document {i}"
            label = source + (f" (p.{int(page)+1})" if page is not None else "")
            st.markdown(f'<div class="source-ref-item"><span class="source-ref-num">{i}.</span>{label}</div>', unsafe_allow_html=True)
    elif st.session_state.doc_names:
        for i, name in enumerate(st.session_state.doc_names, start=1):
            short = os.path.splitext(name)[0]
            short = short[:28] + "..." if len(short) > 28 else short
            st.markdown(f'<div class="source-ref-item"><span class="source-ref-num">{i}.</span>{short}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:0.76rem;color:rgba(0,0,0,0.28);padding:0.5rem 0;">No documents loaded yet.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)