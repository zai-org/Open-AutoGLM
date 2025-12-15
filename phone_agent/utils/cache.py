"""Caching utilities for Phone Agent."""

import hashlib
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, ttl: int = 300) -> None:
        """
        Initialize cache.

        Args:
            ttl: Time to live in seconds (default: 5 minutes).
        """
        self.ttl = ttl
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Cached value or None if expired/missing.
        """
        if key not in self._cache:
            self._misses += 1
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > self.ttl:
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
        """
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        logger.debug("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate": f"{hit_rate:.1f}%",
            "size": len(self._cache),
        }


class ScreenshotCache:
    """Cache for device screenshots."""

    def __init__(self, max_size: int = 5) -> None:
        """
        Initialize screenshot cache.

        Args:
            max_size: Maximum number of screenshots to cache.
        """
        self.max_size = max_size
        self._cache: Dict[str, tuple[Any, float]] = {}

    def get_hash(self, data: bytes) -> str:
        """Calculate hash of screenshot data."""
        return hashlib.md5(data).hexdigest()

    def get(self, device_id: Optional[str] = None) -> Optional[Any]:
        """Get cached screenshot for device."""
        key = device_id or "default"
        if key in self._cache:
            screenshot, timestamp = self._cache[key]
            logger.debug(f"Retrieved cached screenshot for {key}")
            return screenshot
        return None

    def set(self, screenshot: Any, device_id: Optional[str] = None) -> None:
        """Cache screenshot for device."""
        key = device_id or "default"
        
        # Keep cache size under control
        if len(self._cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        
        self._cache[key] = (screenshot, time.time())
        logger.debug(f"Cached screenshot for {key}")

    def is_different(self, new_data: bytes, device_id: Optional[str] = None) -> bool:
        """Check if new screenshot is different from cached one."""
        key = device_id or "default"
        if key not in self._cache:
            return True
        
        # Compare hashes for efficiency
        cached_screenshot, _ = self._cache[key]
        if hasattr(cached_screenshot, 'raw_data'):
            old_hash = self.get_hash(cached_screenshot.raw_data)
            new_hash = self.get_hash(new_data)
            return old_hash != new_hash
        
        return True

    def clear(self) -> None:
        """Clear screenshot cache."""
        self._cache.clear()
        logger.debug("Screenshot cache cleared")
