import subprocess

from phone_agent.adb import input as adb_input


def test_type_text_targets_adb_keyboard_package(monkeypatch) -> None:
    commands: list[list[str]] = []

    def fake_run(command, **kwargs):
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(adb_input.subprocess, "run", fake_run)

    adb_input.type_text("你好", device_id="device-1")

    command = commands[0]
    assert command[:3] == ["adb", "-s", "device-1"]
    assert command[-2:] == ["-p", "com.android.adbkeyboard"]


def test_clear_text_targets_adb_keyboard_package(monkeypatch) -> None:
    commands: list[list[str]] = []

    def fake_run(command, **kwargs):
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(adb_input.subprocess, "run", fake_run)

    adb_input.clear_text(device_id="device-1")

    command = commands[0]
    assert command[:3] == ["adb", "-s", "device-1"]
    assert command[-2:] == ["-p", "com.android.adbkeyboard"]
