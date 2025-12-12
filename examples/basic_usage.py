#!/usr/bin/env python3
"""
Phone Agent Usage Examples / Phone Agent 使用示例

Demonstrates how to use Phone Agent for phone automation tasks via Python API.
演示如何通过 Python API 使用 Phone Agent 进行手机自动化任务。
"""

from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.config import get_messages
from phone_agent.model import ModelConfig


def example_basic_task(lang: str = "cn"):
    """Basic task example / 基础任务示例"""
    msgs = get_messages(lang)

    # Configure model endpoint
    model_config = ModelConfig(
        base_url="http://localhost:8000/v1",
        model_name="autoglm-phone-9b",
        temperature=0.1,
    )

    # Configure Agent behavior
    agent_config = AgentConfig(
        max_steps=50,
        verbose=True,
        lang=lang,
    )

    # Create Agent
    agent = PhoneAgent(
        model_config=model_config,
        agent_config=agent_config,
    )

    # Execute task
    result = agent.run("打开小红书搜索美食攻略")
    print(f"{msgs['task_result']}: {result}")


def example_with_callbacks(lang: str = "cn"):
    """Task example with callbacks / 带回调的任务示例"""
    msgs = get_messages(lang)

    def my_confirmation(message: str) -> bool:
        """Sensitive operation confirmation callback / 敏感操作确认回调"""
        print(f"\n[{msgs['confirmation_required']}] {message}")
        response = input(f"{msgs['continue_prompt']}: ")
        return response.lower() in ("yes", "y", "是")

    def my_takeover(message: str) -> None:
        """Manual takeover callback / 人工接管回调"""
        print(f"\n[{msgs['manual_operation_required']}] {message}")
        print(msgs["manual_operation_hint"])
        input(f"{msgs['press_enter_when_done']}: ")

    # Create Agent with custom callbacks
    agent_config = AgentConfig(lang=lang)
    agent = PhoneAgent(
        agent_config=agent_config,
        confirmation_callback=my_confirmation,
        takeover_callback=my_takeover,
    )

    # Execute task that may require confirmation
    result = agent.run("打开淘宝搜索无线耳机并加入购物车")
    print(f"{msgs['task_result']}: {result}")


def example_step_by_step(lang: str = "cn"):
    """Step-by-step execution example (for debugging) / 单步执行示例（用于调试）"""
    msgs = get_messages(lang)

    agent_config = AgentConfig(lang=lang)
    agent = PhoneAgent(agent_config=agent_config)

    # Initialize task
    result = agent.step("打开美团搜索附近的火锅店")
    print(f"{msgs['step']} 1: {result.action}")

    # Continue if not finished
    while not result.finished and agent.step_count < 10:
        result = agent.step()
        print(f"{msgs['step']} {agent.step_count}: {result.action}")
        print(f"  {msgs['thinking']}: {result.thinking[:100]}...")

    print(f"\n{msgs['final_result']}: {result.message}")


def example_multiple_tasks(lang: str = "cn"):
    """Batch task example / 批量任务示例"""
    msgs = get_messages(lang)

    agent_config = AgentConfig(lang=lang)
    agent = PhoneAgent(agent_config=agent_config)

    tasks = [
        "打开高德地图查看实时路况",
        "打开大众点评搜索附近的咖啡店",
        "打开bilibili搜索Python教程",
    ]

    for task in tasks:
        print(f"\n{'=' * 50}")
        print(f"{msgs['task']}: {task}")
        print("=" * 50)

        result = agent.run(task)
        print(f"{msgs['result']}: {result}")

        # Reset Agent state
        agent.reset()


def example_remote_device(lang: str = "cn"):
    """Remote device example / 远程设备示例"""
    from phone_agent.adb import ADBConnection

    msgs = get_messages(lang)

    # Create connection manager
    conn = ADBConnection()

    # Connect to remote device
    success, message = conn.connect("192.168.1.100:5555")
    if not success:
        print(f"{msgs['connection_failed']}: {message}")
        return

    print(f"{msgs['connection_successful']}: {message}")

    # Create Agent with device specified
    agent_config = AgentConfig(
        device_id="192.168.1.100:5555",
        verbose=True,
        lang=lang,
    )

    agent = PhoneAgent(agent_config=agent_config)

    # Execute task
    result = agent.run("打开微信查看消息")
    print(f"{msgs['task_result']}: {result}")

    # Disconnect
    conn.disconnect("192.168.1.100:5555")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phone Agent Usage Examples")
    parser.add_argument(
        "--lang",
        type=str,
        default="cn",
        choices=["cn", "en"],
        help="Language for UI messages (cn=Chinese, en=English)",
    )
    args = parser.parse_args()

    msgs = get_messages(args.lang)

    print("Phone Agent Usage Examples")
    print("=" * 50)

    # Run basic example
    print(f"\n1. Basic Task Example")
    print("-" * 30)
    example_basic_task(args.lang)

    # Uncomment to run other examples
    # print(f"\n2. Task Example with Callbacks")
    # print("-" * 30)
    # example_with_callbacks(args.lang)

    # print(f"\n3. Step-by-step Example")
    # print("-" * 30)
    # example_step_by_step(args.lang)

    # print(f"\n4. Batch Task Example")
    # print("-" * 30)
    # example_multiple_tasks(args.lang)

    # print(f"\n5. Remote Device Example")
    # print("-" * 30)
    # example_remote_device(args.lang)
