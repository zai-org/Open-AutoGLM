from dataclasses import dataclass

import phone_agent.agent as agent_module
import phone_agent.agent_ios as agent_ios_module
from phone_agent.agent import AgentConfig, PhoneAgent
from phone_agent.agent_ios import IOSAgentConfig, IOSPhoneAgent
from phone_agent.model.client import ModelResponse


@dataclass
class FakeScreenshot:
    base64_data: str = ""
    width: int = 1080
    height: int = 2400


class FakeDeviceFactory:
    def get_screenshot(self, device_id=None):
        return FakeScreenshot()

    def get_current_app(self, device_id=None):
        return "test.app"


class FakeModelClient:
    def request(self, messages):
        return ModelResponse(
            thinking="bad action",
            action="[{'Type': 'Type'}]",
            raw_content="[{'Type': 'Type'}]",
        )


def test_parse_error_returns_failure_without_executing_action(monkeypatch) -> None:
    monkeypatch.setattr(agent_module, "get_device_factory", lambda: FakeDeviceFactory())

    agent = PhoneAgent(agent_config=AgentConfig(verbose=False))
    agent.model_client = FakeModelClient()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("malformed action should not be executed")

    monkeypatch.setattr(agent.action_handler, "execute", fail_if_called)

    result = agent.step("do something")

    assert result.success is False
    assert result.finished is True
    assert result.action is None
    assert "Failed to parse action" in result.message


class FakeWDAConnection:
    def __init__(self, wda_url):
        self.wda_url = wda_url

    def start_wda_session(self):
        return False, None


def test_ios_parse_error_returns_failure_without_executing_action(
    monkeypatch,
) -> None:
    monkeypatch.setattr(agent_ios_module, "XCTestConnection", FakeWDAConnection)
    monkeypatch.setattr(
        agent_ios_module, "get_screenshot", lambda **kwargs: FakeScreenshot()
    )
    monkeypatch.setattr(
        agent_ios_module, "get_current_app", lambda **kwargs: "test.app"
    )

    agent = IOSPhoneAgent(agent_config=IOSAgentConfig(verbose=False))
    agent.model_client = FakeModelClient()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("malformed action should not be executed")

    monkeypatch.setattr(agent.action_handler, "execute", fail_if_called)

    result = agent.step("do something")

    assert result.success is False
    assert result.finished is True
    assert result.action is None
    assert "Failed to parse action" in result.message
