"""XCTest utilities for iOS device interaction via WebDriverAgent/XCUITest."""

from phone_agent.xctest.connection import (
    ConnectionType,
    DeviceInfo,
    XCTestConnection,
    list_devices,
    quick_connect,
)
from phone_agent.xctest.device import (
    back,
    double_tap,
    get_scale_factor,
    get_current_app,
    home,
    launch_app,
    long_press,
    set_scale_factor,
    swipe,
    tap,
)
from phone_agent.xctest.input import (
    clear_text,
    type_text,
)
from phone_agent.xctest.screenshot import get_screenshot

__all__ = [
    # Screenshot
    "get_screenshot",
    # Input
    "type_text",
    "clear_text",
    # Device control
    "get_current_app",
    "tap",
    "swipe",
    "back",
    "home",
    "double_tap",
    "long_press",
    "launch_app",
    "set_scale_factor",
    "get_scale_factor",
    # Connection management
    "XCTestConnection",
    "DeviceInfo",
    "ConnectionType",
    "quick_connect",
    "list_devices",
]

# Re-export convenience methods (available on XCTestConnection).
# Kept for discoverability in higher-level modules.

