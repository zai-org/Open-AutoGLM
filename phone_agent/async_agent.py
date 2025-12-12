"""Async PhoneAgent for orchestrating phone automation."""

import asyncio
import json
import traceback
from dataclasses import dataclass
from typing import Any, Callable

from phone_agent.actions import ActionHandler
from phone_agent.actions.handler import do, finish, parse_action
from phone_agent.adb.async_device import get_current_app_async
from phone_agent.adb.async_screenshot import get_screenshot_async
from phone_agent.config import get_messages, get_system_prompt
from phone_agent.model import ModelConfig
from phone_agent.model.async_client import AsyncModelClient
from phone_agent.model.client import MessageBuilder
from phone_agent.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AsyncAgentConfig:
    """Configuration for the AsyncPhoneAgent."""

    max_steps: int = 100
    device_id: str | None = None
    lang: str = "cn"
    system_prompt: str | None = None
    verbose: bool = True

    def __post_init__(self):
        if self.system_prompt is None:
            self.system_prompt = get_system_prompt(self.lang)


@dataclass
class AsyncStepResult:
    """Result of a single async agent step."""

    success: bool
    finished: bool
    action: dict[str, Any] | None
    thinking: str
    message: str | None = None


class AsyncPhoneAgent:
    """
    Async AI-powered agent for automating Android phone interactions.

    This is the async version of PhoneAgent, providing better performance
    for I/O-bound operations like screenshots and network requests.

    Args:
        model_config: Configuration for the AI model.
        agent_config: Configuration for the agent behavior.
        confirmation_callback: Optional async callback for sensitive action confirmation.
        takeover_callback: Optional async callback for takeover requests.

    Example:
        >>> import asyncio
        >>> from phone_agent.async_agent import AsyncPhoneAgent
        >>> from phone_agent.model import ModelConfig
        >>>
        >>> async def main():
        >>>     model_config = ModelConfig(base_url="http://localhost:8000/v1")
        >>>     agent = AsyncPhoneAgent(model_config)
        >>>     result = await agent.run("Open WeChat and send a message")
        >>>     print(result)
        >>>
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        model_config: ModelConfig | None = None,
        agent_config: AsyncAgentConfig | None = None,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
    ):
        self.model_config = model_config or ModelConfig()
        self.agent_config = agent_config or AsyncAgentConfig()

        self.model_client = AsyncModelClient(self.model_config)
        self.action_handler = ActionHandler(
            device_id=self.agent_config.device_id,
            confirmation_callback=confirmation_callback,
            takeover_callback=takeover_callback,
        )

        self._context: list[dict[str, Any]] = []
        self._step_count = 0

    async def run(self, task: str) -> str:
        """
        Run the agent to complete a task (async).

        Args:
            task: Natural language description of the task.

        Returns:
            Final message from the agent.
        """
        self._context = []
        self._step_count = 0

        # First step with user prompt
        result = await self._execute_step(task, is_first=True)

        if result.finished:
            return result.message or "Task completed"

        # Continue until finished or max steps reached
        while self._step_count < self.agent_config.max_steps:
            result = await self._execute_step(is_first=False)

            if result.finished:
                return result.message or "Task completed"

        return "Max steps reached"

    async def step(self, task: str | None = None) -> AsyncStepResult:
        """
        Execute a single step of the agent (async).

        Useful for manual control or debugging.

        Args:
            task: Task description (only needed for first step).

        Returns:
            AsyncStepResult with step details.
        """
        is_first = len(self._context) == 0

        if is_first and not task:
            raise ValueError("Task is required for the first step")

        return await self._execute_step(task, is_first)

    def reset(self) -> None:
        """Reset the agent state for a new task."""
        self._context = []
        self._step_count = 0

    async def _execute_step(
        self, user_prompt: str | None = None, is_first: bool = False
    ) -> AsyncStepResult:
        """Execute a single step of the agent loop (async)."""
        self._step_count += 1

        # Capture current screen state (async)
        screenshot = await get_screenshot_async(self.agent_config.device_id)
        current_app = await get_current_app_async(self.agent_config.device_id)

        # Build messages
        if is_first:
            self._context.append(
                MessageBuilder.create_system_message(self.agent_config.system_prompt)
            )

            screen_info = MessageBuilder.build_screen_info(current_app)
            text_content = f"{user_prompt}\n\n{screen_info}"

            self._context.append(
                MessageBuilder.create_user_message(
                    text=text_content, image_base64=screenshot.base64_data
                )
            )
        else:
            screen_info = MessageBuilder.build_screen_info(current_app)
            text_content = f"** Screen Info **\n\n{screen_info}"

            self._context.append(
                MessageBuilder.create_user_message(
                    text=text_content, image_base64=screenshot.base64_data
                )
            )

        # Get model response (async)
        try:
            response = await self.model_client.request(self._context)
        except Exception as e:
            if self.agent_config.verbose:
                traceback.print_exc()
            return AsyncStepResult(
                success=False,
                finished=True,
                action=None,
                thinking="",
                message=f"Model error: {e}",
            )

        # Parse action from response
        try:
            action = parse_action(response.action)
        except ValueError:
            if self.agent_config.verbose:
                traceback.print_exc()
            action = finish(message=response.action)

        if self.agent_config.verbose:
            # Print thinking process
            msgs = get_messages(self.agent_config.lang)
            print("\n" + "=" * 50)
            print(f"💭 {msgs['thinking']}:")
            print("-" * 50)
            print(response.thinking)
            print("-" * 50)
            print(f"🎯 {msgs['action']}:")
            print(json.dumps(action, ensure_ascii=False, indent=2))
            print("=" * 50 + "\n")

        # Remove image from context to save space
        self._context[-1] = MessageBuilder.remove_images_from_message(self._context[-1])

        # Execute action (sync, but can be made async if needed)
        try:
            result = self.action_handler.execute(
                action, screenshot.width, screenshot.height
            )
        except Exception as e:
            if self.agent_config.verbose:
                traceback.print_exc()
            result = self.action_handler.execute(
                finish(message=str(e)), screenshot.width, screenshot.height
            )

        # Add assistant response to context
        self._context.append(
            MessageBuilder.create_assistant_message(
                f"<think>{response.thinking}</think><answer>{response.action}</answer>"
            )
        )

        # Check if finished
        finished = action.get("_metadata") == "finish" or result.should_finish

        if finished and self.agent_config.verbose:
            msgs = get_messages(self.agent_config.lang)
            print("\n" + "🎉 " + "=" * 48)
            print(
                f"✅ {msgs['task_completed']}: {result.message or action.get('message', msgs['done'])}"
            )
            print("=" * 50 + "\n")

        return AsyncStepResult(
            success=result.success,
            finished=finished,
            action=action,
            thinking=response.thinking,
            message=result.message or action.get("message"),
        )

    @property
    def context(self) -> list[dict[str, Any]]:
        """Get the current conversation context."""
        return self._context.copy()

    @property
    def step_count(self) -> int:
        """Get the current step count."""
        return self._step_count

