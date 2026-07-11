"""Regression tests for ModelClient._parse_response tag/marker ordering.

The system prompt asks the model to answer in the form::

    <think>{reasoning}</think>
    <answer>{action}</answer>

where ``{action}`` is a ``do(...)`` or ``finish(...)`` call. These tests pin
down that a fully tagged response is split into a clean ``(thinking, action)``
pair, with the surrounding XML tags removed from *both* parts.

Previously the ``do(action=`` / ``finish(message=`` markers were matched before
the ``<answer>`` tag was stripped, so the action string retained a trailing
``</answer>`` (e.g. ``do(action="Tap", element=[500, 300])</answer>``). That
string is not valid Python and later fails ``parse_action``, which makes the
agent abort the step. See ``phone_agent.model.client.ModelClient._parse_response``.

No network or device access is required: ``ModelClient`` is instantiated with
its default config and the OpenAI client constructor performs no I/O.
"""

import pytest

from phone_agent.model.client import ModelClient


@pytest.fixture
def client():
    """A ModelClient built from the default configuration."""
    return ModelClient()


class TestTaggedResponsesAreClean:
    """A tagged answer must not leak XML tags into the action string."""

    def test_tagged_do_action_has_no_trailing_answer_tag(self, client):
        content = (
            "<think>I should tap the search box</think>"
            '<answer>do(action="Tap", element=[500, 300])</answer>'
        )
        thinking, action = client._parse_response(content)

        assert thinking == "I should tap the search box"
        assert action == 'do(action="Tap", element=[500, 300])'
        # Regression: the closing tag must not remain in the action.
        assert "</answer>" not in action
        assert "<answer>" not in action

    def test_tagged_finish_action_has_no_trailing_answer_tag(self, client):
        content = (
            "<think>task is complete</think>"
            '<answer>finish(message="all done")</answer>'
        )
        thinking, action = client._parse_response(content)

        assert thinking == "task is complete"
        assert action == 'finish(message="all done")'
        assert "</answer>" not in action

    def test_tagged_response_with_newlines(self, client):
        content = (
            "<think>navigate back</think>\n<answer>do(action=\"Back\")</answer>"
        )
        thinking, action = client._parse_response(content)

        assert thinking == "navigate back"
        assert action == 'do(action="Back")'

    def test_answer_tag_without_think_tag(self, client):
        content = 'some reasoning<answer>do(action="Home")</answer>'
        thinking, action = client._parse_response(content)

        assert thinking == "some reasoning"
        assert action == 'do(action="Home")'


class TestTaglessResponsesUnchanged:
    """Existing tag-less behaviour (Rules 2-4) must be preserved."""

    def test_tagless_do(self, client):
        thinking, action = client._parse_response(
            'I will tap the button. do(action="Tap", element=[500, 500])'
        )
        assert thinking == "I will tap the button."
        assert action == 'do(action="Tap", element=[500, 500])'

    def test_tagless_finish(self, client):
        thinking, action = client._parse_response(
            'I have completed the task. finish(message="all done")'
        )
        assert thinking == "I have completed the task."
        assert action == 'finish(message="all done")'

    def test_tagless_finish_precedes_do(self, client):
        thinking, action = client._parse_response(
            'do(action="Tap", element=[1, 2]) then finish(message="ok")'
        )
        assert thinking == 'do(action="Tap", element=[1, 2]) then'
        assert action == 'finish(message="ok")'

    def test_plain_text_fallback(self, client):
        thinking, action = client._parse_response("just some plain text")
        assert thinking == ""
        assert action == "just some plain text"
