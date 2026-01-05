"""Tests for readline support in interactive mode.

This test verifies that main.py imports readline to enable arrow key
navigation and history browsing in interactive mode (Issue #223).
"""

import os
import re
import unittest


class TestReadlineSupport(unittest.TestCase):
    """Test that main.py has readline import for arrow key support."""

    def test_main_py_imports_readline(self):
        """Verify main.py imports readline module."""
        main_py_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'main.py'
        )

        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for readline import (with try/except for cross-platform compatibility)
        self.assertIn('import readline', content,
                      "main.py should import readline for arrow key support")

    def test_readline_import_has_error_handling(self):
        """Verify readline import has try/except for Windows compatibility."""
        main_py_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'main.py'
        )

        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that readline import is wrapped in try/except
        pattern = r'try:\s*\n\s*import readline.*?\nexcept ImportError:'
        match = re.search(pattern, content, re.DOTALL)
        self.assertIsNotNone(match,
                             "readline import should be wrapped in try/except for Windows compatibility")


if __name__ == '__main__':
    unittest.main()
