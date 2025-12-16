"""iOS PhoneAgent class for orchestrating iOS phone automation."""

from dataclasses import dataclass
from typing import Callable

from phone_agent.actions.handler_ios import IOSActionHandler
from phone_agent.agent_base import BaseAgentConfig, BasePhoneAgent, StepResult
from phone_agent.model import ModelConfig
from phone_agent.xctest import XCTestConnection, get_current_app, get_screenshot


@dataclass
class IOSAgentConfig(BaseAgentConfig):
    """Configuration for the iOS PhoneAgent."""

    wda_url: str = "http://localhost:8100"
    session_id: str | None = None
    device_id: str | None = None  # iOS device UDID
    scale_factor: float | None = None


class IOSPhoneAgent(BasePhoneAgent):
    """
    AI-powered agent for automating iOS phone interactions.

    The agent uses a vision-language model to understand screen content
    and decide on actions to complete user tasks via WebDriverAgent.

    Args:
        model_config: Configuration for the AI model.
        agent_config: Configuration for the iOS agent behavior.
        confirmation_callback: Optional callback for sensitive action confirmation.
        takeover_callback: Optional callback for takeover requests.

    Example:
        >>> from phone_agent.agent_ios import IOSPhoneAgent, IOSAgentConfig
        >>> from phone_agent.model import ModelConfig
        >>>
        >>> model_config = ModelConfig(base_url="http://localhost:8000/v1")
        >>> agent_config = IOSAgentConfig(wda_url="http://localhost:8100")
        >>> agent = IOSPhoneAgent(model_config, agent_config)
        >>> agent.run("Open Safari and search for Apple")
    """

    def __init__(
        self,
        model_config: ModelConfig | None = None,
        agent_config: IOSAgentConfig | None = None,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
    ):
        resolved_model_config = model_config or ModelConfig()
        resolved_agent_config = agent_config or IOSAgentConfig()

        # Initialize WDA connection and create session if needed
        self.wda_connection = XCTestConnection(wda_url=resolved_agent_config.wda_url)

        # Auto-create session if not provided
        if resolved_agent_config.session_id is None:
            success, session_id = self.wda_connection.start_wda_session()
            if success and session_id != "session_started":
                resolved_agent_config.session_id = session_id
                if resolved_agent_config.verbose:
                    print(f"✅ Created WDA session: {session_id}")
            elif resolved_agent_config.verbose:
                print(f"⚠️  Using default WDA session (no explicit session ID)")

        action_handler = IOSActionHandler(
            wda_url=resolved_agent_config.wda_url,
            session_id=resolved_agent_config.session_id,
            scale_factor=resolved_agent_config.scale_factor,
            confirmation_callback=confirmation_callback,
            takeover_callback=takeover_callback,
        )

        super().__init__(
            model_config=resolved_model_config,
            agent_config=resolved_agent_config,
            action_handler=action_handler,
            get_screenshot=lambda: get_screenshot(
                wda_url=resolved_agent_config.wda_url,
                session_id=resolved_agent_config.session_id,
                device_id=resolved_agent_config.device_id,
            ),
            get_current_app=lambda: get_current_app(
                wda_url=resolved_agent_config.wda_url,
                session_id=resolved_agent_config.session_id,
            ),
        )
