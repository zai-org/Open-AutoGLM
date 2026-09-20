from unittest.mock import Mock

import pytest

from phone_agent.actions.handler import ActionHandler
from phone_agent.agent import AgentConfig, PhoneAgent
from phone_agent.model.client import ModelResponse


def action(name: str, **kwargs):
    return {"_metadata": "do", "action": name, **kwargs}


class TestNoteAndCallApi:
    def test_note_records_content_for_call_api(self):
        callback = Mock(return_value="Top recommendations: cafe A")
        handler = ActionHandler(call_api_callback=callback)

        assert handler.execute(
            action("Note", message="Cafe A has the best rating"), 1, 1
        ).success
        result = handler.execute(
            action("Call_API", instruction="Summarize the recommendations"), 1, 1
        )

        assert result.success is True
        assert result.message == "Top recommendations: cafe A"
        callback.assert_called_once_with(
            "Summarize the recommendations", ["Cafe A has the best rating"]
        )

    def test_note_and_call_api_validate_required_fields(self):
        handler = ActionHandler(call_api_callback=Mock(return_value="summary"))

        missing_note = handler.execute(action("Note", message=""), 1, 1)
        missing_instruction = handler.execute(
            action("Call_API", instruction=""), 1, 1
        )

        assert missing_note.success is False
        assert missing_instruction.success is False

    def test_reset_clears_recorded_notes(self):
        callback = Mock(return_value="summary")
        handler = ActionHandler(call_api_callback=callback)
        handler.execute(action("Note", message="old page"), 1, 1)
        handler.reset()

        handler.execute(action("Call_API", instruction="summarize"), 1, 1)

        callback.assert_called_once_with("summarize", [])


def test_call_api_uses_a_summary_request(monkeypatch: pytest.MonkeyPatch):
    agent = PhoneAgent(agent_config=AgentConfig(lang="en", verbose=False))
    response = ModelResponse(thinking="", action="", raw_content="summary")
    request = Mock(return_value=response)
    monkeypatch.setattr(agent.model_client, "request", request)

    assert (
        agent._call_api("Summarize these pages", ["Page one content"])
        == "summary"
    )

    messages = request.call_args.args[0]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Page one content" in messages[1]["content"][-1]["text"]


def test_call_api_result_is_injected_into_the_next_user_message(monkeypatch):
    class Screenshot:
        base64_data = None
        width = 100
        height = 200

    device = Mock()
    device.get_screenshot.return_value = Screenshot()
    device.get_current_app.return_value = "Home"
    monkeypatch.setattr("phone_agent.agent.get_device_factory", lambda: device)

    agent = PhoneAgent(agent_config=AgentConfig(system_prompt="system", verbose=False))
    agent._context = [
        {"role": "system", "content": "system"},
        {"role": "assistant", "content": "previous action"},
    ]
    agent._pending_call_api_result = "Summary from the recorded pages"
    request = Mock(
        return_value=ModelResponse(
            thinking="", action='finish(message="done")', raw_content="done"
        )
    )
    monkeypatch.setattr(agent.model_client, "request", request)

    result = agent._execute_step(is_first=False)

    assert result.finished is True
    user_message = next(
        message
        for message in reversed(request.call_args.args[0])
        if message["role"] == "user"
    )
    assert user_message["role"] == "user"
    assert "Summary from the recorded pages" in user_message["content"][-1]["text"]
