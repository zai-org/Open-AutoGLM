"""Trajectory recorder for PhoneAgent operations.

This module provides functionality to record screenshots, actions, and context
during agent execution for debugging, analysis, and replay purposes.
"""

import json
import os
import shutil
import base64
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class StepRecord:
    """Record of a single agent step."""

    step_number: int
    timestamp: str
    screenshot_filename: Optional[str]
    action: Optional[dict[str, Any]]
    thinking: str
    current_app: Optional[str]
    screen_width: int
    screen_height: int
    context_snapshot: Optional[list[dict[str, Any]]] = None
    message: Optional[str] = None
    success: bool = True


@dataclass
class TrajectorySummary:
    """Summary of a complete agent trajectory."""

    task: str
    start_time: str
    end_time: Optional[str]
    total_steps: int
    success: bool
    final_message: Optional[str]
    record_dir: str


class TrajectoryRecorder:
    """Records agent trajectory including screenshots, actions, and context.

    The recorder saves data to a directory structure like:
        trajectories/
            2024-01-15_14-30-22_task_description/
                summary.json
                step_001.png
                step_001.json
                step_002.png
                step_002.json
                ...
    """

    def __init__(
        self,
        output_dir: str = "trajectories",
        save_screenshots: bool = True,
        save_context: bool = True,
        max_trajectories: Optional[int] = None,
    ):
        """Initialize the trajectory recorder.

        Args:
            output_dir: Base directory to save trajectories.
            save_screenshots: Whether to save screenshot images.
            save_context: Whether to save full context snapshots.
            max_trajectories: Maximum number of trajectories to keep (oldest removed).
        """
        self.output_dir = Path(output_dir)
        self.save_screenshots = save_screenshots
        self.save_context = save_context
        self.max_trajectories = max_trajectories

        self._record_dir: Optional[Path] = None
        self._task: Optional[str] = None
        self._start_time: Optional[str] = None
        self._steps: list[StepRecord] = []
        self._current_step = 0

    def start_session(self, task: str, task_name: Optional[str] = None) -> str:
        """Start a new trajectory recording session.

        Args:
            task: The task description.
            task_name: Optional short name for the directory (sanitized).

        Returns:
            Path to the record directory.
        """
        self._task = task
        self._start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._steps = []
        self._current_step = 0

        # Create directory name
        if task_name:
            safe_name = self._sanitize_filename(task_name)
            dir_name = f"{self._start_time}_{safe_name}"
        else:
            safe_task = self._sanitize_filename(task[:30])
            dir_name = f"{self._start_time}_{safe_task}"

        self._record_dir = self.output_dir / dir_name
        self._record_dir.mkdir(parents=True, exist_ok=True)

        # Cleanup old trajectories if needed
        if self.max_trajectories:
            self._cleanup_old_trajectories()

        return str(self._record_dir)

    def record_step(
        self,
        screenshot_base64: Optional[str] = None,
        action: Optional[dict[str, Any]] = None,
        thinking: str = "",
        current_app: Optional[str] = None,
        screen_width: int = 0,
        screen_height: int = 0,
        context: Optional[list[dict[str, Any]]] = None,
        message: Optional[str] = None,
        success: bool = True,
    ) -> str:
        """Record a single step of the agent.

        Args:
            screenshot_base64: Base64-encoded screenshot image.
            action: The action executed in this step.
            thinking: The model's thinking process.
            current_app: Name of the current app.
            screen_width: Screen width in pixels.
            screen_height: Screen height in pixels.
            context: Optional full context snapshot.
            message: Optional result message.
            success: Whether the step succeeded.

        Returns:
            Path to the saved step data file.
        """
        if not self._record_dir:
            raise RuntimeError("Session not started. Call start_session() first.")

        self._current_step += 1
        step_num = self._current_step

        # Save screenshot
        screenshot_filename = None
        if self.save_screenshots and screenshot_base64:
            screenshot_filename = f"step_{step_num:03d}.png"
            screenshot_path = self._record_dir / screenshot_filename
            self._save_base64_image(screenshot_base64, screenshot_path)

        # Save context if needed
        context_snapshot = None
        if self.save_context and context:
            context_snapshot = context

        # Create step record
        record = StepRecord(
            step_number=step_num,
            timestamp=datetime.now().isoformat(),
            screenshot_filename=screenshot_filename,
            action=action,
            thinking=thinking,
            current_app=current_app,
            screen_width=screen_width,
            screen_height=screen_height,
            context_snapshot=context_snapshot,
            message=message,
            success=success,
        )

        self._steps.append(record)

        # Save step data
        step_filename = f"step_{step_num:03d}.json"
        step_path = self._record_dir / step_filename
        with open(step_path, "w", encoding="utf-8") as f:
            json.dump(asdict(record), f, ensure_ascii=False, indent=2)

        return str(step_path)

    def end_session(
        self, success: bool = True, final_message: Optional[str] = None
    ) -> TrajectorySummary:
        """End the trajectory recording session and save summary.

        Args:
            success: Whether the overall task succeeded.
            final_message: Final result message.

        Returns:
            TrajectorySummary with session details.
        """
        if not self._record_dir:
            raise RuntimeError("Session not started. Call start_session() first.")

        summary = TrajectorySummary(
            task=self._task or "",
            start_time=self._start_time or "",
            end_time=datetime.now().isoformat(),
            total_steps=self._current_step,
            success=success,
            final_message=final_message,
            record_dir=str(self._record_dir),
        )

        # Save summary
        summary_path = self._record_dir / "summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(asdict(summary), f, ensure_ascii=False, indent=2)

        return summary

    def get_steps(self) -> list[StepRecord]:
        """Get all recorded steps."""
        return self._steps.copy()

    def get_record_dir(self) -> Optional[str]:
        """Get the current record directory."""
        return str(self._record_dir) if self._record_dir else None

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize a string for use in a filename."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, "_")
        name = name.replace("\n", " ").replace("\r", "")
        return name.strip()[:50]

    @staticmethod
    def _save_base64_image(base64_data: str, output_path: Path) -> None:
        """Save a base64-encoded image to file."""
        # Strip data URI prefix if present
        if "," in base64_data:
            base64_data = base64_data.split(",", 1)[1]

        image_data = base64.b64decode(base64_data)
        with open(output_path, "wb") as f:
            f.write(image_data)

    def _cleanup_old_trajectories(self) -> None:
        """Remove old trajectories to stay under max_trajectories limit."""
        if not self.output_dir.exists():
            return

        # Get all trajectory directories sorted by creation time
        trajectories = []
        for item in self.output_dir.iterdir():
            if item.is_dir():
                trajectories.append((item.stat().st_ctime, item))

        trajectories.sort()  # Oldest first

        # Remove excess
        while len(trajectories) >= self.max_trajectories:
            _, old_dir = trajectories.pop(0)
            try:
                shutil.rmtree(old_dir)
            except Exception:
                pass


