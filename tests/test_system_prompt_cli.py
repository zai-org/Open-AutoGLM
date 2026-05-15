import sys
from argparse import Namespace

import pytest

import main


def test_parse_args_accepts_inline_system_prompt(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--system-prompt", "Use short Android launcher labels."],
    )

    args = main.parse_args()

    assert args.system_prompt == "Use short Android launcher labels."
    assert args.system_prompt_file is None


def test_resolve_system_prompt_reads_file(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Report each launcher step to the user.", encoding="utf-8")

    system_prompt = main.resolve_system_prompt(None, str(prompt_file))

    assert system_prompt == "Report each launcher step to the user."


def test_resolve_system_prompt_rejects_inline_and_file(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("file prompt", encoding="utf-8")

    with pytest.raises(ValueError, match="--system-prompt"):
        main.resolve_system_prompt("inline prompt", str(prompt_file))


@pytest.mark.parametrize("device_type", ["adb", "ios"])
def test_main_passes_custom_system_prompt_to_agent_config(monkeypatch, device_type):
    captured = {}
    args = Namespace(
        apikey="EMPTY",
        base_url="http://localhost:8000/v1",
        device_id=None,
        device_type=device_type,
        lang="en",
        list_apps=False,
        max_steps=3,
        model="autoglm-phone-9b",
        quiet=True,
        system_prompt="Only use short launcher labels.",
        system_prompt_file=None,
        task="Open the launcher",
        wda_url="http://localhost:8100",
    )

    class FakeAgent:
        def __init__(self, model_config, agent_config):
            captured["agent_config"] = agent_config

        def run(self, task):
            return "ok"

    class FakeDeviceFactory:
        def list_devices(self):
            return []

    monkeypatch.setattr(main, "parse_args", lambda: args)
    monkeypatch.setattr(main, "handle_device_commands", lambda _args: False)
    monkeypatch.setattr(main, "check_system_requirements", lambda *_, **__: True)
    monkeypatch.setattr(main, "check_model_api", lambda *_, **__: True)
    monkeypatch.setattr(main, "set_device_type", lambda _device_type: None)
    monkeypatch.setattr(main, "get_device_factory", lambda: FakeDeviceFactory())
    monkeypatch.setattr(main, "list_ios_devices", lambda: [])
    monkeypatch.setattr(main, "PhoneAgent", FakeAgent)
    monkeypatch.setattr(main, "IOSPhoneAgent", FakeAgent)

    main.main()

    assert captured["agent_config"].system_prompt == "Only use short launcher labels."
