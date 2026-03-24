#!/usr/bin/env python3
"""
Phone Agent Trajectory Recording Examples / Phone Agent 轨迹记录示例

Demonstrates how to record agent operations including screenshots, actions, and context.
演示如何记录 agent 操作，包括截屏、动作和上下文。
"""

from phone_agent import PhoneAgent, TrajectoryRecorder, load_trajectory
from phone_agent.agent import AgentConfig
from phone_agent.config import get_messages
from phone_agent.model import ModelConfig


def example_trajectory_with_config(lang: str = "cn"):
    """Record trajectory using AgentConfig options / 使用 AgentConfig 配置记录轨迹"""
    msgs = get_messages(lang)

    # Configure model endpoint
    model_config = ModelConfig(
        base_url="http://localhost:8000/v1",
        model_name="autoglm-phone-9b",
        temperature=0.1,
    )

    # Configure Agent with trajectory recording enabled
    agent_config = AgentConfig(
        max_steps=50,
        verbose=True,
        lang=lang,
        # Trajectory recording options
        record_trajectory=True,
        trajectory_output_dir="trajectories",
        trajectory_save_screenshots=True,
        trajectory_save_context=True,
        trajectory_max_sessions=10,  # Keep last 10 sessions
    )

    # Create Agent
    agent = PhoneAgent(
        model_config=model_config,
        agent_config=agent_config,
    )

    # Execute task - trajectory will be recorded automatically
    print(f"{msgs['task']}: 打开小红书搜索美食攻略")
    result = agent.run("打开小红书搜索美食攻略")
    print(f"{msgs['task_result']}: {result}")

    # Get trajectory info
    if agent.trajectory_summary:
        print(f"\n📁 轨迹保存位置: {agent.trajectory_summary.record_dir}")
        print(f"📊 总步数: {agent.trajectory_summary.total_steps}")
        print(f"✅ 成功: {agent.trajectory_summary.success}")


def example_custom_trajectory_recorder(lang: str = "cn"):
    """Use custom TrajectoryRecorder instance / 使用自定义的 TrajectoryRecorder 实例"""
    msgs = get_messages(lang)

    # Create a custom trajectory recorder
    trajectory_recorder = TrajectoryRecorder(
        output_dir="my_custom_trajectories",
        save_screenshots=True,
        save_context=False,  # Don't save full context to save space
        max_trajectories=5,
    )

    # Create AgentConfig without trajectory options
    agent_config = AgentConfig(
        max_steps=50,
        verbose=True,
        lang=lang,
        # record_trajectory defaults to False since we're passing a custom recorder
    )

    # Pass the custom recorder to PhoneAgent
    agent = PhoneAgent(
        agent_config=agent_config,
        trajectory_recorder=trajectory_recorder,
    )

    # Execute task
    result = agent.run("打开微信")
    print(f"{msgs['task_result']}: {result}")

    # Access trajectory info
    print(f"\n轨迹目录: {agent.trajectory_dir}")


def example_load_and_inspect_trajectory():
    """Load and inspect a previously recorded trajectory / 加载并查看已记录的轨迹"""
    # Path to a recorded trajectory directory
    trajectory_dir = "trajectories/2024-01-15_14-30-22_打开小红书搜索美食攻略"

    try:
        # Load the trajectory
        summary, steps = load_trajectory(trajectory_dir)

        print("=" * 60)
        print("📊 轨迹摘要")
        print("=" * 60)
        print(f"任务: {summary.task}")
        print(f"开始时间: {summary.start_time}")
        print(f"结束时间: {summary.end_time}")
        print(f"总步数: {summary.total_steps}")
        print(f"成功: {summary.success}")
        print(f"最终消息: {summary.final_message}")
        print()

        print("=" * 60)
        print("📝 步骤详情")
        print("=" * 60)

        for step in steps:
            print(f"\n--- 步骤 {step.step_number} ---")
            print(f"时间: {step.timestamp}")
            print(f"当前应用: {step.current_app}")
            print(f"屏幕: {step.screen_width}x{step.screen_height}")
            print(f"截图: {step.screenshot_filename}")
            print(f"成功: {step.success}")
            print(f"思考: {step.thinking[:100]}...")
            print(f"动作: {step.action}")
            if step.message:
                print(f"消息: {step.message}")

    except FileNotFoundError:
        print(f"轨迹目录不存在: {trajectory_dir}")
        print("请先运行一个记录轨迹的示例。")


