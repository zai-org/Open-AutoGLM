"""Unit tests for phone_agent.actions.handler.parse_action.

These tests exercise the parsing of raw model output strings into action
dictionaries. They are pure and deterministic — no device or network access.
"""

import pytest

from phone_agent.actions.handler import do, finish, parse_action


class TestParseDoActions:
    """Tests for parsing ``do(...)`` actions."""

    def test_parse_tap(self):
        action = parse_action('do(action="Tap", element=[500, 500])')
        assert action["_metadata"] == "do"
        assert action["action"] == "Tap"
        assert action["element"] == [500, 500]

    def test_parse_launch(self):
        action = parse_action('do(action="Launch", app="Settings")')
        assert action["_metadata"] == "do"
        assert action["action"] == "Launch"
        assert action["app"] == "Settings"

    def test_parse_swipe(self):
        action = parse_action(
            'do(action="Swipe", start=[100, 200], end=[100, 800])'
        )
        assert action["_metadata"] == "do"
        assert action["action"] == "Swipe"
        assert action["start"] == [100, 200]
        assert action["end"] == [100, 800]

    def test_parse_back(self):
        action = parse_action('do(action="Back")')
        assert action["_metadata"] == "do"
        assert action["action"] == "Back"

    def test_parse_double_tap(self):
        action = parse_action('do(action="Double Tap", element=[300, 400])')
        assert action["action"] == "Double Tap"
        assert action["element"] == [300, 400]

    def test_parse_wait_with_duration(self):
        action = parse_action('do(action="Wait", duration="3 seconds")')
        assert action["action"] == "Wait"
        assert action["duration"] == "3 seconds"

    def test_parse_tap_with_confirmation_message(self):
        action = parse_action(
            'do(action="Tap", element=[500, 500], message="Confirm payment?")'
        )
        assert action["action"] == "Tap"
        assert action["element"] == [500, 500]
        assert action["message"] == "Confirm payment?"


class TestParseTypeActions:
    """Tests for the special-cased ``Type`` / ``Type_Name`` parsing path."""

    def test_parse_type_simple(self):
        action = parse_action('do(action="Type", text="hello")')
        assert action["_metadata"] == "do"
        assert action["action"] == "Type"
        assert action["text"] == "hello"

    def test_parse_type_with_spaces(self):
        action = parse_action('do(action="Type", text="hello world")')
        assert action["text"] == "hello world"

    def test_parse_type_name_normalized_to_type(self):
        # Type_Name is handled by the same code path and normalized to "Type"
        action = parse_action('do(action="Type_Name", text="Alice")')
        assert action["action"] == "Type"
        assert action["text"] == "Alice"

    def test_parse_type_with_special_characters(self):
        action = parse_action('do(action="Type", text="user@example.com")')
        assert action["text"] == "user@example.com"


class TestParseFinishActions:
    """Tests for parsing ``finish(...)`` actions."""

    def test_parse_finish_simple(self):
        action = parse_action('finish(message="Task completed")')
        assert action["_metadata"] == "finish"
        assert action["message"] == "Task completed"

    def test_parse_finish_with_punctuation(self):
        action = parse_action('finish(message="Done, all good.")')
        assert action["_metadata"] == "finish"
        assert action["message"] == "Done, all good."


class TestParseErrors:
    """Tests for malformed input handling."""

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse_action("")

    def test_unknown_prefix_raises(self):
        with pytest.raises(ValueError):
            parse_action('run(action="Tap")')

    def test_garbage_input_raises(self):
        with pytest.raises(ValueError):
            parse_action("this is not an action")


class TestActionHelpers:
    """Tests for the ``do`` and ``finish`` helper constructors."""

    def test_do_helper_adds_metadata(self):
        action = do(action="Tap", element=[1, 2])
        assert action["_metadata"] == "do"
        assert action["action"] == "Tap"
        assert action["element"] == [1, 2]

    def test_finish_helper_adds_metadata(self):
        action = finish(message="bye")
        assert action["_metadata"] == "finish"
        assert action["message"] == "bye"
