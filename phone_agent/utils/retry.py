"""Retry utilities for network operations and ADB commands."""

import subprocess
import time
from functools import wraps
from typing import Any, Callable, TypeVar

from phone_agent.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3).
        delay: Initial delay between retries in seconds (default: 1.0).
        backoff: Multiplier for delay after each retry (default: 2.0).
        exceptions: Tuple of exceptions to catch and retry on (default: all exceptions).
        on_retry: Optional callback function called on each retry.
            Receives (exception, attempt_number) as arguments.

    Returns:
        Decorated function.

    Example:
        >>> @retry(max_attempts=3, delay=1.0)
        ... def unreliable_function():
        ...     # May fail sometimes
        ...     pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {current_delay}s..."
                    )

                    if on_retry:
                        on_retry(e, attempt)

                    time.sleep(current_delay)
                    current_delay *= backoff

            # Should never reach here, but for type checking
            raise last_exception  # type: ignore

        return wrapper

    return decorator


def retry_adb_command(
    max_attempts: int = 3,
    delay: float = 1.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Specialized retry decorator for ADB commands.

    Retries on common ADB failures like connection errors.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3).
        delay: Initial delay between retries in seconds (default: 1.0).

    Returns:
        Decorated function.
    """
    return retry(
        max_attempts=max_attempts,
        delay=delay,
        exceptions=(
            ConnectionError,
            TimeoutError,
            OSError,
            subprocess.TimeoutExpired,
        ),
    )

