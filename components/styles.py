# ── components/styles.py ───────────────────────────────────
# Apple macOS-inspired light theme

import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&display=swap');

    *, html, body, [class*="css"] {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif !important;
        box-sizing: border-box;
    }

    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="collapsedControl"],
    [data-testid="stDecoration"] { display: none !important; }

    /* ── BASE ── */
    .stApp {
        background: #f0f0f2 !important;
        color: #1c1c1e !important;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid rgba(0,0,0,0.08) !important;
        min-width: 260px !important;
        max-width: 280px !important;
        box-shadow: 2px 0 12px rgba(0,0,0,0.04);
    }

    [data-testid="stSidebar"] > div {
        padding: 0 !important;
    }

    /* ── SIDEBAR ELEMENTS ── */
    .sb-logo {
        padding: 1.4rem 1.2rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        border-bottom: 1px solid rgba(0,0,0,0.06);
    }

    .sb-logo-icon {
        width: 30px; height: 30px;
        background: linear-gradient(135deg, #0071e3 0%, #34aadc 100%);
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 15px;
        box-shadow: 0 2px 8px rgba(0,113,227,0.3);
        flex-shrink: 0;
    }

    .sb-logo-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1c1c1e;
        letter-spacing: -0.3px;
    }

    .sb-logo-badge {
        font-size: 0.55rem;
        font-weight: 600;
        background: rgba(0,113,227,0.08);
        color: #0071e3;
        border: 1px solid rgba(0,113,227,0.18);
        border-radius: 4px;
        padding: 0.1rem 0.35rem;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        margin-left: auto;
    }

    .sb-new-chat-wrap {
        padding: 1rem 1.1rem 0.6rem;
    }

    .sb-search-wrap {
        padding: 0 1.1rem 0.8rem;
    }

    .sb-section-label {
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 0.9px;
        text-transform: uppercase;
        color: rgba(0,0,0,0.28);
        padding: 0.5rem 1.2rem 0.3rem;
    }

    .sb-chat-item {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.46rem 1.1rem;
        color: rgba(0,0,0,0.5);
        font-size: 0.82rem;
        font-weight: 400;
        cursor: pointer;
        border-radius: 8px;
        margin: 0.06rem 0.5rem;
        transition: all 0.15s ease;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .sb-chat-item:hover {
        background: rgba(0,0,0,0.05);
        color: rgba(0,0,0,0.75);
    }

    .sb-chat-item.active {
        background: rgba(0,113,227,0.08);
        color: #0071e3;
        font-weight: 500;
    }

    .sb-chat-icon {
        font-size: 0.85rem;
        opacity: 0.6;
        flex-shrink: 0;
    }

    .sb-doc-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.38rem 1.2rem;
        font-size: 0.78rem;
        color: rgba(0,0,0,0.42);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .sb-doc-dot {
        width: 5px; height: 5px;
        border-radius: 50%;
        background: #34c759;
        flex-shrink: 0;
        box-shadow: 0 0 5px rgba(52,199,89,0.5);
    }

    .sb-divider {
        height: 1px;
        background: rgba(0,0,0,0.06);
        margin: 0.6rem 1.2rem;
    }

    .sb-pinned-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.42rem 1.2rem;
        font-size: 0.81rem;
        color: rgba(0,0,0,0.45);
        cursor: pointer;
    }

    /* ── STREAMLIT BUTTON OVERRIDES ── */
    .stButton > button {
        background: #0071e3 !important;
        border: none !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        padding: 0.52rem 1rem !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 4px rgba(0,113,227,0.3) !important;
        letter-spacing: -0.1px !important;
    }

    .stButton > button:hover {
        background: #0077ed !important;
        box-shadow: 0 2px 10px rgba(0,113,227,0.4) !important;
        transform: translateY(-0.5px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        background: #006bd6 !important;
    }

    /* Secondary buttons */
    .secondary-btn > button {
        background: rgba(0,0,0,0.04) !important;
        color: rgba(0,0,0,0.6) !important;
        box-shadow: none !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
    }

    .secondary-btn > button:hover {
        background: rgba(0,0,0,0.07) !important;
        color: rgba(0,0,0,0.8) !important;
        box-shadow: none !important;
    }

    /* ── MAIN LAYOUT ── */
    .block-container {
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* ── MODE TABS ── */
    .mode-tabs-bar {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.85rem 1.5rem;
        background: #ffffff;
        border-bottom: 1px solid rgba(0,0,0,0.07);
        position: sticky;
        top: 0;
        z-index: 100;
        backdrop-filter: blur(12px);
    }

    .mode-tab {
        padding: 0.38rem 1.1rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 500;
        color: rgba(0,0,0,0.45);
        cursor: pointer;
        transition: all 0.15s ease;
        border: none;
        background: transparent;
        white-space: nowrap;
    }

    .mode-tab:hover {
        background: rgba(0,0,0,0.06);
        color: rgba(0,0,0,0.7);
    }

    .mode-tab.active {
        background: #0071e3;
        color: #ffffff;
        font-weight: 600;
        box-shadow: 0 1px 6px rgba(0,113,227,0.35);
    }

    .mode-tabs-pill-group {
        display: flex;
        background: rgba(0,0,0,0.05);
        border-radius: 999px;
        padding: 3px;
        gap: 0;
    }

    .mode-status-bar {
        padding: 0.45rem 1.5rem;
        background: rgba(0,113,227,0.04);
        border-bottom: 1px solid rgba(0,113,227,0.1);
        font-size: 0.74rem;
        color: rgba(0,0,0,0.4);
    }

    .mode-status-bar strong {
        color: #0071e3;
    }

    /* ── HERO ── */
    .hero {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 55vh;
        text-align: center;
        padding: 2rem 1.5rem;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1c1c1e;
        letter-spacing: -1.2px;
        line-height: 1.15;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: rgba(0,0,0,0.38);
        line-height: 1.6;
        margin-bottom: 2.8rem;
        max-width: 400px;
        font-weight: 400;
    }

    /* ── MODE CARDS ── */
    .mode-cards-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        width: 100%;
        max-width: 780px;
        margin: 0 auto;
    }

    .mode-card {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.07);
        border-radius: 18px;
        padding: 1.4rem 1rem 1.2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05), 0 4px 16px rgba(0,0,0,0.04);
    }

    .mode-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1), 0 1px 6px rgba(0,0,0,0.06);
        border-color: rgba(0,113,227,0.2);
    }

    .mode-card-icon {
        font-size: 1.6rem;
        margin-bottom: 0.7rem;
        display: block;
        filter: grayscale(0.2);
    }

    .mode-card-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #1c1c1e;
        margin-bottom: 0.38rem;
        letter-spacing: -0.2px;
    }

    .mode-card-desc {
        font-size: 0.74rem;
        color: rgba(0,0,0,0.38);
        line-height: 1.5;
        font-weight: 400;
    }

    /* ── DOCUMENT CONTEXT BANNER ── */
    .doc-context-bar {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.55rem 1rem;
        background: rgba(0,113,227,0.05);
        border: 1px solid rgba(0,113,227,0.1);
        border-radius: 12px;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }

    .doc-context-label {
        font-size: 0.63rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        color: rgba(0,113,227,0.6);
        flex-shrink: 0;
    }

    .doc-context-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.14rem 0.5rem;
        background: rgba(0,113,227,0.08);
        border: 1px solid rgba(0,113,227,0.15);
        border-radius: 999px;
        font-size: 0.7rem;
        color: #0071e3;
        font-weight: 500;
    }

    /* ── MESSAGES ── */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0.5rem 0 !important;
        margin: 0 !important;
    }

    [data-testid="chatAvatarIcon-user"],
    [data-testid="chatAvatarIcon-assistant"] { display: none !important; }

    /* User message — right-aligned blue bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        display: flex !important;
        justify-content: flex-end !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown p {
        background: #0071e3 !important;
        color: #ffffff !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 0.65rem 1.05rem !important;
        display: inline-block !important;
        font-size: 0.88rem !important;
        max-width: 72% !important;
        line-height: 1.6 !important;
        font-weight: 400 !important;
        box-shadow: 0 2px 8px rgba(0,113,227,0.2) !important;
    }

    /* Assistant message */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #ffffff !important;
        border-radius: 16px !important;
        padding: 1rem 1.2rem !important;
        margin: 0.4rem 0 !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        color: #1c1c1e !important;
        font-size: 0.88rem !important;
        line-height: 1.75 !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown p {
        color: #1c1c1e !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown strong {
        color: #0071e3 !important;
        font-weight: 600 !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown h1,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown h2,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown h3 {
        color: #1c1c1e !important;
        font-weight: 700 !important;
        margin-top: 0.8rem !important;
        letter-spacing: -0.3px !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown li {
        color: rgba(0,0,0,0.7) !important;
        margin-bottom: 0.22rem !important;
    }

    /* ── SOURCES PANEL ── */
    .sources-panel {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.07);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        height: fit-content;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    }

    .sources-panel-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #1c1c1e;
        letter-spacing: -0.2px;
        margin-bottom: 0.3rem;
    }

    .sources-panel-sub {
        font-size: 0.68rem;
        color: rgba(0,0,0,0.35);
        margin-bottom: 0.8rem;
    }

    .source-ref-item {
        background: #f5f5f7;
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.5rem;
        font-size: 0.76rem;
        color: rgba(0,0,0,0.6);
        line-height: 1.45;
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.15s ease;
    }

    .source-ref-item:hover {
        border-color: rgba(0,113,227,0.2);
        background: rgba(0,113,227,0.03);
        color: #0071e3;
    }

    .source-ref-num {
        font-weight: 700;
        color: #0071e3;
        margin-right: 0.3rem;
    }

    /* ── INPUT BAR ── */
    .input-wrapper {
        position: fixed;
        bottom: 0;
        left: 260px;
        right: 0;
        background: linear-gradient(to top, #f0f0f2 60%, transparent);
        padding: 0 2rem 1.6rem;
        z-index: 999;
    }

    .input-box {
        max-width: 760px;
        margin: 0 auto;
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.1);
        border-radius: 18px;
        box-shadow: 0 2px 20px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
        transition: border-color 0.2s, box-shadow 0.2s;
        overflow: hidden;
    }

    .input-box:focus-within {
        border-color: rgba(0,113,227,0.35);
        box-shadow: 0 2px 20px rgba(0,0,0,0.08), 0 0 0 3px rgba(0,113,227,0.1);
    }

    [data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #1c1c1e !important;
        font-size: 0.9rem !important;
        padding: 0.9rem 1.1rem 0.65rem !important;
        min-height: 50px !important;
        line-height: 1.55 !important;
        caret-color: #0071e3 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: rgba(0,0,0,0.25) !important;
    }

    [data-testid="stChatInput"] button {
        background: #0071e3 !important;
        border-radius: 10px !important;
        margin: 0.38rem !important;
        box-shadow: 0 1px 6px rgba(0,113,227,0.3) !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stChatInput"] button:hover {
        background: #0077ed !important;
        box-shadow: 0 2px 10px rgba(0,113,227,0.4) !important;
    }

    .input-bottom {
        border-top: 1px solid rgba(0,0,0,0.05);
        padding: 0.3rem 0.8rem 0.5rem;
    }

    /* ── FILE UPLOADER ── */
    [data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    [data-testid="stFileUploader"] > div:first-child,
    [data-testid="stFileUploader"] section {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    [data-testid="stFileUploader"] section button {
        background: rgba(0,0,0,0.04) !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 8px !important;
        color: rgba(0,0,0,0.45) !important;
        font-size: 0.72rem !important;
        padding: 0.24rem 0.65rem !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stFileUploader"] section button:hover {
        background: rgba(0,113,227,0.06) !important;
        border-color: rgba(0,113,227,0.2) !important;
        color: #0071e3 !important;
    }

    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] span {
        color: rgba(0,0,0,0.28) !important;
        font-size: 0.68rem !important;
    }

    /* ── MISC ── */
    [data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.07) !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    }

    [data-testid="stExpander"] summary {
        color: rgba(0,0,0,0.4) !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
    }

    .stSpinner > div { border-top-color: #0071e3 !important; }
    .stCaption { color: rgba(0,0,0,0.3) !important; font-size: 0.72rem !important; }
    hr { border-color: rgba(0,0,0,0.07) !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.12); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.22); }

    /* Success / warning / error messages */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
        font-size: 0.82rem !important;
    }

    /* Checkbox */
    [data-testid="stCheckbox"] label {
        font-size: 0.82rem !important;
        color: rgba(0,0,0,0.55) !important;
    }

    /* Spacer */
    .spacer-bottom { height: 140px; }

    /* Main chat area padding */
    .main-chat-area {
        padding: 0 1.5rem;
        max-width: 820px;
        margin: 0 auto;
    }

    /* Mobile */
    @media (max-width: 768px) {
        .input-wrapper { left: 0 !important; padding: 0 1rem 1.4rem !important; }
        .block-container { padding: 0 !important; }
        .hero-title { font-size: 1.8rem !important; }
        .mode-cards-grid { grid-template-columns: repeat(2, 1fr) !important; }
    }
    </style>
    """, unsafe_allow_html=True)