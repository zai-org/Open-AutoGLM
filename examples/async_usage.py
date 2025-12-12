"""Example usage of AsyncPhoneAgent."""

import asyncio

from phone_agent.async_agent import AsyncAgentConfig, AsyncPhoneAgent
from phone_agent.model import ModelConfig


async def main():
    """Example async agent usage."""
    # Configure model
    model_config = ModelConfig(
        base_url="http://localhost:8000/v1",
        model_name="autoglm-phone-9b",
    )

    # Configure agent
    agent_config = AsyncAgentConfig(
        max_steps=100,
        verbose=True,
        lang="cn",
    )

    # Create async agent
    agent = AsyncPhoneAgent(
        model_config=model_config,
        agent_config=agent_config,
    )

    # Run task
    print("Running async task...")
    result = await agent.run("打开微信，对文件传输助手发送消息：Hello from async!")
    print(f"Result: {result}")


async def step_by_step_example():
    """Example of step-by-step async execution."""
    model_config = ModelConfig(
        base_url="http://localhost:8000/v1",
        model_name="autoglm-phone-9b",
    )

    agent = AsyncPhoneAgent(model_config=model_config)

    # Execute steps manually
    task = "打开微信"
    result = await agent.step(task)
    print(f"Step 1: {result.action}")

    if not result.finished:
        result = await agent.step()
        print(f"Step 2: {result.action}")


if __name__ == "__main__":
    # Run main example
    asyncio.run(main())

    # Or run step-by-step example
    # asyncio.run(step_by_step_example())

