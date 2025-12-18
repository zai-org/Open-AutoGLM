#!/usr/bin/env python3
"""AutoGLM 客户端切换示例"""

from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig


def main():
    """客户端切换演示"""
    # 创建 agent
    config = ModelConfig(base_url="http://localhost:8080/v1")
    agent = PhoneAgent(model_config=config)
    
    print(f"默认: {type(agent.model_client).__name__}")
    
    # 切换客户端
    agent.switch_client("llama")
    print(f"llama: {type(agent.model_client).__name__}")
    
    agent.switch_client("openai")
    print(f"openai: {type(agent.model_client).__name__}")
    
    agent.switch_client("auto")
    print(f"auto: {type(agent.model_client).__name__}")


if __name__ == "__main__":
    main()
