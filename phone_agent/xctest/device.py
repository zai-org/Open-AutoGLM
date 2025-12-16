"""Device control utilities for iOS automation via WebDriverAgent."""

import time

from phone_agent.config.apps_ios import APP_PACKAGES_IOS as APP_PACKAGES
from phone_agent.xctest.wda_client import WDAClient, WDAError

DEFAULT_SCREEN_SIZE = (375, 812)  # iPhone points (iPhone X and later)


def _get_client(
    wda_url: str, session_id: str | None, client: WDAClient | None
) -> WDAClient:
    return client or WDAClient(wda_url, session_id=session_id)


def get_current_app(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    client: WDAClient | None = None,
) -> str:
    """
    Get the currently active app bundle ID and name.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.

    Returns:
        The app name if recognized, otherwise "System Home".
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        data = wda.get("wda/activeAppInfo", use_session=False, timeout=5.0)
        if not isinstance(data, dict):
            return "System Home"

        value = data.get("value", {})
        bundle_id = value.get("bundleId", "") if isinstance(value, dict) else ""
        if bundle_id:
            for app_name, package in APP_PACKAGES.items():
                if package == bundle_id:
                    return app_name
    except WDAError as e:
        print(f"Error getting current app: {e}")

    return "System Home"


def tap(
    x: int,
    y: int,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
    client: WDAClient | None = None,
) -> None:
    """
    Tap at the specified coordinates using WebDriver W3C Actions API.

    Args:
        x: X coordinate (points).
        y: Y coordinate (points).
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after tap.
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        actions = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "finger1",
                    "parameters": {"pointerType": "touch"},
                    "actions": [
                        {"type": "pointerMove", "duration": 0, "x": x, "y": y},
                        {"type": "pointerDown", "button": 0},
                        {"type": "pause", "duration": 100},
                        {"type": "pointerUp", "button": 0},
                    ],
                }
            ]
        }
        wda.post("actions", json=actions, timeout=15.0)
        time.sleep(delay)
    except WDAError as e:
        print(f"Error tapping: {e}")


def double_tap(
    x: int,
    y: int,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
    client: WDAClient | None = None,
) -> None:
    """
    Double tap at the specified coordinates using WebDriver W3C Actions API.

    Args:
        x: X coordinate (points).
        y: Y coordinate (points).
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after double tap.
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        actions = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "finger1",
                    "parameters": {"pointerType": "touch"},
                    "actions": [
                        {"type": "pointerMove", "duration": 0, "x": x, "y": y},
                        {"type": "pointerDown", "button": 0},
                        {"type": "pause", "duration": 100},
                        {"type": "pointerUp", "button": 0},
                        {"type": "pause", "duration": 100},
                        {"type": "pointerDown", "button": 0},
                        {"type": "pause", "duration": 100},
                        {"type": "pointerUp", "button": 0},
                    ],
                }
            ]
        }
        wda.post("actions", json=actions, timeout=10.0)
        time.sleep(delay)
    except WDAError as e:
        print(f"Error double tapping: {e}")


def long_press(
    x: int,
    y: int,
    duration: float = 3.0,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
    client: WDAClient | None = None,
) -> None:
    """
    Long press at the specified coordinates using WebDriver W3C Actions API.

    Args:
        x: X coordinate (points).
        y: Y coordinate (points).
        duration: Duration of press in seconds.
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after long press.
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        duration_ms = int(duration * 1000)
        actions = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "finger1",
                    "parameters": {"pointerType": "touch"},
                    "actions": [
                        {"type": "pointerMove", "duration": 0, "x": x, "y": y},
                        {"type": "pointerDown", "button": 0},
                        {"type": "pause", "duration": duration_ms},
                        {"type": "pointerUp", "button": 0},
                    ],
                }
            ]
        }
        wda.post("actions", json=actions, timeout=float(duration + 10))
        time.sleep(delay)
    except WDAError as e:
        print(f"Error long pressing: {e}")


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration: float | None = None,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
    client: WDAClient | None = None,
) -> None:
    """
    Swipe from start to end coordinates using WDA dragfromtoforduration endpoint.

    Args:
        start_x: Starting X coordinate (points).
        start_y: Starting Y coordinate (points).
        end_x: Ending X coordinate (points).
        end_y: Ending Y coordinate (points).
        duration: Duration of swipe in seconds (auto-calculated if None).
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after swipe.
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        if duration is None:
            dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
            duration = dist_sq / 1000000
            duration = max(0.3, min(duration, 2.0))

        payload = {
            "fromX": start_x,
            "fromY": start_y,
            "toX": end_x,
            "toY": end_y,
            "duration": duration,
        }
        wda.post(
            "wda/dragfromtoforduration",
            json=payload,
            timeout=float(duration + 10),
        )
        time.sleep(delay)
    except WDAError as e:
        print(f"Error swiping: {e}")


def back(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
    client: WDAClient | None = None,
) -> None:
    """
    Navigate back (swipe from left edge).

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after navigation.

    Note:
        iOS doesn't have a universal back button. This simulates a back gesture
        by swiping from the left edge of the screen.
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        screen_w, screen_h = get_screen_size(wda_url=wda_url, session_id=session_id, client=wda)
        y = int(screen_h * 0.5)
        to_x = int(screen_w * 0.4)

        payload = {"fromX": 0, "fromY": y, "toX": to_x, "toY": y, "duration": 0.3}
        wda.post("wda/dragfromtoforduration", json=payload, timeout=10.0)
        time.sleep(delay)
    except WDAError as e:
        print(f"Error performing back gesture: {e}")


