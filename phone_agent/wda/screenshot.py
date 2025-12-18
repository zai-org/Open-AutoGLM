"""Screenshot utilities for capturing iOS device screen via WebDriverAgent."""

import base64
import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

from PIL import Image

from phone_agent.wda.client import get_client

logger = logging.getLogger(__name__)


@dataclass
class Screenshot:
    """Represents a captured screenshot."""
    
    base64_data: str
    width: int
    height: int
    is_sensitive: bool = False


def get_screenshot(device_id: str | None = None, timeout: int = 10) -> Screenshot:
    """
    Capture a screenshot from the connected iOS device via WDA.
    
    Args:
        device_id: WDA URL (e.g., http://192.168.0.105:8100) or None to use default
        timeout: Timeout in seconds for screenshot operation
        
    Returns:
        Screenshot object containing base64 data and dimensions
        
    Note:
        If the screenshot fails, a black fallback image is returned with is_sensitive=True.
    """
    client = get_client(device_id)
    
    try:
        # WDA returns screenshot as base64 encoded PNG
        resp = client.get("/screenshot")
        
        if "error" in resp:
            logger.error(f"Screenshot error: {resp.get('error')}")
            return _create_fallback_screenshot(is_sensitive=True)
        
        base64_data = resp.get("value", "")
        
        if not base64_data:
            return _create_fallback_screenshot(is_sensitive=True)
        
        # Decode to get image dimensions
        try:
            img_bytes = base64.b64decode(base64_data)
            img = Image.open(BytesIO(img_bytes))
            width, height = img.size
        except Exception as e:
            logger.warning(f"Failed to decode screenshot: {e}")
            # Use default iPhone dimensions
            width, height = 1170, 2532
        
        return Screenshot(
            base64_data=base64_data,
            width=width,
            height=height,
            is_sensitive=False
        )
        
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return _create_fallback_screenshot(is_sensitive=False)


def _create_fallback_screenshot(is_sensitive: bool = False) -> Screenshot:
    """
    Create a black fallback image when screenshot fails.
    
    Args:
        is_sensitive: Whether the failure was due to sensitive content
        
    Returns:
        Screenshot with black image
    """
    # Default iPhone 14 Pro dimensions
    default_width, default_height = 1179, 2556
    
    black_img = Image.new("RGB", (default_width, default_height), color="black")
    buffered = BytesIO()
    black_img.save(buffered, format="PNG")
    base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return Screenshot(
        base64_data=base64_data,
        width=default_width,
        height=default_height,
        is_sensitive=is_sensitive
    )


def get_screen_size(device_id: str | None = None) -> tuple[int, int]:
    """
    Get the screen size of the iOS device.
    
    Args:
        device_id: WDA URL or None to use default
        
    Returns:
        Tuple of (width, height) in points
    """
    client = get_client(device_id)
    
    try:
        resp = client.get("/wda/screen")
        value = resp.get("value", {})
        screen_size = value.get("screenSize", {})
        width = int(screen_size.get("width", 390))
        height = int(screen_size.get("height", 844))
        return width, height
    except Exception as e:
        logger.warning(f"Failed to get screen size: {e}")
        # Default to iPhone 14 Pro dimensions in points
        return 393, 852


def get_screen_scale(device_id: str | None = None) -> float:
    """
    Get the screen scale factor of the iOS device.
    
    Args:
        device_id: WDA URL or None to use default
        
    Returns:
        Screen scale factor (e.g., 3.0 for Retina displays)
    """
    client = get_client(device_id)
    
    try:
        resp = client.get("/wda/screen")
        value = resp.get("value", {})
        return float(value.get("scale", 3.0))
    except Exception as e:
        logger.debug(f"Failed to get screen scale: {e}")
        return 3.0
