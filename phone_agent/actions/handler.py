"""Action handler for processing AI model outputs."""

import ast
import re
import time
from dataclasses import dataclass
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
from phone_agent.config.apps import APP_PACKAGES
from phone_agent.utils.logger import get_logger
from phone_agent.utils.validation import (
    validate_app_name,
    validate_relative_coordinates,
)

logger = get_logger(__name__)


@dataclass
class ActionResult:
    """Result of an action execution."""

    success: bool
    should_finish: bool
    message: str | None = None
    requires_confirmation: bool = False


class ActionHandler:
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
        self.device_id = device_id
        self.confirmation_callback = confirmation_callback or self._default_confirmation
        self.takeover_callback = takeover_callback or self._default_takeover

    def execute(
        self, action: dict[str, Any], screen_width: int, screen_height: int
    ) -> ActionResult:
        """
        Execute an action from the AI model.

        Args:
            action: The action dictionary from the model.
            screen_width: Current screen width in pixels.
            screen_height: Current screen height in pixels.

        Returns:
            ActionResult indicating success and whether to finish.
        """
        action_type = action.get("_metadata")

        if action_type == "finish":
            return ActionResult(
                success=True, should_finish=True, message=action.get("message")
            )

        if action_type != "do":
            return ActionResult(
                success=False,
                should_finish=True,
                message=f"Unknown action type: {action_type}",
            )

        action_name = action.get("action")
        handler_method = self._get_handler(action_name)

        if handler_method is None:
            return ActionResult(
                success=False,
                should_finish=False,
                message=f"Unknown action: {action_name}",
            )

        try:
            return handler_method(action, screen_width, screen_height)
        except Exception as e:
            return ActionResult(
                success=False, should_finish=False, message=f"Action failed: {e}"
            )

    def _get_handler(self, action_name: str) -> Callable | None:
        """Get the handler method for an action."""
        handlers = {
            "Launch": self._handle_launch,
            "Tap": self._handle_tap,
            "Type": self._handle_type,
            "Type_Name": self._handle_type,
            "Swipe": self._handle_swipe,
            "Back": self._handle_back,
            "Home": self._handle_home,
            "Double Tap": self._handle_double_tap,
            "Long Press": self._handle_long_press,
            "Wait": self._handle_wait,
            "Take_over": self._handle_takeover,
            "Note": self._handle_note,
            "Call_API": self._handle_call_api,
            "Interact": self._handle_interact,
        }
        return handlers.get(action_name)

    def _convert_relative_to_absolute(
        self, element: list[int], screen_width: int, screen_height: int
    ) -> tuple[int, int]:
        """Convert relative coordinates (0-1000) to absolute pixels."""
        return validate_relative_coordinates(element, screen_width, screen_height)

    def _handle_launch(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle app launch action."""
        app_name = action.get("app")
        if not app_name:
            logger.error("Launch action: No app name specified")
            return ActionResult(False, False, "No app name specified")

        try:
            validated_app = validate_app_name(app_name, set(APP_PACKAGES.keys()))
            success = launch_app(validated_app, self.device_id)
            if success:
                logger.info(f"Successfully launched app: {validated_app}")
                return ActionResult(True, False)
            logger.warning(f"Failed to launch app: {validated_app}")
            return ActionResult(False, False, f"App not found: {validated_app}")
        except ValueError as e:
            logger.error(f"Invalid app name: {e}")
            return ActionResult(False, False, str(e))

    def _handle_tap(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle tap action."""
        element = action.get("element")
        if not element:
            logger.error("Tap action: No element coordinates provided")
            return ActionResult(False, False, "No element coordinates")

        try:
            x, y = self._convert_relative_to_absolute(element, width, height)
            logger.debug(f"Tapping at coordinates: ({x}, {y})")

            # Check for sensitive operation
            if "message" in action:
                if not self.confirmation_callback(action["message"]):
                    logger.info("User cancelled sensitive operation")
                    return ActionResult(
                        success=False,
                        should_finish=True,
                        message="User cancelled sensitive operation",
                    )

            tap(x, y, self.device_id)
            return ActionResult(True, False)
        except ValueError as e:
            logger.error(f"Invalid coordinates: {e}")
            return ActionResult(False, False, str(e))

    def _handle_type(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle text input action."""
        text = action.get("text", "")

        # Switch to ADB keyboard
        original_ime = detect_and_set_adb_keyboard(self.device_id)
        time.sleep(1.0)

        # Clear existing text and type new text
        clear_text(self.device_id)
        time.sleep(1.0)

        type_text(text, self.device_id)
        time.sleep(1.0)

        # Restore original keyboard
        restore_keyboard(original_ime, self.device_id)
        time.sleep(1.0)

        return ActionResult(True, False)

    def _handle_swipe(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle swipe action."""
        start = action.get("start")
        end = action.get("end")

        if not start or not end:
            return ActionResult(False, False, "Missing swipe coordinates")

        start_x, start_y = self._convert_relative_to_absolute(start, width, height)
        end_x, end_y = self._convert_relative_to_absolute(end, width, height)

        swipe(start_x, start_y, end_x, end_y, device_id=self.device_id)
        return ActionResult(True, False)

    def _handle_back(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle back button action."""
        back(self.device_id)
        return ActionResult(True, False)

    def _handle_home(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle home button action."""
        home(self.device_id)
        return ActionResult(True, False)

    def _handle_double_tap(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle double tap action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        double_tap(x, y, self.device_id)
        return ActionResult(True, False)

    def _handle_long_press(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle long press action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        long_press(x, y, device_id=self.device_id)
        return ActionResult(True, False)

    def _handle_wait(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle wait action."""
        duration_str = action.get("duration", "1 seconds")
        try:
            duration = float(duration_str.replace("seconds", "").strip())
        except ValueError:
            duration = 1.0

        time.sleep(duration)
        return ActionResult(True, False)

    def _handle_takeover(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle takeover request (login, captcha, etc.)."""
        message = action.get("message", "User intervention required")
        self.takeover_callback(message)
        return ActionResult(True, False)

    def _handle_note(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle note action (placeholder for content recording)."""
        # This action is typically used for recording page content
        # Implementation depends on specific requirements
        return ActionResult(True, False)

    def _handle_call_api(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle API call action (placeholder for summarization)."""
        # This action is typically used for content summarization
        # Implementation depends on specific requirements
        return ActionResult(True, False)

    def _handle_interact(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle interaction request (user choice needed)."""
        # This action signals that user input is needed
        return ActionResult(True, False, message="User interaction required")

    @staticmethod
    def _default_confirmation(message: str) -> bool:
        """Default confirmation callback using console input."""
        response = input(f"Sensitive operation: {message}\nConfirm? (Y/N): ")
        return response.upper() == "Y"

    @staticmethod
    def _default_takeover(message: str) -> None:
        """Default takeover callback using console input."""
        input(f"{message}\nPress Enter after completing manual operation...")


def parse_action(response: str) -> dict[str, Any]:
    """
    Parse action from model response safely without using eval().

    This function safely parses action strings like:
    - do(action="Tap", element=[100, 200])
    - finish(message="Task completed")

    Args:
        response: Raw response string from the model.

    Returns:
        Parsed action dictionary.

    Raises:
        ValueError: If the response cannot be parsed.
    """
    try:
        response = response.strip()
        
        # Handle finish() calls
        if response.startswith("finish"):
            return _parse_finish_action(response)
        
        # Handle do() calls
        if response.startswith("do"):
            return _parse_do_action(response)
        
        # Try to parse as JSON-like structure
        try:
            # Attempt to parse as JSON first
            import json
            action = json.loads(response)
            if isinstance(action, dict):
                return action
        except (json.JSONDecodeError, ValueError):
            pass
        
        raise ValueError(f"Failed to parse action: {response}")
    except Exception as e:
        raise ValueError(f"Failed to parse action: {e}")


def _parse_finish_action(response: str) -> dict[str, Any]:
    """Safely parse finish() action."""
    # Pattern: finish(message="...")
    match = re.match(r'finish\(message=["\']([^"\']*)["\']\)', response)
    if match:
        return {
            "_metadata": "finish",
            "message": match.group(1),
        }
    
    # Pattern: finish(message='...')
    match = re.match(r"finish\(message=['\"]([^'\"]*)['\"]\)", response)
    if match:
        return {
            "_metadata": "finish",
            "message": match.group(1),
        }
    
    # Fallback: try to extract message manually
    if "message=" in response:
        # Extract content between quotes
        match = re.search(r'message=["\']([^"\']*)["\']', response)
        if match:
            return {
                "_metadata": "finish",
                "message": match.group(1),
            }
    
    # Default finish action
    return {
        "_metadata": "finish",
        "message": response.replace("finish(", "").replace(")", "").strip(),
    }


def _parse_do_action(response: str) -> dict[str, Any]:
    """Safely parse do() action using AST."""
    try:
        # Use AST to safely parse the function call
        # This is safer than eval() as it only parses, doesn't execute
        tree = ast.parse(response, mode="eval")
        
        if isinstance(tree.body, ast.Call):
            call = tree.body
            if isinstance(call.func, ast.Name) and call.func.id == "do":
                action = {"_metadata": "do"}
                
                # Parse keyword arguments
                for keyword in call.keywords:
                    key = keyword.arg
                    if key is None:
                        continue
                    
                    value = _ast_to_python_value(keyword.value)
                    action[key] = value
                
                return action
    except (SyntaxError, ValueError, AttributeError):
        pass
    
    # Fallback: use regex to parse common patterns
    action = {"_metadata": "do"}
    
    # Extract action name
    action_match = re.search(r'action=["\']([^"\']*)["\']', response)
    if action_match:
        action["action"] = action_match.group(1)
    
    # Extract element coordinates [x, y]
    element_match = re.search(r'element=\[(\d+),\s*(\d+)\]', response)
    if element_match:
        action["element"] = [int(element_match.group(1)), int(element_match.group(2))]
    
    # Extract app name
    app_match = re.search(r'app=["\']([^"\']*)["\']', response)
    if app_match:
        action["app"] = app_match.group(1)
    
    # Extract text
    text_match = re.search(r'text=["\']([^"\']*)["\']', response)
    if text_match:
        action["text"] = text_match.group(1)
    
    # Extract start and end coordinates for swipe
    start_match = re.search(r'start=\[(\d+),\s*(\d+)\]', response)
    if start_match:
        action["start"] = [int(start_match.group(1)), int(start_match.group(2))]
    
    end_match = re.search(r'end=\[(\d+),\s*(\d+)\]', response)
    if end_match:
        action["end"] = [int(end_match.group(1)), int(end_match.group(2))]
    
    # Extract message
    message_match = re.search(r'message=["\']([^"\']*)["\']', response)
    if message_match:
        action["message"] = message_match.group(1)
    
    # Extract duration
    duration_match = re.search(r'duration=["\']([^"\']*)["\']', response)
    if duration_match:
        action["duration"] = duration_match.group(1)
    
    return action


def _ast_to_python_value(node: ast.AST) -> Any:
    """Convert AST node to Python value safely."""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):  # Python < 3.8 compatibility
        return node.s
    elif isinstance(node, ast.Num):  # Python < 3.8 compatibility
        return node.n
    elif isinstance(node, ast.List):
        return [_ast_to_python_value(item) for item in node.elts]
    elif isinstance(node, ast.Tuple):
        return tuple(_ast_to_python_value(item) for item in node.elts)
    elif isinstance(node, ast.Dict):
        return {
            _ast_to_python_value(k): _ast_to_python_value(v)
            for k, v in zip(node.keys, node.values)
        }
    elif isinstance(node, ast.NameConstant):  # Python < 3.8 compatibility
        return node.value
    elif isinstance(node, ast.Name):
        # Handle built-in constants
        if node.id == "True":
            return True
        elif node.id == "False":
            return False
        elif node.id == "None":
            return None
    raise ValueError(f"Unsupported AST node type: {type(node)}")


def do(**kwargs) -> dict[str, Any]:
    """Helper function for creating 'do' actions."""
    kwargs["_metadata"] = "do"
    return kwargs


def finish(**kwargs) -> dict[str, Any]:
    """Helper function for creating 'finish' actions."""
    kwargs["_metadata"] = "finish"
    return kwargs
