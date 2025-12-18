"""Alternative model client using requests for llama-server compatibility."""

import json
import time
from dataclasses import dataclass
from typing import Any

import requests

from phone_agent.config.i18n import get_message
from phone_agent.model.client import ModelConfig, ModelResponse


class LlamaModelClient:
    """
    Client for interacting with llama-server using requests.
    
    This bypasses OpenAI Python library compatibility issues.
    """

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig()
        self.api_url = f"{self.config.base_url}/chat/completions"

    def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """
        Send a request to the model.

        Args:
            messages: List of message dictionaries in OpenAI format.

        Returns:
            ModelResponse containing thinking and action.
        """
        start_time = time.time()
        time_to_first_token = None
        time_to_thinking_end = None

        payload = {
            "messages": messages,
            "model": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "frequency_penalty": self.config.frequency_penalty,
            "stream": True,
        }

        response = requests.post(
            self.api_url,
            json=payload,
            stream=True,
            timeout=300,
        )
        if response.status_code != 200:
            print(f"[DEBUG] Error response: {response.text[:500]}")
        response.raise_for_status()

        raw_content = ""
        buffer = ""
        action_markers = ["finish(message=", "do(action="]
        in_action_phase = False
        first_token_received = False

        for line in response.iter_lines():
            if not line:
                continue
            
            line_str = line.decode('utf-8')
            if not line_str.startswith('data: '):
                continue
            
            data_str = line_str[6:]
            if data_str == '[DONE]':
                break
            
            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            if not chunk.get('choices'):
                continue
            
            choice = chunk['choices'][0]
            
            # Check finish reason
            finish_reason = choice.get('finish_reason')
            if finish_reason and finish_reason != 'stop':
                print(f"\n[DEBUG] finish_reason: {finish_reason}")
            
            delta = choice.get('delta', {})
            content = delta.get('content')
            
            if content is None:
                continue
            
            raw_content += content

            if not first_token_received:
                time_to_first_token = time.time() - start_time
                first_token_received = True

            if in_action_phase:
                continue

            buffer += content

            marker_found = False
            for marker in action_markers:
                if marker in buffer:
                    thinking_part = buffer.split(marker, 1)[0]
                    print(thinking_part, end="", flush=True)
                    print()
                    in_action_phase = True
                    marker_found = True

                    if time_to_thinking_end is None:
                        time_to_thinking_end = time.time() - start_time
                    break

            if marker_found:
                continue

            is_potential_marker = False
            for marker in action_markers:
                for i in range(1, len(marker)):
                    if buffer.endswith(marker[:i]):
                        is_potential_marker = True
                        break
                if is_potential_marker:
                    break

            if not is_potential_marker:
                print(buffer, end="", flush=True)
                buffer = ""

        total_time = time.time() - start_time

        thinking, action = self._parse_response(raw_content)

        lang = self.config.lang
        print()
        print("=" * 50)
        print(f"[Time] {get_message('performance_metrics', lang)}:")
        print("-" * 50)
        if time_to_first_token is not None:
            print(f"{get_message('time_to_first_token', lang)}: {time_to_first_token:.3f}s")
        if time_to_thinking_end is not None:
            print(f"{get_message('time_to_thinking_end', lang)}:        {time_to_thinking_end:.3f}s")
        print(f"{get_message('total_inference_time', lang)}:          {total_time:.3f}s")
        print("=" * 50)

        return ModelResponse(
            thinking=thinking,
            action=action,
            raw_content=raw_content,
            time_to_first_token=time_to_first_token,
            time_to_thinking_end=time_to_thinking_end,
            total_time=total_time,
        )

    def _parse_response(self, content: str) -> tuple[str, str]:
        """Parse the model response into thinking and action parts."""
        if "finish(message=" in content:
            parts = content.split("finish(message=", 1)
            thinking = parts[0].strip()
            action = "finish(message=" + parts[1]
            return thinking, action

        if "do(action=" in content:
            parts = content.split("do(action=", 1)
            thinking = parts[0].strip()
            action = "do(action=" + parts[1]
            return thinking, action

        if "<answer>" in content:
            parts = content.split("<answer>", 1)
            thinking = parts[0].replace("<think>", "").replace("</think>", "").strip()
            action = parts[1].replace("</answer>", "").strip()
            return thinking, action

        return "", content
