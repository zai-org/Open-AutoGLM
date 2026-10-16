"""Model response streams close when their consumer stops early."""

import json
from contextlib import contextmanager

import httpx
import openai
import pytest

from phone_agent.model import client as model_client


class TrackedBody(httpx.SyncByteStream):
    def __init__(self, iteration_error=None):
        self.closed = False
        self.iteration_error = iteration_error

    def __iter__(self):
        for index, content in enumerate(("Thinking text. ", 'do(action="Home")')):
            if index and self.iteration_error is not None:
                raise self.iteration_error
            chunk = {
                "id": "test-stream",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "test-model",
                "choices": [
                    {"index": 0, "delta": {"content": content}, "finish_reason": None}
                ],
            }
            yield f"data: {json.dumps(chunk)}\n\n".encode()
        yield b"data: [DONE]\n\n"

    def close(self):
        self.closed = True


@contextmanager
def streaming_client(monkeypatch, body):
    def respond(request):
        assert request.url == httpx.URL("http://test.local/v1/chat/completions")
        return httpx.Response(
            200, headers={"content-type": "text/event-stream"}, stream=body
        )

    with httpx.Client(transport=httpx.MockTransport(respond)) as http_client:
        real_openai = openai.OpenAI
        monkeypatch.setattr(
            model_client,
            "OpenAI",
            lambda **kwargs: real_openai(http_client=http_client, **kwargs),
        )
        client = model_client.ModelClient(
            model_client.ModelConfig(
                base_url="http://test.local/v1", api_key="test-placeholder"
            )
        )
        try:
            yield client
        finally:
            client.client.close()
            body.close()


def test_normal_response_closes_stream(monkeypatch):
    body = TrackedBody()
    with streaming_client(monkeypatch, body) as client:
        response = client.request([{"role": "user", "content": "test"}])
        assert response.thinking == "Thinking text."
        assert response.action == 'do(action="Home")'
        assert response.raw_content == 'Thinking text. do(action="Home")'
        assert response.time_to_first_token is not None
        assert response.time_to_thinking_end is not None
        assert response.total_time is not None
        assert body.closed


@pytest.mark.parametrize(
    "error",
    [
        RuntimeError("output failed"),
        BrokenPipeError("pipe closed"),
        KeyboardInterrupt(),
    ],
    ids=["exception", "broken-pipe", "keyboard-interrupt"],
)
def test_consumer_error_closes_stream_and_propagates(monkeypatch, error):
    body = TrackedBody()

    def fail_print(*args, **kwargs):
        raise error

    with streaming_client(monkeypatch, body) as client:
        monkeypatch.setattr(model_client, "print", fail_print, raising=False)
        with pytest.raises(type(error)) as raised:
            client.request([{"role": "user", "content": "test"}])
        assert raised.value is error
        assert body.closed


def test_iteration_error_closes_stream_and_propagates(monkeypatch):
    error = RuntimeError("stream read failed")
    body = TrackedBody(iteration_error=error)
    with streaming_client(monkeypatch, body) as client:
        with pytest.raises(RuntimeError) as raised:
            client.request([{"role": "user", "content": "test"}])
        assert raised.value is error
        assert body.closed
