"""Tests for Android device command result handling."""

from subprocess import CompletedProcess
from unittest.mock import patch

from phone_agent.adb import device


@patch.object(device.time, "sleep")
@patch.object(device.subprocess, "run")
def test_launch_app_returns_false_when_adb_fails(run, sleep):
    run.return_value = CompletedProcess(["adb"], 1, stdout="", stderr="device offline")

    with patch.dict(device.APP_PACKAGES, {"Test App": "com.example.test"}, clear=False):
        assert device.launch_app("Test App") is False

    sleep.assert_not_called()


@patch.object(device.time, "sleep")
@patch.object(device.subprocess, "run")
def test_launch_app_returns_false_when_monkey_aborts(run, sleep):
    run.return_value = CompletedProcess(
        ["adb"],
        0,
        stdout="** No activities found to run, monkey aborted.",
        stderr="",
    )

    with patch.dict(device.APP_PACKAGES, {"Test App": "com.example.test"}, clear=False):
        assert device.launch_app("Test App") is False

    sleep.assert_not_called()


@patch.object(device.time, "sleep")
@patch.object(device.subprocess, "run")
def test_launch_app_returns_true_after_successful_monkey_run(run, sleep):
    run.return_value = CompletedProcess(
        ["adb"],
        0,
        stdout="Events injected: 1",
        stderr="",
    )

    with patch.dict(device.APP_PACKAGES, {"Test App": "com.example.test"}, clear=False):
        assert device.launch_app("Test App") is True

    sleep.assert_called_once()
