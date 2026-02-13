# AgentBay 集成示例

本目录包含 AgentBay 与 Phone Agent 集成的示例代码。

## 文件说明

- `phone_agent_integration.py`: 演示如何通过 AgentBay 创建远程设备会话，并使用 Phone Agent 执行自动化任务

## 🔑 API Key 设置

### 步骤 1: 获取 API Key

1. 注册 [https://aliyun.com](https://aliyun.com)

2. 访问 [AgentBay 控制台](https://agentbay.console.aliyun.com/service-management)

3. 创建并复制您的 API Key

## 前置要求

### 1. 安装依赖

```bash
pip install wuying-agentbay-sdk
```

### 2. 环境变量配置
配置以下环境变量：

```bash
# AgentBay API Key
AGENTBAY_API_KEY=your_agentbay_api_key_here

# Model API 配置
MODEL_BASE_URL=http://your-model-api-url/v1
MODEL_NAME=AutoGLM-Phone-9B
MODEL_API_KEY=your_model_api_key_here
```

### 3. ADB 公钥

确保你的 ADB 公钥文件存在于 `~/.android/adbkey.pub`。如果没有，可以通过以下方式生成：

```bash
# 如果 ADB 还没有生成密钥，先连接一次设备
adb devices

# 公钥文件会自动生成在 ~/.android/adbkey.pub
```

## 使用方法

### 运行示例

```bash
cd examples/agentbay
python phone_agent_integration.py
```

## 工作流程

示例代码的执行流程如下：

1. **加载 ADB 公钥**
   - 从 `~/.android/adbkey.pub` 读取 ADB 公钥

2. **创建 AgentBay 会话**
   - 使用 AgentBay API 创建移动设备会话
   - 获取会话 ID 和资源 URL

3. **获取 ADB 连接信息**
   - 通过会话获取远程设备的 ADB 连接 URL
   - URL 格式：`adb connect IP:PORT`

4. **连接到远程设备**
   - 使用 ADB 连接到远程 Android 设备
   - 验证连接状态
   - 获取设备信息（设备 ID、状态等）

5. **配置 Phone Agent**
   - 配置模型 API（base_url、model_name、api_key）
   - 配置 Agent（device_id、max_steps、verbose）

6. **执行任务**
   - 使用 Phone Agent 执行自动化任务
   - 示例任务：打开设置并查询 Android 版本

7. **清理资源**
   - 断开 ADB 连接
   - 删除 AgentBay 会话

## 代码示例

```python
from agentbay import AgentBay, CreateSessionParams
from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.model import ModelConfig
from phone_agent.adb import ADBConnection

# 1. 创建 AgentBay 会话
client = AgentBay(api_key=os.environ.get("AGENTBAY_API_KEY"))
params = CreateSessionParams(image_id="imgc-0aae4rgi82zos4fwy")
result = client.create(params)
session = result.session

# 2. 获取 ADB 连接 URL
adb_result = session.mobile.get_adb_url(adbkey_pub=adbkey_pub)
address = adb_result.data.replace("adb connect ", "")

# 3. 连接到设备
conn = ADBConnection()
conn.connect(address)

# 4. 配置并运行 Phone Agent
model_config = ModelConfig(
    base_url=os.environ.get("MODEL_BASE_URL"),
    model_name=os.environ.get("MODEL_NAME"),
    api_key=os.environ.get("MODEL_API_KEY"),
)

agent_config = AgentConfig(
    device_id=address,
    max_steps=50,
    verbose=True,
)

agent = PhoneAgent(model_config=model_config, agent_config=agent_config)
result = agent.run("打开设置帮我查一下当前的Android版本")

# 5. 清理
conn.disconnect(address)
client.delete(session)
```

## 注意事项

1. **等待设备就绪**
   - 获取 ADB URL 后，建议等待 20 秒左右，确保远程设备完全启动

2. **设备连接**
   - 如果 `get_device_info()` 返回 `None`，代码会自动尝试从设备列表中获取第一个设备

3. **错误处理**
   - 代码包含完整的错误处理和资源清理逻辑
   - 即使出现错误，也会确保断开连接和删除会话

4. **API Key 安全**
   - 不要将 API Key 提交到版本控制系统
   - 使用 `.env` 文件管理敏感信息，并确保 `.env` 在 `.gitignore` 中

## 故障排查

### 问题：无法连接到设备

- 检查 ADB 是否已安装：`adb version`
- 检查网络连接
- 确认 AgentBay 会话已成功创建
- 增加等待时间（当前为 20 秒）

### 问题：ADB 认证失败

- 确认 `~/.android/adbkey.pub` 文件存在且格式正确
- 检查 AgentBay 是否已正确配置你的 ADB 公钥

### 问题：模型 API 调用失败

- 检查 `MODEL_BASE_URL` 是否正确
- 确认 `MODEL_API_KEY` 有效
- 验证模型名称 `MODEL_NAME` 是否正确

## 相关文档

- [AgentBay SDK 文档](https://github.com/wuying-tech/agentbay-sdk)
- [AgentBay 官网](https://help.aliyun.com/zh/agentbay/developer-reference/sdk-access-guide/)
- [Phone Agent 主文档](../../README.md)
- [基础使用示例](../basic_usage.py)
