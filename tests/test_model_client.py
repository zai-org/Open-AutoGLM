"""Unit tests for phone_agent.model.client.

These tests exercise the pure, deterministic logic in the model client:

* ``ModelClient._parse_response`` — splits raw model output into a
  ``(thinking, action)`` tuple according to a fixed set of rules.
* ``MessageBuilder`` — a collection of static helpers that assemble the
  OpenAI-format message dictionaries sent to the model.
* ``ModelConfig`` / ``ModelResponse`` — configuration and response dataclasses.

No network or device access is required. ``ModelClient`` is instantiated with
its default config; the OpenAI client constructor does not perform any I/O, so
these tests remain hermetic and fast.
"""

import json

import pytest

from phone_agent.model.client import (
    MessageBuilder,
    ModelClient,
    ModelConfig,
    ModelResponse,
)


@pytest.fixture
def client():
    """A ModelClient built from the default configuration."""
    return ModelClient()


class TestParseResponseFinish:
    """Rule 1: content containing ``finish(message=``."""

    def test_finish_splits_thinking_and_action(self, client):
        thinking, action = client._parse_response(
            'I have completed the task. finish(message="all done")'
        )
        assert thinking == "I have completed the task."
        assert action == 'finish(message="all done")'

    def test_finish_thinking_is_stripped(self, client):
        thinking, action = client._parse_response(
            '   leading and trailing   finish(message="x")'
        )
        assert thinking == "leading and trailing"
        assert action == 'finish(message="x")'

    def test_finish_with_empty_thinking(self, client):
        thinking, action = client._parse_response('finish(message="done")')
        assert thinking == ""
        assert action == 'finish(message="done")'


class TestParseResponseDo:
    """Rule 2: content containing ``do(action=`` (and no finish)."""

    def test_do_splits_thinking_and_action(self, client):
        thinking, action = client._parse_response(
            'I will tap the button. do(action="Tap", element=[500, 500])'
        )
        assert thinking == "I will tap the button."
        assert action == 'do(action="Tap", element=[500, 500])'

    def test_do_action_prefix_is_preserved(self, client):
        _, action = client._parse_response('reason do(action="Back")')
        assert action.startswith("do(action=")
        assert action == 'do(action="Back")'

    def test_finish_takes_precedence_over_do(self, client):
        # When both markers are present, ``finish(message=`` wins (Rule 1
        # is checked before Rule 2), so the ``do(...)`` call ends up in the
        # thinking segment.
        thinking, action = client._parse_response(
            'do(action="Tap", element=[1, 2]) then finish(message="ok")'
        )
        assert thinking == 'do(action="Tap", element=[1, 2]) then'
        assert action == 'finish(message="ok")'


class TestParseResponseLegacyXml:
    """Rule 3: legacy ``<think>``/``<answer>`` XML fallback.

    Reached only when neither ``finish(message=`` nor ``do(action=`` appears
    verbatim in the content, since those rules are checked first.
    """

    def test_xml_tags_are_stripped(self, client):
        thinking, action = client._parse_response(
            "<think>navigate home</think><answer>press_home()</answer>"
        )
        assert thinking == "navigate home"
        assert action == "press_home()"

    def test_xml_without_think_tags(self, client):
        thinking, action = client._parse_response(
            "some reasoning<answer>press_home()</answer>"
        )
        assert thinking == "some reasoning"
        assert action == "press_home()"


class TestParseResponseFallback:
    """Rule 4: no recognizable markers."""

    def test_plain_text_returns_empty_thinking(self, client):
        thinking, action = client._parse_response("just some plain text")
        assert thinking == ""
        assert action == "just some plain text"

    def test_empty_string(self, client):
        thinking, action = client._parse_response("")
        assert thinking == ""
        assert action == ""


class TestMessageBuilderSystem:
    """Tests for ``MessageBuilder.create_system_message``."""

    def test_system_message_shape(self):
        msg = MessageBuilder.create_system_message("you are an agent")
        assert msg == {"role": "system", "content": "you are an agent"}


