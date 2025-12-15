import base64
import os
import subprocess
import tempfile
import time
import uuid
from io import BytesIO

from PIL import Image

from phone_agent.adb.screenshot import Screenshot
from phone_agent.device.base import DeviceController


class HarmonyDeviceController(DeviceController):
    def __init__(self, hdc_path: str, target: str | None = None):
        self.hdc_path = hdc_path
        self.target = target

    def _hdc_prefix(self) -> list[str]:
        cmd = [self.hdc_path]
        if self.target:
            cmd.extend(["-t", self.target])
        return cmd

    def get_screenshot(self) -> Screenshot:
        remote_path = "/data/local/tmp/screenshot.png"
        local_path = os.path.join(
            tempfile.gettempdir(), f"harmony_screenshot_{uuid.uuid4()}.png"
        )

        try:
            subprocess.run(
                self._hdc_prefix() + ["shell", "rm", remote_path],
                capture_output=True,
                text=True,
            )
            time.sleep(0.5)
            subprocess.run(
                self._hdc_prefix()
                + ["shell", "uitest", "screenCap", "-p", remote_path],
                capture_output=True,
                text=True,
            )
            time.sleep(0.5)
            subprocess.run(
                self._hdc_prefix() + ["file", "recv", remote_path, local_path],
                capture_output=True,
                text=True,
            )
            time.sleep(0.5)

            if not os.path.exists(local_path):
                return self._create_fallback_screenshot(False)

            img = Image.open(local_path)
            width, height = img.size

            buffered = BytesIO()
            img.save(buffered, format="PNG")
            base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

            os.remove(local_path)

            return Screenshot(
                base64_data=base64_data, width=width, height=height, is_sensitive=False
            )
        except Exception:
            return self._create_fallback_screenshot(False)

    def tap(self, x: int, y: int) -> None:
        subprocess.run(
            self._hdc_prefix()
            + ["shell", "uitest", "uiInput", "click", str(x), str(y)],
            capture_output=True,
            text=True,
        )

    def swipe(self, x1: int, y1: int, x2: int, y2: int) -> None:
        subprocess.run(
            self._hdc_prefix()
            + [
                "shell",
                "uitest",
                "uiInput",
                "swipe",
                str(x1),
                str(y1),
                str(x2),
                str(y2),
                "500",
            ],
            capture_output=True,
            text=True,
        )

    def back(self) -> None:
        subprocess.run(
            self._hdc_prefix()
            + ["shell", "uitest", "uiInput", "keyEvent", "Back"],
            capture_output=True,
            text=True,
        )

    def home(self) -> None:
        subprocess.run(
            self._hdc_prefix()
            + ["shell", "uitest", "uiInput", "keyEvent", "Home"],
            capture_output=True,
            text=True,
        )

    def type_text(self, text: str) -> None:
        safe_text = text.replace("\\n", "_").replace("\n", "_")
        for ch in safe_text:
            if ch == " ":
                subprocess.run(
                    self._hdc_prefix()
                    + ["shell", "uitest", "uiInput", "keyEvent", "2050"],
                    capture_output=True,
                    text=True,
                )
            elif ch == "_":
                subprocess.run(
                    self._hdc_prefix()
                    + ["shell", "uitest", "uiInput", "keyEvent", "2054"],
                    capture_output=True,
                    text=True,
                )
            elif ch.isdigit() or ("a" <= ch <= "z") or ("A" <= ch <= "Z"):
                subprocess.run(
                    self._hdc_prefix()
                    + ["shell", "uitest", "uiInput", "inputText", "1", "1", ch],
                    capture_output=True,
                    text=True,
                )
            elif ch in "-.,!?@'°/:;()":
                subprocess.run(
                    self._hdc_prefix()
                    + [
                        "shell",
                        "uitest",
                        "uiInput",
                        "inputText",
                        "1",
                        "1",
                        ch,
                    ],
                    capture_output=True,
                    text=True,
                )
            else:
                subprocess.run(
                    self._hdc_prefix()
                    + ["shell", "uitest", "uiInput", "inputText", "1", "1", ch],
                    capture_output=True,
                    text=True,
                )
            time.sleep(0.05)

    def launch_app(self, app_name: str) -> bool:
        return False

    def get_current_app(self) -> str:
        return "Harmony Device"

    def _create_fallback_screenshot(self, is_sensitive: bool) -> Screenshot:
        width = 1080
        height = 2400
        img = Image.new("RGB", (width, height), color="black")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return Screenshot(
            base64_data=base64_data,
            width=width,
            height=height,
            is_sensitive=is_sensitive,
        )


