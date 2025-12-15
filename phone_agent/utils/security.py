"""Security utilities for Phone Agent."""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates and sanitizes user input."""

    # Regex patterns for security checks
    PATTERNS = {
        "sql_injection": r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)",
        "script_injection": r"(<script|javascript:|onerror=|onclick=)",
        "path_traversal": r"(\.\./|\.\.\\)",
    }

    @staticmethod
    def validate_text_input(text: str, max_length: int = 1000) -> bool:
        """
        Validate text input for safety.

        Args:
            text: Input text to validate.
            max_length: Maximum allowed length.

        Returns:
            True if valid, False otherwise.
        """
        if not isinstance(text, str):
            logger.warning("Input must be a string")
            return False

        if len(text) > max_length:
            logger.warning(f"Input exceeds maximum length of {max_length}")
            return False

        # Check for dangerous patterns
        for pattern_name, pattern in InputValidator.PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential {pattern_name} detected in input")
                return False

        return True

    @staticmethod
    def sanitize_app_name(app_name: str) -> Optional[str]:
        """
        Sanitize application name.

        Args:
            app_name: Application name to sanitize.

        Returns:
            Sanitized app name or None if invalid.
        """
        if not isinstance(app_name, str):
            return None

        # Allow only alphanumeric, spaces, and common punctuation
        sanitized = re.sub(r"[^a-zA-Z0-9\s\-_]", "", app_name).strip()

        if not sanitized:
            logger.warning("App name becomes empty after sanitization")
            return None

        if len(sanitized) > 256:
            logger.warning("App name exceeds maximum length")
            return None

        return sanitized

    @staticmethod
    def sanitize_coordinates(x: int, y: int, max_x: int = 2000, max_y: int = 2000) -> bool:
        """
        Validate screen coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.
            max_x: Maximum X value.
            max_y: Maximum Y value.

        Returns:
            True if valid, False otherwise.
        """
        if not isinstance(x, int) or not isinstance(y, int):
            logger.warning("Coordinates must be integers")
            return False

        if x < 0 or x > max_x or y < 0 or y > max_y:
            logger.warning(f"Coordinates out of bounds: ({x}, {y})")
            return False

        return True


class SensitiveDataFilter:
    """Filter and mask sensitive data in logs."""

    # Patterns for sensitive data
    SENSITIVE_PATTERNS = {
        "phone": r"\b1[0-9]{10}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "api_key": r"(api[_-]?key|apikey)[\s]*[:=][\s]*['\"]?([^\s'\"]+)['\"]?",
        "password": r"(password|passwd|pwd)[\s]*[:=][\s]*['\"]?([^\s'\"]+)['\"]?",
    }

    @staticmethod
    def mask_sensitive_data(text: str) -> str:
        """
        Mask sensitive data in text.

        Args:
            text: Text to process.

        Returns:
            Text with sensitive data masked.
        """
        if not isinstance(text, str):
            return text

        result = text
        for pattern_name, pattern in SensitiveDataFilter.SENSITIVE_PATTERNS.items():
            result = re.sub(
                pattern,
                lambda m: f"[{pattern_name.upper()}_REDACTED]",
                result,
                flags=re.IGNORECASE,
            )

        return result

    @staticmethod
    def filter_log_message(message: str) -> str:
        """
        Filter sensitive data from log messages.

        Args:
            message: Log message.

        Returns:
            Filtered log message.
        """
        return SensitiveDataFilter.mask_sensitive_data(message)


class RateLimiter:
    """Rate limiting for API calls."""

    def __init__(self, max_calls: int = 100, time_window: int = 60) -> None:
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum calls allowed.
            time_window: Time window in seconds.
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def is_allowed(self) -> bool:
        """
        Check if action is allowed.

        Returns:
            True if within rate limit, False otherwise.
        """
        import time

        now = time.time()

        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True

        logger.warning(
            f"Rate limit exceeded: {len(self.calls)} calls in {self.time_window}s"
        )
        return False

    def get_reset_time(self) -> float:
        """Get time until rate limit resets."""
        if not self.calls:
            return 0.0

        import time

        oldest_call = min(self.calls)
        reset_time = oldest_call + self.time_window - time.time()
        return max(0.0, reset_time)
