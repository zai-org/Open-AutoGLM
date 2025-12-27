#!/usr/bin/env python3
"""
AgentBay 与 Phone Agent 集成示例

演示如何：
1. 通过 AgentBay 创建移动设备会话
2. 获取 ADB 连接信息
3. 连接到远程 Android 设备
4. 使用 Phone Agent 执行自动化任务
"""

import os
import time
import subprocess

from agentbay import AgentBay, CreateSessionParams

from phone_agent import PhoneAgent
from phone_agent.adb import ADBConnection, get_current_app
from phone_agent.agent import AgentConfig
from phone_agent.model import ModelConfig


def launch_agentbay_task():
    """
    通过 AgentBay 创建远程设备会话，并使用 Phone Agent 执行任务。

    流程：
    1. 加载 ADB 公钥
    2. 创建 AgentBay 会话
    3. 获取 ADB 连接 URL
    4. 连接到远程设备
    5. 使用 Phone Agent 执行任务
    6. 清理资源
    """
    # Step 1: Load ADB public key
    adbkey_path = os.path.expanduser("~/.android/adbkey.pub")
    with open(adbkey_path, "r") as f:
        adbkey_pub = f.read().strip()
    print(f"ADB key loaded (first 50 chars): {adbkey_pub[:50]}...")

    # Initialize AgentBay client
    client = AgentBay(api_key=os.environ.get("AGENTBAY_API_KEY"))
    session = None
    conn = None
    address = None

    try:
        # Step 2: Create mobile session
        print("\n📱 Creating mobile session...")
        params = CreateSessionParams(image_id="mobile_latest")
        result = client.create(params)
        session = result.session
        print(f"✅ Session created: {session.session_id}")

        # Step 3: Get ADB connection URL
        print("\n🔗 Getting ADB connection URL...")
        adb_result = session.mobile.get_adb_url(adbkey_pub=adbkey_pub)

        if not adb_result.success:
            print(f"❌ Failed: {adb_result.error_message}")
            return

        print(f"✅ Resource URL: {session.resource_url}")
        print(f"✅ ADB URL: {adb_result.data}")
        print(f"✅ Request ID: {adb_result.request_id}")

        # Wait for device to be ready
        print("\n⏳ Waiting for device to be ready...")
        time.sleep(20)

        # Step 4: Parse the ADB connect command
        adb_url = adb_result.data  # "adb connect 47.99.76.99:54321"
        # Extract just the address part for later use
        address = adb_url.replace("adb connect ", "")

        # Step 5: Connect via ADB
        print(f"\n🔌 Connecting to device...")
        print(f"Command: {adb_url}")

        # Create connection manager
        conn = ADBConnection()

        # Connect to device
        success, message = conn.connect(address)

        if not success:
            print(f"❌ Failed: {message}")
            return

        print(f"✅ Connected to device: {message}")

        # Get device info
        device_info = conn.get_device_info(address)
        if device_info is None:
            # If device info is None, try to get the first one in device list
            devices = conn.list_devices()
            if devices:
                device_info = devices[0]
            else:
                print(f"❌ No device found")
                return

        device_id = device_info.device_id
        print(f"✅ Device ID: {device_id}")
        print(f"✅ Device status: {device_info.status}")

        # Enable ADB keyboard IME
        print("\n⌨️  Enabling ADB keyboard IME...")
        try:
            adb_prefix = ["adb", "-s", device_id] if device_id else ["adb"]
            result = subprocess.run(
                adb_prefix + ["shell", "ime", "enable", "com.android.adbkeyboard/.AdbIME"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                print("✅ ADB keyboard IME enabled")
            else:
                print(f"⚠️  Warning: Failed to enable ADB keyboard IME: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Warning: Error enabling ADB keyboard IME: {e}")

        # Find current app
        current_app = get_current_app(device_id)
        print(f"✅ Current app: {current_app}")

        # Step 6: Configure and run Phone Agent
        print("\n🤖 Configuring Phone Agent...")
        model_config = ModelConfig(
            base_url=os.environ.get("MODEL_BASE_URL", "http://localhost:8000/v1"),
            model_name=os.environ.get("MODEL_NAME", "GLM-4.1V-9B-Thinking"),
            temperature=0.1,
            api_key=os.environ.get("MODEL_API_KEY", "EMPTY"),
        )

        agent_config = AgentConfig(
            device_id=device_id,  # Use the connected device
            max_steps=50,
            verbose=True,
        )

        agent = PhoneAgent(
            model_config=model_config,
            agent_config=agent_config,
        )

        # Step 7: Run task
        print("\n🚀 Running task...")
        task = "打开设置帮我查一下当前的手机存储用量"
        print(f"Task: {task}")

        result = agent.run(task)
        print(f"\n✅ Task completed!")
        print(f"Result: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Step 8: Cleanup
        print("\n🧹 Cleaning up...")
        if conn and address:
            try:
                conn.disconnect(address)
                print("✅ Disconnected from device")
            except Exception as e:
                print(f"⚠️  Error disconnecting: {e}")

        if session:
            try:
                client.delete(session)
                print("✅ Session deleted")
            except Exception as e:
                print(f"⚠️  Error deleting session: {e}")


if __name__ == "__main__":
    launch_agentbay_task()
