"""Async model client for AI inference using OpenAI-compatible API."""

import json
from typing import Any

from openai import AsyncOpenAI

from phone_agent.model.client import ModelConfig, ModelResponse
from phone_agent.utils.logger import get_logger

logger = get_logger(__name__)


class AsyncModelClient:
    """
    Async client for interacting with OpenAI-compatible vision-language models.

    Args:
        config: Model configuration.
    """

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig()
        self.client = AsyncOpenAI(
            base_url=self.config.base_url, api_key=self.config.api_key
        )

    async def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """
        Send an async request to the model with automatic retry on failure.

        Args:
            messages: List of message dictionaries in OpenAI format.

        Returns:
            ModelResponse containing thinking and action.

        Raises:
            ValueError: If the response cannot be parsed.
            ConnectionError: If connection fails after retries.
        """
        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                extra_body=self.config.extra_body,
                stream=False,
            )

            raw_content = response.choices[0].message.content

            # Parse thinking and action from response
            thinking, action = self._parse_response(raw_content)

            logger.debug(f"Model response parsed successfully. Action: {action[:100]}...")

            return ModelResponse(thinking=thinking, action=action, raw_content=raw_content)
        except Exception as e:
            logger.error(f"Model request failed: {e}")
            raise

    def _parse_response(self, content: str) -> tuple[str, str]:
        """
        Parse the model response into thinking and action parts.

        This uses the same parsing logic as the sync client.

        Args:
            content: Raw response content.

        Returns:
            Tuple of (thinking, action).
        """
        # Import from sync client to reuse logic
        from phone_agent.model.client import ModelClient

        sync_client = ModelClient(self.config)
        return sync_client._parse_response(content)

