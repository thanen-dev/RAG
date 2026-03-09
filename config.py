import os
from dotenv import load_dotenv

load_dotenv()

# --- API ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def validate_config():
    errors = []
    if not GROQ_API_KEY:
        errors.append("GROQ_API_KEY is required. Set it in your .env file.")
    return errors

# --- MODEL ---
LLM_MODEL = os.getenv("LLM_MODEL", "moonshotai/kimi-k2-instruct")

# --- EMBEDDING ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# --- RAG SETTINGS ---
# Smaller chunks = more precise retrieval, better for specific document Q&A
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE",    "800"))   # was 1500 — too large
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))   # was 200
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "6"))     # was 8 — fewer, more precise

# --- APP INFO ---
APP_NAME = os.getenv("APP_NAME", "StudyMind")
APP_ICON = os.getenv("APP_ICON", "🧠")