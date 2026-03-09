# ── app.py ─────────────────────────────────────────────────
# Entry point. Ties everything together.
# This file should stay short — just imports and flow control.

import streamlit as st
import time
from config import APP_NAME, APP_ICON, validate_config
from components.styles import apply_styles
from components.sidebar import render_sidebar
from components.chat import render_hero, render_document_context, render_chat_history, render_sources
from core.document import build_vectorstore
from core.rag import get_answer
from utils.logger import setup_logging, log_user_action, log_performance, log_error
from utils.session import save_current_session, load_current_session, clear_current_session, archive_current_session

# Set up logging
logger = setup_logging()

# ── Validate configuration ──
config_errors = validate_config()
if config_errors:
    log_error("CONFIG_ERROR", "Configuration validation failed", "; ".join(config_errors))
    st.error("Configuration Error:")
    for error in config_errors:
        st.error(f"• {error}")
    st.stop()

# ── Page config ──
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Apply styles ──
apply_styles()

import time


# ── Session state ──
def initialize_session_state():
    """Initialize session state with default values and try to load saved session."""
    defaults = {
        "vectorstore": None,
        "chat_history": [],
        "doc_names": [],
        "debug_mode": False,
        "question_timestamps": [],
        "session_loaded": False
    }
    
    # Set defaults
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Try to load saved session on first run
    if not st.session_state.session_loaded:
        try:
            saved_session = load_current_session()
            if saved_session:
                st.session_state.chat_history = saved_session.get("chat_history", [])
                st.session_state.doc_names = saved_session.get("doc_names", [])
                st.session_state.debug_mode = saved_session.get("debug_mode", False)
                st.session_state.session_loaded = True
                
                if st.session_state.chat_history:
                    log_user_action("SESSION_LOADED", f"Loaded {len(st.session_state.chat_history)} messages")
                    
        except Exception as e:
            log_error("SESSION_LOAD_ERROR", str(e))
            st.session_state.session_loaded = True  # Don't try again

initialize_session_state()

# ── Sidebar ──
render_sidebar()

# ── Hero (only when empty) ──
if not st.session_state.vectorstore and not st.session_state.chat_history:
    render_hero()

# ── Chat history ──
if st.session_state.chat_history:
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    render_document_context()
    render_chat_history()

st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

# ── Fixed bottom input bar ──
st.markdown('<div class="input-wrapper"><div class="input-box">', unsafe_allow_html=True)

# Upload row
st.markdown('<div class="input-bottom">', unsafe_allow_html=True)
col_upload, col_status = st.columns([4, 1])

with col_upload:
    uploaded_files = st.file_uploader(
        "attach",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="uploader",
    )

with col_status:
    if st.session_state.vectorstore:
        st.markdown(
            f'<span style="font-size:0.72rem;color:#4ade80;">✦ {len(st.session_state.doc_names)} doc(s)</span>',
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)

# Auto-process on upload with a simple limit on number of documents
MAX_DOCS_PER_SESSION = 10

