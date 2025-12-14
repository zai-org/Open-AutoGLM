"""Main PhoneAgent class for orchestrating phone automation."""

import json
import traceback
from dataclasses import dataclass
from typing import Any, Callable
from pathlib import Path
from datetime import datetime

from phone_agent.actions import ActionHandler
from phone_agent.actions.handler import do, finish, parse_action
from phone_agent.adb import get_current_app, get_screenshot
from phone_agent.config import get_messages, get_system_prompt
from phone_agent.model import ModelClient, ModelConfig
from phone_agent.model.client import MessageBuilder


@dataclass
class AgentConfig:
    """Configuration for the PhoneAgent."""

    max_steps: int = 100
    device_id: str | None = None
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


class PhoneAgent:
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
        self.model_config = model_config or ModelConfig()
        self.agent_config = agent_config or AgentConfig()

        self.model_client = ModelClient(self.model_config)
        self.action_handler = ActionHandler(
            device_id=self.agent_config.device_id,
            confirmation_callback=confirmation_callback,
            takeover_callback=takeover_callback,
        )

        self._context: list[dict[str, Any]] = []
        self._step_count = 0
        self._recorded_actions: list[dict[str, Any]] = []

    def run(
        self,
        task: str,
        recording_id: str = "",
    ) -> str:
        """
        Run the agent to complete a task.

        Args:
            task: Natural language description of the task.
            enable_recording: Whether to record actions to a file.
            recording_file: Path to save recorded actions. If None, auto-generates filename.
            playback_file: Path to a recording file to playback instead of using AI.

        Returns:
            Final message from the agent.
        """
        self._context = []
        self._step_count = 0
        self._recorded_actions = []
        
        if recording_id:
            recording_path = Path(f"recordings/{recording_id}.json")
            if recording_path.exists():
                return self._playback_from_file(recording_path)
            recording_path.parent.mkdir(parents=True, exist_ok=True)

        # First step with user prompt
        result = self._execute_step(task, is_first=True, enable_recording=bool(recording_id))

        if result.finished:
            if recording_id:
                self._save_recording(recording_path, task)
            return result.message or "Task completed"
        
        print(recording_id)

        # Continue until finished or max steps reached
        while self._step_count < self.agent_config.max_steps:
            result = self._execute_step(is_first=False, enable_recording=bool(recording_id))

            if result.finished:
                if recording_id:
                    self._save_recording(recording_path, task)
                return result.message or "Task completed"

        return "Max steps reached"

    def _playback_from_file(self, playback_path: Path) -> str:
        """
        Playback recorded actions from a file without using AI.

        Args:
            playback_path: Path to the recording file.

        Returns:
            Final message from the playback.
        """

        try:
            with open(playback_path, "r", encoding="utf-8") as f:
                recording_data = json.load(f)
        except Exception as e:
            return f"Failed to load recording file: {e}"

        actions = recording_data.get("actions", [])
        task = recording_data.get("task", "Unknown task")

        msgs = get_messages(self.agent_config.lang)
        print("\n" + "=" * 50)
        print(f"🎬 Playback Mode: {task}")
        print(f"📝 Total actions: {len(actions)}")
        print("=" * 50 + "\n")

        for idx, action_data in enumerate(actions, 1):
            action = action_data["action"]
            
            if self.agent_config.verbose:
                print("\n" + "=" * 50)
                print(f"Step {idx}/{len(actions)}")
                print(f"🎯 {msgs['action']}:")
                print(json.dumps(action, ensure_ascii=False, indent=2))
                print("=" * 50 + "\n")

            # Get current screen dimensions
            screenshot = get_screenshot(self.agent_config.device_id)

            # Execute action
            try:
                result = self.action_handler.execute(
                    action, screenshot.width, screenshot.height
                )
            except Exception as e:
                if self.agent_config.verbose:
                    traceback.print_exc()
                return f"Playback failed at step {idx}: {e}"

            # Check if finished
            if action.get("_metadata") == "finish" or result.should_finish:
                if self.agent_config.verbose:
                    print("\n" + "🎉 " + "=" * 48)
                    print(
                        f"✅ {msgs['task_completed']}: {result.message or action.get('message', msgs['done'])}"
                    )
                    print("=" * 50 + "\n")
                return result.message or action.get("message", "Task completed")

        return "Playback completed"

    def _save_recording(self, recording_path: Path, task: str) -> None:
        """
        Save recorded actions to a file.

        Args:
            recording_path: Path to save the recording.
            task: Original task description.
        """
        recording_data = {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "total_steps": len(self._recorded_actions),
            "actions": self._recorded_actions,
        }

        try:
            with open(recording_path, "w", encoding="utf-8") as f:
                json.dump(recording_data, f, ensure_ascii=False, indent=2)
            
            if self.agent_config.verbose:
                print(f"\n💾 Recording saved to: {recording_path}")
                print(f"📝 Total actions recorded: {len(self._recorded_actions)}\n")
        except Exception as e:
            print(f"\n❌ Failed to save recording: {e}\n")

    def step(self, task: str | None = None) -> StepResult:
        """
        Execute a single step of the agent.

        Useful for manual control or debugging.

        Args:
            task: Task description (only needed for first step).

        Returns:
            StepResult with step details.
        """
        is_first = len(self._context) == 0

        if is_first and not task:
            raise ValueError("Task is required for the first step")

        return self._execute_step(task, is_first)

    def reset(self) -> None:
        """Reset the agent state for a new task."""
        self._context = []
        self._step_count = 0
        self._recorded_actions = []

    def _execute_step(
        self,
        user_prompt: str | None = None,
        is_first: bool = False,
        enable_recording: bool = False,
    ) -> StepResult:
        """Execute a single step of the agent loop."""
        self._step_count += 1

        # Capture current screen state
        screenshot = get_screenshot(self.agent_config.device_id)
        current_app = get_current_app(self.agent_config.device_id)

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
            # Print thinking process
            print("-" * 50)
            print(f"🎯 {msgs['action']}:")
            print(json.dumps(action, ensure_ascii=False, indent=2))
            print("=" * 50 + "\n")

        # Record action if recording is enabled
        if enable_recording:
            self._recorded_actions.append({
                "step": self._step_count,
                "action": action,
                "thinking": response.thinking,
                "app": current_app,
            })

        # Remove image from context to save space
        self._context[-1] = MessageBuilder.remove_images_from_message(self._context[-1])

        # Execute action
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

    @property
    def recorded_actions(self) -> list[dict[str, Any]]:
        """Get the recorded actions."""
        return self._recorded_actions.copy()