"""Logging and monitoring utilities for Phone Agent."""

import logging
import logging.handlers
import time
from pathlib import Path
from typing import Optional

from phone_agent.utils.cache import SimpleCache


class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self) -> None:
        """Initialize performance monitor."""
        self.logger = logging.getLogger(__name__)
        self._metrics: SimpleCache = SimpleCache(ttl=3600)
        self._start_times: dict[str, float] = {}

    def start_timer(self, name: str) -> None:
        """Start a named timer."""
        self._start_times[name] = time.time()

    def end_timer(self, name: str) -> float:
        """
        End a named timer and record duration.

        Args:
            name: Timer name.

        Returns:
            Duration in seconds.
        """
        if name not in self._start_times:
            self.logger.warning(f"Timer '{name}' was not started")
            return 0.0

        duration = time.time() - self._start_times[name]
        del self._start_times[name]

        # Store metric
        metrics = self._metrics.get(name) or []
        metrics.append(duration)
        self._metrics.set(name, metrics)

        return duration

    def get_metrics(self, name: str) -> Optional[list[float]]:
        """Get recorded metrics for a timer."""
        return self._metrics.get(name)

    def get_average(self, name: str) -> float:
        """Get average duration for a timer."""
        metrics = self.get_metrics(name)
        if not metrics:
            return 0.0
        return sum(metrics) / len(metrics)

    def print_report(self) -> None:
        """Print performance report."""
        print("\n" + "=" * 60)
        print("📊 Performance Report")
        print("=" * 60)

        for key, metrics in self._metrics._cache.items():
            if isinstance(metrics[0], list):
                data = metrics[0]
                print(f"\n{key}:")
                print(f"  Count: {len(data)}")
                print(f"  Average: {sum(data) / len(data):.3f}s")
                print(f"  Min: {min(data):.3f}s")
                print(f"  Max: {max(data):.3f}s")

        print("=" * 60 + "\n")


class LoggerSetup:
    """Setup and configure logging."""

    @staticmethod
    def setup_logging(
        name: str = "phone_agent",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        verbose: bool = False,
    ) -> logging.Logger:
        """
        Setup logging configuration.

        Args:
            name: Logger name.
            level: Logging level.
            log_file: Optional log file path.
            verbose: Enable verbose logging.

        Returns:
            Configured logger.
        """
        logger = logging.getLogger(name)
        
        if verbose:
            level = logging.DEBUG

        logger.setLevel(level)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10 * 1024 * 1024, backupCount=5
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get or create a logger with the given name."""
        return logging.getLogger(name)


# Global performance monitor instance
_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    return _monitor
