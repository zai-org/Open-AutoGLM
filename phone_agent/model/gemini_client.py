"""Gemini API client for AI inference using Google's Generative AI."""

import base64
import io
import json
import time
from dataclasses import dataclass
from typing import Any

from phone_agent.config.i18n import get_message
from phone_agent.model.client import ModelConfig, ModelResponse, MessageBuilder


class GeminiModelClient:
    """
    Client for interacting with Google's Gemini vision-language models.

    This client provides compatibility with the OpenAI-style interface while
    using Google's Generative AI API under the hood.
    """

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig()

        # Import and configure Gemini
        from google import genai
        self.genai = genai
        self.client = genai.Client(api_key=self.config.api_key)

    def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """
        Send a request to the Gemini model.

        Args:
            messages: List of message dictionaries in OpenAI format.

        Returns:
            ModelResponse containing thinking and action.

        Raises:
            ValueError: If the response cannot be parsed.
        """
        # Start timing
        start_time = time.time()
        time_to_first_token = None
        time_to_thinking_end = None

        # Convert OpenAI format messages to Gemini format
        contents = self._convert_messages(messages)

        # Start streaming
        response = self.client.models.generate_content_stream(
            model=self.config.model_name,
            contents=contents,
            generation_config={
                "max_output_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
            }
        )

        raw_content = ""
        buffer = ""  # Buffer to hold content that might be part of a marker
        action_markers = ["finish(message=", "do(action="]
        in_action_phase = False  # Track if we've entered the action phase
        first_token_received = False

        for chunk in response:
            if hasattr(chunk, 'text') and chunk.text:
                content = chunk.text
                raw_content += content

                # Record time to first token
                if not first_token_received:
                    time_to_first_token = time.time() - start_time
                    first_token_received = True

                if in_action_phase:
                    # Already in action phase, just accumulate content without printing
                    continue

                buffer += content

                # Check if any marker is fully present in buffer
                marker_found = False
                for marker in action_markers:
                    if marker in buffer:
                        # Marker found, print everything before it
                        thinking_part = buffer.split(marker, 1)[0]
                        print(thinking_part, end="", flush=True)
                        print()  # Print newline after thinking is complete
                        in_action_phase = True
                        marker_found = True

                        # Record time to thinking end
                        if time_to_thinking_end is None:
                            time_to_thinking_end = time.time() - start_time

                        break

                if marker_found:
                    continue  # Continue to collect remaining content

                # Check if buffer ends with a prefix of any marker
                # If so, don't print yet (wait for more content)
                is_potential_marker = False
                for marker in action_markers:
                    for i in range(1, len(marker)):
                        if buffer.endswith(marker[:i]):
                            is_potential_marker = True
                            break
                    if is_potential_marker:
                        break

                if not is_potential_marker:
                    # Safe to print the buffer
                    print(buffer, end="", flush=True)
                    buffer = ""

        # Calculate total time
        total_time = time.time() - start_time

        # Parse thinking and action from response
        thinking, action = self._parse_response(raw_content)

        # Print performance metrics
        lang = self.config.lang
        print()
        print("=" * 50)
        print(f"⏱️  {get_message('performance_metrics', lang)}:")
        print("-" * 50)
        if time_to_first_token is not None:
            print(
                f"{get_message('time_to_first_token', lang)}: {time_to_first_token:.3f}s"
            )
        if time_to_thinking_end is not None:
            print(
                f"{get_message('time_to_thinking_end', lang)}:        {time_to_thinking_end:.3f}s"
            )
        print(
            f"{get_message('total_inference_time', lang)}:          {total_time:.3f}s"
        )
        print("=" * 50)

        return ModelResponse(
            thinking=thinking,
            action=action,
            raw_content=raw_content,
            time_to_first_token=time_to_first_token,
            time_to_thinking_end=time_to_thinking_end,
            total_time=total_time,
        )

    def _convert_messages(self, messages: list[dict[str, Any]]) -> str | list[dict]:
        """
        Convert OpenAI format messages to Gemini format.

        Args:
            messages: List of messages in OpenAI format

        Returns:
            Content in Gemini format
        """
        # Collect system prompt
        system_prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg.get("content", "")
                break

        # Find the first user message with content
        user_content = ""
        image_data = None

        for msg in messages:
            if msg["role"] == "user":
                content = msg.get("content", "")

                if isinstance(content, list):
                    # Handle multi-modal content
                    for item in content:
                        if item.get("type") == "text":
                            user_content = item["text"]
                        elif item.get("type") == "image_url":
                            # Extract base64 image data
                            image_url = item["image_url"]["url"]
                            if image_url.startswith("data:image/png;base64,"):
                                base64_data = image_url.split(",", 1)[1]
                                image_data = base64.b64decode(base64_data)
                else:
                    user_content = content
                break  # Only process the first user message

        # Combine system prompt and user content
        if system_prompt:
            user_content = f"System: {system_prompt}\n\nUser: {user_content}"

        # If there's an image, return a list with both text and image
        if image_data:
            return [
                {"text": user_content},
                {"inline_data": {
                    "mime_type": "image/png",
                    "data": base64.b64encode(image_data).decode('utf-8')
                }}
            ]
        else:
            return user_content

    def _parse_response(self, content: str) -> tuple[str, str]:
        """
        Parse the model response into thinking and action parts.

        Parsing rules:
        1. If content contains 'finish(message=', everything before is thinking,
           everything from 'finish(message=' onwards is action.
        2. If rule 1 doesn't apply but content contains 'do(action=',
           everything before is thinking, everything from 'do(action=' onwards is action.
        3. Fallback: If content contains '<answer>', use legacy parsing with XML tags.
        4. Otherwise, return empty thinking and full content as action.

        Args:
            content: Raw response content.

        Returns:
            Tuple of (thinking, action).
        """
        # Rule 1: Check for finish(message=
        if "finish(message=" in content:
            parts = content.split("finish(message=", 1)
            thinking = parts[0].strip()
            action = "finish(message=" + parts[1]
            return thinking, action

        # Rule 2: Check for do(action=
        if "do(action=" in content:
            parts = content.split("do(action=", 1)
            thinking = parts[0].strip()
            action = "do(action=" + parts[1]
            return thinking, action

        # Rule 3: Fallback to legacy XML tag parsing
        if "<answer>" in content:
            parts = content.split("<answer>", 1)
            thinking = parts[0].replace("", "").replace("", "").strip()
            action = parts[1].replace("</answer>", "").strip()
            return thinking, action

        # Rule 4: No markers found, return content as action
        return "", content