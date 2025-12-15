"""Performance metrics collection and reporting."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class StepMetrics:
    """Metrics for a single agent step."""

    screenshot_time: float = 0.0
    model_inference_time: float = 0.0
    action_execution_time: float = 0.0
    total_time: float = 0.0
    step_number: int = 0
    action_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "step": self.step_number,
            "action_type": self.action_type,
            "screenshot_ms": round(self.screenshot_time * 1000, 2),
            "inference_ms": round(self.model_inference_time * 1000, 2),
            "execution_ms": round(self.action_execution_time * 1000, 2),
            "total_ms": round(self.total_time * 1000, 2),
        }

    def __str__(self) -> str:
        """String representation of metrics."""
        return (
            f"Step {self.step_number} ({self.action_type}): "
            f"Screenshot={self.screenshot_time*1000:.1f}ms, "
            f"Inference={self.model_inference_time*1000:.1f}ms, "
            f"Execution={self.action_execution_time*1000:.1f}ms, "
            f"Total={self.total_time*1000:.1f}ms"
        )


@dataclass
class SessionMetrics:
    """Metrics for an entire agent session."""

    total_steps: int = 0
    total_time: float = 0.0
    steps: list[StepMetrics] = field(default_factory=list)
    start_time: float = 0.0

    def add_step(self, step_metric: StepMetrics) -> None:
        """Add a step's metrics."""
        self.steps.append(step_metric)
        self.total_steps = len(self.steps)

    def finalize(self) -> None:
        """Calculate final metrics."""
        if self.start_time > 0:
            self.total_time = time.time() - self.start_time

    def get_average_times(self) -> Dict[str, float]:
        """Get average times for each operation."""
        if not self.steps:
            return {}

        avg_screenshot = sum(s.screenshot_time for s in self.steps) / len(self.steps)
        avg_inference = sum(s.model_inference_time for s in self.steps) / len(self.steps)
        avg_execution = sum(s.action_execution_time for s in self.steps) / len(self.steps)

        return {
            "avg_screenshot_ms": round(avg_screenshot * 1000, 2),
            "avg_inference_ms": round(avg_inference * 1000, 2),
            "avg_execution_ms": round(avg_execution * 1000, 2),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_steps": self.total_steps,
            "total_time_s": round(self.total_time, 2),
            "steps": [step.to_dict() for step in self.steps],
            "averages": self.get_average_times(),
        }

    def print_summary(self) -> None:
        """Print a summary of the session metrics."""
        logger.info("=" * 60)
        logger.info("📊 Session Metrics Summary")
        logger.info("=" * 60)
        logger.info(f"Total Steps: {self.total_steps}")
        logger.info(f"Total Time: {self.total_time:.2f}s")

        averages = self.get_average_times()
        logger.info(f"Average Screenshot Time: {averages.get('avg_screenshot_ms', 0):.1f}ms")
        logger.info(f"Average Inference Time: {averages.get('avg_inference_ms', 0):.1f}ms")
        logger.info(f"Average Execution Time: {averages.get('avg_execution_ms', 0):.1f}ms")
        logger.info("=" * 60)


class MetricsCollector:
    """Context manager for collecting metrics."""

    def __init__(self) -> None:
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def __enter__(self) -> "MetricsCollector":
        """Enter context and start timer."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and record elapsed time."""
        self.end_time = time.time()

    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.end_time == 0:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return self.elapsed * 1000
