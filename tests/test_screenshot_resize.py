import base64
from io import BytesIO

from PIL import Image

from phone_agent.adb.screenshot import (
    _create_fallback_screenshot,
    _resize_image_to_model_limit,
)


def _decode_image_size(base64_data: str) -> tuple[int, int]:
    image_data = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_data))
    return image.size


def test_resize_image_to_model_limit_preserves_aspect_ratio() -> None:
    image = Image.new("RGB", (1240, 2772), color="white")

    resized = _resize_image_to_model_limit(image)

    assert resized.size == (916, 2048)


def test_fallback_screenshot_stays_within_model_limit() -> None:
    screenshot = _create_fallback_screenshot(is_sensitive=False)

    assert max(screenshot.width, screenshot.height) <= 2048
    assert _decode_image_size(screenshot.base64_data) == (
        screenshot.width,
        screenshot.height,
    )
