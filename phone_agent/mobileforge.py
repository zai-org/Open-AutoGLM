"""MobileForge model protocol support for the AutoGLM device runtime."""

import json
import re
from typing import Any

MOBILEFORGE_SYSTEM_PROMPT = """You are a helpful assistant that controls a mobile device.
The device may run Android or HarmonyOS. Decide the next single action from the
current screenshot. Screen coordinates are normalized to a 1000 by 1000 canvas.

Return exactly these three blocks and nothing else:
<thinking>One brief sentence explaining the next move.</thinking>
<tool_call>{"name":"mobile_use","arguments":{...}}</tool_call>
<conclusion>A concise UI observation and intended action.</conclusion>

The mobile_use arguments support:
- {"action":"click","coordinate":[x,y]}
- {"action":"long_press","coordinate":[x,y],"time":seconds}
- {"action":"swipe","coordinate":[x1,y1],"coordinate2":[x2,y2]}
- {"action":"type","text":"text"}
- {"action":"system_button","button":"Back"|"Home"}
- {"action":"open","text":"app name"}
- {"action":"wait","time":seconds}
- {"action":"answer","text":"answer"}
- {"action":"terminate","status":"success"|"failure"}

Always verify the visible result of the previous action before continuing. Use
terminate only after the task is complete or demonstrably infeasible.
"""


def _extract_json_object(text: str) -> dict[str, Any]:
    """Extract a MobileForge tool-call object, tolerating fenced JSON."""
    match = re.search(r"<tool_call>\s*(.*?)\s*</tool_call>", text, re.DOTALL | re.I)
    payload = match.group(1).strip() if match else text.strip()
    payload = re.sub(r"^```(?:json)?\s*|\s*```$", "", payload, flags=re.I)
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        start, end = payload.find("{"), payload.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("MobileForge response contains no JSON tool call") from exc
        try:
            value = json.loads(payload[start : end + 1])
        except json.JSONDecodeError as nested:
            raise ValueError(
                f"Invalid MobileForge tool-call JSON: {nested}"
            ) from nested
    if not isinstance(value, dict):
        raise ValueError("MobileForge tool call must be a JSON object")
    return value


def parse_mobileforge_response(content: str) -> tuple[str, str]:
    """Convert a MobileForge mobile_use call into AutoGLM's action DSL."""
    thinking_match = re.search(
        r"<thinking>\s*(.*?)\s*</thinking>", content, re.DOTALL | re.I
    )
    thinking = thinking_match.group(1).strip() if thinking_match else ""
    tool_call = _extract_json_object(content)
    arguments = tool_call.get("arguments", tool_call)
    if not isinstance(arguments, dict):
        raise ValueError("MobileForge tool-call arguments must be an object")

    action_type = str(arguments.get("action", "")).lower()
    if action_type in {"click", "tap"}:
        action = f'do(action="Tap", element={json.dumps(arguments.get("coordinate"))})'
    elif action_type == "long_press":
        action = (
            f'do(action="Long Press", '
            f"element={json.dumps(arguments.get('coordinate'))})"
        )
    elif action_type == "swipe":
        action = (
            f'do(action="Swipe", '
            f"start={json.dumps(arguments.get('coordinate'))}, "
            f"end={json.dumps(arguments.get('coordinate2'))})"
        )
    elif action_type in {"type", "input_text"}:
        text = json.dumps(str(arguments.get("text", "")), ensure_ascii=False)
        action = f'do(action="Type", text={text})'
    elif action_type in {"open", "open_app"}:
        app = arguments.get("text", arguments.get("app_name", ""))
        app = json.dumps(str(app), ensure_ascii=False)
        action = f'do(action="Launch", app={app})'
    elif action_type == "system_button":
        button = str(arguments.get("button", "")).lower()
        if button == "back":
            action = 'do(action="Back")'
        elif button == "home":
            action = 'do(action="Home")'
        else:
            raise ValueError(f"Unsupported system button: {button}")
    elif action_type == "wait":
        seconds = arguments.get("time", 1)
        action = f'do(action="Wait", duration="{seconds} seconds")'
    elif action_type == "answer":
        message = json.dumps(str(arguments.get("text", "")), ensure_ascii=False)
        action = f"finish(message={message})"
    elif action_type == "terminate":
        status = str(arguments.get("status", "success"))
        message = "Task completed" if status == "success" else "Task infeasible"
        action = f"finish(message={json.dumps(message)})"
    else:
        raise ValueError(
            f"Unsupported MobileForge action: {action_type or '<missing>'}"
        )
    return thinking, action
