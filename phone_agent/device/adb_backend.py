import time

from phone_agent.adb import (
    back as adb_back,
    get_current_app as adb_get_current_app,
    home as adb_home,
    launch_app as adb_launch_app,
    swipe as adb_swipe,
    tap as adb_tap,
)
from phone_agent.adb.input import (
    clear_text,
    detect_and_set_adb_keyboard,
    restore_keyboard,
    type_text as adb_type_text,
)
from phone_agent.adb.screenshot import Screenshot, get_screenshot as adb_get_screenshot
from phone_agent.config.timing import TIMING_CONFIG
from phone_agent.device.base import DeviceController


class AdbDeviceController(DeviceController):
    def __init__(self, device_id: str | None = None):
        self.device_id = device_id

    def get_screenshot(self) -> Screenshot:
        return adb_get_screenshot(self.device_id)

    def tap(self, x: int, y: int) -> None:
        adb_tap(x, y, self.device_id)

    def swipe(self, x1: int, y1: int, x2: int, y2: int) -> None:
        adb_swipe(x1, y1, x2, y2, device_id=self.device_id)

    def back(self) -> None:
        adb_back(self.device_id)

    def home(self) -> None:
        adb_home(self.device_id)

    def type_text(self, text: str) -> None:
        original_ime = detect_and_set_adb_keyboard(self.device_id)
        time.sleep(TIMING_CONFIG.action.keyboard_switch_delay)
        clear_text(self.device_id)
        time.sleep(TIMING_CONFIG.action.text_clear_delay)
        adb_type_text(text, self.device_id)
        time.sleep(TIMING_CONFIG.action.text_input_delay)
        restore_keyboard(original_ime, self.device_id)
        time.sleep(TIMING_CONFIG.action.keyboard_restore_delay)

    def launch_app(self, app_name: str) -> bool:
        return adb_launch_app(app_name, self.device_id)

    def get_current_app(self) -> str:
        return adb_get_current_app(self.device_id)


