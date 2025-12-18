"""Device control utilities for iOS automation via WebDriverAgent."""

import logging
import time
from typing import Optional

from phone_agent.config.apps_ios import IOS_APP_PACKAGES as IOS_APP_BUNDLES
from phone_agent.wda.client import get_client

logger = logging.getLogger(__name__)


# iOS screen scale factor for coordinate conversion
# Modern iPhones (6+, X, 11, 12, 13, 14, 15 Pro) use @3x
# iPhone SE, older devices use @2x
# WDA expects coordinates in POINTS, not PIXELS!
# Pixels = Points * Scale
DEFAULT_SCALE_FACTOR = 3.0

# Cache for scale factor to avoid repeated HTTP calls
_scale_factor_cache: dict[str, float] = {}


def _get_scale_factor(device_id: str | None = None) -> float:
    """
    Get the screen scale factor for the device (with caching).
    
    Returns:
        Scale factor (typically 2.0 or 3.0)
    """
    cache_key = device_id or "default"
    
    # Return cached value if available
    if cache_key in _scale_factor_cache:
        return _scale_factor_cache[cache_key]
    
    # Query WDA for scale factor
    try:
        client = get_client(device_id)
        resp = client.get("/wda/screen", use_session=False)
        value = resp.get("value", {})
        scale = float(value.get("scale", DEFAULT_SCALE_FACTOR))
    except Exception as e:
        logger.debug(f"Failed to get scale factor, using default: {e}")
        scale = DEFAULT_SCALE_FACTOR
    
    # Cache the result
    _scale_factor_cache[cache_key] = scale
    logger.debug(f"Cached scale factor for {cache_key}: {scale}")
    
    return scale


def _pixels_to_points(x: int, y: int, device_id: str | None = None) -> tuple[float, float]:
    """
    Convert pixel coordinates to points for WDA.
    
    WDA expects coordinates in points (logical coordinates),
    not pixels. Modern iPhones use @3x scaling.
    
    Args:
        x: X coordinate in pixels
        y: Y coordinate in pixels
        device_id: WDA URL or None to use default
        
    Returns:
        Tuple of (x_points, y_points)
    """
    scale = _get_scale_factor(device_id)
    return x / scale, y / scale


def get_current_app(device_id: str | None = None) -> str:
    """
    Get the currently focused app name.
    
    Args:
        device_id: WDA URL or None to use default
        
    Returns:
        The app name if recognized, otherwise the bundleId or "SpringBoard"
    """
    client = get_client(device_id)
    
    try:
        resp = client.get("/wda/activeAppInfo")
        value = resp.get("value", {})
        bundle_id = value.get("bundleId", "")
        
        if not bundle_id:
            return "SpringBoard"
        
        # Reverse lookup app name from bundle ID
        for name, bid in IOS_APP_BUNDLES.items():
            if bid == bundle_id:
                return name
        
        # Return bundleId if not in our mapping
        return bundle_id
        
    except Exception as e:
        logger.error(f"Failed to get current app: {e}")
        return "SpringBoard"


def tap(x: int, y: int, device_id: str | None = None, delay: float = 0.5) -> None:
    """
    Tap at the specified coordinates.
    
    Args:
        x: X coordinate in pixels (will be converted to points)
        y: Y coordinate in pixels (will be converted to points)
        device_id: WDA URL or None to use default
        delay: Delay in seconds after tap
    """
    client = get_client(device_id)
    x_pt, y_pt = _pixels_to_points(x, y, device_id)
    logger.debug(f"[tap] pixels=({x}, {y}) -> points=({x_pt:.1f}, {y_pt:.1f})")
    client.post("/wda/tap", {"x": x_pt, "y": y_pt})
    time.sleep(delay)


def double_tap(x: int, y: int, device_id: str | None = None, delay: float = 0.5) -> None:
    """
    Double tap at the specified coordinates.
    
    Args:
        x: X coordinate in pixels (will be converted to points)
        y: Y coordinate in pixels (will be converted to points)
        device_id: WDA URL or None to use default
        delay: Delay in seconds after double tap
    """
    client = get_client(device_id)
    x_pt, y_pt = _pixels_to_points(x, y, device_id)
    client.post("/wda/doubleTap", {"x": x_pt, "y": y_pt})
    time.sleep(delay)


