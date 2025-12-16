"""Input utilities for iOS device text input via WebDriverAgent."""

import time

from phone_agent.xctest.wda_client import WDAClient, WDAError

def _get_client(
    wda_url: str, session_id: str | None, client: WDAClient | None
) -> WDAClient:
    return client or WDAClient(wda_url, session_id=session_id)


def type_text(
    text: str,
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    frequency: int = 60,
    client: WDAClient | None = None,
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
        wda = _get_client(wda_url, session_id, client)
        wda.post(
            "wda/keys",
            json={"value": list(text), "frequency": frequency},
            timeout=30.0,
            allow_status=(200, 201),
        )
    except WDAError as e:
        print(f"Error typing text: {e}")


def clear_text(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    client: WDAClient | None = None,
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
        wda = _get_client(wda_url, session_id, client)

        data = wda.get("element/active", timeout=10.0)
        element_id = None
        if isinstance(data, dict):
            value = data.get("value", {})
            if isinstance(value, dict):
                element_id = value.get("ELEMENT") or value.get(
                    "element-6066-11e4-a52e-4f735466cecf"
                )

        if element_id:
            wda.post(
                f"element/{element_id}/clear",
                timeout=10.0,
                allow_status=(200, 201, 204),
            )
            return

        _clear_with_backspace(wda_url, session_id, client=client)

    except WDAError as e:
        print(f"Error clearing text: {e}")


def _clear_with_backspace(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    max_backspaces: int = 100,
    client: WDAClient | None = None,
) -> None:
    """
    Clear text by sending backspace keys.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        max_backspaces: Maximum number of backspaces to send.
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        backspace_char = "\u0008"
        wda.post(
            "wda/keys",
            json={"value": [backspace_char] * max_backspaces},
            timeout=10.0,
            allow_status=(200, 201),
        )
    except WDAError as e:
        print(f"Error clearing with backspace: {e}")


def send_keys(
    keys: list[str],
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    client: WDAClient | None = None,
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
        wda = _get_client(wda_url, session_id, client)
        wda.post("wda/keys", json={"value": keys}, timeout=10.0, allow_status=(200, 201))
    except WDAError as e:
        print(f"Error sending keys: {e}")


def press_enter(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    delay: float = 0.5,
    client: WDAClient | None = None,
) -> None:
    """
    Press the Enter/Return key.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
        delay: Delay in seconds after pressing enter.
    """
    send_keys(["\n"], wda_url, session_id, client=client)
    time.sleep(delay)


def hide_keyboard(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    client: WDAClient | None = None,
) -> None:
    """
    Hide the on-screen keyboard.

    Args:
        wda_url: WebDriverAgent URL.
        session_id: Optional WDA session ID.
    """
    try:
        wda = _get_client(wda_url, session_id, client)
        wda.post(
            "wda/keyboard/dismiss",
            use_session=False,
            timeout=10.0,
            allow_status=(200, 201, 204),
        )
    except WDAError as e:
        print(f"Error hiding keyboard: {e}")


def is_keyboard_shown(
    wda_url: str = "http://localhost:8100",
    session_id: str | None = None,
    client: WDAClient | None = None,
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
        wda = _get_client(wda_url, session_id, client)
        data = wda.get("wda/keyboard/shown", timeout=5.0)
        if isinstance(data, dict):
            return bool(data.get("value", False))
    except WDAError:
        return False

    return False


def set_pasteboard(
    text: str,
    wda_url: str = "http://localhost:8100",
    client: WDAClient | None = None,
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
        wda = client or WDAClient(wda_url)
        wda.post(
            "wda/setPasteboard",
            use_session=False,
            json={"content": text, "contentType": "plaintext"},
            timeout=10.0,
            allow_status=(200, 201, 204),
        )
    except WDAError as e:
        print(f"Error setting pasteboard: {e}")


def get_pasteboard(
    wda_url: str = "http://localhost:8100",
    client: WDAClient | None = None,
) -> str | None:
    """
    Get the device pasteboard (clipboard) content.

    Args:
        wda_url: WebDriverAgent URL.

    Returns:
        Pasteboard content or None if failed.
    """
    try:
        wda = client or WDAClient(wda_url)
        data = wda.post(
            "wda/getPasteboard",
            use_session=False,
            timeout=10.0,
            allow_status=(200, 201),
        )
        if isinstance(data, dict):
            return data.get("value")
    except WDAError as e:
        print(f"Error getting pasteboard: {e}")

    return None
