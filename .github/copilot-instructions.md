# Open-AutoGLM — AI Coding Agent Guide

Purpose: Make AI agents immediately productive in this repo. Focus on the CLI entry (`main.py`), the agent loop (`phone_agent/agent.py`), ADB interactions (`phone_agent/adb/**`), action execution (`phone_agent/actions/handler.py`), prompts and i18n (`phone_agent/config/**`), and the model client (`phone_agent/model/**`).

## Architecture
- **CLI (`main.py`):** Parses args, runs environment checks (ADB, devices, ADB Keyboard), connects/disconnects devices, and orchestrates one-shot or interactive tasks. Builds `ModelConfig` and `AgentConfig`, then runs `PhoneAgent.run(task)`.
- **Agent Loop (`phone_agent/agent.py`):** For each step, captures a screenshot + current app via ADB, builds messages using `MessageBuilder`, calls `ModelClient.request()`, parses an action string, executes via `ActionHandler`, and decides finish conditions. Keeps short conversation context (images stripped after send).
- **Model Client (`phone_agent/model/client.py`):** OpenAI-compatible chat completions. Parses response into `thinking` and `action` using markers: `finish(message=...)`, `do(action=...)`, or legacy `<think>/<answer>`.
- **Actions (`phone_agent/actions/handler.py`):** Executes UI actions via ADB: `Launch`, `Tap`, `Type`, `Swipe`, `Back`, `Home`, etc. Coordinates are relative (0–1000) and converted to absolute pixels. Sensitive actions may require confirmation.
- **ADB Layer (`phone_agent/adb/**`):** Device management, input, screenshots, app detection. Used by handler and agent.
- **Prompts & i18n (`phone_agent/config/**`):** `get_system_prompt(lang)` and `get_messages(lang)` control guidance and console text. Lang is `cn` or `en`.

## Data Flow
- User task → CLI → `PhoneAgent`.
- Step: ADB screenshot + current app → `MessageBuilder` → `ModelClient.request` → `ModelResponse(thinking, action)`.
- Parse action → `ActionHandler.execute` via ADB → result → context appends assistant `<think>/<answer>` → check finish (`_metadata == 'finish'` or `result.should_finish`).

## Conventions
- **Action format:** Model must return either `finish(message=...)` or `do(action="Tap"|"Launch"|... , element=[x,y], ... )`. See `parse_action()` and handler keys. Use exact keys; unknown actions are rejected.
- **Relative coords:** UI elements use `[x,y]` in 0–1000 scale; convert with `_convert_relative_to_absolute`.
- **Images in context:** After sending a screenshot, the agent removes image parts to control token usage.
- **Language:** `--lang cn|en` selects system prompt and console messages.

## Workflows
- **Install:**
  ```bash
  pip install -r requirements.txt
  pip install -e .
  ```
- **ADB setup:** Ensure `adb` in PATH and ADB Keyboard installed/enabled.
- **List devices/apps:**
  ```bash
  python main.py --list-devices
  python main.py --list-apps
  ```
- **Connect device (WiFi):**
  ```bash
  python main.py --enable-tcpip 5555
  python main.py --connect <ip>:5555
  ```
- **Run task:**
  ```bash
  python main.py --base-url http://localhost:8000/v1 --model autoglm-phone-9b "Open Chrome and search headphones"
  ```
- **Interactive mode:** Run `python main.py` with no task and type commands; use `quit` to exit.

## Integration Points
- **Model server:** OpenAI-compatible `/chat/completions`. Connectivity checked in `check_model_api()` by issuing a small chat request.
- **Device I/O:** All UI automations happen through ADB wrappers (`phone_agent/adb/*`). Keyboard switching handled automatically during `Type` via ADB Keyboard.
- **Apps registry:** `phone_agent/config/apps.py` provides `list_supported_apps()` used by `--list-apps`.

## Tips for Agents
- When generating actions, prefer `finish(message=...)` as the terminal step; otherwise use `do(...)` with supported `action` names.
- Provide concise `thinking` before the action; the system will print it for transparency.
- Use `Note`/`Call_API` only as placeholders; they currently return success without side effects.
- If an action needs user confirmation, include a `message` in the `Tap` payload; the default callback will prompt.

## Debugging
- Use `--quiet` to reduce console noise; otherwise the agent prints thinking/action.
- Exceptions during model or ADB calls are caught and turned into `finish(message=...)` with the error string.
- Encoding issues on Windows: run with `PYTHONIOENCODING=utf-8`.

## Key Files
- `main.py`, `phone_agent/agent.py`, `phone_agent/actions/handler.py`, `phone_agent/model/client.py`, `phone_agent/config/prompts_*.py`, `phone_agent/adb/*`.

If anything here is unclear or missing (e.g., specific ADB helpers or prompts), tell me which parts to expand and we’ll refine this guide.