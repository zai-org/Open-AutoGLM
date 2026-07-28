#!/usr/bin/env python3
"""Validate MobileForge model responses against Open-AutoGLM's adapter."""

import argparse
import base64
import json
import time
from pathlib import Path
from typing import Any

import requests

from phone_agent.actions.handler import parse_action
from phone_agent.mobileforge import parse_mobileforge_response


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000/v1")
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--image-dir", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=1024)
    return parser.parse_args()


def image_data_url(image_dir: Path, reference: str) -> str:
    root = image_dir.resolve()
    path = (root / reference).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Image reference escapes --image-dir: {reference}")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def build_messages(sample: dict[str, Any], image_dir: Path) -> list[dict[str, Any]]:
    messages = []
    for message in sample["conversations"]:
        if message["role"] == "assistant":
            continue
        content = message["content"]
        if not isinstance(content, list):
            messages.append({"role": message["role"], "content": content})
            continue
        parts = []
        for part in content:
            if part.get("type") == "text":
                parts.append({"type": "text", "text": part["text"]})
            elif part.get("type") == "image_url":
                url = image_data_url(image_dir, part["image_url"]["url"])
                parts.append({"type": "image_url", "image_url": {"url": url}})
        messages.append({"role": message["role"], "content": parts})
    return messages


def main() -> None:
    args = parse_args()
    with args.data.open(encoding="utf-8") as data_file:
        data = json.load(data_file)
    positives = [sample for sample in data if sample.get("is_positive")]
    samples = positives[:: args.stride][: args.samples]
    if not samples:
        raise ValueError("No positive samples selected")

    parsed_count = 0
    for index, sample in enumerate(samples, start=1):
        started = time.monotonic()
        response = requests.post(
            f"{args.base_url}/chat/completions",
            json={
                "model": args.model,
                "messages": build_messages(sample, args.image_dir),
                "max_tokens": args.max_tokens,
                "temperature": 0.0,
            },
            timeout=180,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        thinking, action = parse_mobileforge_response(content)
        parsed = parse_action(action)
        duration = time.monotonic() - started
        print(
            f"sample={index} duration={duration:.1f}s "
            f"action={parsed.get('action', parsed.get('_metadata'))} "
            f"thinking={thinking[:80]!r}"
        )
        parsed_count += 1

    print(f"Parsed {parsed_count}/{len(samples)} responses into valid actions")


if __name__ == "__main__":
    main()
