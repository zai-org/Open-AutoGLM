"""Input utilities for iOS device text input via WebDriverAgent."""

import logging
import time
from typing import Optional

from phone_agent.wda.client import get_client

logger = logging.getLogger(__name__)


def type_text(text: str, device_id: str | None = None, frequency: int = 60) -> None:
    """
    Type text into the currently focused input field using global keyboard.
    
    Based on gekowa's working iOS implementation.
    
    Args:
        text: The text to type
        device_id: WDA URL or None to use default
        frequency: Typing frequency (keys per minute), default 60
        
    Note:
        The input field MUST be focused (tapped) before calling this!
        This uses WDA's global keyboard input (not element-specific).
    """
    if not text:
        return
    
    client = get_client(device_id)
    
    # Send keys as array of characters with frequency parameter
    # This is the gekowa method that works reliably
    client.post("/wda/keys", {"value": list(text), "frequency": frequency}, use_session=True)


def clear_text(device_id: str | None = None) -> None:
    """
    Clear text in the currently focused input field.
    
    Based on gekowa's working iOS implementation.
    This tries to:
    1. Get the active element and call clear on it
    2. Fallback to sending backspace keys if no active element
    
    Args:
        device_id: WDA URL or None to use default
        
    Note:
        The input field must be focused before calling this function.
    """
    client = get_client(device_id)
    
    try:
        # Try to get the active element first
        resp = client.get("/element/active", use_session=True)
        
        if "value" in resp and isinstance(resp["value"], dict):
            # Try both WDA and W3C element ID formats
            element_id = resp["value"].get("ELEMENT") or resp["value"].get("element-6066-11e4-a52e-4f735466cecf")
            
            if element_id:
                # Clear the active element
                client.post(f"/element/{element_id}/clear", use_session=True)
                return
    except Exception as e:
        logger.debug(f"Failed to clear element, using backspace fallback: {e}")
        pass
    
    # Fallback: send backspace keys (gekowa method)
    _clear_with_backspace(device_id)


def _clear_with_backspace(device_id: str | None = None, max_backspaces: int = 100) -> None:
    """
    Clear text by sending backspace keys.
    
    Args:
        device_id: WDA URL or None to use default
        max_backspaces: Maximum number of backspaces to send (default 100)
    """
    client = get_client(device_id)
    
    # Send backspace Unicode character multiple times
    backspace_char = "\u0008"  # Backspace Unicode
    try:
        client.post("/wda/keys", {"value": [backspace_char] * max_backspaces}, use_session=True)
    except Exception as e:
        logger.warning(f"Error clearing with backspace: {e}")
    

def hide_keyboard(device_id: str | None = None) -> None:
    """
    Hide/dismiss the on-screen keyboard.
    
    Args:
        device_id: WDA URL or None to use default
    """
    client = get_client(device_id)
    
    try:
        # WDA /wda/keyboard/dismiss REQUIRES a session (per WDA source code)
        # FBCustomCommands.m line 43: no .withoutSession modifier
        resp = client.post("/wda/keyboard/dismiss", use_session=True)
        if "error" in resp:
            # Silently ignore - keyboard may already be hidden
            pass
    except Exception as e:
        # Silently ignore keyboard dismiss errors - not critical
        pass


def is_keyboard_shown(device_id: str | None = None) -> bool:
    """
    Check if the on-screen keyboard is currently shown.
    
    Args:
        device_id: WDA URL or None to use default
        
    Returns:
        True if keyboard is shown, False otherwise
    """
    client = get_client(device_id)
    
    try:
        resp = client.get("/wda/keyboard/shown", use_session=True)
        return resp.get("value", False)
    except Exception as e:
        logger.debug(f"Failed to check keyboard status: {e}")
        return False


def detect_and_set_adb_keyboard(device_id: str | None = None) -> str:
    """
    Detect keyboard status (iOS compatibility stub).
    
    iOS doesn't require keyboard switching like Android's ADB Keyboard.
    This function exists for API compatibility with the ADB module.
    
    Args:
        device_id: WDA URL or None to use default
        
    Returns:
        Empty string (no keyboard switching needed on iOS)
    """
    # iOS uses native keyboard - no switching needed
    # Return empty string for compatibility
    return ""


def restore_keyboard(ime: str, device_id: str | None = None) -> None:
    """
    Restore keyboard (iOS compatibility stub).
    
    iOS doesn't require keyboard restoration like Android.
    This function exists for API compatibility with the ADB module.
    
    Args:
        ime: The IME identifier (ignored on iOS)
        device_id: WDA URL or None to use default
    """
    # Nothing to restore on iOS
    pass
