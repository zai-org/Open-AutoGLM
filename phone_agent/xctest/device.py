"""Device control utilities for iOS automation via WebDriverAgent."""

import subprocess
import time
from typing import Optional

from phone_agent.config.apps_ios import APP_PACKAGES_IOS as APP_PACKAGES

SCALE_FACTOR = 3 # 3 for most modern iPhone 

def _get_wda_session_url(wda_url: str, session_id: str | None, endpoint: str) -> str:
    """
    Get the correct WDA URL for a session endpoint.

    Args:
        wda_url: Base WDA URL.
        session_id: Optional session ID.
        endpoint: The endpoint path.

    Returns:
        Full URL for the endpoint.
    """
    base = wda_url.rstrip("/")
    if session_id:
        return f"{base}/session/{session_id}/{endpoint}"
    else:
        # Try to use WDA endpoints without session when possible
        return f"{base}/{endpoint}"


def get_current_app(
    wda_url: str = "http://localhost:8100", session_id: str | None = None
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
        import requests

        # Get active app info from WDA using activeAppInfo endpoint
        response = requests.get(
            f"{wda_url.rstrip('/')}/wda/activeAppInfo", timeout=5, verify=False
        )

        if response.status_code == 200:
            data = response.json()
            # Extract bundle ID from response
            # Response format: {"value": {"bundleId": "com.apple.AppStore", "name": "", "pid": 825, "processArguments": {...}}, "sessionId": "..."}
            value = data.get("value", {})
            bundle_id = value.get("bundleId", "")

            if bundle_id:
                # Try to find app name from bundle ID
                for app_name, package in APP_PACKAGES.items():
                    if package == bundle_id:
                        return app_name

            return "System Home"

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error getting current app: {e}")

    return "System Home"


def tap(
    x: int,
    y: int,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """
    Tap at the specified coordinates using WebDriver W3C Actions API.

    Args:
        x: X coordinate.
        y: Y coordinate.
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after tap.
    """
    try:
        import requests

        url = _get_wda_session_url(wda_url, session_id, "actions")

        # W3C WebDriver Actions API for tap/click
        actions = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "finger1",
                    "parameters": {"pointerType": "touch"},
                    "actions": [
                        {"type": "pointerMove", "duration": 0, "x": x / SCALE_FACTOR, "y": y / SCALE_FACTOR},
                        {"type": "pointerDown", "button": 0},
                        {"type": "pause", "duration": 0.1},
                        {"type": "pointerUp", "button": 0},
                    ],
                }
            ]
        }

        requests.post(url, json=actions, timeout=15, verify=False)

        time.sleep(delay)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error tapping: {e}")


def double_tap(
    x: int,
    y: int,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """
    Double tap at the specified coordinates using WebDriver W3C Actions API.

    Args:
        x: X coordinate.
        y: Y coordinate.
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after double tap.
    """
    try:
        import requests

        url = _get_wda_session_url(wda_url, session_id, "actions")

        # W3C WebDriver Actions API for double tap
        actions = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "finger1",
                    "parameters": {"pointerType": "touch"},
                    "actions": [
                        {"type": "pointerMove", "duration": 0, "x": x / SCALE_FACTOR, "y": y / SCALE_FACTOR},
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

        requests.post(url, json=actions, timeout=10, verify=False)

        time.sleep(delay)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error double tapping: {e}")


def long_press(
    x: int,
    y: int,
    duration: float = 3.0,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """
    Long press at the specified coordinates using WebDriver W3C Actions API.

    Args:
        x: X coordinate.
        y: Y coordinate.
        duration: Duration of press in seconds.
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after long press.
    """
    try:
        import requests

        url = _get_wda_session_url(wda_url, session_id, "actions")

        # W3C WebDriver Actions API for long press
        # Convert duration to milliseconds
        duration_ms = int(duration * 1000)

        actions = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "finger1",
                    "parameters": {"pointerType": "touch"},
                    "actions": [
                        {"type": "pointerMove", "duration": 0, "x": x / SCALE_FACTOR, "y": y / SCALE_FACTOR},
                        {"type": "pointerDown", "button": 0},
                        {"type": "pause", "duration": duration_ms},
                        {"type": "pointerUp", "button": 0},
                    ],
                }
            ]
        }

        requests.post(url, json=actions, timeout=int(duration + 10), verify=False)

        time.sleep(delay)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
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
) -> None:
    """
    Swipe from start to end coordinates using WDA dragfromtoforduration endpoint.

    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        duration: Duration of swipe in seconds (auto-calculated if None).
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after swipe.
    """
    try:
        import requests

        if duration is None:
            # Calculate duration based on distance
            dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
            duration = dist_sq / 1000000  # Convert to seconds
            duration = max(0.3, min(duration, 2.0))  # Clamp between 0.3-2 seconds

        url = _get_wda_session_url(wda_url, session_id, "wda/dragfromtoforduration")

        # WDA dragfromtoforduration API payload
        payload = {
            "fromX": start_x / SCALE_FACTOR,
            "fromY": start_y / SCALE_FACTOR,
            "toX": end_x / SCALE_FACTOR,
            "toY": end_y / SCALE_FACTOR,
            "duration": duration,
        }

        requests.post(url, json=payload, timeout=int(duration + 10), verify=False)

        time.sleep(delay)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error swiping: {e}")


def back(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
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
        import requests

        url = _get_wda_session_url(wda_url, session_id, "wda/dragfromtoforduration")

        # Swipe from left edge to simulate back gesture
        payload = {
            "fromX": 0,
            "fromY": 640,
            "toX": 400,
            "toY": 640,
            "duration": 0.3,
        }

        requests.post(url, json=payload, timeout=10, verify=False)

        time.sleep(delay)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error performing back gesture: {e}")


def home(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """
    Press the home button.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after pressing home.
    """
    try:
        import requests

        url = f"{wda_url.rstrip('/')}/wda/homescreen"

        requests.post(url, timeout=10, verify=False)

        time.sleep(delay)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error pressing home: {e}")


def launch_app(
    app_name: str,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
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
        import requests

        bundle_id = APP_PACKAGES[app_name]
        url = _get_wda_session_url(wda_url, session_id, "wda/apps/launch")

        response = requests.post(
            url, json={"bundleId": bundle_id}, timeout=10, verify=False
        )

        time.sleep(delay)
        return response.status_code in (200, 201)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
        return False
    except Exception as e:
        print(f"Error launching app: {e}")
        return False


def get_screen_size(
    wda_url: str = "http://localhost:8100", session_id: str | None = None
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
        import requests

        url = _get_wda_session_url(wda_url, session_id, "window/size")

        response = requests.get(url, timeout=5, verify=False)

        if response.status_code == 200:
            data = response.json()
            value = data.get("value", {})
            width = value.get("width", 375)
            height = value.get("height", 812)
            return width, height

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error getting screen size: {e}")

    # Default iPhone screen size (iPhone X and later)
    return 375, 812


def press_button(
    button_name: str,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 1.0,
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
        import requests

        url = f"{wda_url.rstrip('/')}/wda/pressButton"

        requests.post(url, json={"name": button_name}, timeout=10, verify=False)

        time.sleep(delay)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error pressing button: {e}")
