"""Screenshot utilities for capturing HarmonyOS device screen."""

import base64
import os
import tempfile
import uuid
from dataclasses import dataclass
from io import BytesIO

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
    capture_id = uuid.uuid4().hex
    temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_{capture_id}.png")
    remote_path = f"/data/local/tmp/openautoglm_screenshot_{capture_id}.jpeg"
    hdc_prefix = _get_hdc_prefix(device_id)

    try:
        result = _run_hdc_command(
            hdc_prefix + ["shell", "screenshot", remote_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = result.stdout + result.stderr
        if (
            "fail" in output.lower()
            or "error" in output.lower()
            or "not found" in output.lower()
        ):
            result = _run_hdc_command(
                hdc_prefix + ["shell", "snapshot_display", "-f", remote_path],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = result.stdout + result.stderr
            if "fail" in output.lower() or "error" in output.lower():
                return _create_fallback_screenshot(is_sensitive=True)

        _run_hdc_command(
            hdc_prefix + ["file", "recv", remote_path, temp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if not os.path.exists(temp_path):
            return _create_fallback_screenshot(is_sensitive=False)

        with Image.open(temp_path) as img:
            width, height = img.size
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return Screenshot(
            base64_data=base64_data,
            width=width,
            height=height,
            is_sensitive=False,
        )

    except Exception as exc:
        print(f"Screenshot error: {exc}")
        return _create_fallback_screenshot(is_sensitive=False)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

        try:
            _run_hdc_command(
                hdc_prefix + ["shell", "rm", "-f", remote_path],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except Exception:
            pass


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
