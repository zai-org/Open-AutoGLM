"""Tests for action parsing functionality."""

import pytest

from phone_agent.actions.handler import parse_action


class TestParseAction:
    """Test cases for parse_action function."""

    def test_parse_do_action_with_tap(self):
        """Test parsing do(action="Tap", element=[100, 200])."""
        response = 'do(action="Tap", element=[100, 200])'
        result = parse_action(response)
        
        assert result["_metadata"] == "do"
        assert result["action"] == "Tap"
        assert result["element"] == [100, 200]

    def test_parse_do_action_with_launch(self):
        """Test parsing do(action="Launch", app="微信")."""
        response = 'do(action="Launch", app="微信")'
        result = parse_action(response)
        
        assert result["_metadata"] == "do"
        assert result["action"] == "Launch"
        assert result["app"] == "微信"

    def test_parse_do_action_with_type(self):
        """Test parsing do(action="Type", text="Hello")."""
        response = 'do(action="Type", text="Hello")'
        result = parse_action(response)
        
        assert result["_metadata"] == "do"
        assert result["action"] == "Type"
        assert result["text"] == "Hello"

    def test_parse_do_action_with_swipe(self):
        """Test parsing do(action="Swipe", start=[100, 200], end=[300, 400])."""
        response = 'do(action="Swipe", start=[100, 200], end=[300, 400])'
        result = parse_action(response)
        
        assert result["_metadata"] == "do"
        assert result["action"] == "Swipe"
        assert result["start"] == [100, 200]
        assert result["end"] == [300, 400]

    def test_parse_finish_action(self):
        """Test parsing finish(message="Task completed")."""
        response = 'finish(message="Task completed")'
        result = parse_action(response)
        
        assert result["_metadata"] == "finish"
        assert result["message"] == "Task completed"

    def test_parse_finish_action_single_quotes(self):
        """Test parsing finish with single quotes."""
        response = "finish(message='Task completed')"
        result = parse_action(response)
        
        assert result["_metadata"] == "finish"
        assert result["message"] == "Task completed"

    def test_parse_invalid_action(self):
        """Test parsing invalid action raises ValueError."""
        with pytest.raises(ValueError):
            parse_action("invalid action")

    def test_parse_empty_string(self):
        """Test parsing empty string raises ValueError."""
        with pytest.raises(ValueError):
            parse_action("")

    def test_parse_action_with_message(self):
        """Test parsing action with confirmation message."""
        response = 'do(action="Tap", element=[100, 200], message="Sensitive operation")'
        result = parse_action(response)
        
        assert result["_metadata"] == "do"
        assert result["action"] == "Tap"
        assert result["element"] == [100, 200]
        assert result["message"] == "Sensitive operation"

    def test_parse_action_with_duration(self):
        """Test parsing Wait action with duration."""
        response = 'do(action="Wait", duration="2 seconds")'
        result = parse_action(response)
        
        assert result["_metadata"] == "do"
        assert result["action"] == "Wait"
        assert result["duration"] == "2 seconds"

