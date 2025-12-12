"""Logging utilities for phone_agent."""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def get_logger(
    name: str = "phone_agent",
    level: Optional[int] = None,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (default: "phone_agent").
        level: Logging level (default: INFO).
        use_colors: Whether to use colored output (default: True).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers
    if logger.handlers:
        return logger

    # Set level
    if level is None:
        level = logging.INFO
    logger.setLevel(level)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create formatter
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

