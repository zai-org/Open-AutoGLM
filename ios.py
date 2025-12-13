#!/usr/bin/env python3
"""
Phone Agent iOS CLI - AI-powered iOS phone automation.

Usage:
    python ios.py [OPTIONS]

Environment Variables:
    PHONE_AGENT_BASE_URL: Model API base URL (default: http://localhost:8000/v1)
    PHONE_AGENT_MODEL: Model name (default: autoglm-phone-9b)
    PHONE_AGENT_MAX_STEPS: Maximum steps per task (default: 100)
    PHONE_AGENT_WDA_URL: WebDriverAgent URL (default: http://localhost:8100)
    PHONE_AGENT_DEVICE_ID: iOS device UDID for multi-device setups
"""

import argparse
import os
import shutil
import subprocess
import sys
from urllib.parse import urlparse

from openai import OpenAI

from phone_agent.agent_ios import IOSAgentConfig, IOSPhoneAgent
from phone_agent.config.apps_ios import list_supported_apps
from phone_agent.model import ModelConfig
from phone_agent.xctest import XCTestConnection, list_devices


def check_system_requirements(wda_url: str = "http://localhost:8100") -> bool:
    """
    Check system requirements before running the agent.

    Checks:
    1. libimobiledevice tools installed
    2. At least one iOS device connected
    3. WebDriverAgent is running

    Args:
        wda_url: WebDriverAgent URL to check.

    Returns:
        True if all checks pass, False otherwise.
    """
    print("🔍 Checking system requirements...")
    print("-" * 50)

    all_passed = True

    # Check 1: libimobiledevice installed
    print("1. Checking libimobiledevice installation...", end=" ")
    if shutil.which("idevice_id") is None:
        print("❌ FAILED")
        print("   Error: libimobiledevice is not installed or not in PATH.")
        print("   Solution: Install libimobiledevice:")
        print("     - macOS: brew install libimobiledevice")
        print("     - Linux: sudo apt-get install libimobiledevice-utils")
        all_passed = False
    else:
        # Double check by running idevice_id
        try:
            result = subprocess.run(
                ["idevice_id", "-ln"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("✅ OK")
            else:
                print("❌ FAILED")
                print("   Error: idevice_id command failed to run.")
                all_passed = False
        except FileNotFoundError:
            print("❌ FAILED")
            print("   Error: idevice_id command not found.")
            all_passed = False
        except subprocess.TimeoutExpired:
            print("❌ FAILED")
            print("   Error: idevice_id command timed out.")
            all_passed = False

    # If libimobiledevice is not installed, skip remaining checks
    if not all_passed:
        print("-" * 50)
        print("❌ System check failed. Please fix the issues above.")
        return False

    # Check 2: iOS Device connected
    print("2. Checking connected iOS devices...", end=" ")
    try:
        devices = list_devices()

        if not devices:
            print("❌ FAILED")
            print("   Error: No iOS devices connected.")
            print("   Solution:")
            print("     1. Connect your iOS device via USB")
            print("     2. Unlock the device and tap 'Trust This Computer'")
            print("     3. Verify connection: idevice_id -l")
            print("     4. Or connect via WiFi using device IP")
            all_passed = False
        else:
            device_names = [
                d.device_name or d.device_id[:8] + "..." for d in devices
            ]
            print(f"✅ OK ({len(devices)} device(s): {', '.join(device_names)})")
    except Exception as e:
        print("❌ FAILED")
        print(f"   Error: {e}")
        all_passed = False

    # If no device connected, skip WebDriverAgent check
    if not all_passed:
        print("-" * 50)
        print("❌ System check failed. Please fix the issues above.")
        return False

    # Check 3: WebDriverAgent running
    print(f"3. Checking WebDriverAgent ({wda_url})...", end=" ")
    try:
        conn = XCTestConnection(wda_url=wda_url)

        if conn.is_wda_ready():
            print("✅ OK")
            # Get WDA status for additional info
            status = conn.get_wda_status()
            if status:
                session_id = status.get("sessionId", "N/A")
                print(f"   Session ID: {session_id}")
        else:
            print("❌ FAILED")
            print("   Error: WebDriverAgent is not running or not accessible.")
            print("   Solution:")
            print("     1. Run WebDriverAgent on your iOS device via Xcode")
            print("     2. For USB: Set up port forwarding: iproxy 8100 8100")
            print(
                "     3. For WiFi: Use device IP, e.g., --wda-url http://192.168.1.100:8100"
            )
            print("     4. Verify in browser: open http://localhost:8100/status")
            print("\n   Quick setup guide:")
            print(
                "     git clone https://github.com/appium/WebDriverAgent.git && cd WebDriverAgent"
            )
            print("     ./Scripts/bootstrap.sh")
            print("     open WebDriverAgent.xcodeproj")
            print("     # Configure signing, then Product > Test (Cmd+U)")
            all_passed = False
    except Exception as e:
        print("❌ FAILED")
        print(f"   Error: {e}")
        all_passed = False

    print("-" * 50)

    if all_passed:
        print("✅ All system checks passed!\n")
    else:
        print("❌ System check failed. Please fix the issues above.")

    return all_passed


def check_model_api(base_url: str, api_key: str, model_name: str) -> bool:
    """
    Check if the model API is accessible and the specified model exists.

    Checks:
    1. Network connectivity to the API endpoint
    2. Model exists in the available models list

    Args:
        base_url: The API base URL
        model_name: The model name to check

    Returns:
        True if all checks pass, False otherwise.
    """
    print("🔍 Checking model API...")
    print("-" * 50)

    all_passed = True

    # Check 1: Network connectivity
    print(f"1. Checking API connectivity ({base_url})...", end=" ")
    try:
        # Parse the URL to get host and port
        parsed = urlparse(base_url)

        # Create OpenAI client
        client = OpenAI(base_url=base_url, api_key=api_key, timeout=10.0)

        # Try to list models (this tests connectivity)
        models_response = client.models.list()
        available_models = [model.id for model in models_response.data]

        print("✅ OK")

        # Check 2: Model exists
        print(f"2. Checking model '{model_name}'...", end=" ")
        if model_name in available_models:
            print("✅ OK")
        else:
            print("❌ FAILED")
            print(f"   Error: Model '{model_name}' not found.")
            print(f"   Available models:")
            for m in available_models[:10]:  # Show first 10 models
                print(f"     - {m}")
            if len(available_models) > 10:
                print(f"     ... and {len(available_models) - 10} more")
            all_passed = False

    except Exception as e:
        print("❌ FAILED")
        error_msg = str(e)

        # Provide more specific error messages
        if "Connection refused" in error_msg or "Connection error" in error_msg:
            print(f"   Error: Cannot connect to {base_url}")
            print("   Solution:")
            print("     1. Check if the model server is running")
            print("     2. Verify the base URL is correct")
            print(f"     3. Try: curl {base_url}/models")
        elif "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
            print(f"   Error: Connection to {base_url} timed out")
            print("   Solution:")
            print("     1. Check your network connection")
            print("     2. Verify the server is responding")
        elif (
            "Name or service not known" in error_msg
            or "nodename nor servname" in error_msg
        ):
            print(f"   Error: Cannot resolve hostname")
            print("   Solution:")
            print("     1. Check the URL is correct")
            print("     2. Verify DNS settings")
        else:
            print(f"   Error: {error_msg}")

        all_passed = False

    print("-" * 50)

    if all_passed:
        print("✅ Model API checks passed!\n")
    else:
        print("❌ Model API check failed. Please fix the issues above.")

    return all_passed


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Phone Agent iOS - AI-powered iOS phone automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run with default settings
    python ios.py

    # Specify model endpoint
    python ios.py --base-url http://localhost:8000/v1

    # Run with specific device
    python ios.py --device-id <UDID>

    # Use WiFi connection
    python ios.py --wda-url http://192.168.1.100:8100

    # List connected devices
    python ios.py --list-devices

    # Check device pairing status
    python ios.py --pair

    # List supported apps
    python ios.py --list-apps

    # Run a specific task
    python ios.py "Open Safari and search for iPhone tips"
        """,
    )

    # Model options
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1"),
        help="Model API base URL",
    )

    parser.add_argument(
        "--api-key",
        type=str,
        default="EMPTY",
        help="Model API KEY",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b"),
        help="Model name",
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=int(os.getenv("PHONE_AGENT_MAX_STEPS", "100")),
        help="Maximum steps per task",
    )

    # iOS Device options
    parser.add_argument(
        "--device-id",
        "-d",
        type=str,
        default=os.getenv("PHONE_AGENT_DEVICE_ID"),
        help="iOS device UDID",
    )

    parser.add_argument(
        "--wda-url",
        type=str,
        default=os.getenv("PHONE_AGENT_WDA_URL", "http://localhost:8100"),
        help="WebDriverAgent URL (default: http://localhost:8100)",
    )

    parser.add_argument(
        "--list-devices", action="store_true", help="List connected iOS devices and exit"
    )

    parser.add_argument(
        "--pair",
        action="store_true",
        help="Pair with iOS device (required for some operations)",
    )

    parser.add_argument(
        "--wda-status",
        action="store_true",
        help="Show WebDriverAgent status and exit",
    )

    # Other options
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress verbose output"
    )

    parser.add_argument(
        "--list-apps", action="store_true", help="List supported apps and exit"
    )

    parser.add_argument(
        "--lang",
        type=str,
        choices=["cn", "en"],
        default=os.getenv("PHONE_AGENT_LANG", "cn"),
        help="Language for system prompt (cn or en, default: cn)",
    )

    parser.add_argument(
        "task",
        nargs="?",
        type=str,
        help="Task to execute (interactive mode if not provided)",
    )

    return parser.parse_args()


def handle_device_commands(args) -> bool:
    """
    Handle iOS device-related commands.

    Returns:
        True if a device command was handled (should exit), False otherwise.
    """
    conn = XCTestConnection(wda_url=args.wda_url)

    # Handle --list-devices
    if args.list_devices:
        devices = list_devices()
        if not devices:
            print("No iOS devices connected.")
            print("\nTroubleshooting:")
            print("  1. Connect device via USB")
            print("  2. Unlock device and trust this computer")
            print("  3. Run: idevice_id -l")
        else:
            print("Connected iOS devices:")
            print("-" * 70)
            for device in devices:
                conn_type = device.connection_type.value
                model_info = f"{device.model}" if device.model else "Unknown"
                ios_info = f"iOS {device.ios_version}" if device.ios_version else ""
                name_info = device.device_name or "Unnamed"

                print(f"  ✓ {name_info}")
                print(f"    UDID: {device.device_id}")
                print(f"    Model: {model_info}")
                print(f"    OS: {ios_info}")
                print(f"    Connection: {conn_type}")
                print("-" * 70)
        return True

    # Handle --pair
    if args.pair:
        print("Pairing with iOS device...")
        success, message = conn.pair_device(args.device_id)
        print(f"{'✓' if success else '✗'} {message}")
        return True

    # Handle --wda-status
    if args.wda_status:
        print(f"Checking WebDriverAgent status at {args.wda_url}...")
        print("-" * 50)

        if conn.is_wda_ready():
            print("✓ WebDriverAgent is running")

            status = conn.get_wda_status()
            if status:
                print(f"\nStatus details:")
                value = status.get("value", {})
                print(f"  Session ID: {status.get('sessionId', 'N/A')}")
                print(f"  Build: {value.get('build', {}).get('time', 'N/A')}")

                current_app = value.get("currentApp", {})
                if current_app:
                    print(f"\nCurrent App:")
                    print(f"  Bundle ID: {current_app.get('bundleId', 'N/A')}")
                    print(f"  Process ID: {current_app.get('pid', 'N/A')}")
        else:
            print("✗ WebDriverAgent is not running")
            print("\nPlease start WebDriverAgent on your iOS device:")
            print("  1. Open WebDriverAgent.xcodeproj in Xcode")
            print("  2. Select your device")
            print("  3. Run WebDriverAgentRunner (Product > Test or Cmd+U)")
            print(f"  4. For USB: Run port forwarding: iproxy 8100 8100")

        return True

    return False


def main():
    """Main entry point."""
    args = parse_args()

    # Handle --list-apps (no system check needed)
    if args.list_apps:
        print("Supported iOS apps:")
        print("\nNote: For iOS apps, Bundle IDs are configured in:")
        print("  phone_agent/config/apps_ios.py")
        print("\nCurrently configured apps:")
        for app in sorted(list_supported_apps()):
            print(f"  - {app}")
        print(
            "\nTo add iOS apps, find the Bundle ID and add to APP_PACKAGES_IOS dictionary."
        )
        return

    # Handle device commands (these may need partial system checks)
    if handle_device_commands(args):
        return

    # Run system requirements check before proceeding
    if not check_system_requirements(wda_url=args.wda_url):
        sys.exit(1)

    # Check model API connectivity and model availability
    # if not check_model_api(args.base_url, args.api_key, args.model):
    #     sys.exit(1)

    # Create configurations
    model_config = ModelConfig(
        base_url=args.base_url,
        model_name=args.model,
        api_key=args.api_key
    )

    agent_config = IOSAgentConfig(
        max_steps=args.max_steps,
        wda_url=args.wda_url,
        device_id=args.device_id,
        verbose=not args.quiet,
        lang=args.lang,
    )

    # Create iOS agent
    agent = IOSPhoneAgent(
        model_config=model_config,
        agent_config=agent_config,
    )

    # Print header
    print("=" * 50)
    print("Phone Agent iOS - AI-powered iOS automation")
    print("=" * 50)
    print(f"Model: {model_config.model_name}")
    print(f"Base URL: {model_config.base_url}")
    print(f"WDA URL: {args.wda_url}")
    print(f"Max Steps: {agent_config.max_steps}")
    print(f"Language: {agent_config.lang}")

    # Show device info
    devices = list_devices()
    if agent_config.device_id:
        print(f"Device: {agent_config.device_id}")
    elif devices:
        device = devices[0]
        print(f"Device: {device.device_name or device.device_id[:16]}")
        print(f"        {device.model}, iOS {device.ios_version}")

    print("=" * 50)

    # Run with provided task or enter interactive mode
    if args.task:
        print(f"\nTask: {args.task}\n")
        result = agent.run(args.task)
        print(f"\nResult: {result}")
    else:
        # Interactive mode
        print("\nEntering interactive mode. Type 'quit' to exit.\n")

        while True:
            try:
                task = input("Enter your task: ").strip()

                if task.lower() in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break

                if not task:
                    continue

                print()
                result = agent.run(task)
                print(f"\nResult: {result}\n")
                agent.reset()

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
