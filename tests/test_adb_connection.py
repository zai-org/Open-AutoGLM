import subprocess
from unittest.mock import patch

import pytest

from phone_agent.adb.connection import ADBConnection


@pytest.mark.parametrize(
    "adb_path,device_id",
    [("adb", None), ("adb", "device-123"), ("/custom tools/adb", "device-123")],
)
def test_device_ip_falls_back_to_wlan0_with_a_valid_adb_command(adb_path, device_id):
    prefix = [adb_path] + (["-s", device_id] if device_id else [])
    route_command = prefix + ["shell", "ip", "route"]
    address_command = prefix + ["shell", "ip", "addr", "show", "wlan0"]

    def run(command, **kwargs):
        if command == route_command:
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command == address_command:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="2: wlan0: <UP>\n    inet 192.0.2.8/24 brd 192.0.2.255 scope global wlan0\n",
                stderr="",
            )
        return subprocess.CompletedProcess(
            command, 1, stdout="", stderr='Object "shell" is unknown'
        )

    with patch("phone_agent.adb.connection.subprocess.run", side_effect=run) as mocked:
        assert ADBConnection(adb_path).get_device_ip(device_id) == "192.0.2.8"

    assert [call.args[0] for call in mocked.call_args_list] == [
        route_command,
        address_command,
    ]


def test_device_ip_prefers_route_source_without_running_fallback():
    with patch(
        "phone_agent.adb.connection.subprocess.run",
        return_value=subprocess.CompletedProcess(
            [], 0, stdout="default via 192.0.2.1 dev wlan0 src 192.0.2.8\n", stderr=""
        ),
    ) as mocked:
        assert ADBConnection().get_device_ip() == "192.0.2.8"
    mocked.assert_called_once_with(
        ["adb", "shell", "ip", "route"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )


def test_device_ip_returns_none_when_neither_command_has_an_ipv4_address():
    with patch(
        "phone_agent.adb.connection.subprocess.run",
        return_value=subprocess.CompletedProcess(
            [], 0, stdout="2: wlan0: <UP>\n    inet6 fe80::1/64 scope link\n", stderr=""
        ),
    ):
        assert ADBConnection().get_device_ip() is None


def test_device_ip_handles_command_timeout():
    with patch(
        "phone_agent.adb.connection.subprocess.run",
        side_effect=subprocess.TimeoutExpired(["adb"], 5),
    ):
        assert ADBConnection().get_device_ip() is None
