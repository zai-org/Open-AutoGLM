# AutoGLM llama.cpp 集成 (临时解决方案)

为 Open-AutoGLM 添加 llama.cpp 本地推理支持，解决兼容性问题。

> **注意**: 这是一个临时解决方案，用于快速解决 OpenAI SDK 与 llama.cpp server 的兼容性问题。

## 变更文件

**新增**:
- `phone_agent/model/factory.py` - 客户端工厂
- `phone_agent/model/llama_client.py` - llama.cpp 客户端

**修改**:
- `phone_agent/agent.py` - 添加切换方法
- `phone_agent/model/__init__.py` - 导出工厂

## 使用方式

```python
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig

agent = PhoneAgent(ModelConfig(base_url="http://localhost:8080/v1"))
agent.switch_client("llama")  # 切换到 llama.cpp
agent.switch_client("auto")   # 自动检测
```

## 解决问题

- JSON 解析错误
- 流式响应处理差异  
- OpenAI SDK 兼容性问题

**为 Open-AutoGLM 带来完整的本地推理能力。**
