"""Exercise real MCP request construction through scripted phone agent turns."""

import asyncio
import copy
import json
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import Mock, patch

import anyio
import httpx
import pytest

from phone_agent.agent import AgentConfig, PhoneAgent
from phone_agent.agent_ios import IOSAgentConfig, IOSPhoneAgent
from phone_agent.config import get_system_prompt
from phone_agent.device_factory import DeviceFactory, DeviceType
from phone_agent.model.client import ModelResponse
from phone_agent.search import (
    MCP_URL,
    USER_AGENT,
    ParallelSearch,
    SearchAction,
    SearchConfig,
    format_results,
)

QUERY = "NASA Artemis current mission"
SOURCE_URL = "https://www.nasa.gov/artemis/"
RESULTS = {
    "results": [
        {"title": "Artemis", "url": SOURCE_URL, "excerpts": ["Current mission facts."]}
    ]
}


def response(action):
    return ModelResponse(
        thinking="Plan the requested task", action=action, raw_content=action
    )


@pytest.fixture
def mcp_server(monkeypatch):
    """Use the real SDK and HTTP client with an observed JSON-RPC transport."""
    state = SimpleNamespace(
        requests=[],
        clients=[],
        data=RESULTS,
        error=False,
        delay=0,
        text_only=False,
        http_error=False,
        missing_tool=False,
    )
    original = httpx.AsyncClient

    async def handle(request):
        state.requests.append(request)
        assert str(request.url) == MCP_URL
        assert request.headers["User-Agent"] == USER_AGENT
        data = json.loads(request.content)
        method = data["method"]
        if method == "notifications/initialized":
            return httpx.Response(202)
        if method == "initialize":
            result = {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "search-fixture", "version": "1"},
            }
        elif method == "tools/list":
            result = {
                "tools": [{"name": "web_search", "inputSchema": {"type": "object"}}]
            }
            if state.missing_tool:
                result = {"tools": []}
        elif method == "tools/call":
            assert data["params"]["name"] == "web_search"
            assert data["params"]["arguments"]["objective"] == QUERY
            assert data["params"]["arguments"]["search_queries"] == [QUERY]
            assert len(data["params"]["arguments"]["session_id"]) == 36
            if state.http_error:
                return httpx.Response(503, text="private provider diagnostics")
            if state.delay:
                await anyio.sleep(state.delay)
            result = {
                "content": [{"type": "text", "text": json.dumps(state.data)}],
                "isError": state.error,
            }
            if not state.text_only:
                result["structuredContent"] = state.data
        else:
            raise AssertionError(method)
        return httpx.Response(
            200, json={"jsonrpc": "2.0", "id": data["id"], "result": result}
        )

    class ObservedClient(original):
        def __init__(self, **kwargs):
            super().__init__(**kwargs, transport=httpx.MockTransport(handle))
            state.clients.append(self)

    monkeypatch.setattr("phone_agent.search.httpx.AsyncClient", ObservedClient)
    # No ambient Parallel credentials may be picked up by the anonymous resolver.
    monkeypatch.setenv("PARALLEL_API_KEY", "ambient-must-not-be-used")
    return state


@pytest.fixture(params=["android", "harmonyos", "ios"])
def agent_factory(request):
    platform = request.param
    module = "phone_agent.agent_ios" if platform == "ios" else "phone_agent.agent"
    with ExitStack() as stack:
        stack.enter_context(patch(module + ".ModelClient"))
        screenshot = SimpleNamespace(base64_data="screen", width=1080, height=1920)
        if platform == "ios":
            stack.enter_context(patch(module + ".XCTestConnection"))
            stack.enter_context(
                patch(module + ".get_screenshot", return_value=screenshot)
            )
            stack.enter_context(
                patch(module + ".get_current_app", return_value="Notes")
            )
        else:
            device = DeviceFactory(
                DeviceType.ADB if platform == "android" else DeviceType.HDC
            )
            device_module = (
                "phone_agent.adb" if platform == "android" else "phone_agent.hdc"
            )
            stack.enter_context(
                patch(device_module + ".get_screenshot", return_value=screenshot)
            )
            stack.enter_context(
                patch(device_module + ".get_current_app", return_value="Notes")
            )
            stack.enter_context(
                patch(module + ".get_device_factory", return_value=device)
            )

        def create(search=None, confirmation=None, provider=None):
            common = dict(verbose=False, search=search or SearchConfig())
            if platform == "ios":
                config = IOSAgentConfig(session_id="fixture-session", **common)
                agent = IOSPhoneAgent(
                    agent_config=config,
                    confirmation_callback=confirmation or Mock(return_value=True),
                    search_provider=provider,
                )
            else:
                config = AgentConfig(device_id=platform + "-device", **common)
                agent = PhoneAgent(
                    agent_config=config,
                    confirmation_callback=confirmation or Mock(return_value=True),
                    search_provider=provider,
                )
            agent.model_client.request.side_effect = [
                response(f'do(action="Search", query="{QUERY}")'),
                response('finish(message="Draft ready with sources")'),
            ]
            return agent

        yield create