def example_manual_recording():
    """Manually use TrajectoryRecorder for custom recording / 手动使用 TrajectoryRecorder 进行自定义记录"""
    # Create recorder
    recorder = TrajectoryRecorder(
        output_dir="manual_trajectories",
        save_screenshots=True,
        save_context=True,
    )

    # Start a session
    record_dir = recorder.start_session(
        task="自定义记录任务",
        task_name="自定义任务",
    )
    print(f"记录开始: {record_dir}")

    # Record some steps manually
    # In real usage, you would get screenshot from your device
    recorder.record_step(
        screenshot_base64=None,  # Replace with actual base64 screenshot
        action={"_metadata": "do", "action": "Launch", "app": "设置"},
        thinking="需要先打开设置应用",
        current_app="桌面",
        screen_width=1080,
        screen_height=2340,
        context=None,
        message=None,
        success=True,
    )

    recorder.record_step(
        screenshot_base64=None,
        action={"_metadata": "do", "action": "Tap", "element": [500, 800]},
        thinking="点击蓝牙选项",
        current_app="设置",
        screen_width=1080,
        screen_height=2340,
        context=None,
        message=None,
        success=True,
    )

    # End the session
    summary = recorder.end_session(
        success=True,
        final_message="任务完成",
    )

    print(f"记录完成: {summary.record_dir}")
    print(f"总步数: {summary.total_steps}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phone Agent Trajectory Examples")
    parser.add_argument(
        "--lang",
        type=str,
        default="cn",
        choices=["cn", "en"],
        help="Language for UI messages",
    )
    args = parser.parse_args()

    msgs = get_messages(args.lang)

    print("Phone Agent 轨迹记录示例")
    print("=" * 60)
    print()
    print("📁 目录结构:")
    print("  trajectories/")
    print("    2024-01-15_14-30-22_任务描述/")
    print("      summary.json          # 轨迹摘要")
    print("      step_001.png          # 步骤1截图")
    print("      step_001.json         # 步骤1数据")
    print("      step_002.png          # 步骤2截图")
    print("      step_002.json         # 步骤2数据")
    print("      ...")
    print()
    print("📋 step_XXX.json 包含:")
    print("  - step_number: 步骤号")
    print("  - timestamp: 时间戳")
    print("  - screenshot_filename: 截图文件名")
    print("  - action: 执行的动作")
    print("  - thinking: 模型思考过程")
    print("  - current_app: 当前应用")
    print("  - screen_width/screen_height: 屏幕尺寸")
    print("  - context_snapshot: 上下文快照（可选）")
    print("  - message: 结果消息")
    print("  - success: 是否成功")
    print()

    # Uncomment examples to run them

    # print("\n" + "=" * 60)
    # print("示例 1: 通过配置启用轨迹记录")
    # print("=" * 60)
    # example_trajectory_with_config(args.lang)

    # print("\n" + "=" * 60)
    # print("示例 2: 使用自定义 TrajectoryRecorder")
    # print("=" * 60)
    # example_custom_trajectory_recorder(args.lang)

    # print("\n" + "=" * 60)
    # print("示例 3: 加载并查看已记录的轨迹")
    # print("=" * 60)
    # example_load_and_inspect_trajectory()

    # print("\n" + "=" * 60)
    # print("示例 4: 手动使用 TrajectoryRecorder")
    # print("=" * 60)
    # example_manual_recording()
