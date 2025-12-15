"""
Best practices guide for using Open-AutoGLM.

This document outlines recommended patterns and practices for optimal
performance and maintainability.
"""

# 1. 配置管理最佳实践
# ========================

# ✅ 推荐：使用环境变量管理敏感信息
# export PHONE_AGENT_API_KEY="your_key_here"
# export PHONE_AGENT_BASE_URL="http://localhost:8000/v1"
# python main.py

# ❌ 不推荐：硬编码 API 密钥
# config = ModelConfig(api_key="your_key_here")  # 危险！


# 2. 错误处理最佳实践
# ========================

from typing import Optional
import logging
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig

logger = logging.getLogger(__name__)


def run_task_safely(task: str, max_retries: int = 3) -> Optional[str]:
    """
    Run a task with proper error handling and retries.

    Args:
        task: The task to run.
        max_retries: Maximum number of retries.

    Returns:
        Task result or None if failed.
    """
    for attempt in range(max_retries):
        try:
            config = ModelConfig()
            agent = PhoneAgent(model_config=config)
            result = agent.run(task)
            logger.info(f"Task completed successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                import time

                time.sleep(2 ** attempt)  # 指数退避
            else:
                logger.error("All attempts failed")
                return None


# 3. 日志配置最佳实践
# ========================


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging with recommended configuration.

    Args:
        verbose: Enable verbose (DEBUG) logging.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # 控制台输出
            logging.FileHandler("phone_agent.log"),  # 文件输出
        ],
    )

    # 降低第三方库的日志级别
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# 4. 资源管理最佳实践
# ========================


def run_with_cleanup(task: str) -> None:
    """
    Run task with proper resource cleanup.

    Args:
        task: The task to run.
    """
    config = ModelConfig()
    agent = PhoneAgent(model_config=config)

    try:
        result = agent.run(task)
        logger.info(f"Result: {result}")
    finally:
        # 清理资源
        agent.reset()
        logger.info("Resources cleaned up")


# 5. 步进执行最佳实践（用于调试）
# ========================


def debug_task_step_by_step(task: str) -> None:
    """
    Execute task step by step for debugging.

    Useful for understanding agent behavior and debugging issues.

    Args:
        task: The task to debug.
    """
    config = ModelConfig()
    agent = PhoneAgent(model_config=config, verbose=True)

    # 执行第一步
    result = agent.step(task)
    print(f"Step 1: {result.action}")
    print(f"Success: {result.success}")

    # 继续执行后续步骤
    step = 2
    while not result.finished and step < agent.agent_config.max_steps:
        result = agent.step()
        print(f"\nStep {step}: {result.action}")
        print(f"Success: {result.success}")
        step += 1

    print(f"\nTotal steps: {agent.step_count}")


# 6. 性能监控最佳实践
# ========================


def run_with_metrics(task: str) -> None:
    """
    Run task while collecting performance metrics.

    Args:
        task: The task to run.
    """
    from phone_agent.metrics import SessionMetrics, MetricsCollector

    metrics = SessionMetrics()
    metrics.start_time = __import__("time").time()

    config = ModelConfig()
    agent = PhoneAgent(model_config=config)

    try:
        with MetricsCollector() as timer:
            result = agent.run(task)
        logger.info(f"Task result: {result}")
    finally:
        metrics.finalize()
        metrics.print_summary()


# 7. 多设备支持最佳实践
# ========================


def run_on_device(task: str, device_id: str) -> Optional[str]:
    """
    Run task on specific device.

    Args:
        task: The task to run.
        device_id: The ADB device ID.

    Returns:
        Task result or None if failed.
    """
    from phone_agent.agent import AgentConfig

    config = ModelConfig()
    agent_config = AgentConfig(device_id=device_id)
    agent = PhoneAgent(model_config=config, agent_config=agent_config)

    return agent.run(task)


# 8. 批量任务处理最佳实践
# ========================


def run_batch_tasks(tasks: list[str]) -> dict[str, Optional[str]]:
    """
    Run multiple tasks sequentially.

    Args:
        tasks: List of tasks to run.

    Returns:
        Dictionary mapping task to result.
    """
    config = ModelConfig()
    results = {}

    for i, task in enumerate(tasks):
        try:
            logger.info(f"Running task {i + 1}/{len(tasks)}: {task}")
            agent = PhoneAgent(model_config=config)
            result = agent.run(task)
            results[task] = result
            logger.info(f"Task completed: {result}")
        except Exception as e:
            logger.error(f"Task failed: {e}")
            results[task] = None
        finally:
            # 任务间延迟
            import time

            time.sleep(1)

    return results


# 9. 自定义回调最佳实践
# ========================


def custom_confirmation_callback(message: str) -> bool:
    """
    Custom confirmation callback for sensitive operations.

    Args:
        message: Confirmation message.

    Returns:
        True to confirm, False to cancel.
    """
    logger.warning(f"Sensitive operation: {message}")
    # 实现自定义确认逻辑
    # 例如：调用 API、发送通知等
    return True


def custom_takeover_callback(message: str) -> None:
    """
    Custom takeover callback for user intervention.

    Args:
        message: Takeover reason message.
    """
    logger.error(f"Manual intervention required: {message}")
    # 实现自定义接管逻辑
    # 例如：发送警报、记录日志等


def run_with_callbacks(task: str) -> None:
    """
    Run task with custom callbacks.

    Args:
        task: The task to run.
    """
    config = ModelConfig()
    agent = PhoneAgent(
        model_config=config,
        confirmation_callback=custom_confirmation_callback,
        takeover_callback=custom_takeover_callback,
    )
    agent.run(task)


# 10. 配置验证最佳实践
# ========================


def validate_setup() -> bool:
    """
    Validate the entire setup before running tasks.

    Returns:
        True if setup is valid, False otherwise.
    """
    from phone_agent.config.validator import (
        ConfigValidator,
        SecureConfig,
    )

    logger.info("Validating setup...")

    try:
        # 验证 ADB
        ConfigValidator.validate_adb_config()
        logger.info("✓ ADB is properly configured")

        # 验证模型配置
        config = SecureConfig.load_from_env()
        ConfigValidator.validate_model_config(config)
        logger.info("✓ Model configuration is valid")

        # 验证代理配置
        ConfigValidator.validate_agent_config(config)
        logger.info("✓ Agent configuration is valid")

        return True
    except Exception as e:
        logger.error(f"Setup validation failed: {e}")
        return False


if __name__ == "__main__":
    # 示例：完整的最佳实践工作流
    setup_logging(verbose=True)

    if validate_setup():
        # 运行任务
        run_task_safely("打开微信")
        
        # 运行带指标的任务
        # run_with_metrics("打开微信发送消息")
    else:
        logger.error("Setup validation failed. Please check your configuration.")
