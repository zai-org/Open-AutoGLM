"""Input utilities for iOS device text input via WebDriverAgent."""

import time


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


def type_text(
    text: str,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    frequency: int = 60,
) -> None:
    """
    Type text into the currently focused input field.

    Args:
        text: The text to type.
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        frequency: Typing frequency (keys per minute). Default is 60.

    Note:
        The input field must be focused before calling this function.
        Use tap() to focus on the input field first.
    """
    try:
        import requests

        url = _get_wda_session_url(wda_url, session_id, "wda/keys")

        # Send text to WDA
        response = requests.post(
            url, json={"value": list(text), "frequency": frequency}, timeout=30, verify=False
        )

        if response.status_code not in (200, 201):
            print(f"Warning: Text input may have failed. Status: {response.status_code}")

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error typing text: {e}")


def clear_text(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
) -> None:
    """
    Clear text in the currently focused input field.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.

    Note:
        This sends a clear command to the active element.
        The input field must be focused before calling this function.
    """
    try:
        import requests

        # First, try to get the active element
        url = _get_wda_session_url(wda_url, session_id, "element/active")

        response = requests.get(url, timeout=10, verify=False)

        if response.status_code == 200:
            data = response.json()
            element_id = data.get("value", {}).get("ELEMENT") or data.get("value", {}).get("element-6066-11e4-a52e-4f735466cecf")

            if element_id:
                # Clear the element
                clear_url = _get_wda_session_url(wda_url, session_id, f"element/{element_id}/clear")
                requests.post(clear_url, timeout=10, verify=False)
                return

        # Fallback: send backspace commands
        _clear_with_backspace(wda_url, session_id)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error clearing text: {e}")


def _clear_with_backspace(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    max_backspaces: int = 100,
) -> None:
    """
    Clear text by sending backspace keys.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        max_backspaces: Maximum number of backspaces to send.
    """
    try:
        import requests

        url = _get_wda_session_url(wda_url, session_id, "wda/keys")

        # Send backspace character multiple times
        backspace_char = "\u0008"  # Backspace Unicode character
        requests.post(
            url,
            json={"value": [backspace_char] * max_backspaces},
            timeout=10,
            verify=False,
        )

    except Exception as e:
        print(f"Error clearing with backspace: {e}")


def send_keys(
    keys: list[str],
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
) -> None:
    """
    Send a sequence of keys.

    Args:
        keys: List of keys to send.
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.

    Example:
        >>> send_keys(["H", "e", "l", "l", "o"])
        >>> send_keys(["\n"])  # Send enter key
    """
    try:
        import requests

        url = _get_wda_session_url(wda_url, session_id, "wda/keys")

        requests.post(url, json={"value": keys}, timeout=10, verify=False)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error sending keys: {e}")


def press_enter(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 0.5,
) -> None:
    """
    Press the Enter/Return key.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after pressing enter.
    """
    send_keys(["\n"], wda_url, session_id)
    time.sleep(delay)


def hide_keyboard(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
) -> None:
    """
    Hide the on-screen keyboard.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
    """
    try:
        import requests

        url = f"{wda_url.rstrip('/')}/wda/keyboard/dismiss"

        requests.post(url, timeout=10, verify=False)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error hiding keyboard: {e}")


def is_keyboard_shown(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
) -> bool:
    """
    Check if the on-screen keyboard is currently shown.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.

    Returns:
        True if keyboard is shown, False otherwise.
    """
    try:
        import requests

        url = _get_wda_session_url(wda_url, session_id, "wda/keyboard/shown")

        response = requests.get(url, timeout=5, verify=False)

        if response.status_code == 200:
            data = response.json()
            return data.get("value", False)

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception:
        pass

    return False


def set_pasteboard(
    text: str,
    wda_url: str = "http://localhost:8100",
) -> None:
    """
    Set the device pasteboard (clipboard) content.

    Args:
        text: Text to set in pasteboard.
        wda_url: WebDriverAgent URL.

    Note:
        This can be useful for inputting large amounts of text.
        After setting pasteboard, you can simulate paste gesture.
    """
    try:
        import requests

        url = f"{wda_url.rstrip('/')}/wda/setPasteboard"

        requests.post(
            url, json={"content": text, "contentType": "plaintext"}, timeout=10, verify=False
        )

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error setting pasteboard: {e}")


def get_pasteboard(
    wda_url: str = "http://localhost:8100",
) -> str | None:
    """
    Get the device pasteboard (clipboard) content.

    Args:
        wda_url: WebDriverAgent URL.

    Returns:
        Pasteboard content or None if failed.
    """
    try:
        import requests

        url = f"{wda_url.rstrip('/')}/wda/getPasteboard"

        response = requests.post(url, timeout=10, verify=False)

        if response.status_code == 200:
            data = response.json()
            return data.get("value")

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error getting pasteboard: {e}")

    return None
