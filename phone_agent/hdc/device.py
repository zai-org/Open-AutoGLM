"""Device control utilities for HarmonyOS automation."""

import os
import subprocess
import time
from typing import List, Optional, Tuple

from phone_agent.config.apps_harmonyos import APP_ABILITIES, APP_PACKAGES
from phone_agent.config.timing import TIMING_CONFIG
from phone_agent.hdc.connection import _run_hdc_command


def get_current_app(device_id: str | None = None) -> str:
    """
    Get the currently focused app name.

    Args:
        device_id: Optional HDC device ID for multi-device setups.

    Returns:
        The app name if recognized, otherwise "System Home".
    """
    hdc_prefix = _get_hdc_prefix(device_id)

    result = _run_hdc_command(
        hdc_prefix + ["shell", "hidumper", "-s", "WindowManagerService", "-a", "-a"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    output = result.stdout
    if not output:
        raise ValueError("No output from hidumper")

    # Parse window focus info
    for line in output.split("\n"):
        if "focused" in line.lower() or "current" in line.lower():
            for app_name, package in APP_PACKAGES.items():
                if package in line:
                    return app_name

    return "System Home"


def tap(
    x: int, y: int, device_id: str | None = None, delay: float | None = None
) -> None:
    """
    Tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional HDC device ID.
        delay: Delay in seconds after tap. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.device.default_tap_delay

    hdc_prefix = _get_hdc_prefix(device_id)

    # HarmonyOS uses uitest uiInput click
    _run_hdc_command(
        hdc_prefix + ["shell", "uitest", "uiInput", "click", str(x), str(y)],
        capture_output=True
    )
    time.sleep(delay)


def double_tap(
    x: int, y: int, device_id: str | None = None, delay: float | None = None
) -> None:
    """
    Double tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional HDC device ID.
        delay: Delay in seconds after double tap. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.device.default_double_tap_delay

    hdc_prefix = _get_hdc_prefix(device_id)

    # HarmonyOS uses uitest uiInput doubleClick
    _run_hdc_command(
        hdc_prefix + ["shell", "uitest", "uiInput", "doubleClick", str(x), str(y)],
        capture_output=True
    )
    time.sleep(delay)


def long_press(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: str | None = None,
    delay: float | None = None,
) -> None:
    """
    Long press at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        duration_ms: Duration of press in milliseconds (note: HarmonyOS longClick may not support duration).
        device_id: Optional HDC device ID.
        delay: Delay in seconds after long press. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.device.default_long_press_delay

    hdc_prefix = _get_hdc_prefix(device_id)

    # HarmonyOS uses uitest uiInput longClick
    # Note: longClick may have a fixed duration, duration_ms parameter might not be supported
    _run_hdc_command(
        hdc_prefix + ["shell", "uitest", "uiInput", "longClick", str(x), str(y)],
        capture_output=True,
    )
    time.sleep(delay)


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    delay: float | None = None,
) -> None:
    """
    Swipe from start to end coordinates.

    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        duration_ms: Duration of swipe in milliseconds (auto-calculated if None).
        device_id: Optional HDC device ID.
        delay: Delay in seconds after swipe. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.device.default_swipe_delay

    hdc_prefix = _get_hdc_prefix(device_id)

    if duration_ms is None:
        # Calculate duration based on distance
        dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
        duration_ms = int(dist_sq / 1000)
        duration_ms = max(500, min(duration_ms, 1000))  # Clamp between 500-1000ms

    # HarmonyOS uses uitest uiInput swipe
    # Format: swipe startX startY endX endY duration
    _run_hdc_command(
        hdc_prefix
        + [
            "shell",
            "uitest",
            "uiInput",
            "swipe",
            str(start_x),
            str(start_y),
            str(end_x),
            str(end_y),
            str(duration_ms),
        ],
        capture_output=True,
    )
    time.sleep(delay)


def back(device_id: str | None = None, delay: float | None = None) -> None:
    """
    Press the back button.

    Args:
        device_id: Optional HDC device ID.
        delay: Delay in seconds after pressing back. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.device.default_back_delay

    hdc_prefix = _get_hdc_prefix(device_id)

    # HarmonyOS uses uitest uiInput keyEvent Back
    _run_hdc_command(
        hdc_prefix + ["shell", "uitest", "uiInput", "keyEvent", "Back"],
        capture_output=True
    )
    time.sleep(delay)


def home(device_id: str | None = None, delay: float | None = None) -> None:
    """
    Press the home button.

    Args:
        device_id: Optional HDC device ID.
        delay: Delay in seconds after pressing home. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.device.default_home_delay

    hdc_prefix = _get_hdc_prefix(device_id)

    # HarmonyOS uses uitest uiInput keyEvent Home
    _run_hdc_command(
        hdc_prefix + ["shell", "uitest", "uiInput", "keyEvent", "Home"],
        capture_output=True
    )
    time.sleep(delay)


def launch_app(
    app_name: str, device_id: str | None = None, delay: float | None = None
) -> bool:
    """
    Launch an app by name.

    Args:
        app_name: The app name (must be in APP_PACKAGES).
        device_id: Optional HDC device ID.
        delay: Delay in seconds after launching. If None, uses configured default.

    Returns:
        True if app was launched, False if app not found.
    """
    if delay is None:
        delay = TIMING_CONFIG.device.default_launch_delay

    if app_name not in APP_PACKAGES:
        print(f"[HDC] App '{app_name}' not found in HarmonyOS app list")
        print(f"[HDC] Available apps: {', '.join(sorted(APP_PACKAGES.keys())[:10])}...")
        return False

    hdc_prefix = _get_hdc_prefix(device_id)
    bundle = APP_PACKAGES[app_name]

    # Get the ability name for this bundle
    # Default to "EntryAbility" if not specified in APP_ABILITIES
    ability = APP_ABILITIES.get(bundle, "EntryAbility")

    # HarmonyOS uses 'aa start' command to launch apps
    # Format: aa start -b {bundle} -a {ability}
    _run_hdc_command(
        hdc_prefix
        + [
            "shell",
            "aa",
            "start",
            "-b",
            bundle,
            "-a",
            ability,
        ],
        capture_output=True,
    )
    time.sleep(delay)
    return True


def _get_hdc_prefix(device_id: str | None) -> list:
    """Get HDC command prefix with optional device specifier."""
    if device_id:
        return ["hdc", "-t", device_id]
    return ["hdc"]
