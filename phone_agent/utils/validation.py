"""Input validation utilities."""

from typing import Any


def validate_coordinates(
    x: int | float, y: int | float, width: int, height: int
) -> tuple[int, int]:
    """
    Validate and clamp coordinates to screen bounds.

    Args:
        x: X coordinate.
        y: Y coordinate.
        width: Screen width.
        height: Screen height.

    Returns:
        Validated (x, y) tuple clamped to screen bounds.
    """
    x = max(0, min(int(x), width - 1))
    y = max(0, min(int(y), height - 1))
    return x, y


def validate_relative_coordinates(
    element: list[int | float], screen_width: int, screen_height: int
) -> tuple[int, int]:
    """
    Validate and convert relative coordinates (0-1000) to absolute pixels.

    Args:
        element: List of [x, y] coordinates in relative format (0-1000).
        screen_width: Screen width in pixels.
        screen_height: Screen height in pixels.

    Returns:
        Tuple of (x, y) absolute coordinates.

    Raises:
        ValueError: If element format is invalid.
    """
    if not isinstance(element, list) or len(element) < 2:
        raise ValueError(f"Invalid element format: {element}. Expected [x, y]")

    x_rel = float(element[0])
    y_rel = float(element[1])

    if not (0 <= x_rel <= 1000) or not (0 <= y_rel <= 1000):
        raise ValueError(
            f"Relative coordinates must be between 0 and 1000. Got: [{x_rel}, {y_rel}]"
        )

    x = int(x_rel / 1000 * screen_width)
    y = int(y_rel / 1000 * screen_height)

    return validate_coordinates(x, y, screen_width, screen_height)


def validate_app_name(app_name: str, allowed_apps: set[str] | None = None) -> str:
    """
    Validate app name.

    Args:
        app_name: App name to validate.
        allowed_apps: Optional set of allowed app names.

    Returns:
        Validated app name.

    Raises:
        ValueError: If app name is invalid.
    """
    if not app_name or not isinstance(app_name, str):
        raise ValueError(f"Invalid app name: {app_name}")

    app_name = app_name.strip()

    if allowed_apps and app_name not in allowed_apps:
        raise ValueError(
            f"App '{app_name}' not in allowed apps: {sorted(allowed_apps)}"
        )

    return app_name


def validate_port(port: int) -> int:
    """
    Validate TCP port number.

    Args:
        port: Port number to validate.

    Returns:
        Validated port number.

    Raises:
        ValueError: If port is out of valid range.
    """
    if not isinstance(port, int) or not (1 <= port <= 65535):
        raise ValueError(f"Invalid port number: {port}. Must be between 1 and 65535")
    return port


def validate_url(url: str) -> str:
    """
    Validate URL format.

    Args:
        url: URL to validate.

    Returns:
        Validated URL.

    Raises:
        ValueError: If URL format is invalid.
    """
    if not url or not isinstance(url, str):
        raise ValueError(f"Invalid URL: {url}")

    url = url.strip()

    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError(f"URL must start with http:// or https://: {url}")

    return url

