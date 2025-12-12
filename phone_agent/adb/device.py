"""Device control utilities for Android automation."""

import subprocess
import time
from typing import List

from phone_agent.config.apps import APP_PACKAGES
from phone_agent.logger import logger


def _run_adb_command(
    cmd: List[str], capture_output: bool = True, text: bool = False
) -> subprocess.CompletedProcess:
    """
    Run an ADB command and print it for debugging.

    Args:
        cmd: The command list to execute.
        capture_output: Whether to capture stdout/stderr.
        text: Whether to decode output as text.

    Returns:
        The CompletedProcess result.
    """
    cmd_str = " ".join(cmd)
    logger.debug(f"[ADB] {cmd_str}")
    return subprocess.run(cmd, capture_output=capture_output, text=text)


def get_current_app(device_id: str | None = None) -> str:
    """
    Get the currently focused app name.

    Args:
        device_id: Optional ADB device ID for multi-device setups.

    Returns:
        The app name if recognized, otherwise "System Home".
    """
    adb_prefix = _get_adb_prefix(device_id)

    result = _run_adb_command(
        adb_prefix + ["shell", "dumpsys", "window"], capture_output=True, text=True
    )
    output = result.stdout

    # Parse window focus info
    for line in output.split("\n"):
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            for app_name, package in APP_PACKAGES.items():
                if package in line:
                    return app_name

    return "System Home"


def tap(x: int, y: int, device_id: str | None = None, delay: float = 1.0) -> None:
    """
    Tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after tap.
    """
    adb_prefix = _get_adb_prefix(device_id)
    _run_adb_command(adb_prefix + ["shell", "input", "tap", str(x), str(y)])
    time.sleep(delay)


def double_tap(
    x: int, y: int, device_id: str | None = None, delay: float = 1.0
) -> None:
    """
    Double tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after double tap.
    """
    adb_prefix = _get_adb_prefix(device_id)

    _run_adb_command(adb_prefix + ["shell", "input", "tap", str(x), str(y)])
    time.sleep(0.1)
    _run_adb_command(adb_prefix + ["shell", "input", "tap", str(x), str(y)])
    time.sleep(delay)


def long_press(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """
    Long press at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        duration_ms: Duration of press in milliseconds.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after long press.
    """
    adb_prefix = _get_adb_prefix(device_id)

    _run_adb_command(
        adb_prefix
        + ["shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms)]
    )
    time.sleep(delay)


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """
    Swipe from start to end coordinates.

    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        duration_ms: Duration of swipe in milliseconds (auto-calculated if None).
        device_id: Optional ADB device ID.
        delay: Delay in seconds after swipe.
    """
    adb_prefix = _get_adb_prefix(device_id)

    if duration_ms is None:
        # Calculate duration based on distance
        dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
        duration_ms = int(dist_sq / 1000)
        duration_ms = max(1000, min(duration_ms, 2000))  # Clamp between 1000-2000ms

    _run_adb_command(
        adb_prefix
        + [
            "shell",
            "input",
            "swipe",
            str(start_x),
            str(start_y),
            str(end_x),
            str(end_y),
            str(duration_ms),
        ]
    )
    time.sleep(delay)


def back(device_id: str | None = None, delay: float = 1.0) -> None:
    """
    Press the back button.

    Args:
        device_id: Optional ADB device ID.
        delay: Delay in seconds after pressing back.
    """
    adb_prefix = _get_adb_prefix(device_id)

    _run_adb_command(adb_prefix + ["shell", "input", "keyevent", "4"])
    time.sleep(delay)


def home(device_id: str | None = None, delay: float = 1.0) -> None:
    """
    Press the home button.

    Args:
        device_id: Optional ADB device ID.
        delay: Delay in seconds after pressing home.
    """
    adb_prefix = _get_adb_prefix(device_id)

    _run_adb_command(adb_prefix + ["shell", "input", "keyevent", "KEYCODE_HOME"])
    time.sleep(delay)


def launch_app(app_name: str, device_id: str | None = None, delay: float = 1.0) -> bool:
    """
    Launch an app by name.

    Args:
        app_name: The app name (must be in APP_PACKAGES).
        device_id: Optional ADB device ID.
        delay: Delay in seconds after launching.

    Returns:
        True if app was launched, False if app not found.
    """
    if app_name not in APP_PACKAGES:
        return False

    adb_prefix = _get_adb_prefix(device_id)
    package = APP_PACKAGES[app_name]

    _run_adb_command(
        adb_prefix
        + [
            "shell",
            "monkey",
            "-p",
            package,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ]
    )
    time.sleep(delay)
    return True


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]
