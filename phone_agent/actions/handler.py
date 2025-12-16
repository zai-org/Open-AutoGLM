"""Action handler for processing AI model outputs."""

import ast
import time
from typing import Any, Callable

from phone_agent.adb import (
    back,
    clear_text,
    detect_and_set_adb_keyboard,
    double_tap,
    home,
    launch_app,
    long_press,
    restore_keyboard,
    swipe,
    tap,
    type_text,
)
from phone_agent.actions.base_handler import BaseActionHandler
from phone_agent.actions.types import ActionResult
from phone_agent.config.timing import TIMING_CONFIG


class ActionHandler(BaseActionHandler):
    """
    Handles execution of actions from AI model output.

    Args:
        device_id: Optional ADB device ID for multi-device setups.
        confirmation_callback: Optional callback for sensitive action confirmation.
            Should return True to proceed, False to cancel.
        takeover_callback: Optional callback for takeover requests (login, captcha).
    """

    def __init__(
        self,
        device_id: str | None = None,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
    ):
        super().__init__(
            confirmation_callback=confirmation_callback, takeover_callback=takeover_callback
        )
        self.device_id = device_id

    def _launch_app(self, app_name: str) -> bool:
        return launch_app(app_name, self.device_id)

    def _tap(self, x: int, y: int) -> None:
        tap(x, y, self.device_id)

    def _type_text(self, text: str) -> None:
        # Switch to ADB keyboard
        original_ime = detect_and_set_adb_keyboard(self.device_id)
        time.sleep(TIMING_CONFIG.action.keyboard_switch_delay)

        # Clear existing text and type new text
        clear_text(self.device_id)
        time.sleep(TIMING_CONFIG.action.text_clear_delay)

        type_text(text, self.device_id)
        time.sleep(TIMING_CONFIG.action.text_input_delay)

        # Restore original keyboard
        restore_keyboard(original_ime, self.device_id)
        time.sleep(TIMING_CONFIG.action.keyboard_restore_delay)

    def _swipe(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        swipe(start_x, start_y, end_x, end_y, device_id=self.device_id)

    def _back(self) -> None:
        back(self.device_id)

    def _home(self) -> None:
        home(self.device_id)

    def _double_tap(self, x: int, y: int) -> None:
        double_tap(x, y, self.device_id)

    def _long_press(self, x: int, y: int) -> None:
        long_press(x, y, device_id=self.device_id)


def parse_action(response: str) -> dict[str, Any]:
    """
    Parse action from model response.

    Args:
        response: Raw response string from the model.

    Returns:
        Parsed action dictionary.

    Raises:
        ValueError: If the response cannot be parsed.
    """
    try:
        response = response.strip()
        if response.startswith('do(action="Type"') or response.startswith(
            'do(action="Type_Name"'
        ):
            text = response.split("text=", 1)[1][1:-2]
            action = {"_metadata": "do", "action": "Type", "text": text}
            return action
        elif response.startswith("do"):
            # Use AST parsing instead of eval for safety
            try:
                tree = ast.parse(response, mode="eval")
                if not isinstance(tree.body, ast.Call):
                    raise ValueError("Expected a function call")

                call = tree.body
                # Extract keyword arguments safely
                action = {"_metadata": "do"}
                for keyword in call.keywords:
                    key = keyword.arg
                    value = ast.literal_eval(keyword.value)
                    action[key] = value

                return action
            except (SyntaxError, ValueError) as e:
                raise ValueError(f"Failed to parse do() action: {e}")

        elif response.startswith("finish"):
            action = {
                "_metadata": "finish",
                "message": response.replace("finish(message=", "")[1:-2],
            }
        else:
            raise ValueError(f"Failed to parse action: {response}")
        return action
    except Exception as e:
        raise ValueError(f"Failed to parse action: {e}")


def do(**kwargs) -> dict[str, Any]:
    """Helper function for creating 'do' actions."""
    kwargs["_metadata"] = "do"
    return kwargs


def finish(**kwargs) -> dict[str, Any]:
    """Helper function for creating 'finish' actions."""
    kwargs["_metadata"] = "finish"
    return kwargs
