"""Shared agent loop for different device backends."""

from __future__ import annotations

import json
import traceback
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from phone_agent.actions.handler import finish, parse_action
from phone_agent.actions.types import ActionResult
from phone_agent.config import get_messages, get_system_prompt
from phone_agent.model import ModelClient, ModelConfig
from phone_agent.model.client import MessageBuilder


@dataclass
class BaseAgentConfig:
    """Configuration shared across all device backends."""

    max_steps: int = 100
    lang: str = "cn"
    system_prompt: str | None = None
    verbose: bool = True

    def __post_init__(self):
        if self.system_prompt is None:
            self.system_prompt = get_system_prompt(self.lang)


@dataclass
class StepResult:
    """Result of a single agent step."""

    success: bool
    finished: bool
    action: dict[str, Any] | None
    thinking: str
    message: str | None = None


class ScreenshotLike(Protocol):
    """Minimum interface needed from screenshot providers."""

    base64_data: str
    width: int
    height: int


class ActionHandlerLike(Protocol):
    """Minimum interface needed from action handlers."""

    def execute(
        self, action: dict[str, Any], screen_width: int, screen_height: int
    ) -> ActionResult: ...


class BasePhoneAgent:
    """Platform-agnostic agent loop."""

    def __init__(
        self,
        *,
        model_config: ModelConfig | None = None,
        agent_config: BaseAgentConfig | None = None,
        action_handler: ActionHandlerLike,
        get_screenshot: Callable[[], ScreenshotLike],
        get_current_app: Callable[[], str],
    ):
        self.model_config = model_config or ModelConfig()
        self.agent_config = agent_config or BaseAgentConfig()

        self.model_client = ModelClient(self.model_config)
        self.action_handler = action_handler

        self._get_screenshot = get_screenshot
        self._get_current_app = get_current_app

        self._context: list[dict[str, Any]] = []
        self._step_count = 0

    def run(self, task: str) -> str:
        """Run the agent to complete a task."""
        self._context = []
        self._step_count = 0

        result = self._execute_step(task, is_first=True)
        if result.finished:
            return result.message or "Task completed"

        while self._step_count < self.agent_config.max_steps:
            result = self._execute_step(is_first=False)
            if result.finished:
                return result.message or "Task completed"

        return "Max steps reached"

    def step(self, task: str | None = None) -> StepResult:
        """Execute a single step (useful for debugging)."""
        is_first = len(self._context) == 0
        if is_first and not task:
            raise ValueError("Task is required for the first step")
        return self._execute_step(task, is_first)

    def reset(self) -> None:
        """Reset the agent state for a new task."""
        self._context = []
        self._step_count = 0

    def _execute_step(
        self, user_prompt: str | None = None, is_first: bool = False
    ) -> StepResult:
        """Execute a single step of the agent loop."""
        self._step_count += 1

        screenshot = self._get_screenshot()
        current_app = self._get_current_app()

        if is_first:
            self._context.append(
                MessageBuilder.create_system_message(self.agent_config.system_prompt or "")
            )

            screen_info = MessageBuilder.build_screen_info(current_app)
            text_content = f"{user_prompt}\n\n{screen_info}"
        else:
            screen_info = MessageBuilder.build_screen_info(current_app)
            text_content = f"** Screen Info **\n\n{screen_info}"

        self._context.append(
            MessageBuilder.create_user_message(
                text=text_content, image_base64=screenshot.base64_data
            )
        )

        # Get model response
        try:
            msgs = get_messages(self.agent_config.lang)
            print("\n" + "=" * 50)
            print(f"💭 {msgs['thinking']}:")
            print("-" * 50)
            response = self.model_client.request(self._context)
        except Exception as e:
            if self.agent_config.verbose:
                traceback.print_exc()
            return StepResult(
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
            print("-" * 50)
            print(f"🎯 {msgs['action']}:")
            print(json.dumps(action, ensure_ascii=False, indent=2))
            print("=" * 50 + "\n")

        # Remove image from context to save space
        self._context[-1] = MessageBuilder.remove_images_from_message(self._context[-1])

        # Execute action
        try:
            result = self.action_handler.execute(action, screenshot.width, screenshot.height)
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

        finished = action.get("_metadata") == "finish" or result.should_finish
        if finished and self.agent_config.verbose:
            msgs = get_messages(self.agent_config.lang)
            print("\n" + "🎉 " + "=" * 48)
            print(
                f"✅ {msgs['task_completed']}: {result.message or action.get('message', msgs['done'])}"
            )
            print("=" * 50 + "\n")

        return StepResult(
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

