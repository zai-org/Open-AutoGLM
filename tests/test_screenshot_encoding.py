"""Tests for screenshot.py encoding handling.

This test verifies that subprocess.run uses binary mode (text=False) to avoid
UTF-8 encoding errors when handling screenshot operations (Issue #224).
"""

import os
import re
import unittest


class TestScreenshotEncodingFix(unittest.TestCase):
    """Test that screenshot.py uses binary mode for subprocess calls."""

    def test_screenshot_uses_binary_mode_for_screencap(self):
        """Verify screencap command uses text=False."""
        screenshot_py_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'phone_agent', 'adb', 'screenshot.py'
        )

        with open(screenshot_py_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the screencap subprocess.run call
        screencap_pattern = r'subprocess\.run\([^)]*screencap[^)]*\)'
        match = re.search(screencap_pattern, content, re.DOTALL)
        self.assertIsNotNone(match, "Could not find subprocess.run with screencap")

        subprocess_call = match.group(0)

        # Verify text=False is used (binary mode)
        self.assertIn('text=False', subprocess_call,
                      "screencap should use text=False for binary mode")

    def test_screenshot_uses_binary_mode_for_pull(self):
        """Verify pull command uses text=False."""
        screenshot_py_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'phone_agent', 'adb', 'screenshot.py'
        )

        with open(screenshot_py_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the pull subprocess.run call
        pull_pattern = r'subprocess\.run\([^)]*"pull"[^)]*\)'
        match = re.search(pull_pattern, content, re.DOTALL)
        self.assertIsNotNone(match, "Could not find subprocess.run with pull")

        subprocess_call = match.group(0)

        # Verify text=False is used (binary mode)
        self.assertIn('text=False', subprocess_call,
                      "pull should use text=False for binary mode")

    def test_screenshot_decodes_output_with_error_handling(self):
        """Verify output is decoded with errors='replace'."""
        screenshot_py_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'phone_agent', 'adb', 'screenshot.py'
        )

        with open(screenshot_py_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for proper decoding with error handling
        self.assertIn('decode("utf-8", errors="replace")', content,
                      "Output should be decoded with errors='replace' to handle surrogates")


if __name__ == '__main__':
    unittest.main()