def test_anonymous_search_reaches_next_planning_turn(agent_factory, mcp_server):
    consent = Mock(return_value=True)
    agent = agent_factory(confirmation=consent)
    seen = []
    responses = iter(agent.model_client.request.side_effect)

    def plan(messages):
        seen.append(copy.deepcopy(messages))
        return next(responses)

    agent.model_client.request.side_effect = plan
    assert (
        agent.run("Look up mission facts and prepare a note")
        == "Draft ready with sources"
    )
    observation = seen[1][-1]["content"][-1]["text"]
    assert SOURCE_URL in observation
    assert "Current mission facts." in observation
    assert "Untrusted reference data" in observation
    assert [m["role"] for m in seen[1]] == ["system", "user", "assistant", "user"]
    assert "Search" in seen[0][0]["content"]
    notice = consent.call_args.args[0]
    assert QUERY in notice and "Parallel" in notice and "privacy-policy" in notice
    assert len(mcp_server.requests) == 4
    assert all(client.is_closed for client in mcp_server.clients)
    assert all("authorization" not in r.headers for r in mcp_server.requests)
    # Only an approved query and an opaque conversation id leave the agent.
    call = json.loads(mcp_server.requests[-1].content)
    assert set(call["params"]["arguments"]) == {
        "objective",
        "search_queries",
        "session_id",
    }
    assert b"screen" not in mcp_server.requests[-1].content


@pytest.mark.parametrize("enabled,allowed", [(False, True), (True, False)])
def test_disabled_or_denied_search_never_connects(
    agent_factory, mcp_server, enabled, allowed
):
    consent = Mock(return_value=allowed)
    agent = agent_factory(search=SearchConfig(enabled=enabled), confirmation=consent)
    first = agent.step("Find a public fact")
    assert not first.success and not first.finished
    assert not mcp_server.requests
    assert consent.call_count == int(enabled)
    agent.step()
    assert (
        "Search observation (unavailable)" in agent.context[-2]["content"][-1]["text"]
    )


def test_configured_credentials_and_text_content(mcp_server):
    mcp_server.text_only = True
    output = ParallelSearch(SearchConfig(api_key="explicit-key")).search(
        QUERY, "a" * 36
    )
    assert SOURCE_URL in output
    assert all(
        r.headers["authorization"] == "Bearer explicit-key" for r in mcp_server.requests
    )


@pytest.mark.parametrize(
    "failure", ["tool", "malformed", "timeout", "http", "missing_tool"]
)
def test_errors_reach_next_turn_without_claiming_success(
    agent_factory, mcp_server, failure
):
    if failure == "tool":
        mcp_server.error = True
    elif failure == "malformed":
        mcp_server.data = {"unexpected": "not search results"}
    elif failure == "timeout":
        mcp_server.delay = 1
    elif failure == "http":
        mcp_server.http_error = True
    else:
        mcp_server.missing_tool = True
    agent = agent_factory(
        search=SearchConfig(timeout=0.1 if failure == "timeout" else 30)
    )
    result = agent.step("Look up a fact")
    assert not result.success and not result.finished
    agent.step()
    text = agent.context[-2]["content"][-1]["text"]
    assert "unavailable" in text and "Do not repeat" in text
    assert "ambient-must-not-be-used" not in text
    assert all(client.is_closed for client in mcp_server.clients)


def test_custom_prompts_and_disabled_defaults_are_preserved():
    for config in (AgentConfig, IOSAgentConfig):
        assert config(system_prompt="Saved prompt").system_prompt == "Saved prompt"
        assert (
            config(search=SearchConfig(enabled=False)).system_prompt
            == get_system_prompt()
        )
        assert config(lang="en").system_prompt.startswith(get_system_prompt("en"))


