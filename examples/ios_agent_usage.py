#!/usr/bin/env python3
"""
iOS Agent 使用示例

演示如何使用 IOSPhoneAgent 类来自动化 iOS 设备操作。

前置要求:
1. 安装 libimobiledevice: brew install libimobiledevice
2. 在 iOS 设备上运行 WebDriverAgent
3. 设置端口转发 (如果通过 USB): iproxy 8100 8100
4. 模型服务运行在 http://localhost:8000/v1
"""

from phone_agent import IOSPhoneAgent
from phone_agent.agent_ios import IOSAgentConfig
from phone_agent.model import ModelConfig


def main():
    print("=" * 60)
    print("iOS Phone Agent 使用示例")
    print("=" * 60)

    # 配置模型
    model_config = ModelConfig(
        base_url="http://localhost:8000/v1",
        model_name="autoglm-phone-9b",
        temperature=0.0,
    )

    # 配置 iOS Agent
    agent_config = IOSAgentConfig(
        max_steps=50,
        wda_url="http://localhost:8100",  # WebDriverAgent URL
        lang="cn",  # 使用中文提示
        verbose=True,  # 显示详细日志
    )

    # 创建 iOS Agent
    agent = IOSPhoneAgent(
        model_config=model_config,
        agent_config=agent_config,
    )

    print("\n配置信息:")
    print(f"  模型服务: {model_config.base_url}")
    print(f"  模型名称: {model_config.model_name}")
    print(f"  WDA URL: {agent_config.wda_url}")
    print(f"  最大步数: {agent_config.max_steps}")
    print(f"  语言: {agent_config.lang}")
    print("=" * 60)

    # 示例任务列表
    tasks = [
        "打开设置",
        # "打开 Safari 并搜索 Apple",
        # "打开相机应用",
        # "返回主屏幕",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"\n\n{'=' * 60}")
        print(f"任务 {i}/{len(tasks)}: {task}")
        print("=" * 60)

        try:
            result = agent.run(task)
            print(f"\n✅ 任务完成: {result}")

            # 重置 Agent 状态以执行下一个任务
            agent.reset()

        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断")
            break
        except Exception as e:
            print(f"\n❌ 任务失败: {e}")
            import traceback

            traceback.print_exc()
            break

    print("\n" + "=" * 60)
    print("所有任务执行完成!")
    print("=" * 60)


def example_with_callbacks():
    """演示如何使用回调函数"""

    def confirmation_callback(message: str) -> bool:
        """敏感操作确认回调"""
        print(f"\n⚠️  敏感操作: {message}")
        response = input("是否继续? (y/n): ")
        return response.lower() == "y"

    def takeover_callback(message: str) -> None:
        """人工接管回调"""
        print(f"\n🤚 需要人工介入: {message}")
        input("完成操作后按回车继续...")

    # 配置
    model_config = ModelConfig(base_url="http://localhost:8000/v1")
    agent_config = IOSAgentConfig(wda_url="http://localhost:8100")

    # 创建带回调的 Agent
    agent = IOSPhoneAgent(
        model_config=model_config,
        agent_config=agent_config,
        confirmation_callback=confirmation_callback,
        takeover_callback=takeover_callback,
    )

    # 执行任务
    result = agent.run("打开设置并查看电池状态")
    print(f"结果: {result}")


def example_step_by_step():
    """演示单步执行模式"""
    model_config = ModelConfig(base_url="http://localhost:8000/v1")
    agent_config = IOSAgentConfig(wda_url="http://localhost:8100", verbose=True)

    agent = IOSPhoneAgent(model_config, agent_config)

    # 执行第一步
    print("\n执行第一步...")
    result = agent.step(task="打开 Safari")

    print(f"\n步骤结果:")
    print(f"  成功: {result.success}")
    print(f"  完成: {result.finished}")
    print(f"  思考: {result.thinking[:100]}...")
    print(f"  动作: {result.action}")
    print(f"  消息: {result.message}")

    # 继续执行后续步骤
    while not result.finished and agent.step_count < 10:
        print(f"\n执行第 {agent.step_count + 1} 步...")
        result = agent.step()

        if result.finished:
            print(f"\n✅ 任务完成: {result.message}")
            break

    # 查看上下文
    print(f"\n对话上下文长度: {len(agent.context)}")
    print(f"总步数: {agent.step_count}")


def example_wifi_connection():
    """演示 WiFi 连接"""
    # 使用 WiFi 连接 (设备 IP 地址)
    model_config = ModelConfig(base_url="http://localhost:8000/v1")
    agent_config = IOSAgentConfig(
        wda_url="http://192.168.1.100:8100",  # 替换为实际设备 IP
        lang="cn",
    )

    agent = IOSPhoneAgent(model_config, agent_config)

    result = agent.run("打开相机")
    print(f"结果: {result}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1]

        if mode == "callbacks":
            print("运行回调示例...")
            example_with_callbacks()
        elif mode == "step":
            print("运行单步执行示例...")
            example_step_by_step()
        elif mode == "wifi":
            print("运行 WiFi 连接示例...")
            example_wifi_connection()
        else:
            print(f"未知模式: {mode}")
            print("可用模式: callbacks, step, wifi")
    else:
        # 默认运行主示例
        main()
