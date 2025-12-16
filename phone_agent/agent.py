"""Main PhoneAgent class for orchestrating phone automation."""

from dataclasses import dataclass
from typing import Callable

from phone_agent.actions import ActionHandler
from phone_agent.adb import get_current_app, get_screenshot
from phone_agent.agent_base import BaseAgentConfig, BasePhoneAgent, StepResult
from phone_agent.model import ModelConfig


@dataclass
class AgentConfig(BaseAgentConfig):
    """Configuration for the PhoneAgent."""

    device_id: str | None = None


class PhoneAgent(BasePhoneAgent):
    """
    AI-powered agent for automating Android phone interactions.

    The agent uses a vision-language model to understand screen content
    and decide on actions to complete user tasks.

    Args:
        model_config: Configuration for the AI model.
        agent_config: Configuration for the agent behavior.
        confirmation_callback: Optional callback for sensitive action confirmation.
        takeover_callback: Optional callback for takeover requests.

    Example:
        >>> from phone_agent import PhoneAgent
        >>> from phone_agent.model import ModelConfig
        >>>
        >>> model_config = ModelConfig(base_url="http://localhost:8000/v1")
        >>> agent = PhoneAgent(model_config)
        >>> agent.run("Open WeChat and send a message to John")
    """

    def __init__(
        self,
        model_config: ModelConfig | None = None,
        agent_config: AgentConfig | None = None,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
    ):
        resolved_model_config = model_config or ModelConfig()
        resolved_agent_config = agent_config or AgentConfig()

        action_handler = ActionHandler(
            device_id=resolved_agent_config.device_id,
            confirmation_callback=confirmation_callback,
            takeover_callback=takeover_callback,
        )

        super().__init__(
            model_config=resolved_model_config,
            agent_config=resolved_agent_config,
            action_handler=action_handler,
            get_screenshot=lambda: get_screenshot(resolved_agent_config.device_id),
            get_current_app=lambda: get_current_app(resolved_agent_config.device_id),
        )
