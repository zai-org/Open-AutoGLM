"""Device factory for HarmonyOS (HDC) devices."""

from enum import Enum
from typing import Any


class DeviceType(Enum):
    """Type of device connection tool."""

    HDC = "hdc"


class DeviceFactory:
    """
    Factory class for getting device-specific implementations.

    This keeps a single control surface for HarmonyOS (HDC) devices.
    """

    def __init__(self, device_type: DeviceType = DeviceType.HDC):
        """
        Initialize the device factory.

        Args:
            device_type: The type of device to use (ADB or HDC).
        """
        self.device_type = device_type
        self._module = None

    @property
    def module(self):
        """Get the appropriate device module (currently only hdc)."""
        if self._module is None:
            if self.device_type == DeviceType.HDC:
                from phone_agent import hdc

                self._module = hdc
            else:
                raise ValueError(f"Unknown device type: {self.device_type}")
        return self._module

    def get_screenshot(self, device_id: str | None = None, timeout: int = 10):
        """Get screenshot from device."""
        return self.module.get_screenshot(device_id, timeout)

    def get_current_app(self, device_id: str | None = None) -> str:
        """Get current app name."""
        return self.module.get_current_app(device_id)

    def tap(
        self, x: int, y: int, device_id: str | None = None, delay: float | None = None
    ):
        """Tap at coordinates."""
        return self.module.tap(x, y, device_id, delay)

    def double_tap(
        self, x: int, y: int, device_id: str | None = None, delay: float | None = None
    ):
        """Double tap at coordinates."""
        return self.module.double_tap(x, y, device_id, delay)

    def long_press(
        self,
        x: int,
        y: int,
        duration_ms: int = 3000,
        device_id: str | None = None,
        delay: float | None = None,
    ):
        """Long press at coordinates."""
        return self.module.long_press(x, y, duration_ms, device_id, delay)

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int | None = None,
        device_id: str | None = None,
        delay: float | None = None,
    ):
        """Swipe from start to end."""
        return self.module.swipe(
            start_x, start_y, end_x, end_y, duration_ms, device_id, delay
        )

    def back(self, device_id: str | None = None, delay: float | None = None):
        """Press back button."""
        return self.module.back(device_id, delay)

    def home(self, device_id: str | None = None, delay: float | None = None):
        """Press home button."""
        return self.module.home(device_id, delay)

    def launch_app(
        self, app_name: str, device_id: str | None = None, delay: float | None = None
    ) -> bool:
        """Launch an app."""
        return self.module.launch_app(app_name, device_id, delay)

    def type_text(self, text: str, device_id: str | None = None):
        """Type text."""
        return self.module.type_text(text, device_id)

    def clear_text(self, device_id: str | None = None):
        """Clear text."""
        return self.module.clear_text(device_id)

    def detect_and_set_keyboard(self, device_id: str | None = None) -> str:
        """Detect and set keyboard if supported."""
        return self.module.detect_and_set_keyboard(device_id)

    def restore_keyboard(self, ime: str, device_id: str | None = None):
        """Restore keyboard."""
        return self.module.restore_keyboard(ime, device_id)

    def list_devices(self):
        """List connected devices."""
        return self.module.list_devices()

    def get_connection_class(self):
        """Get the connection class (HDCConnection)."""
        if self.device_type == DeviceType.HDC:
            from phone_agent.hdc import HDCConnection

            return HDCConnection
        raise ValueError(f"Unknown device type: {self.device_type}")


# Global device factory instance
_device_factory: DeviceFactory | None = None


def set_device_type(device_type: DeviceType):
    """
    Set the global device type.

    Args:
        device_type: The device type to use (HDC).
    """
    global _device_factory
    _device_factory = DeviceFactory(device_type)


def get_device_factory() -> DeviceFactory:
    """
    Get the global device factory instance.

    Returns:
        The device factory instance.
    """
    global _device_factory
    if _device_factory is None:
        _device_factory = DeviceFactory(DeviceType.HDC)  # Default to HDC
    return _device_factory
