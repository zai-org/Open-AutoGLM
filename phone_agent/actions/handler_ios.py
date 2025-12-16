"""Action handler for iOS automation using WebDriverAgent."""

import time
from typing import Any, Callable

from phone_agent.actions.base_handler import BaseActionHandler
from phone_agent.actions.types import ActionResult
from phone_agent.xctest import (
    back,
    double_tap,
    home,
    launch_app,
    long_press,
    swipe,
    tap,
)
from phone_agent.xctest.input import clear_text, hide_keyboard, type_text


class IOSActionHandler(BaseActionHandler):
    """
    Handles execution of actions from AI model output for iOS devices.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        confirmation_callback: Optional callback for sensitive action confirmation.
            Should return True to proceed, False to cancel.
        takeover_callback: Optional callback for takeover requests (login, captcha).
    """

    def __init__(
        self,
        wda_url: str = "http://localhost:8100",
        session_id: str | None = None,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
    ):
        self.wda_url = wda_url
        self.session_id = session_id
        super().__init__(
            confirmation_callback=confirmation_callback, takeover_callback=takeover_callback
        )

    def _launch_app(self, app_name: str) -> bool:
        return launch_app(app_name, wda_url=self.wda_url, session_id=self.session_id)

    def _tap(self, x: int, y: int) -> None:
        tap(x, y, wda_url=self.wda_url, session_id=self.session_id)

    def _type_text(self, text: str) -> None:
        clear_text(wda_url=self.wda_url, session_id=self.session_id)
        time.sleep(0.5)

        type_text(text, wda_url=self.wda_url, session_id=self.session_id)
        time.sleep(0.5)

        hide_keyboard(wda_url=self.wda_url, session_id=self.session_id)
        time.sleep(0.5)

    def _swipe(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        swipe(
            start_x,
            start_y,
            end_x,
            end_y,
            wda_url=self.wda_url,
            session_id=self.session_id,
        )

    def _back(self) -> None:
        back(wda_url=self.wda_url, session_id=self.session_id)

    def _home(self) -> None:
        home(wda_url=self.wda_url, session_id=self.session_id)

    def _double_tap(self, x: int, y: int) -> None:
        double_tap(x, y, wda_url=self.wda_url, session_id=self.session_id)

    def _long_press(self, x: int, y: int) -> None:
        long_press(x, y, duration=3.0, wda_url=self.wda_url, session_id=self.session_id)
