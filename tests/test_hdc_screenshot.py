import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

import phone_agent.hdc.screenshot as screenshot_module


class HDCScreenshotTempFileTests(unittest.TestCase):
    def _successful_runner(self, commands):
        def fake_run(command, **kwargs):
            commands.append(command)
            if command[1:3] == ["file", "recv"]:
                Image.new("RGB", (3, 2), color="white").save(
                    command[-1], format="JPEG"
                )
            return SimpleNamespace(stdout="", stderr="")

        return fake_run

    def test_success_uses_unique_remote_path_and_cleans_temp_files(self):
        commands = []
        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch.object(
                    screenshot_module.uuid,
                    "uuid4",
                    return_value=SimpleNamespace(hex="capture-one"),
                ),
                patch.object(
                    screenshot_module.tempfile,
                    "gettempdir",
                    return_value=temp_dir,
                ),
                patch.object(
                    screenshot_module,
                    "_run_hdc_command",
                    side_effect=self._successful_runner(commands),
                ),
            ):
                result = screenshot_module.get_screenshot()

            local_path = os.path.join(temp_dir, "screenshot_capture-one.png")
            remote_path = "/data/local/tmp/openautoglm_screenshot_capture-one.jpeg"
            self.assertEqual(result.width, 3)
            self.assertEqual(result.height, 2)
            self.assertFalse(result.is_sensitive)
            self.assertFalse(os.path.exists(local_path))
            self.assertEqual(commands[0], ["hdc", "shell", "screenshot", remote_path])
            self.assertIn(["hdc", "file", "recv", remote_path, local_path], commands)
            self.assertEqual(
                commands[-1], ["hdc", "shell", "rm", "-f", remote_path]
            )

    def test_each_capture_uses_a_different_remote_path(self):
        commands = []
        ids = [
            SimpleNamespace(hex="capture-one"),
            SimpleNamespace(hex="capture-two"),
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch.object(screenshot_module.uuid, "uuid4", side_effect=ids),
                patch.object(
                    screenshot_module.tempfile,
                    "gettempdir",
                    return_value=temp_dir,
                ),
                patch.object(
                    screenshot_module,
                    "_run_hdc_command",
                    side_effect=self._successful_runner(commands),
                ),
            ):
                screenshot_module.get_screenshot()
                screenshot_module.get_screenshot()

        capture_commands = [
            command
            for command in commands
            if command[1:3] == ["shell", "screenshot"]
        ]
        self.assertEqual(len(capture_commands), 2)
        self.assertNotEqual(capture_commands[0][-1], capture_commands[1][-1])

    def test_sensitive_fallback_still_cleans_remote_path(self):
        commands = []

        def fake_run(command, **kwargs):
            commands.append(command)
            if "screenshot" in command or "snapshot_display" in command:
                return SimpleNamespace(stdout="", stderr="error")
            return SimpleNamespace(stdout="", stderr="")

        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch.object(
                    screenshot_module.uuid,
                    "uuid4",
                    return_value=SimpleNamespace(hex="capture-failed"),
                ),
                patch.object(
                    screenshot_module.tempfile,
                    "gettempdir",
                    return_value=temp_dir,
                ),
                patch.object(
                    screenshot_module,
                    "_run_hdc_command",
                    side_effect=fake_run,
                ),
            ):
                result = screenshot_module.get_screenshot()

        remote_path = "/data/local/tmp/openautoglm_screenshot_capture-failed.jpeg"
        self.assertTrue(result.is_sensitive)
        self.assertEqual(
            commands[-1], ["hdc", "shell", "rm", "-f", remote_path]
        )


if __name__ == "__main__":
    unittest.main()
