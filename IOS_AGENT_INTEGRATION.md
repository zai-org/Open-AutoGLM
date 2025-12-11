# iOS Agent 集成完成

## 🎉 更新总结

已成功在 `phone_agent` 模块中实现完整的 iOS 支持,现在 `ios.py` 使用真正的 iOS Agent 而不是 Android ADB 后端。

## 📁 新增文件

### 1. **phone_agent/agent_ios.py** (IOSPhoneAgent)
专门为 iOS 设备设计的 Agent 类,功能完全对等于 Android 的 `PhoneAgent`。

```python
from phone_agent import IOSPhoneAgent
from phone_agent.agent_ios import IOSAgentConfig
from phone_agent.model import ModelConfig

# 创建 iOS Agent
model_config = ModelConfig(base_url="http://localhost:8000/v1")
agent_config = IOSAgentConfig(wda_url="http://localhost:8100")

agent = IOSPhoneAgent(model_config, agent_config)
result = agent.run("打开 Safari")
```

**主要特性:**
- ✅ 使用 WebDriverAgent 与 iOS 设备通信
- ✅ 支持所有标准操作 (tap, swipe, type, etc.)
- ✅ 完整的对话上下文管理
- ✅ 步数控制和错误处理
- ✅ 详细的 verbose 模式输出

### 2. **phone_agent/actions/handler_ios.py** (IOSActionHandler)
iOS 专用的动作处理器,处理所有设备操作。

**支持的动作:**
- Launch (启动应用)
- Tap (点击)
- Double Tap (双击)
- Long Press (长按)
- Type (文本输入)
- Swipe (滑动)
- Back (返回手势)
- Home (主屏幕)
- Wait (等待)
- Take_over (人工接管)

**特点:**
- 自动坐标转换 (相对坐标 → 绝对像素)
- 敏感操作确认机制
- 文本输入自动处理 (清除旧文本、隐藏键盘)
- 完整的错误处理

### 3. **examples/ios_agent_usage.py**
完整的 iOS Agent 使用示例。

**包含示例:**
- 基础任务执行
- 回调函数使用
- 单步执行模式
- WiFi 连接配置

## 🔄 更新的文件

### 1. **ios.py**
现在使用真正的 `IOSPhoneAgent` 而不是 Android 的 `PhoneAgent`。

**之前:**
```python
from phone_agent import PhoneAgent
agent = PhoneAgent(model_config, agent_config)  # ❌ 使用 ADB 后端
```

**现在:**
```python
from phone_agent.agent_ios import IOSPhoneAgent, IOSAgentConfig
agent = IOSPhoneAgent(model_config, agent_config)  # ✅ 使用 WDA 后端
```

### 2. **phone_agent/__init__.py**
导出新的 iOS 类。

```python
from phone_agent.agent import PhoneAgent
from phone_agent.agent_ios import IOSPhoneAgent

__all__ = ["PhoneAgent", "IOSPhoneAgent"]
```

## 🎯 配置对比

### Android Agent (PhoneAgent)

```python
from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig

agent_config = AgentConfig(
    max_steps=100,
    device_id="emulator-5554",  # ADB device ID
    lang="cn",
    verbose=True,
)

agent = PhoneAgent(model_config, agent_config)
```

### iOS Agent (IOSPhoneAgent)

```python
from phone_agent import IOSPhoneAgent
from phone_agent.agent_ios import IOSAgentConfig

agent_config = IOSAgentConfig(
    max_steps=100,
    wda_url="http://localhost:8100",  # WebDriverAgent URL
    session_id=None,  # 可选的 WDA session ID
    device_id="00008030-001A...",  # iOS UDID (可选)
    lang="cn",
    verbose=True,
)

agent = IOSPhoneAgent(model_config, agent_config)
```

## 📊 类结构对比

| 组件 | Android | iOS |
|------|---------|-----|
| Agent 类 | `PhoneAgent` | `IOSPhoneAgent` |
| 配置类 | `AgentConfig` | `IOSAgentConfig` |
| 动作处理器 | `ActionHandler` | `IOSActionHandler` |
| 设备通信 | `phone_agent.adb` | `phone_agent.xctest` |
| 截图 | `adb.get_screenshot()` | `xctest.get_screenshot()` |
| 当前应用 | `adb.get_current_app()` | `xctest.get_current_app()` |

## 🚀 使用示例

### 1. 命令行使用

```bash
# 检查系统要求
python ios.py --list-devices
python ios.py --wda-status

# 执行任务
python ios.py "打开设置"
python ios.py "打开 Safari 并搜索 Apple"

# WiFi 连接
python ios.py --wda-url http://192.168.1.100:8100 "打开相机"
```

### 2. Python API 使用

```python
from phone_agent import IOSPhoneAgent
from phone_agent.agent_ios import IOSAgentConfig
from phone_agent.model import ModelConfig

# 配置
model_config = ModelConfig(
    base_url="http://localhost:8000/v1",
    model_name="autoglm-phone-9b",
)

agent_config = IOSAgentConfig(
    wda_url="http://localhost:8100",
    max_steps=50,
    lang="cn",
    verbose=True,
)

# 创建并运行
agent = IOSPhoneAgent(model_config, agent_config)
result = agent.run("打开 Safari 并访问 apple.com")
print(result)
```

