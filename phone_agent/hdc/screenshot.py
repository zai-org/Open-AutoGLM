"""Screenshot utilities for capturing HarmonyOS device screen."""

import base64
import os
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from io import BytesIO
from typing import Tuple

from PIL import Image
from phone_agent.hdc.connection import _run_hdc_command


@dataclass
class Screenshot:
    """Represents a captured screenshot."""

    base64_data: str
    width: int
    height: int
    is_sensitive: bool = False


def get_screenshot(device_id: str | None = None, timeout: int = 10) -> Screenshot:
    """
    Capture a screenshot from the connected HarmonyOS device.

    Args:
        device_id: Optional HDC device ID for multi-device setups.
        timeout: Timeout in seconds for screenshot operations.

    Returns:
        Screenshot object containing base64 data and dimensions.

    Note:
        If the screenshot fails (e.g., on sensitive screens like payment pages),
        a black fallback image is returned with is_sensitive=True.
    """
    temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_{uuid.uuid4()}.png")
    hdc_prefix = _get_hdc_prefix(device_id)

    try:
        # Execute screenshot command
        # HarmonyOS HDC only supports JPEG format
        remote_path = "/data/local/tmp/tmp_screenshot.jpeg"

        # Try method 1: hdc shell screenshot (newer HarmonyOS versions)
        result = _run_hdc_command(
            hdc_prefix + ["shell", "screenshot", remote_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Check for screenshot failure (sensitive screen)
        output = result.stdout + result.stderr
        if "fail" in output.lower() or "error" in output.lower() or "not found" in output.lower():
            # Try method 2: snapshot_display (older versions or different devices)
            result = _run_hdc_command(
                hdc_prefix + ["shell", "snapshot_display", "-f", remote_path],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = result.stdout + result.stderr
            if "fail" in output.lower() or "error" in output.lower():
                return _create_fallback_screenshot(is_sensitive=True)

        # Pull screenshot to local temp path
        # Note: remote file is JPEG, but PIL can open it regardless of local extension
        _run_hdc_command(
            hdc_prefix + ["file", "recv", remote_path, temp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if not os.path.exists(temp_path):
            return _create_fallback_screenshot(is_sensitive=False)

        # Read JPEG image and convert to PNG for model inference
        # PIL automatically detects the image format from file content
        img = Image.open(temp_path)
        width, height = img.size

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Cleanup
        os.remove(temp_path)

        return Screenshot(
            base64_data=base64_data, width=width, height=height, is_sensitive=False
        )

    except Exception as e:
        print(f"Screenshot error: {e}")
        return _create_fallback_screenshot(is_sensitive=False)


def _get_hdc_prefix(device_id: str | None) -> list:
    """Get HDC command prefix with optional device specifier."""
    if device_id:
        return ["hdc", "-t", device_id]
    return ["hdc"]


def _create_fallback_screenshot(is_sensitive: bool) -> Screenshot:
    """Create a black fallback image when screenshot fails."""
    default_width, default_height = 1080, 2400

    black_img = Image.new("RGB", (default_width, default_height), color="black")
    buffered = BytesIO()
    black_img.save(buffered, format="PNG")
    base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return Screenshot(
        base64_data=base64_data,
        width=default_width,
        height=default_height,
        is_sensitive=is_sensitive,
    )
