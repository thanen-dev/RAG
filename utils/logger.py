# ── utils/logger.py ───────────────────────────────────────────
# Centralized logging configuration for the application.

import logging
import sys
from datetime import datetime
from pathlib import Path
import os

def setup_logging():
    """Set up centralized logging with file and console output."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"rag_app_{timestamp}.log"
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # More detailed logging to file
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return root_logger

def log_user_action(action: str, details: str = ""):
    """Log user actions for monitoring."""
    logger = logging.getLogger("user_actions")
    if details:
        logger.info(f"USER_ACTION: {action} - {details}")
    else:
        logger.info(f"USER_ACTION: {action}")

def log_performance(operation: str, duration_ms: float, details: str = ""):
    """Log performance metrics."""
    logger = logging.getLogger("performance")
    if details:
        logger.info(f"PERF: {operation} took {duration_ms:.2f}ms - {details}")
    else:
        logger.info(f"PERF: {operation} took {duration_ms:.2f}ms")

def log_error(error_type: str, error_message: str, context: str = ""):
    """Log errors with context."""
    logger = logging.getLogger("errors")
    if context:
        logger.error(f"ERROR [{error_type}]: {error_message} - Context: {context}")
    else:
        logger.error(f"ERROR [{error_type}]: {error_message}")

# Initialize logging when module is imported
setup_logging()
