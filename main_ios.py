#!/usr/bin/env python3
"""
Phone Agent CLI for iOS - AI-powered iPhone automation via WebDriverAgent.

Usage:
    python main_ios.py [OPTIONS]

Environment Variables:
    PHONE_AGENT_BASE_URL: Model API base URL (default: http://localhost:8000/v1)
    PHONE_AGENT_MODEL: Model name (default: autoglm-phone-9b)
    PHONE_AGENT_API_KEY: API key for model authentication (default: EMPTY)
    PHONE_AGENT_MAX_STEPS: Maximum steps per task (default: 100)
    PHONE_AGENT_WDA_URL: WebDriverAgent URL (default: http://localhost:8100)

Prerequisites:
    1. WebDriverAgent must be running on the iOS device
    2. Start WDA with: xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'id=YOUR_DEVICE_ID' test
    3. Find WDA URL in logs: ServerURLHere->http://[IP]:8100<-ServerURLHere
"""

import argparse
import os
import sys

import requests
from openai import OpenAI

# Import iOS-specific modules
from phone_agent.wda import get_client, get_screenshot, get_current_app, set_wda_url
from phone_agent.wda.device import IOS_APP_BUNDLES
from phone_agent.model import ModelConfig


def check_wda_connection(wda_url: str) -> bool:
    """
    Check if WebDriverAgent is running and accessible.
    
    Args:
        wda_url: WDA server URL
        
    Returns:
        True if WDA is accessible, False otherwise
    """
    print("🔍 Checking iOS device connection...")
    print("-" * 50)
    
    print(f"1. Checking WDA connectivity ({wda_url})...", end=" ")
    
    try:
        resp = requests.get(f"{wda_url}/status", timeout=5)
        if resp.status_code == 200:
            print("✅ OK")
        else:
            print(f"❌ FAILED (status: {resp.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ FAILED")
        print("   Error: Cannot connect to WebDriverAgent.")
        print("   Solution:")
        print("     1. Make sure WDA is running on your iOS device")
        print("     2. Start WDA with:")
        print("        xcodebuild -project WebDriverAgent.xcodeproj \\")
        print("                   -scheme WebDriverAgentRunner \\")
        print("                   -destination 'id=YOUR_DEVICE_ID' test")
        print("     3. Find the URL in logs: ServerURLHere->http://[IP]:8100<-ServerURLHere")
        return False
    except Exception as e:
        print(f"❌ FAILED ({e})")
        return False
    
    # Check screenshot capability
    print("2. Checking screenshot capability...", end=" ")
    try:
        screenshot = get_screenshot(wda_url)
        if screenshot.base64_data and not screenshot.is_sensitive:
            print(f"✅ OK ({screenshot.width}x{screenshot.height})")
        else:
            print("⚠️  Warning: Screenshot may be limited")
    except Exception as e:
        print(f"⚠️  Warning: {e}")
    
    # Check current app
    print("3. Checking active app detection...", end=" ")
    try:
        current_app = get_current_app(wda_url)
        print(f"✅ OK (Current: {current_app})")
    except Exception as e:
        print(f"⚠️  Warning: {e}")
    
    print("-" * 50)
    print("✅ iOS device connection OK!\n")
    return True


def check_model_api(base_url: str, model_name: str, api_key: str = "EMPTY") -> bool:
    """
    Check if the model API is accessible.
    
    Args:
        base_url: The API base URL
        model_name: The model name to check
        api_key: The API key for authentication
        
    Returns:
        True if API is accessible, False otherwise
    """
    print("🔍 Checking model API...")
    print("-" * 50)
    
    print(f"1. Checking API connectivity ({base_url})...", end=" ")
    
    try:
        client = OpenAI(base_url=base_url, api_key=api_key, timeout=30.0)
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10,
        )
        if response.choices:
            print("✅ OK")
        else:
            print("❌ FAILED (no response)")
            return False
    except Exception as e:
        print(f"❌ FAILED")
        print(f"   Error: {e}")
        return False
    
    print("-" * 50)
    print("✅ Model API checks passed!\n")
    return True


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Phone Agent for iOS - AI-powered iPhone automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run with WDA on localhost
    python main_ios.py --wda-url http://localhost:8100 "打开小红书搜索美食"

    # Run with WDA on device IP
    python main_ios.py --wda-url http://192.168.0.105:8100 "打开闲鱼搜索二手iPhone"

    # Use third-party model service
    python main_ios.py --wda-url http://192.168.0.105:8100 \\
        --base-url https://open.bigmodel.cn/api/paas/v4 \\
        --model autoglm-phone \\
        --apikey YOUR_API_KEY \\
        "打开淘宝搜索无线耳机"

    # List supported iOS apps
    python main_ios.py --list-apps

    # Check WDA connection only
    python main_ios.py --wda-url http://192.168.0.105:8100 --check-only
        """,
    )
    
    # iOS/WDA options
    parser.add_argument(
        "--wda-url",
        type=str,
        default=os.getenv("PHONE_AGENT_WDA_URL", "http://localhost:8100"),
        help="WebDriverAgent URL (default: http://localhost:8100)",
    )
    
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check WDA connection and exit",
    )

    # Model options
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1"),
        help="Model API base URL",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b"),
        help="Model name",
    )

    parser.add_argument(
        "--apikey",
        type=str,
        default=os.getenv("PHONE_AGENT_API_KEY", "EMPTY"),
        help="API key for model authentication",
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=int(os.getenv("PHONE_AGENT_MAX_STEPS", "100")),
        help="Maximum steps per task",
    )

    # Other options
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress verbose output"
    )

    parser.add_argument(
        "--list-apps", action="store_true", help="List supported iOS apps and exit"
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


def main():
    """Main entry point for iOS agent."""
    args = parse_args()
    
    # Handle --list-apps
    if args.list_apps:
        print("Supported iOS apps:")
        print("-" * 40)
        # Group by first letter for better display
        apps = sorted(set(IOS_APP_BUNDLES.keys()))
        for app in apps:
            print(f"  - {app}")
        print(f"\nTotal: {len(apps)} apps")
        return
    
    # Set WDA URL globally
    set_wda_url(args.wda_url)
    
    # Check WDA connection
    if not check_wda_connection(args.wda_url):
        sys.exit(1)
    
    # Handle --check-only
    if args.check_only:
        print("✅ All checks passed. WDA is ready for automation.")
        return
    
    # Check model API
    if not check_model_api(args.base_url, args.model, args.apikey):
        sys.exit(1)
    
    # Import iOS-specific agent
    from phone_agent.agent_ios import PhoneAgentIOS, AgentConfig
    
    # Create configurations
    model_config = ModelConfig(
        base_url=args.base_url,
        model_name=args.model,
        api_key=args.apikey,
    )

    agent_config = AgentConfig(
        max_steps=args.max_steps,
        device_id=args.wda_url,  # Use WDA URL as device_id for iOS
        verbose=not args.quiet,
        lang=args.lang,
    )

    # Create iOS agent
    agent = PhoneAgentIOS(
        model_config=model_config,
        agent_config=agent_config,
    )

    # Print header
    print("=" * 50)
    print("Phone Agent for iOS - AI-powered iPhone automation")
    print("=" * 50)
    print(f"Model: {model_config.model_name}")
    print(f"Base URL: {model_config.base_url}")
    print(f"WDA URL: {args.wda_url}")
    print(f"Max Steps: {agent_config.max_steps}")
    print(f"Language: {agent_config.lang}")
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
