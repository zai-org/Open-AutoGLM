"""Example demonstrating Phone Agent optimization features."""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.model import ModelConfig
from phone_agent.utils import (
    ConfigLoader,
    ConfigValidator,
    InputValidator,
    LoggerSetup,
    SensitiveDataFilter,
    get_performance_monitor,
)


def main():
    """Run optimization examples."""
    
    # 1. Setup logging
    print("=" * 60)
    print("📝 示例 1: 日志设置")
    print("=" * 60)
    
    logger = LoggerSetup.setup_logging(
        "optimization_demo",
        verbose=True,
        log_file="logs/demo.log"
    )
    logger.info("日志系统初始化完成")
    
    # 2. Configuration loading
    print("\n" + "=" * 60)
    print("⚙️  示例 2: 配置加载")
    print("=" * 60)
    
    try:
        # 从环境变量加载配置
        config = ConfigLoader.from_env()
        logger.info(f"从环境变量加载配置: {config}")
        
        # 验证配置
        ConfigValidator.validate_agent_config(config)
        logger.info("✅ 配置验证成功")
    except Exception as e:
        logger.error(f"配置错误: {e}")
    
    # 3. Input validation
    print("\n" + "=" * 60)
    print("🔒 示例 3: 输入验证")
    print("=" * 60)
    
    test_inputs = [
        ("打开微信", True),
        ("SELECT * FROM users", False),  # SQL 注入
        ("a" * 2000, False),  # 过长
        ("<script>alert('xss')</script>", False),  # 脚本注入
    ]
    
    for text, expected in test_inputs:
        valid = InputValidator.validate_text_input(text[:50] + "..." if len(text) > 50 else text)
        status = "✅" if valid == expected else "⚠️"
        logger.info(f"{status} 输入验证: {text[:30]}... => {valid}")
    
    # 4. Sensitive data filtering
    print("\n" + "=" * 60)
    print("🔐 示例 4: 敏感数据过滤")
    print("=" * 60)
    
    sensitive_texts = [
        "我的手机号是 13812345678",
        "Email: test@example.com",
        "API key: sk-1234567890abcdef",
        "password=mypassword123",
    ]
    
    for text in sensitive_texts:
        filtered = SensitiveDataFilter.filter_log_message(text)
        logger.info(f"原始: {text}")
        logger.info(f"过滤: {filtered}")
    
    # 5. Performance monitoring
    print("\n" + "=" * 60)
    print("⏱️  示例 5: 性能监控")
    print("=" * 60)
    
    monitor = get_performance_monitor()
    
    # 模拟操作
    import time
    
    operations = ["screenshot", "model_inference", "adb_tap", "text_input"]
    
    for op in operations:
        monitor.start_timer(op)
        # 模拟操作耗时
        time.sleep(0.1 + (hash(op) % 10) * 0.01)
        duration = monitor.end_timer(op)
        logger.info(f"{op}: {duration:.3f}s")
    
    # 打印性能报告
    print("\n" + "-" * 60)
    monitor.print_report()
    
    # 6. Agent configuration
    print("=" * 60)
    print("🤖 示例 6: Agent 配置与初始化")
    print("=" * 60)
    
    try:
        model_config = ModelConfig(
            base_url="http://localhost:8000/v1",
            api_key="demo-key",
            model_name="autoglm-phone-9b",
            max_tokens=2000,
            temperature=0.0,
        )
        
        agent_config = AgentConfig(
            max_steps=50,
            device_id="emulator-5554",
            lang="cn",
            verbose=True,
        )
        
        logger.info("✅ Model 配置验证成功")
        logger.info("✅ Agent 配置验证成功")
        
        # 这里可以创建 Agent（如果设备可用）
        # agent = PhoneAgent(model_config, agent_config)
        
    except ValueError as e:
        logger.error(f"配置错误: {e}")
    
    # 7. Summary
    print("\n" + "=" * 60)
    print("📊 优化特性总结")
    print("=" * 60)
    
    features = [
        "✨ 日志记录和调试支持",
        "✨ 灵活的配置管理",
        "✨ 输入验证和安全检查",
        "✨ 敏感数据过滤",
        "✨ 性能监控和指标追踪",
        "✨ 类型注解和错误处理",
        "✨ 可配置的缓存机制",
        "✨ 速率限制和资源控制",
    ]
    
    for feature in features:
        logger.info(feature)
    
    print("\n✅ 所有示例完成!")
    print("📖 更多详情请查看: OPTIMIZATION_GUIDE.md\n")


if __name__ == "__main__":
    main()
