"""Async device control utilities for Android automation."""

import asyncio
import subprocess
import time
from typing import List, Optional, Tuple

from phone_agent.config.apps import APP_PACKAGES
from phone_agent.utils.logger import get_logger
from phone_agent.utils.retry import retry_adb_command

logger = get_logger(__name__)


async def get_current_app_async(device_id: str | None = None) -> str:
    """
    Get the currently focused app name (async).

    Args:
        device_id: Optional ADB device ID for multi-device setups.

    Returns:
        The app name if recognized, otherwise "System Home".
    """
    return await asyncio.to_thread(_get_current_app_sync, device_id)


def _get_current_app_sync(device_id: str | None = None) -> str:
    """Synchronous helper for get_current_app."""
    adb_prefix = _get_adb_prefix(device_id)

    result = subprocess.run(
        adb_prefix + ["shell", "dumpsys", "window"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode != 0:
        logger.warning(f"Failed to get current app: {result.stderr}")
        return "System Home"

    output = result.stdout

    # Parse window focus info
    for line in output.split("\n"):
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            for app_name, package in APP_PACKAGES.items():
                if package in line:
                    logger.debug(f"Current app detected: {app_name}")
                    return app_name

    return "System Home"


async def tap_async(
    x: int, y: int, device_id: str | None = None, delay: float = 1.0
) -> None:
    """
    Tap at the specified coordinates (async).

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after tap.
    """
    await asyncio.to_thread(_tap_sync, x, y, device_id, delay)


def _tap_sync(x: int, y: int, device_id: str | None = None, delay: float = 1.0) -> None:
    """Synchronous helper for tap."""
    adb_prefix = _get_adb_prefix(device_id)

    result = subprocess.run(
        adb_prefix + ["shell", "input", "tap", str(x), str(y)],
        capture_output=True,
        timeout=5,
    )

    if result.returncode != 0:
        logger.warning(f"Tap command failed: {result.stderr}")
        raise RuntimeError(f"Failed to tap at ({x}, {y}): {result.stderr}")

    time.sleep(delay)


async def double_tap_async(
    x: int, y: int, device_id: str | None = None, delay: float = 1.0
) -> None:
    """
    Double tap at the specified coordinates (async).

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after double tap.
    """
    await tap_async(x, y, device_id, delay=0.1)
    await tap_async(x, y, device_id, delay=delay)


async def long_press_async(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """
    Long press at the specified coordinates (async).

    Args:
        x: X coordinate.
        y: Y coordinate.
        duration_ms: Duration of press in milliseconds.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after long press.
    """
    await asyncio.to_thread(_long_press_sync, x, y, duration_ms, device_id, delay)


def _long_press_sync(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """Synchronous helper for long_press."""
    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix
        + ["shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms)],
        capture_output=True,
        timeout=5,
    )
    time.sleep(delay)


async def swipe_async(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """
    Swipe from start to end coordinates (async).

    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        duration_ms: Duration of swipe in milliseconds (auto-calculated if None).
        device_id: Optional ADB device ID.
        delay: Delay in seconds after swipe.
    """
    await asyncio.to_thread(_swipe_sync, start_x, start_y, end_x, end_y, duration_ms, device_id, delay)


def _swipe_sync(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """Synchronous helper for swipe."""
    adb_prefix = _get_adb_prefix(device_id)

    if duration_ms is None:
        # Calculate duration based on distance
        dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
        duration_ms = int(dist_sq / 1000)
        duration_ms = max(1000, min(duration_ms, 2000))  # Clamp between 1000-2000ms

    subprocess.run(
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
        ],
        capture_output=True,
        timeout=5,
    )
    time.sleep(delay)


async def back_async(device_id: str | None = None, delay: float = 1.0) -> None:
    """
    Press the back button (async).

    Args:
        device_id: Optional ADB device ID.
        delay: Delay in seconds after pressing back.
    """
    await asyncio.to_thread(_back_sync, device_id, delay)


def _back_sync(device_id: str | None = None, delay: float = 1.0) -> None:
    """Synchronous helper for back."""
    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "4"], capture_output=True, timeout=5
    )
    time.sleep(delay)


async def home_async(device_id: str | None = None, delay: float = 1.0) -> None:
    """
    Press the home button (async).

    Args:
        device_id: Optional ADB device ID.
        delay: Delay in seconds after pressing home.
    """
    await asyncio.to_thread(_home_sync, device_id, delay)


def _home_sync(device_id: str | None = None, delay: float = 1.0) -> None:
    """Synchronous helper for home."""
    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "KEYCODE_HOME"],
        capture_output=True,
        timeout=5,
    )
    time.sleep(delay)


async def launch_app_async(
    app_name: str, device_id: str | None = None, delay: float = 1.0
) -> bool:
    """
    Launch an app by name (async).

    Args:
        app_name: The app name (must be in APP_PACKAGES).
        device_id: Optional ADB device ID.
        delay: Delay in seconds after launching.

    Returns:
        True if app was launched, False if app not found.
    """
    return await asyncio.to_thread(_launch_app_sync, app_name, device_id, delay)


def _launch_app_sync(
    app_name: str, device_id: str | None = None, delay: float = 1.0
) -> bool:
    """Synchronous helper for launch_app."""
    from phone_agent.config.apps import APP_PACKAGES

    if app_name not in APP_PACKAGES:
        return False

    adb_prefix = _get_adb_prefix(device_id)
    package = APP_PACKAGES[app_name]

    subprocess.run(
        adb_prefix
        + [
            "shell",
            "monkey",
            "-p",
            package,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ],
        capture_output=True,
        timeout=10,
    )
    time.sleep(delay)
    return True


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]

