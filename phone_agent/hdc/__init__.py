"""HDC utilities for HarmonyOS device interaction."""

from phone_agent.hdc.connection import (
    HDCConnection,
    ConnectionType,
    DeviceInfo,
    list_devices,
    quick_connect,
    set_hdc_verbose,
)
from phone_agent.hdc.device import (
    back,
    double_tap,
    get_current_app,
    home,
    launch_app,
    long_press,
    swipe,
    tap,
)
from phone_agent.hdc.input import (
    clear_text,
    detect_and_set_adb_keyboard,
    restore_keyboard,
    type_text,
)
from phone_agent.hdc.screenshot import get_screenshot

__all__ = [
    # Screenshot
    "get_screenshot",
    # Input
    "type_text",
    "clear_text",
    "detect_and_set_adb_keyboard",
    "restore_keyboard",
    # Device control
    "get_current_app",
    "tap",
    "swipe",
    "back",
    "home",
    "double_tap",
    "long_press",
    "launch_app",
    # Connection management
    "HDCConnection",
    "DeviceInfo",
    "ConnectionType",
    "quick_connect",
    "list_devices",
    "set_hdc_verbose",
]
