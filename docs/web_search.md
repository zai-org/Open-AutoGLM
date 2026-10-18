# Web search during phone tasks

Phone Agent can look up current public facts before using them in a phone task,
for example, finding a mission update before preparing a note. Both the
Android/HarmonyOS and iOS agents support a separate action:

```python
do(action="Search", query="NASA Artemis current mission")
```

The built-in prompts advertise this action by default. It uses
[Parallel Search MCP](https://docs.parallel.ai/integrations/mcp/search-mcp)
over Streamable HTTP, with no account or API key required. Anonymous search uses
Fast mode and has service limits. Install the normal runtime dependencies with
`pip install -r requirements.txt`; no model deployment packages are needed for
the search client itself.

Before each search, the agent asks for confirmation with the provider and exact
query. Declining prevents the request. The default provider sends only that query
and an opaque conversation identifier to `https://search.parallel.ai/mcp`, never
screenshots or conversation history. Do not approve a query containing private
messages, credentials, or other sensitive information. Parallel processes requests
over HTTPS in US-based data centers. Retention varies with its processing policy;
review the [privacy policy](https://parallel.ai/privacy-policy) and
[data-handling FAQ](https://docs.parallel.ai/resources/faqs) before approving.

Results are limited to five sources and a bounded text observation, with complete
source URLs. They are included with the next screenshot sent to your configured
model. Search results are untrusted reference data and do not authorize phone
operations. Existing sensitive-operation confirmations and manual takeover still
apply. `Search` does not operate the phone or implement page fetching;
`Call_API` retains its existing page-summary meaning.

## Disable or configure search

To keep phone tasks from using external search, pass `--disable-search` to
`main.py` or `ios.py`. This also prevents requests if a model emits `Search`
anyway. In Python, use the same configuration for either agent:

```python
from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.search import SearchConfig

agent = PhoneAgent(
    agent_config=AgentConfig(search=SearchConfig(enabled=False)),
)
```

`IOSAgentConfig` accepts the same `search` field. Search configuration does not
change your model endpoint, model credentials, device, or custom system prompt.
Custom prompts are preserved exactly; add the `Search` action description yourself
if you want your custom prompt to use it. Your selected model must follow that
action format. For example, inspect `agent.step(...)` when trying a new model.

`SearchConfig(timeout=15, api_key="your-parallel-key")` sets the overall request
timeout and explicitly opts into authenticated Parallel requests. The client does
not read ambient `PARALLEL_API_KEY` or model credentials. There is no automatic
provider fallback after an error. Failed or denied search becomes an unavailable
observation so the planner can explain the limitation or continue using the phone.
Press Ctrl-C to cancel an in-flight search; cancellation closes its MCP session.

Applications can pass `search_provider=provider` to either agent to preserve their
own search implementation. The provider must implement
`search(query: str, session_id: str) -> str`, expose a `name` and `privacy_notice`
for the confirmation, and handle its own timeout/cancellation. The agent still
enforces search disablement and per-query confirmation. If you supply a custom
confirmation callback, it must obtain informed consent before returning `True`.

## Development checks

Run `python -m pytest -q tests/test_search.py`. These tests use scripted model
responses and fake device captures, but exercise the real MCP SDK and HTTP request
construction through both agent loops. They do not require a phone, model server,
or external search quota, and do not measure a model's ability to select actions.
