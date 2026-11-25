import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from phone_agent.xctest.screenshot import _get_screenshot_idevice


@pytest.mark.parametrize("capture_result", ["success", "failed", "corrupt", "timeout"])
def test_idevice_capture_removes_temporary_file(monkeypatch, tmp_path, capture_result):
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))

    def capture(command, **kwargs):
        screenshot_path = Path(command[-1])
        if capture_result == "success":
            with Image.new("RGB", (12, 8)) as image:
                image.save(screenshot_path)
        else:
            screenshot_path.write_bytes(b"partial screenshot")

        if capture_result == "timeout":
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return subprocess.CompletedProcess(command, int(capture_result == "failed"))

    with patch(
        "phone_agent.xctest.screenshot.subprocess.run", side_effect=capture
    ) as run:
        screenshot = _get_screenshot_idevice(device_id="test-device", timeout=10)

    screenshot_path = Path(run.call_args.args[0][-1])
    assert not screenshot_path.exists()
    if capture_result == "success":
        assert screenshot is not None
        assert (screenshot.width, screenshot.height) == (12, 8)
    else:
        assert screenshot is None