def long_press(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: str | None = None,
    delay: float = 0.5,
) -> None:
    """
    Long press at the specified coordinates.
    
    Args:
        x: X coordinate in pixels (will be converted to points)
        y: Y coordinate in pixels (will be converted to points)
        duration_ms: Duration of press in milliseconds
        device_id: WDA URL or None to use default
        delay: Delay in seconds after long press
    """
    client = get_client(device_id)
    x_pt, y_pt = _pixels_to_points(x, y, device_id)
    duration_sec = duration_ms / 1000.0
    client.post("/wda/touchAndHold", {"x": x_pt, "y": y_pt, "duration": duration_sec})
    time.sleep(delay)


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    delay: float = 0.5,
) -> None:
    """
    Swipe from start to end coordinates.
    
    Args:
        start_x: Starting X coordinate in pixels (will be converted to points)
        start_y: Starting Y coordinate in pixels (will be converted to points)
        end_x: Ending X coordinate in pixels (will be converted to points)
        end_y: Ending Y coordinate in pixels (will be converted to points)
        duration_ms: Duration of swipe in milliseconds (default: 500ms)
        device_id: WDA URL or None to use default
        delay: Delay in seconds after swipe
    """
    client = get_client(device_id)
    
    if duration_ms is None:
        duration_ms = 500
    
    duration_sec = duration_ms / 1000.0
    
    # Convert pixels to points
    start_x_pt, start_y_pt = _pixels_to_points(start_x, start_y, device_id)
    end_x_pt, end_y_pt = _pixels_to_points(end_x, end_y, device_id)
    
    # Use drag from-to endpoint
    client.post("/wda/dragfromtoforduration", {
        "fromX": start_x_pt,
        "fromY": start_y_pt,
        "toX": end_x_pt,
        "toY": end_y_pt,
        "duration": duration_sec
    })
    time.sleep(delay)


def back(device_id: str | None = None, delay: float = 0.5) -> None:
    """
    Simulate back navigation on iOS.
    
    iOS doesn't have a back button. This performs an edge swipe from
    the left side of the screen to simulate going back.
    
    Args:
        device_id: WDA URL or None to use default
        delay: Delay in seconds after the gesture
    """
    # Edge swipe from left side of screen
    # NOTE: These are POINT coordinates (not pixels)!
    # For edge swipe, we use points directly since this is a fixed gesture
    client = get_client(device_id)
    
    # Get scale to compute proper pixel coordinates that will be converted back
    scale = _get_scale_factor(device_id)
    
    # Target points: start at x=10pt, swipe to x=150pt
    # Convert to pixels so swipe() can convert them back to points
    swipe(
        start_x=int(10 * scale),   # ~30 pixels on @3x
        start_y=int(400 * scale),  # ~1200 pixels on @3x
        end_x=int(150 * scale),    # ~450 pixels on @3x
        end_y=int(400 * scale),
        duration_ms=300,
        device_id=device_id,
        delay=0
    )
    time.sleep(delay)


def home(device_id: str | None = None, delay: float = 0.5) -> None:
    """
    Go to home screen.
    
    Args:
        device_id: WDA URL or None to use default
        delay: Delay in seconds after going home
    """
    client = get_client(device_id)
    # /wda/homescreen doesn't require session
    client.post("/wda/homescreen", use_session=False)
    time.sleep(delay)


def launch_app(app_name: str, device_id: str | None = None, delay: float = 2.0) -> bool:
    """
    Launch an app by name.
    
    Args:
        app_name: The app name (must be in IOS_APP_BUNDLES)
        device_id: WDA URL or None to use default
        delay: Delay in seconds after launching
        
    Returns:
        True if app was launched, False if app not found
    """
    bundle_id = IOS_APP_BUNDLES.get(app_name)
    
    if not bundle_id:
        # Try case-insensitive match
        for name, bid in IOS_APP_BUNDLES.items():
            if name.lower() == app_name.lower():
                bundle_id = bid
                break
    
    if not bundle_id:
        logger.warning(f"App not found in bundle mapping: {app_name}")
        return False
    
    client = get_client(device_id)
    
    try:
        # Use /wda/apps/launch endpoint instead of creating new session
        # This preserves the existing session
        resp = client.post("/wda/apps/launch", {
            "bundleId": bundle_id,
            "shouldWaitForQuiescence": False
        })
        
        if "error" not in resp:
            time.sleep(delay)
            return True
        else:
            logger.error(f"Failed to launch app: {resp.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to launch app {app_name}: {e}")
        return False


def press_button(button: str, device_id: str | None = None, delay: float = 0.5) -> None:
    """
    Press a physical button on the device.
    
    Args:
        button: Button name (home, volumeUp, volumeDown)
        device_id: WDA URL or None to use default
        delay: Delay in seconds after pressing
    """
    client = get_client(device_id)
    client.post("/wda/pressButton", {"name": button})
    time.sleep(delay)


def lock_screen(device_id: str | None = None) -> None:
    """Lock the device screen."""
    client = get_client(device_id)
    client.post("/wda/lock")


def unlock_screen(device_id: str | None = None) -> None:
    """Unlock the device screen."""
    client = get_client(device_id)
    client.post("/wda/unlock")


def is_locked(device_id: str | None = None) -> bool:
    """Check if the device screen is locked."""
    client = get_client(device_id)
    resp = client.get("/wda/locked")
    return resp.get("value", False)


def get_window_size(device_id: str | None = None) -> tuple[int, int]:
    """
    Get the window size.
    
    Returns:
        Tuple of (width, height)
    """
    client = get_client(device_id)
    resp = client.get("/window/size")
    value = resp.get("value", {})
    return int(value.get("width", 390)), int(value.get("height", 844))
