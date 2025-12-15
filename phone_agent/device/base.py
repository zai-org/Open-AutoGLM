from typing import Protocol

from phone_agent.adb.screenshot import Screenshot


class DeviceController(Protocol):
    def get_screenshot(self) -> Screenshot:
        ...

    def tap(self, x: int, y: int) -> None:
        ...

    def swipe(self, x1: int, y1: int, x2: int, y2: int) -> None:
        ...

    def back(self) -> None:
        ...

    def home(self) -> None:
        ...

    def type_text(self, text: str) -> None:
        ...

    def launch_app(self, app_name: str) -> bool:
        ...

    def get_current_app(self) -> str:
        ...


