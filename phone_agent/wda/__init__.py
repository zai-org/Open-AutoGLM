"""WDA utilities for iOS device interaction via WebDriverAgent.

This module provides the same interface as phone_agent.adb for iOS devices,
allowing the PhoneAgent to work seamlessly with both Android and iOS.
"""

from phone_agent.wda.client import (
    WDAClient,
    get_client,
    set_wda_url,
)
from phone_agent.wda.device import (
    IOS_APP_BUNDLES,
    back,
    double_tap,
    get_current_app,
    get_window_size,
    home,
    is_locked,
    launch_app,
    lock_screen,
    long_press,
    press_button,
    swipe,
    tap,
    unlock_screen,
)
from phone_agent.wda.input import (
    clear_text,
    detect_and_set_adb_keyboard,
    hide_keyboard,
    is_keyboard_shown,
    restore_keyboard,
    type_text,
)
from phone_agent.wda.screenshot import (
    Screenshot,
    get_screen_scale,
    get_screen_size,
    get_screenshot,
)

__all__ = [
    # Client
    "WDAClient",
    "get_client",
    "set_wda_url",
    # Screenshot
    "Screenshot",
    "get_screenshot",
    "get_screen_size",
    "get_screen_scale",
    # Input (compatible with ADB interface)
    "type_text",
    "clear_text",
    "detect_and_set_adb_keyboard",  # Stub for compatibility
    "restore_keyboard",  # Stub for compatibility
    "hide_keyboard",
    "is_keyboard_shown",
    # Device control
    "get_current_app",
    "tap",
    "swipe",
    "back",
    "home",
    "double_tap",
    "long_press",
    "launch_app",
    "press_button",
    "lock_screen",
    "unlock_screen",
    "is_locked",
    "get_window_size",
    # Constants
    "IOS_APP_BUNDLES",
]