class TestMessageBuilderUser:
    """Tests for ``MessageBuilder.create_user_message``."""

    def test_text_only_message(self):
        msg = MessageBuilder.create_user_message("hello")
        assert msg["role"] == "user"
        assert msg["content"] == [{"type": "text", "text": "hello"}]

    def test_message_with_image_puts_image_first(self):
        msg = MessageBuilder.create_user_message("look here", image_base64="QUJD")
        assert msg["role"] == "user"
        assert len(msg["content"]) == 2
        # Image is prepended before the text item.
        assert msg["content"][0]["type"] == "image_url"
        assert (
            msg["content"][0]["image_url"]["url"]
            == "data:image/png;base64,QUJD"
        )
        assert msg["content"][1] == {"type": "text", "text": "look here"}


class TestMessageBuilderAssistant:
    """Tests for ``MessageBuilder.create_assistant_message``."""

    def test_assistant_message_shape(self):
        msg = MessageBuilder.create_assistant_message("done")
        assert msg == {"role": "assistant", "content": "done"}


class TestMessageBuilderRemoveImages:
    """Tests for ``MessageBuilder.remove_images_from_message``."""

    def test_removes_image_items_keeps_text(self):
        msg = MessageBuilder.create_user_message("caption", image_base64="QUJD")
        cleaned = MessageBuilder.remove_images_from_message(msg)
        assert cleaned["content"] == [{"type": "text", "text": "caption"}]

    def test_string_content_is_unchanged(self):
        msg = {"role": "assistant", "content": "plain string"}
        cleaned = MessageBuilder.remove_images_from_message(msg)
        assert cleaned["content"] == "plain string"

    def test_text_only_list_is_unchanged(self):
        msg = MessageBuilder.create_user_message("just text")
        cleaned = MessageBuilder.remove_images_from_message(msg)
        assert cleaned["content"] == [{"type": "text", "text": "just text"}]


class TestMessageBuilderScreenInfo:
    """Tests for ``MessageBuilder.build_screen_info``."""

    def test_returns_valid_json_with_current_app(self):
        result = MessageBuilder.build_screen_info("Settings")
        parsed = json.loads(result)
        assert parsed == {"current_app": "Settings"}

    def test_extra_info_is_merged(self):
        result = MessageBuilder.build_screen_info("Settings", step=3, note="hi")
        parsed = json.loads(result)
        assert parsed["current_app"] == "Settings"
        assert parsed["step"] == 3
        assert parsed["note"] == "hi"

    def test_non_ascii_is_preserved(self):
        # ensure_ascii=False keeps Chinese app names human-readable.
        result = MessageBuilder.build_screen_info("微信")
        assert "微信" in result
        assert json.loads(result)["current_app"] == "微信"


class TestModelConfigDefaults:
    """Tests for the ``ModelConfig`` dataclass defaults."""

    def test_default_values(self):
        config = ModelConfig()
        assert config.base_url == "http://localhost:8000/v1"
        assert config.api_key == "EMPTY"
        assert config.model_name == "autoglm-phone-9b"
        assert config.max_tokens == 3000
        assert config.temperature == 0.0
        assert config.lang == "cn"
        assert config.extra_body == {}

    def test_extra_body_is_independent_per_instance(self):
        a = ModelConfig()
        b = ModelConfig()
        a.extra_body["k"] = "v"
        assert b.extra_body == {}

    def test_overrides_are_applied(self):
        config = ModelConfig(base_url="http://example/v1", lang="en", max_tokens=100)
        assert config.base_url == "http://example/v1"
        assert config.lang == "en"
        assert config.max_tokens == 100


class TestModelResponseDefaults:
    """Tests for the ``ModelResponse`` dataclass."""

    def test_metrics_default_to_none(self):
        resp = ModelResponse(thinking="t", action="a", raw_content="raw")
        assert resp.thinking == "t"
        assert resp.action == "a"
        assert resp.raw_content == "raw"
        assert resp.time_to_first_token is None
        assert resp.time_to_thinking_end is None
        assert resp.total_time is None
