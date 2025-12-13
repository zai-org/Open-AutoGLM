"""Core history management implementation."""

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HistoryItem:
    """通用历史记录项"""
    id: str  # 唯一标识符
    task: str  # 原始任务描述
    context: List[Dict[str, Any]]  # 完整对话上下文
    result: str  # 任务结果
    metadata: Dict[str, Any]  # 附加元数据（如时间戳、标签等）


@dataclass
class HistoryConfig:
    """历史管理配置"""
    max_history: int = 10  # 最大历史记录数量
    enable_auto_save: bool = True  # 是否自动保存历史
    enable_auto_reuse: bool = True  # 是否自动检测并复用历史
    enable_persistence: bool = True  # 是否启用持久化存储
    persistence_file: str = "phone_agent_history.json"  # 持久化文件路径
    reuse_triggers: List[str] = field(default_factory=lambda: [  # 自动复用触发词
        "老样子", "同样", "上次","老地方",'再来','再次', "same as before", "repeat", "again"
    ])


class HistoryManager:
    """通用历史对话管理器"""
    
    def __init__(self, config: Optional[HistoryConfig] = None):
        self.config = config or HistoryConfig()
        self._history: List[HistoryItem] = []
        
        # 从文件加载历史记录
        if self.config.enable_persistence:
            self._load_history_from_file()
        
    def save(self, task: str, context: List[Dict[str, Any]], result: str, metadata: Optional[Dict[str, Any]] = None) -> HistoryItem:
        """保存历史记录"""
        # 生成唯一ID
        history_id = str(uuid.uuid4())[:8]
        # 创建历史记录项
        history_item = HistoryItem(
            id=history_id,
            task=task,
            context=context.copy(),
            result=result,
            metadata=metadata or {"timestamp": time.time()}
        )
        # 添加到历史记录（最新的在前）
        self._history.insert(0, history_item)
        # 限制历史记录数量
        if len(self._history) > self.config.max_history:
            self._history = self._history[:self.config.max_history]
        
        # 保存到文件
        if self.config.enable_persistence:
            self._save_history_to_file()
        
        return history_item
        
    def get(self, history_id: Optional[str] = None, index: int = 0) -> Optional[HistoryItem]:
        """获取历史记录"""
        if history_id:
            # 根据ID查找
            for item in self._history:
                if item.id == history_id:
                    return item
        elif index < len(self._history):
            # 根据索引查找
            return self._history[index]
        return None
        
    def list(self, limit: Optional[int] = None) -> List[HistoryItem]:
        """列出历史记录"""
        return self._history[:limit]
        
    def delete(self, history_id: Optional[str] = None, index: int = 0) -> bool:
        """删除历史记录"""
        if history_id:
            # 根据ID删除
            for i, item in enumerate(self._history):
                if item.id == history_id:
                    self._history.pop(i)
                    return True
        elif index < len(self._history):
            # 根据索引删除
            self._history.pop(index)
            return True
        return False
        
    def clear(self) -> None:
        """清空所有历史记录"""
        self._history.clear()
        # 保存到文件
        if self.config.enable_persistence:
            self._save_history_to_file()
        
    def should_reuse(self, task: str) -> bool:
        """判断是否应该复用历史"""
        if not self.config.enable_auto_reuse:
            return False
        # 检查是否包含触发词
        task_lower = task.lower()
        for trigger in self.config.reuse_triggers:
            if trigger.lower() in task_lower:
                return True
        return False
    
    def _load_history_from_file(self) -> None:
        """从JSON文件加载历史记录"""
        if not os.path.exists(self.config.persistence_file):
            return  # 文件不存在，跳过加载
        
        try:
            with open(self.config.persistence_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                # 将字典转换为HistoryItem对象
                self._history = [HistoryItem(**item) for item in history_data]
        except Exception as e:
            print(f"Warning: Failed to load history from {self.config.persistence_file}: {e}")
            self._history = []
    
    def _save_history_to_file(self) -> None:
        """将历史记录保存到JSON文件"""
        try:
            # 将HistoryItem对象转换为字典
            history_data = [asdict(item) for item in self._history]
            with open(self.config.persistence_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save history to {self.config.persistence_file}: {e}")
    
    def delete(self, history_id: Optional[str] = None, index: int = 0) -> bool:
        """删除历史记录"""
        success = False
        if history_id:
            # 根据ID删除
            for i, item in enumerate(self._history):
                if item.id == history_id:
                    self._history.pop(i)
                    success = True
                    break
        elif index < len(self._history):
            # 根据索引删除
            self._history.pop(index)
            success = True
        
        # 如果删除成功，保存到文件
        if success and self.config.enable_persistence:
            self._save_history_to_file()
        
        return success
