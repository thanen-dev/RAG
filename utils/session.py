# ── utils/session.py ───────────────────────────────────────────
# Session persistence: chat history, document names, vectorstore ID.

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_SESSIONS_DIR   = Path("sessions")
_CURRENT_FILE   = _SESSIONS_DIR / "current_session.json"
_SESSION_VERSION = "1.2"


def _ensure_dir():
    _SESSIONS_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────

def save_current_session(
    chat_history: List[Dict],
    doc_names: List[str],
    debug_mode: bool = False,
    collection_id: str = "",
) -> bool:
    """Persist the current session state to disk."""
    _ensure_dir()
    try:
        data = {
            "version":      _SESSION_VERSION,
            "timestamp":    time.time(),
            "chat_history": chat_history,
            "doc_names":    doc_names,
            "debug_mode":   debug_mode,
            "collection_id": collection_id,   # NEW — lets us reload the vectorstore
        }
        _CURRENT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"Session saved: {len(chat_history)} msgs, {len(doc_names)} docs, id={collection_id[:8] or 'none'}")
        return True
    except Exception as exc:
        logger.error(f"Failed to save session: {exc}")
        return False


def load_current_session() -> Dict[str, Any]:
    """Load session state from disk. Returns empty dict if nothing saved."""
    try:
        if not _CURRENT_FILE.exists():
            return {}
        data = json.loads(_CURRENT_FILE.read_text(encoding="utf-8"))
        logger.info(
            f"Session loaded: {len(data.get('chat_history', []))} msgs, "
            f"collection_id={data.get('collection_id','')[:8] or 'none'}"
        )
        return data
    except Exception as exc:
        logger.error(f"Failed to load session: {exc}")
        return {}


def clear_current_session() -> bool:
    """Delete the saved session file."""
    try:
        if _CURRENT_FILE.exists():
            _CURRENT_FILE.unlink()
            logger.info("Session cleared.")
        return True
    except Exception as exc:
        logger.error(f"Failed to clear session: {exc}")
        return False


def archive_current_session() -> bool:
    """Move the current session to an archive file with a timestamp."""
    try:
        if not _CURRENT_FILE.exists():
            return True
        stamp = time.strftime("%Y%m%d_%H%M%S")
        _CURRENT_FILE.rename(_SESSIONS_DIR / f"session_{stamp}.json")
        logger.info(f"Session archived as session_{stamp}.json")
        return True
    except Exception as exc:
        logger.error(f"Failed to archive session: {exc}")
        return False


def get_session_info() -> Dict[str, Any]:
    """Return a summary dict for display purposes."""
    data = load_current_session()
    if not data:
        return {"status": "no_session"}
    return {
        "status":        "active",
        "messages":      len(data.get("chat_history", [])),
        "documents":     len(data.get("doc_names", [])),
        "collection_id": data.get("collection_id", ""),
        "timestamp":     data.get("timestamp"),
        "debug_mode":    data.get("debug_mode", False),
    }