"""Tests for device.py encoding handling.

This test verifies that subprocess.run is called with proper encoding parameters
to handle Windows GBK/UTF-8 encoding issues (Issue #241).
"""

import os
import re
import unittest


class TestDeviceEncodingFix(unittest.TestCase):
    """Test that device.py has proper encoding parameters."""

    def test_device_py_has_encoding_and_errors_params(self):
        """Verify device.py uses encoding='utf-8' and errors='ignore'."""
        device_py_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'phone_agent', 'adb', 'device.py'
        )

        with open(device_py_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for subprocess.run call with dumpsys window
        dumpsys_pattern = r'subprocess\.run\([^)]*dumpsys.*?window[^)]*\)'
        match = re.search(dumpsys_pattern, content, re.DOTALL)
        self.assertIsNotNone(match, "Could not find subprocess.run with dumpsys window")

        subprocess_call = match.group(0)

        # Verify encoding parameter
        self.assertIn('encoding="utf-8"', subprocess_call,
                      "Missing encoding='utf-8' parameter")

        # Verify errors parameter (key fix for Issue #241)
        self.assertIn('errors="ignore"', subprocess_call,
                      "Missing errors='ignore' parameter for Windows GBK/UTF-8 compatibility")

        # Verify text=True is present
        self.assertIn('text=True', subprocess_call,
                      "Missing text=True parameter")

        # Verify capture_output=True is present
        self.assertIn('capture_output=True', subprocess_call,
                      "Missing capture_output=True parameter")


if __name__ == '__main__':
    unittest.main()
