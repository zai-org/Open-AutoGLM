"""Exercise the installed CLI instead of importing it from the checkout."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def test_wheel_installs_a_working_console_command(tmp_path):
    source = tmp_path / "source"
    shutil.copytree(
        Path(__file__).resolve().parents[1],
        source,
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            "__pycache__",
            "*.egg-info",
            "build",
            "dist",
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
        ),
    )
    wheels = tmp_path / "wheels"
    installed = tmp_path / "installed"
    outside = tmp_path / "outside"
    outside.mkdir()

    def run(*command, cwd=outside, env=None):
        result = subprocess.run(
            command, cwd=cwd, env=env, capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, result.stdout + result.stderr
        return result.stdout

    run(
        sys.executable,
        "setup.py",
        "bdist_wheel",
        "--dist-dir",
        str(wheels),
        cwd=source,
    )
    wheel = next(wheels.glob("*.whl"))
    run(
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-index",
        "--no-deps",
        "--target",
        str(installed),
        str(wheel),
    )

    env = {k: v for k, v in os.environ.items() if not k.startswith("PHONE_AGENT_")}
    env["PYTHONPATH"] = str(installed)
    env["PYTHONIOENCODING"] = "utf-8"
    # An editable development install must not mask a missing wheel module.
    run(
        sys.executable,
        "-c",
        "import importlib.metadata, inspect, pathlib, sys, phone_agent; "
        "entry = next(e for e in importlib.metadata.distribution('phone-agent').entry_points "
        "if e.group == 'console_scripts' and e.name == 'phone-agent'); "
        "root = pathlib.Path(sys.argv[1]).resolve(); "
        "module = inspect.getmodule(entry.load()); "
        "assert pathlib.Path(module.__file__).resolve().is_relative_to(root); "
        "assert pathlib.Path(phone_agent.__file__).resolve().is_relative_to(root)",
        str(installed),
        env=env,
    )
    command_name = "phone-agent.exe" if os.name == "nt" else "phone-agent"
    command = next(installed.rglob(command_name))
    assert "Phone Agent - AI-powered phone automation" in run(
        str(command), "--help", env=env
    )
    for device, heading in (
        ("adb", "Supported Android apps:"),
        ("hdc", "Supported HarmonyOS apps:"),
        ("ios", "Supported iOS apps:"),
    ):
        assert heading in run(
            str(command), "--device-type", device, "--list-apps", env=env
        )