def load_trajectory(record_dir: str) -> tuple[TrajectorySummary, list[StepRecord]]:
    """Load a recorded trajectory from disk.

    Args:
        record_dir: Path to the trajectory directory.

    Returns:
        Tuple of (TrajectorySummary, list[StepRecord])
    """
    record_path = Path(record_dir)

    # Load summary
    summary_path = record_path / "summary.json"
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_dict = json.load(f)
    summary = TrajectorySummary(**summary_dict)

    # Load steps
    steps = []
    step_files = sorted(record_path.glob("step_*.json"))
    for step_file in step_files:
        with open(step_file, "r", encoding="utf-8") as f:
            step_dict = json.load(f)
        steps.append(StepRecord(**step_dict))

    return summary, steps


class DummyTrajectoryRecorder(TrajectoryRecorder):
    """A no-op trajectory recorder that doesn't save anything.

    Useful as a drop-in replacement when trajectory recording is disabled.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start_session(self, task: str, task_name: Optional[str] = None) -> str:
        return ""

    def record_step(self, *args, **kwargs) -> str:
        return ""

    def end_session(self, *args, **kwargs) -> TrajectorySummary:
        return TrajectorySummary(
            task="",
            start_time="",
            end_time="",
            total_steps=0,
            success=True,
            final_message=None,
            record_dir="",
        )

    def get_steps(self) -> list[StepRecord]:
        return []

    def get_record_dir(self) -> Optional[str]:
        return None
