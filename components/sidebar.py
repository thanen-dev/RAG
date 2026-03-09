# ── components/sidebar.py ──────────────────────────────────
# Sidebar UI — Apple macOS-inspired light design.

import streamlit as st

def render_sidebar():
    with st.sidebar:
        # ── Logo ──
        st.markdown("""
        <div class="sb-logo">
            <div class="sb-logo-icon">🧠</div>
            <span class="sb-logo-name">StudyMind</span>
            <span class="sb-logo-badge">Beta</span>
        </div>
        """, unsafe_allow_html=True)

        # ── New Chat Button ──
        st.markdown('<div class="sb-new-chat-wrap">', unsafe_allow_html=True)
        if st.button("＋  New Chat", use_container_width=True, key="new_chat_btn"):
            st.session_state.chat_history = []
            st.session_state.vectorstore = None
            st.session_state.doc_names = []
            st.session_state.question_timestamps = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Recent Chats ──
        st.markdown('<div class="sb-section-label">Recent Chats</div>', unsafe_allow_html=True)

        if st.session_state.chat_history:
            first_msg = st.session_state.chat_history[0]["content"]
            preview = first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
            st.markdown(f'<div class="sb-chat-item active"><span class="sb-chat-icon">💬</span>{preview}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sb-chat-item"><span class="sb-chat-icon">💬</span>No active session</div>', unsafe_allow_html=True)

        # ── Loaded Documents ──
        if st.session_state.doc_names:
            st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sb-section-label">Loaded Documents</div>', unsafe_allow_html=True)
            for name in st.session_state.doc_names:
                short = name[:26] + "..." if len(name) > 26 else name
                st.markdown(f"""
                <div class="sb-doc-item">
                    <div class="sb-doc-dot"></div>
                    {short}
                </div>
                """, unsafe_allow_html=True)

        # ── Session Management ──
        if st.session_state.chat_history or st.session_state.vectorstore:
            st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sb-section-label">Session</div>', unsafe_allow_html=True)
            st.markdown("<div style='padding: 0 0.8rem 0.5rem;'>", unsafe_allow_html=True)

            if st.session_state.chat_history:
                st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
                if st.button("Clear Chat", use_container_width=True, key="clear_chat_btn"):
                    st.session_state.chat_history = []
                    st.session_state.question_timestamps = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.vectorstore:
                st.markdown('<div class="secondary-btn" style="margin-top:0.4rem">', unsafe_allow_html=True)
                if st.button("Reload Documents", use_container_width=True, key="reload_docs_btn"):
                    st.session_state.vectorstore = None
                    st.session_state.doc_names = []
                    st.session_state.chat_history = []
                    st.session_state.question_timestamps = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ── Settings ──
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-section-label">Settings</div>', unsafe_allow_html=True)
        st.markdown("<div style='padding: 0 1rem 0.5rem;'>", unsafe_allow_html=True)

        debug_mode = st.checkbox("Debug Mode", value=st.session_state.get("debug_mode", False))
        st.session_state.debug_mode = debug_mode

        if st.session_state.vectorstore:
            st.markdown(f"""
            <div style='font-size:0.7rem; color:rgba(0,0,0,0.3); margin-top:0.8rem; line-height:1.8;'>
            📄 {len(st.session_state.doc_names)} document(s) loaded<br>
            💬 {len(st.session_state.chat_history)} message(s)
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)