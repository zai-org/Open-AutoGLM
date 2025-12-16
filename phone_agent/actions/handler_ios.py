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
from phone_agent.xctest.device import get_screen_size
from phone_agent.xctest.input import clear_text, hide_keyboard, type_text
from phone_agent.xctest.wda_client import WDAClient


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
        scale_factor: float | None = None,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
    ):
        self.wda_url = wda_url
        self.session_id = session_id
        self._wda_client = WDAClient(self.wda_url, session_id=self.session_id)
        self._scale_factor = scale_factor if (scale_factor and scale_factor > 0) else None
        super().__init__(
            confirmation_callback=confirmation_callback, takeover_callback=takeover_callback
        )

    def execute(
        self, action: dict[str, Any], screen_width: int, screen_height: int
    ) -> ActionResult:
        self._ensure_scale_factor(screen_width, screen_height)
        return super().execute(action, screen_width, screen_height)

    def _ensure_scale_factor(self, screen_width: int, screen_height: int) -> None:
        if self._scale_factor is not None:
            return

        wda_w, wda_h = get_screen_size(
            wda_url=self.wda_url, session_id=self.session_id, client=self._wda_client
        )
        if wda_w <= 0 or wda_h <= 0:
            self._scale_factor = 1.0
            return

        r1 = screen_width / wda_w
        r2 = screen_height / wda_h
        r3 = screen_width / wda_h
        r4 = screen_height / wda_w

        if abs(r1 - r2) <= abs(r3 - r4):
            scale = (r1 + r2) / 2
        else:
            scale = (r3 + r4) / 2

        if scale < 1.0:
            scale = 1.0

        for candidate in (1.0, 2.0, 3.0):
            if abs(scale - candidate) < 0.15:
                scale = candidate
                break

        self._scale_factor = scale

    def _to_points(self, x_px: int, y_px: int) -> tuple[int, int]:
        scale = self._scale_factor or 1.0
        return int(round(x_px / scale)), int(round(y_px / scale))

    def _launch_app(self, app_name: str) -> bool:
        return launch_app(
            app_name,
            wda_url=self.wda_url,
            session_id=self.session_id,
            client=self._wda_client,
        )

    def _tap(self, x: int, y: int) -> None:
        x_pt, y_pt = self._to_points(x, y)
        tap(
            x_pt,
            y_pt,
            wda_url=self.wda_url,
            session_id=self.session_id,
            client=self._wda_client,
        )

    def _type_text(self, text: str) -> None:
        clear_text(wda_url=self.wda_url, session_id=self.session_id, client=self._wda_client)
        time.sleep(0.5)

        type_text(text, wda_url=self.wda_url, session_id=self.session_id, client=self._wda_client)
        time.sleep(0.5)

        hide_keyboard(wda_url=self.wda_url, session_id=self.session_id, client=self._wda_client)
        time.sleep(0.5)

    def _swipe(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        start_x_pt, start_y_pt = self._to_points(start_x, start_y)
        end_x_pt, end_y_pt = self._to_points(end_x, end_y)
        swipe(
            start_x_pt,
            start_y_pt,
            end_x_pt,
            end_y_pt,
            wda_url=self.wda_url,
            session_id=self.session_id,
            client=self._wda_client,
        )

    def _back(self) -> None:
        back(wda_url=self.wda_url, session_id=self.session_id, client=self._wda_client)

    def _home(self) -> None:
        home(wda_url=self.wda_url, session_id=self.session_id, client=self._wda_client)

    def _double_tap(self, x: int, y: int) -> None:
        x_pt, y_pt = self._to_points(x, y)
        double_tap(
            x_pt,
            y_pt,
            wda_url=self.wda_url,
            session_id=self.session_id,
            client=self._wda_client,
        )

    def _long_press(self, x: int, y: int) -> None:
        x_pt, y_pt = self._to_points(x, y)
        long_press(
            x_pt,
            y_pt,
            duration=3.0,
            wda_url=self.wda_url,
            session_id=self.session_id,
            client=self._wda_client,
        )