if uploaded_files and not st.session_state.vectorstore:
    if len(uploaded_files) > MAX_DOCS_PER_SESSION:
        st.warning(
            f"You selected {len(uploaded_files)} files. "
            f"For stability, please upload at most {MAX_DOCS_PER_SESSION} PDFs at once."
        )
    else:
        # Create a progress container
        progress_container = st.container()
        with progress_container:
            st.markdown("### Processing Documents")
            progress_bar = st.progress(0, text="Starting...")
            status_text = st.empty()
        
        try:
            # Step 1: Validate files
            progress_bar.progress(0.1, text="Validating files...")
            status_text.text("Checking file formats and sizes...")
            log_user_action("DOCUMENT_UPLOAD_START", f"Processing {len(uploaded_files)} files")
            
            start_time = time.perf_counter()
            vectorstore, names = build_vectorstore(uploaded_files)
            processing_time = (time.perf_counter() - start_time) * 1000
            
            # Step 2: Loading complete
            progress_bar.progress(0.8, text="Processing complete...")
            status_text.text("Finalizing...")
            
            if vectorstore is None:
                progress_bar.empty()
                status_text.empty()
                if names:
                    st.warning("Some documents were processed, but no content could be extracted. Please check if your PDFs contain readable text.")
                    log_error("DOCUMENT_PROCESSING", "No content extracted from documents", f"Files: {len(uploaded_files)}, Names: {names}")
                else:
                    st.error("Could not process any of the uploaded files. Please ensure they are valid PDF files with text content.")
                    log_error("DOCUMENT_PROCESSING", "No valid documents processed", f"Files: {len(uploaded_files)}")
            else:
                # Step 3: Success
                progress_bar.progress(1.0, text="Complete!")
                status_text.text(f"Successfully loaded {len(names)} document(s)")
                
                # Clear progress indicators after a short delay
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                st.session_state.vectorstore = vectorstore
                st.session_state.doc_names = names
                st.success(f"✅ Successfully processed {len(names)} document(s)")
                
                log_user_action("DOCUMENT_UPLOAD_SUCCESS", f"Processed {len(names)} documents in {processing_time:.2f}ms")
                log_performance("DOCUMENT_PROCESSING", processing_time, f"{len(names)} documents")
                
                # Save session state
                save_current_session(st.session_state.chat_history, st.session_state.doc_names, st.session_state.debug_mode)
                st.rerun()
                
        except ValueError as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"Document processing error: {str(e)}")
            log_error("DOCUMENT_PROCESSING_ERROR", str(e), f"Files: {len(uploaded_files)}")
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error("An unexpected error occurred while processing your documents. Please try again.")
            log_error("DOCUMENT_PROCESSING_UNEXPECTED", str(e), f"Files: {len(uploaded_files)}")

# Chat input
if st.session_state.vectorstore:
    question = st.chat_input("Ask anything about your notes...")
else:
    question = st.chat_input("Upload your notes to begin...")

st.markdown("</div></div>", unsafe_allow_html=True)

# ── Handle question ──
if question and st.session_state.vectorstore:
    # Simple per-session rate limiting
    now = time.time()
    window_seconds = 60
    max_questions_per_window = 12

    st.session_state.question_timestamps = [
        t for t in st.session_state.question_timestamps if now - t < window_seconds
    ]

    if len(st.session_state.question_timestamps) >= max_questions_per_window:
        st.warning(
            "You are asking questions very quickly. Please wait a few seconds and try again."
        )
    else:
        st.session_state.question_timestamps.append(now)

        with st.chat_message("user"):
            st.write(question)
        st.session_state.chat_history.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer, relevant_docs, debug_info = get_answer(
                        st.session_state.vectorstore,
                        question,
                        tuple(st.session_state.doc_names),
                        mode=st.session_state.get("active_mode", "base"),
                        chat_history=st.session_state.chat_history,
                    )
                    st.write(answer)
                    render_sources(relevant_docs)

                    # Show debug info if enabled
                    if st.session_state.debug_mode:
                        with st.expander("RAG debug info"):
                            st.json(debug_info)
                            
                            # Show cache status
                            if debug_info.get("cached"):
                                st.info("⚡ This answer was retrieved from cache")
                            else:
                                st.info("🔍 This answer was generated fresh")

                    # Check for errors in debug info
                    if isinstance(debug_info, dict) and debug_info.get("error"):
                        error_type = debug_info.get("reason", "unknown")
                        if error_type in ["empty_question", "no_vectorstore"]:
                            st.info("Please ensure you have uploaded documents and entered a valid question.")
                        elif error_type == "no_relevant_docs":
                            st.info("I couldn't find relevant information in your documents. Try rephrasing your question.")
                        else:
                            st.warning("There was an issue processing your request. Please try again.")
                        log_error("RAG_ERROR", debug_info.get("error", "Unknown error"), f"Type: {error_type}")
                    else:
                        # Log successful query
                        if isinstance(debug_info, dict) and "total_ms" in debug_info:
                            cache_status = "cached" if debug_info.get("cached") else "generated"
                            log_performance("QUESTION_ANSWERING", debug_info["total_ms"], f"Docs: {debug_info.get('num_docs_retrieved', 0)}, {cache_status}")
                    
                    log_user_action("QUESTION_ANSWERED", f"Question: {question[:50]}...")
                    
                except Exception as e:
                    st.error("An unexpected error occurred. Please try again.")
                    log_error("QUESTION_HANDLING_ERROR", str(e), f"Question: {question[:50]}...")

        # Only add to chat history if we got a valid answer
        if 'answer' in locals() and answer:
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()