def test_provider_override_is_used_without_fallback(agent_factory, mcp_server):
    provider = Mock(name="custom-provider")
    provider.name = "Local research"
    provider.privacy_notice = "Runs locally."
    provider.search.return_value = "Saved provider answer https://example.com/source"
    consent = Mock(return_value=True)
    agent = agent_factory(provider=provider, confirmation=consent)
    assert agent.step("Find a fact").success
    assert not mcp_server.requests
    assert "Local research" in consent.call_args.args[0]
    first_session = provider.search.call_args.args[1]
    provider.search.side_effect = RuntimeError("do not expose provider diagnostics")
    agent.model_client.request.side_effect = [
        response(f'do(action="Search", query="{QUERY}")')
    ]
    assert not agent.step().success
    assert provider.search.call_args.args[1] == first_session
    assert not mcp_server.requests
    agent.reset()
    assert agent.search_action.session_id != first_session
    assert agent._search_observation is None


@pytest.mark.parametrize("cancel", [KeyboardInterrupt, asyncio.CancelledError])
def test_cancellation_propagates_through_agent(agent_factory, mcp_server, cancel):
    provider = Mock()
    provider.name = "Fixture"
    provider.privacy_notice = "Local fixture."
    provider.search.side_effect = cancel
    agent = agent_factory(provider=provider)
    with pytest.raises(cancel):
        agent.step("Find a fact")
    assert not mcp_server.requests


def test_cancelling_mcp_request_closes_transport(mcp_server):
    mcp_server.delay = 1

    async def cancel_request():
        with anyio.move_on_after(0.05) as scope:
            await ParallelSearch(SearchConfig())._search(QUERY, "b" * 36)
        assert scope.cancel_called

    anyio.run(cancel_request)
    assert len(mcp_server.requests) == 4
    assert all(client.is_closed for client in mcp_server.clients)


def test_results_are_bounded_with_complete_safe_urls():
    rows = [
        {"url": "javascript:alert(1)"},
        {"url": "https://user:password@example.com/private"},
        {"url": SOURCE_URL, "title": "T" * 2000, "excerpts": ["x" * 50000]},
    ]
    text = format_results({"results": rows})
    assert len(text) < 10000 and SOURCE_URL in text
    assert "javascript" not in text and "password" not in text
    assert "No usable" in format_results({"results": []})


@pytest.mark.parametrize("query", [None, "", " ", 1, "x" * 1001])
def test_invalid_queries_do_not_connect(mcp_server, query):
    consent = Mock(return_value=True)
    result = SearchAction(SearchConfig(), consent).execute({"query": query})
    assert not result.success and not consent.called and not mcp_server.requests


def test_consent_renders_controls_and_transmits_exact_displayed_query():
    from phone_agent.actions.handler import ActionHandler

    query = "private secret\r\x1b[2Kpublic weather\u202eexample"
    provider = Mock()
    provider.name = "Fixture"
    provider.privacy_notice = "Local fixture."
    provider.search.return_value = "Source text"
    action = SearchAction(
        SearchConfig(), ActionHandler().confirmation_callback, provider
    )
    with patch("builtins.input", return_value="y") as prompt:
        assert action.execute({"query": query}).success
    display = prompt.call_args.args[0]
    assert "\x1b" not in display and "\r" not in display and "\u202e" not in display
    assert "\\r" in display and "\\u001b" in display and "\\u202e" in display
    displayed_query = display.splitlines()[1]
    assert json.loads(displayed_query) == provider.search.call_args.args[0] == query


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan")])
def test_invalid_timeouts_are_rejected(timeout):
    with pytest.raises(ValueError):
        SearchConfig(timeout=timeout)


def test_existing_actions_still_use_device_dispatch(agent_factory, mcp_server):
    from phone_agent.actions.handler import ActionResult

    agent = agent_factory()
    agent.model_client.request.side_effect = [
        response('do(action="Call_API", instruction="Summarize page")')
    ]
    with patch.object(
        agent.action_handler, "execute", return_value=ActionResult(True, False)
    ) as execute:
        assert agent.step("Summarize the page").success
    assert execute.call_args.args[0]["action"] == "Call_API"
    assert agent._search_observation is None
    assert not mcp_server.requests


@pytest.mark.parametrize("entrypoint", ["main", "ios"])
def test_cli_has_explicit_search_disable(entrypoint):
    import importlib

    module = importlib.import_module(entrypoint)
    with patch("sys.argv", [entrypoint + ".py", "--disable-search"]):
        assert module.parse_args().disable_search
