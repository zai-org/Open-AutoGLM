"""Input utilities for Android device text input."""

import base64
import subprocess
from typing import Optional


def type_text(text: str, device_id: str | None = None) -> None:
    """
    Type text into the currently focused input field using ADB Keyboard.

    Args:
        text: The text to type.
        device_id: Optional ADB device ID for multi-device setups.

    Note:
        Requires ADB Keyboard to be installed on the device.
        See: https://github.com/nicnocquee/AdbKeyboard
    """
    adb_prefix = _get_adb_prefix(device_id)
    encoded_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")

    subprocess.run(
        adb_prefix
        + [
            "shell",
            "am",
            "broadcast",
            "-a",
            "ADB_INPUT_B64",
            "--es",
            "msg",
            encoded_text,
        ],
        capture_output=True,
        text=True,
    )


def clear_text(device_id: str | None = None) -> None:
    """
    Clear text in the currently focused input field.

    Args:
        device_id: Optional ADB device ID for multi-device setups.
    """
    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "am", "broadcast", "-a", "ADB_CLEAR_TEXT"],
        capture_output=True,
        text=True,
    )


def detect_and_set_adb_keyboard(device_id: str | None = None) -> str:
    """
    Detect current keyboard and switch to ADB Keyboard if needed.

    Args:
        device_id: Optional ADB device ID for multi-device setups.

    Returns:
        The original keyboard IME identifier for later restoration.
    """
    adb_prefix = _get_adb_prefix(device_id)

    # Get current IME
    result = subprocess.run(
        adb_prefix + ["shell", "settings", "get", "secure", "default_input_method"],
        capture_output=True,
        text=True,
    )
    current_ime = (result.stdout + result.stderr).strip()

    # Switch to ADB Keyboard if not already set
    if "com.android.adbkeyboard/.AdbIME" not in current_ime:
        subprocess.run(
            adb_prefix + ["shell", "ime", "set", "com.android.adbkeyboard/.AdbIME"],
            capture_output=True,
            text=True,
        )

    # Warm up the keyboard
    type_text("", device_id)

    return current_ime


def restore_keyboard(ime: str, device_id: str | None = None) -> None:
    """
    Restore the original keyboard IME.

    Args:
        ime: The IME identifier to restore.
        device_id: Optional ADB device ID for multi-device setups.
    """
    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "ime", "set", ime], capture_output=True, text=True
    )


    return ["adb"]


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]


def install_and_set_adb_keyboard(device_id: str | None = None) -> bool:
    """
    Install and set ADB Keyboard as default.
    
    1. Install APK if not present or always install to ensure version? 
       (Let's try install -r to reinstall/update)
    2. Enable IME
    3. Set IME
    
    Args:
        device_id: Optional ADB device ID.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        adb_prefix = _get_adb_prefix(device_id)
        
        # 1. Install APK
        # Assuming ADBKeyboard.apk is in the project root.
        # We need a robust way to find the apk path.
        # Since this code is in phone_agent/adb/input.py, 
        # project root is ../../../
        
        # Let's try to assume it is in the current working directory or relative to this file
        import os
        from pathlib import Path
        
        # Try to find the APK
        possible_paths = [
            "ADBKeyboard.apk",
            os.path.join("..", "..", "ADBKeyboard.apk"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "ADBKeyboard.apk"),
            "e:\\code\\autoglm\\Open-AutoGLM\\ADBKeyboard.apk" # Fallback absolute path
        ]
        
        apk_path = None
        for p in possible_paths:
            if os.path.exists(p):
                apk_path = p
                break
                
        if not apk_path:
            print("Error: ADBKeyboard.apk not found.")
            return False
            
        print(f"Installing ADB Keyboard from {apk_path}...")
        subprocess.run(
            adb_prefix + ["install", "-r", apk_path],
            capture_output=True,
            check=True
        )
        
        # 2. Enable IME
        print("Enabling ADB Keyboard...")
        subprocess.run(
            adb_prefix + ["shell", "ime", "enable", "com.android.adbkeyboard/.AdbIME"],
            capture_output=True
        )
        
        # 3. Set IME
        print("Setting ADB Keyboard as default...")
        subprocess.run(
            adb_prefix + ["shell", "ime", "set", "com.android.adbkeyboard/.AdbIME"],
            capture_output=True
        )
        
        return True
        
    except Exception as e:
        print(f"Error setting up ADB Keyboard: {e}")
        return False

