"""Logging configuration for Phone Agent."""

import logging
import sys
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Package-level logger
logger = logging.getLogger("phone_agent")


def init_logger(
    level: LogLevel | str = "INFO",
    format_string: str | None = None,
) -> logging.Logger:
    """
    Initialize the phone_agent logger with the specified configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format_string: Custom format string for log messages.
            Defaults to: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    Returns:
        The configured logger instance.

    Example:
        >>> from phone_agent.logger import init_logger
        >>> logger = init_logger("DEBUG")
        >>> logger.debug("Debug message")
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Convert string level to logging constant
    if isinstance(level, str):
        level = level.upper()
        numeric_level = getattr(logging, level, logging.INFO)
    else:
        numeric_level = level

    # Configure the logger
    logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicate logs
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(numeric_level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger
