"""Input utilities for HarmonyOS device text input."""

import base64
import subprocess
from typing import Optional

from phone_agent.hdc.connection import _run_hdc_command
from phone_agent.hdc.device import get_last_tap


def type_text(
    text: str,
    device_id: str | None = None,
    coord_x: int | None = None,
    coord_y: int | None = None,
) -> None:
    """
    Type text into the currently focused input field.

    Args:
        text: The text to type. Supports multi-line text with newline characters.
        device_id: Optional HDC device ID for multi-device setups.
        coord_x: Target x coordinate (optional; falls back to last tap if not provided).
        coord_y: Target y coordinate (optional; falls back to last tap if not provided).

    Note:
        HarmonyOS uses: hdc shell uitest uiInput inputText <x> <y> "文本内容"
        This command requires coordinates; if not provided, last tap is used.
        For multi-line text, the function splits by newlines and sends ENTER keyEvents.
        ENTER key code in HarmonyOS: 2054
        Recommendation: Click on the input field first to focus it, then use this function.
    """
    if coord_x is None or coord_y is None:
        last = get_last_tap(device_id)
        if last:
            coord_x, coord_y = last
        else:
            raise ValueError("inputText requires coordinates; tap the input field first")

    hdc_prefix = _get_hdc_prefix(device_id)

    # Handle multi-line text by splitting on newlines
    if '\n' in text:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line:  # Only process non-empty lines
                # Escape special characters for shell
                escaped_line = line.replace('"', '\\"').replace("$", "\\$")

                _run_hdc_command(
                    hdc_prefix
                    + [
                        "shell",
                        "uitest",
                        "uiInput",
                        "inputText",
                        str(coord_x),
                        str(coord_y),
                        escaped_line,
                    ],
                    capture_output=True,
                    text=True,
                )

            # Send ENTER key event after each line except the last one
            if i < len(lines) - 1:
                try:
                    _run_hdc_command(
                        hdc_prefix + ["shell", "uitest", "uiInput", "keyEvent", "2054"],
                        capture_output=True,
                        text=True,
                    )
                except Exception as e:
                    print(f"[HDC] ENTER keyEvent failed: {e}")
    else:
        # Single line text - original logic
        # Escape special characters for shell (keep quotes for proper text handling)
        # The text will be wrapped in quotes in the command
        escaped_text = text.replace('"', '\\"').replace("$", "\\$")

        # HarmonyOS uitest uiInput inputText command
        # Format: hdc shell uitest uiInput inputText <x> <y> "文本内容"
        _run_hdc_command(
            hdc_prefix
            + [
                "shell",
                "uitest",
                "uiInput",
                "inputText",
                str(coord_x),
                str(coord_y),
                escaped_text,
            ],
            capture_output=True,
            text=True,
        )


def clear_text(device_id: str | None = None) -> None:
    """
    Clear text in the currently focused input field.

    Args:
        device_id: Optional HDC device ID for multi-device setups.

    Note:
        This method uses repeated delete key events to clear text.
        For HarmonyOS, you might also use select all + delete for better efficiency.
    """
    hdc_prefix = _get_hdc_prefix(device_id)
    # Ctrl+A to select all (key code 2072 for Ctrl, 2017 for A)
    # Then delete
    _run_hdc_command(
        hdc_prefix + ["shell", "uitest", "uiInput", "keyEvent", "2072", "2017"],
        capture_output=True,
        text=True,
    )
    _run_hdc_command(
        hdc_prefix + ["shell", "uitest", "uiInput", "keyEvent", "2055"],  # Delete key
        capture_output=True,
        text=True,
    )


def detect_and_set_keyboard(device_id: str | None = None) -> str:
    """
    Detect the current keyboard IME for later restoration.

    HarmonyOS does not currently switch input methods the same way as other platforms;
    this function simply records the existing IME so text input flows can
    restore it if needed.

    Args:
        device_id: Optional HDC device ID for multi-device setups.

    Returns:
        The original keyboard IME identifier for later restoration.
    """
    hdc_prefix = _get_hdc_prefix(device_id)

    # Get current IME (if HarmonyOS supports this)
    try:
        result = _run_hdc_command(
            hdc_prefix + ["shell", "settings", "get", "secure", "default_input_method"],
            capture_output=True,
            text=True,
        )
        current_ime = (result.stdout + result.stderr).strip()

        # HarmonyOS specific keyboard switching can be added here if available
        return current_ime
    except Exception:
        return ""


def restore_keyboard(ime: str, device_id: str | None = None) -> None:
    """
    Restore the original keyboard IME.

    Args:
        ime: The IME identifier to restore.
        device_id: Optional HDC device ID for multi-device setups.
    """
    if not ime:
        return

    hdc_prefix = _get_hdc_prefix(device_id)

    try:
        _run_hdc_command(
            hdc_prefix + ["shell", "ime", "set", ime], capture_output=True, text=True
        )
    except Exception:
        pass


def _get_hdc_prefix(device_id: str | None) -> list:
    """Get HDC command prefix with optional device specifier."""
    if device_id:
        return ["hdc", "-t", device_id]
    return ["hdc"]
