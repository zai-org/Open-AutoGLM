#!/usr/bin/env python3
"""
Batch Task Execution Example / 批量任务执行示例

Demonstrates how to use Phone Agent to execute multiple tasks in batch, including:
- Task list definition
- Sequential execution
- Result tracking and reporting
- Error handling and retry mechanism
- History management for batch tasks
演示如何使用 Phone Agent 批量执行多个任务，包括：
- 任务列表定义
- 顺序执行
- 结果跟踪和报告
- 错误处理和重试机制
- 批量任务的历史管理
"""

import os
import sys
import time
from typing import Dict, List, Tuple

# Add the project root to the Python path
# 将项目根目录添加到 Python 路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.config import get_messages
from phone_agent.model import ModelConfig


class BatchTaskResult:
    """Batch task result structure / 批量任务结果结构"""
    
    def __init__(self, task: str):
        self.task = task
        self.success = False
        self.result = ""
        self.start_time = 0
        self.end_time = 0
        self.duration = 0
        self.error = None
        self.retry_count = 0
    
    def start(self):
        """Mark task as started / 标记任务开始"""
        self.start_time = time.time()
    
    def complete(self, result: str):
        """Mark task as completed / 标记任务完成"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = True
        self.result = result
    
    def fail(self, error: Exception):
        """Mark task as failed / 标记任务失败"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = False
        self.error = str(error)
    
    def increment_retry(self):
        """Increment retry count / 增加重试计数"""
        self.retry_count += 1
    
    def __str__(self):
        status = "✅" if self.success else "❌"
        duration = f"{self.duration:.2f}s"
        if self.success:
            return f"{status} {self.task} ({duration})"
        else:
            return f"{status} {self.task} ({duration}) - Error: {self.error}"


def example_batch_task_execution(
    lang: str = "cn",
    max_retries: int = 2,
    use_history: bool = True
):
    """Batch task execution example / 批量任务执行示例"""
    print("=" * 60)
    print("Phone Agent - Batch Task Execution Example")
    print("=" * 60)
    
    # Configure model endpoint
    model_config = ModelConfig(
        base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key="590af9e737b04858bc891cea879913b1.jGxAfNjDG8Tsl8PB",
        model_name="autoglm-phone",
        temperature=0.1,
    )

    # Configure Agent behavior
    agent_config = AgentConfig(
        max_steps=50,
        verbose=True,
        lang=lang,
    )
    
    # Create Agent with history support
    agent = PhoneAgent(
        model_config=model_config,
        agent_config=agent_config,
    )
    
    # Define batch tasks
    tasks = [
        "打开小红书搜索美食攻略",
        "打开高德地图查看公交",
        "打开美团搜索附近的咖啡店",
        "打开bilibili搜索Python教程",
        "打开微信，查看最近一条消息",
    ]
    
    # Initialize results storage
    results: List[BatchTaskResult] = []
    
    # Start batch execution
    print(f"\n📋 任务列表 ({len(tasks)} tasks):")
    for i, task in enumerate(tasks, 1):
        print(f"   {i}. {task}")
    
    print(f"\n🚀 开始批量执行...")
    total_start_time = time.time()
    
    # Execute tasks sequentially
    for i, task in enumerate(tasks, 1):
        result = BatchTaskResult(task)
        results.append(result)
        
        print(f"\n{'=' * 50}")
        print(f"📱 Task {i}/{len(tasks)}: {task}")
        print(f"{'-' * 50}")
        
        # Execute with retry mechanism
        for attempt in range(max_retries + 1):
            result.start()
            
            try:
                if attempt > 0:
                    print(f"🔄 Retry {attempt}/{max_retries}...")
                    
                # Execute task
                task_result = agent.run(task)
                
                # Task completed successfully
                result.complete(task_result)
                print(f"✅ 任务完成:")
                print(f"   结果: {task_result}")
                break
                
            except Exception as e:
                result.fail(e)
                result.increment_retry()
                print(f"❌ 任务失败:")
                print(f"   Error: {e}")
                
                if attempt < max_retries:
                    print(f"⏱️ 3秒后重试...")
                    time.sleep(3)
                else:
                    print(f"💥 达到最大重试次数")
        
        # Reset agent state for next task (optional, depends on use case)
        if not use_history or "老样子" not in task:
            agent.reset()
    
    # Calculate total statistics
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    success_count = sum(1 for r in results if r.success)
    failure_count = len(results) - success_count
    
    # Generate summary report
    print(f"\n{'=' * 60}")
    print(f"📊 批量执行总结")
    print(f"{'=' * 60}")
    print(f"📋 总任务数: {len(tasks)}")
    print(f"✅ 成功任务数: {success_count}")
    print(f"❌ 失败任务数: {failure_count}")
    print(f"⏱️ 总时长: {total_duration:.2f} 秒")
    print(f"📈 成功率: {success_count / len(tasks) * 100:.1f}%")
    
    print(f"\n{'-' * 60}")
    print(f"📋 任务详情:")
    print(f"{'-' * 60}")
    
    for i, result in enumerate(results, 1):
        status = "✅" if result.success else "❌"
        duration = f"{result.duration:.2f}s"
        retry_info = f" (重试: {result.retry_count})" if result.retry_count > 0 else ""
        
        print(f"   {i}. {status} {result.task} {duration}{retry_info}")
        if not result.success and result.error:
            print(f"      Error: {result.error[:100]}...")
    
    print(f"\n{'=' * 60}")
    print(f"🎉 批量执行完成")
    print(f"{'=' * 60}")
    
    # Save results to file (optional)
    save_results_to_file(results, "batch_results.txt")
    print(f"📁 结果已保存到: batch_results.txt")


def save_results_to_file(results: List[BatchTaskResult], filename: str):
    """Save batch results to file / 将批量结果保存到文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Phone Agent Batch Task Execution Results\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"Task {i}: {result.task}\n")
            f.write(f"Status: {'SUCCESS' if result.success else 'FAILED'}\n")
            f.write(f"Duration: {result.duration:.2f} seconds\n")
            if result.retry_count > 0:
                f.write(f"Retries: {result.retry_count}\n")
            if result.success:
                f.write(f"Result: {result.result}\n")
            else:
                f.write(f"Error: {result.error}\n")
            f.write("-" * 40 + "\n")


def main(lang: str = "cn"):
    """Main function / 主函数"""
    # Run batch task execution example
    example_batch_task_execution(lang)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Phone Agent Batch Task Execution Example")
    parser.add_argument(
        "--lang",
        type=str,
        default="cn",
        choices=["cn", "en"],
        help="Language for UI messages (cn=Chinese, en=English) / UI消息语言（中文/英文）",
    )
    args = parser.parse_args()
    
    main(lang=args.lang)
