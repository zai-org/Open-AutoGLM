"""Model client for AI inference using OpenAI-compatible API."""

import json
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI


@dataclass
class ModelConfig:
    """Configuration for the AI model."""

    base_url: str = "http://localhost:8000/v1"
    api_key: str = "EMPTY"
    model_name: str = "autoglm-phone-9b"
    max_tokens: int = 3000
    temperature: float = 0.0
    top_p: float = 0.85
    frequency_penalty: float = 0.2
    extra_body: dict[str, Any] = field(
        default_factory=lambda: {"skip_special_tokens": False}
    )
    stream: bool = True  # Set to False for local vLLM deployment


@dataclass
class ModelResponse:
    """Response from the AI model."""

    thinking: str
    action: str
    raw_content: str


class ModelClient:
    """
    Client for interacting with OpenAI-compatible vision-language models.

    Args:
        config: Model configuration.
    """

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig()
        self.client = OpenAI(base_url=self.config.base_url, api_key=self.config.api_key)

    def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """
        Send a request to the model.

        Args:
            messages: List of message dictionaries in OpenAI format.

        Returns:
            ModelResponse containing thinking and action.

        Raises:
            ValueError: If the response cannot be parsed.
        """
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            frequency_penalty=self.config.frequency_penalty,
            extra_body=self.config.extra_body,
            stream=self.config.stream,
        )

        # Collect response content
        if self.config.stream:
            raw_content = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    raw_content += chunk.choices[0].delta.content
        else:
            raw_content = response.choices[0].message.content

        # Parse thinking and action from response
        thinking, action = self._parse_response(raw_content)

        return ModelResponse(thinking=thinking, action=action, raw_content=raw_content)

    def _parse_response(self, content: str) -> tuple[str, str]:
        """
        Parse the model response into thinking and action parts.

        Args:
            content: Raw response content.

        Returns:
            Tuple of (thinking, action).
        """
        # Standard format with <think> and <answer> tags
        if "<answer>" in content:
            parts = content.split("<answer>", 1)
            thinking = parts[0].replace("<think>", "").replace("</think>", "").strip()
            action = parts[1].replace("</answer>", "").strip()
            return thinking, action

        # Fallback: extract do(...) or finish(...) from plain text response
        # Use balanced parentheses matching to handle nested brackets
        action = self._extract_action_call(content)
        if action:
            # Find where the action starts in content
            action_start = content.rfind(action[:10])  # Use prefix to locate
            if action_start != -1:
                thinking = content[:action_start].strip()
                return thinking, action

        # No recognizable action found
        return "", content

    def _extract_action_call(self, content: str) -> str | None:
        """
        Extract the last do(...) or finish(...) call from content.
        Handles nested parentheses correctly.
        """
        # Find all potential action starts from the end
        for func_name in ["finish", "do"]:
            # Search from end of string
            idx = content.rfind(func_name + "(")
            if idx == -1:
                continue

            # Extract with balanced parentheses
            start = idx
            paren_count = 0
            in_string = False
            string_char = None
            i = idx + len(func_name)

            while i < len(content):
                char = content[i]

                # Handle string literals
                if char in "\"'" and (i == 0 or content[i - 1] != "\\"):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                elif not in_string:
                    if char == "(":
                        paren_count += 1
                    elif char == ")":
                        paren_count -= 1
                        if paren_count == 0:
                            return content[start : i + 1].strip()
                i += 1

        return None


class MessageBuilder:
    """Helper class for building conversation messages."""

    @staticmethod
    def create_system_message(content: str) -> dict[str, Any]:
        """Create a system message."""
        return {"role": "system", "content": content}

    @staticmethod
    def create_user_message(
        text: str, image_base64: str | None = None
    ) -> dict[str, Any]:
        """
        Create a user message with optional image.

        Args:
            text: Text content.
            image_base64: Optional base64-encoded image.

        Returns:
            Message dictionary.
        """
        content = []

        if image_base64:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                }
            )

        content.append({"type": "text", "text": text})

        return {"role": "user", "content": content}

    @staticmethod
    def create_assistant_message(content: str) -> dict[str, Any]:
        """Create an assistant message."""
        return {"role": "assistant", "content": content}

    @staticmethod
    def remove_images_from_message(message: dict[str, Any]) -> dict[str, Any]:
        """
        Remove image content from a message to save context space.

        Args:
            message: Message dictionary.

        Returns:
            Message with images removed.
        """
        if isinstance(message.get("content"), list):
            message["content"] = [
                item for item in message["content"] if item.get("type") == "text"
            ]
        return message

    @staticmethod
    def build_screen_info(current_app: str, **extra_info) -> str:
        """
        Build screen info string for the model.

        Args:
            current_app: Current app name.
            **extra_info: Additional info to include.

        Returns:
            JSON string with screen info.
        """
        info = {"current_app": current_app, **extra_info}
        return json.dumps(info, ensure_ascii=False)
