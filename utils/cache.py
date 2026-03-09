# ── utils/cache.py ───────────────────────────────────────────
# Simple caching system for query results to improve performance.

import hashlib
import time
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class QueryCache:
    """Simple in-memory cache for query results with TTL."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        
    def _generate_key(self, question: str, doc_names: Tuple[str, ...]) -> str:
        """Generate a cache key based on question and document context."""
        # Create a deterministic key from question and document names
        content = f"{question}|{'|'.join(sorted(doc_names))}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, question: str, doc_names: Tuple[str, ...]) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        key = self._generate_key(question, doc_names)
        
        if key not in self.cache:
            return None
            
        entry = self.cache[key]
        
        # Check if expired
        if time.time() - entry["timestamp"] > self.ttl_seconds:
            del self.cache[key]
            logger.debug(f"Cache entry expired for key: {key}")
            return None
            
        logger.debug(f"Cache hit for question: {question[:50]}...")
        return entry["data"]
    
    def set(self, question: str, doc_names: Tuple[str, ...], data: Dict[str, Any]) -> None:
        """Cache a result with timestamp."""
        key = self._generate_key(question, doc_names)
        
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
            logger.debug(f"Evicted oldest cache entry: {oldest_key}")
        
        self.cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
        logger.debug(f"Cached result for question: {question[:50]}...")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }

# Global cache instance
query_cache = QueryCache()

def get_cached_result(question: str, doc_names: Tuple[str, ...]) -> Optional[Dict[str, Any]]:
    """Get cached result for a query."""
    return query_cache.get(question, doc_names)

def cache_result(question: str, doc_names: Tuple[str, ...], answer: str, relevant_docs: list, debug_info: Dict[str, Any]) -> None:
    """Cache a query result."""
    data = {
        "answer": answer,
        "relevant_docs": relevant_docs,
        "debug_info": debug_info
    }
    query_cache.set(question, doc_names, data)

def clear_cache() -> None:
    """Clear the query cache."""
    query_cache.clear()

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return query_cache.get_stats()