def home(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
    client: WDAClient | None = None,
) -> None:
    """
    Press the home button.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after pressing home.
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        wda.post("wda/homescreen", use_session=False, timeout=10.0, allow_status=(200, 201, 204))
        time.sleep(delay)
    except WDAError as e:
        print(f"Error pressing home: {e}")


def launch_app(
    app_name: str,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
    client: WDAClient | None = None,
) -> bool:
    """
    Launch an app by name.

    Args:
        app_name: The app name (must be in APP_PACKAGES).
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after launching.

    Returns:
        True if app was launched, False if app not found.
    """
    if app_name not in APP_PACKAGES:
        return False

    try:
        wda = _get_client(wda_url, session_id, client)
        bundle_id = APP_PACKAGES[app_name]
        wda.post(
            "wda/apps/launch",
            json={"bundleId": bundle_id},
            timeout=10.0,
            allow_status=(200, 201),
        )
        time.sleep(delay)
        return True
    except WDAError as e:
        print(f"Error launching app: {e}")
        return False


def get_screen_size(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    client: WDAClient | None = None,
) -> tuple[int, int]:
    """
    Get the screen dimensions.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.

    Returns:
        Tuple of (width, height). Returns (375, 812) as default if unable to fetch.
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        data = wda.get("window/size", timeout=5.0)
        if isinstance(data, dict):
            value = data.get("value", data)
            if isinstance(value, dict):
                width = int(value.get("width", DEFAULT_SCREEN_SIZE[0]))
                height = int(value.get("height", DEFAULT_SCREEN_SIZE[1]))
                return width, height
    except WDAError as e:
        print(f"Error getting screen size: {e}")

    return DEFAULT_SCREEN_SIZE


def press_button(
    button_name: str,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
    client: WDAClient | None = None,
) -> None:
    """
    Press a physical button.

    Args:
        button_name: Button name (e.g., "home", "volumeUp", "volumeDown").
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after pressing.
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        wda.post(
            "wda/pressButton",
            use_session=False,
            json={"name": button_name},
            timeout=10.0,
            allow_status=(200, 201, 204),
        )
        time.sleep(delay)
    except WDAError as e:
        print(f"Error pressing button: {e}")