### 3. 批量任务

```python
agent = IOSPhoneAgent(model_config, agent_config)

tasks = [
    "打开设置",
    "查看电池状态",
    "返回主屏幕",
]

for task in tasks:
    result = agent.run(task)
    print(f"{task}: {result}")
    agent.reset()  # 重置状态
```

### 4. 单步执行

```python
agent = IOSPhoneAgent(model_config, agent_config)

# 第一步
result = agent.step(task="打开 Safari")
print(f"步骤 1: {result.action}")

# 后续步骤
while not result.finished:
    result = agent.step()
    print(f"步骤 {agent.step_count}: {result.action}")
```

### 5. 自定义回调

```python
def my_confirmation(message: str) -> bool:
    print(f"⚠️  {message}")
    return input("继续? (y/n): ").lower() == "y"

def my_takeover(message: str) -> None:
    print(f"🤚 {message}")
    input("完成后按回车...")

agent = IOSPhoneAgent(
    model_config,
    agent_config,
    confirmation_callback=my_confirmation,
    takeover_callback=my_takeover,
)
```

## 🔧 IOSAgentConfig 详细说明

```python
@dataclass
class IOSAgentConfig:
    """iOS Agent 配置"""

    max_steps: int = 100
    # 每个任务的最大步数

    wda_url: str = "http://localhost:8100"
    # WebDriverAgent URL
    # - USB: http://localhost:8100 (需要 iproxy)
    # - WiFi: http://<device-ip>:8100

    session_id: str | None = None
    # WDA session ID (可选)
    # 通常自动管理,除非需要复用 session

    device_id: str | None = None
    # iOS 设备 UDID (可选)
    # 用于多设备场景

    lang: str = "cn"
    # 系统提示语言: "cn" 或 "en"

    system_prompt: str | None = None
    # 自定义系统提示 (可选)
    # 默认使用 lang 对应的提示

    verbose: bool = True
    # 是否显示详细日志
    # 包括思考过程和执行动作
```

## 🎨 Verbose 模式输出示例

当 `verbose=True` 时,Agent 会输出详细的执行信息:

```
==================================================
💭 思考过程:
--------------------------------------------------
当前在主屏幕,需要启动设置应用
--------------------------------------------------
🎯 执行动作:
{
  "_metadata": "do",
  "action": "Launch",
  "app": "Settings"
}
==================================================

🎉 ================================================
✅ 任务完成: 已成功打开设置
==================================================
```

## 🔄 与 Android 的对比

### 相似之处
- ✅ 相同的 API 接口设计
- ✅ 相同的配置结构
- ✅ 相同的回调机制
- ✅ 相同的 verbose 模式
- ✅ 相同的步数控制

### 差异之处
| 特性 | Android | iOS |
|------|---------|-----|
| 设备通信 | ADB | WebDriverAgent |
| 连接配置 | `device_id` | `wda_url` + `device_id` |
| 文本输入 | ADB Keyboard | WDA 键盘 API |
| 返回操作 | 系统返回键 | 左边缘滑动手势 |
| 应用标识 | Package Name | Bundle ID |

## 📚 相关文档

1. [IOS_CLI_GUIDE.md](IOS_CLI_GUIDE.md) - ios.py 命令行使用指南
2. [iOS_SUPPORT.md](iOS_SUPPORT.md) - iOS 支持总览
3. [CLI_USAGE.md](CLI_USAGE.md) - Android 和 iOS CLI 对比
4. [phone_agent/xctest/README.md](phone_agent/xctest/README.md) - XCTest 模块详细文档
5. [examples/ios_agent_usage.py](examples/ios_agent_usage.py) - iOS Agent 完整示例

## ✅ 完成检查清单

- [x] 创建 `phone_agent/agent_ios.py` (IOSPhoneAgent)
- [x] 创建 `phone_agent/actions/handler_ios.py` (IOSActionHandler)
- [x] 更新 `ios.py` 使用 IOSPhoneAgent
- [x] 更新 `phone_agent/__init__.py` 导出新类
- [x] 创建 `examples/ios_agent_usage.py` 示例
- [x] 测试代码可以正常导入和运行
- [x] 创建集成文档

## 🚀 快速测试

### 1. 测试导入

```bash
python -c "from phone_agent import IOSPhoneAgent; print('✅ OK')"
```

### 2. 测试 ios.py

```bash
python ios.py --help
python ios.py --list-devices
python ios.py --wda-status
```

### 3. 运行示例

```bash
python examples/ios_agent_usage.py
python examples/ios_agent_usage.py callbacks
python examples/ios_agent_usage.py step
```

## 🎯 下一步建议

1. **测试完整流程**: 在真实设备上测试任务执行
2. **优化性能**: 根据实际使用调整延迟和超时
3. **添加更多示例**: 常见任务的完整示例
4. **改进错误处理**: iOS 特定的错误提示
5. **文档完善**: 添加更多使用场景和最佳实践

## 🎉 总结

现在 Open-AutoGLM 拥有完整的 Android 和 iOS 双平台支持:

- **Android**: `python main.py` → `PhoneAgent` → ADB
- **iOS**: `python ios.py` → `IOSPhoneAgent` → WebDriverAgent

两个平台的 API 保持一致,可以轻松在不同平台之间切换! 🚀
