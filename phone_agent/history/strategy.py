"""Context reuse strategies for history management."""

import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

from phone_agent.history.manager import HistoryItem


class ContextReuseStrategy(ABC):
    """上下文复用策略接口"""
    
    @abstractmethod
    def build_context(self, current_task: str, history_item: HistoryItem) -> List[Dict[str, Any]]:
        """根据历史记录构建当前上下文"""
        pass


class FullReuseStrategy(ContextReuseStrategy):
    """完全复用策略：复用完整历史上下文"""
    
    def build_context(self, current_task: str, history_item: HistoryItem) -> List[Dict[str, Any]]:
        # 复制完整历史上下文
        context = history_item.context.copy()
        # 移除最后可能的用户消息（避免重复）
        if context and context[-1]["role"] == "user":
            context.pop()
        return context


class TaskBasedReuseStrategy(ContextReuseStrategy):
    """基于任务的复用策略：仅复用与当前任务相关的历史"""
    
    def build_context(self, current_task: str, history_item: HistoryItem) -> List[Dict[str, Any]]:
        # 这里可以实现更复杂的任务相关性分析
        # 例如，提取历史中的任务意图，与当前任务进行匹配
        # 简化实现：如果任务类型相似，则复用
        if self._is_similar_task(current_task, history_item.task):
            return self._extract_relevant_context(history_item.context, current_task)
        return []
    
    def _is_similar_task(self, task1: str, task2: str) -> bool:
        # 简化实现：检查任务中是否包含相同的关键词
        keywords1 = set(re.findall(r'\w+', task1.lower()))
        keywords2 = set(re.findall(r'\w+', task2.lower()))
        return len(keywords1.intersection(keywords2)) > 0
    
    def _extract_relevant_context(self, context: List[Dict[str, Any]], current_task: str) -> List[Dict[str, Any]]:
        # 简化实现：返回完整上下文
        return context.copy()


class CustomReuseStrategy(ContextReuseStrategy):
    """自定义复用策略：允许用户通过回调函数自定义上下文构建"""
    
    def __init__(self, custom_builder: Callable[[str, HistoryItem], List[Dict[str, Any]]]):
        self.custom_builder = custom_builder
        
    def build_context(self, current_task: str, history_item: HistoryItem) -> List[Dict[str, Any]]:
        return self.custom_builder(current_task, history_item)


class ReuseStrategyRegistry:
    """复用策略注册表"""
    
    def __init__(self):
        self._strategies = {}
        
    def register(self, name: str, strategy: ContextReuseStrategy):
        """注册复用策略"""
        self._strategies[name] = strategy
        
    def get(self, name: str) -> ContextReuseStrategy:
        """获取复用策略"""
        return self._strategies.get(name)
        
    def list(self) -> List[str]:
        """列出所有策略"""
        return list(self._strategies.keys())


# 全局策略注册表
strategy_registry = ReuseStrategyRegistry()
# 注册内置策略
strategy_registry.register("full", FullReuseStrategy())
strategy_registry.register("task_based", TaskBasedReuseStrategy())
