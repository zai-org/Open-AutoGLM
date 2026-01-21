"""Tests for answer tag cleaning in handler.py.

This test verifies that parse_action properly cleans <answer> and </answer>
tags from model output (Issue #258).
"""

import os
import re
import unittest


class TestAnswerTagCleaning(unittest.TestCase):
    """Test that handler.py cleans answer tags from model output."""

    def test_handler_cleans_answer_tags(self):
        """Verify handler.py removes <answer> and </answer> tags."""
        handler_py_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'phone_agent', 'actions', 'handler.py'
        )

        with open(handler_py_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for answer tag cleaning in parse_action function
        self.assertIn("replace('<answer>', '')", content,
                      "handler.py should remove <answer> tags")
        self.assertIn("replace('</answer>', '')", content,
                      "handler.py should remove </answer> tags")

    def test_answer_tag_cleaning_uses_replace(self):
        """Verify answer tag cleaning uses replace() instead of slice indexing."""
        handler_py_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'phone_agent', 'actions', 'handler.py'
        )

        with open(handler_py_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find parse_action function content
        parse_action_start = content.find('def parse_action')
        self.assertNotEqual(parse_action_start, -1,
                            "Could not find parse_action function")

        # Get function body (until next def or end of file)
        next_def = content.find('\ndef ', parse_action_start + 1)
        if next_def == -1:
            parse_action_body = content[parse_action_start:]
        else:
            parse_action_body = content[parse_action_start:next_def]

        # Verify both tags are cleaned using replace
        self.assertIn(".replace('<answer>', '')", parse_action_body,
                      "Should use replace() for <answer> tag cleaning")
        self.assertIn(".replace('</answer>', '')", parse_action_body,
                      "Should use replace() for </answer> tag cleaning")


if __name__ == '__main__':
    unittest.main()
