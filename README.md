# Open-AutoGLM

[Readme in English](README_en.md)

<div align="center">
<img src=resources/logo.svg width="20%"/>
</div>
<p align="center">
    👋 加入我们的 <a href="resources/WECHAT.md" target="_blank">微信</a> 社区
</p>
<p align="center">
    🎤 进一步在我们的产品 <a href="https://autoglm.zhipuai.cn/autotyper/" target="_blank">智谱 AI 输入法</a> 体验“用嘴发指令”
</p
><p align="center">
    <a href="https://mp.weixin.qq.com/s/wRp22dmRVF23ySEiATiWIQ" target="_blank">AutoGLM 实战派</a> 开发者激励活动火热进行中，跑通、二创即可瓜分数万元现金奖池！成果提交 👉 <a href="https://zhipu-ai.feishu.cn/share/base/form/shrcnE3ZuPD5tlOyVJ7d5Wtir8c?from=navigation" target="_blank">入口</a>
</p>

## 懒人版快速安装

你可以使用 Claude Code，配置 [GLM Coding Plan](https://bigmodel.cn/glm-coding) 后，输入以下提示词，快速部署本项目。

```text
访问文档，为我安装 AutoGLM
https://raw.githubusercontent.com/zai-org/Open-AutoGLM/refs/heads/main/README.md
```

## 项目介绍

Phone Agent 是一个基于 AutoGLM 构建的手机端智能助理框架，它能够以多模态方式理解手机屏幕内容，并通过自动化操作帮助用户完成任务。系统通过 ADB(Android Debug Bridge) 来控制设备，以视觉语言模型进行屏幕感知，再结合智能规划能力生成并执行操作流程。用户只需用自然语言描述需求，如“打开小红书搜索美食”，Phone Agent 即可自动解析意图、理解当前界面、规划下一步动作并完成整个流程。系统还内置敏感操作确认机制，并支持在登录或验证码场景下进行人工接管。同时，它提供远程 ADB/HDC 调试能力，可通过 WiFi 或网络连接设备，实现灵活的远程控制与开发。

> ⚠️
> 本项目仅供研究和学习使用。严禁用于非法获取信息、干扰系统或任何违法活动。请仔细审阅 [使用条款](resources/privacy_policy.txt)。

## 模型下载地址

| Model                         | Download Links                                                                                                                                                         |
|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| AutoGLM-Phone-9B              | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B)<br>[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B)                           |
| AutoGLM-Phone-9B-Multilingual | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B-Multilingual)<br>[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B-Multilingual) |

其中，`AutoGLM-Phone-9B` 是针对中文手机应用优化的模型，而 `AutoGLM-Phone-9B-Multilingual` 支持英语场景，适用于包含英文等其他语言内容的应用。

## 准备工作

你需要完成以下准备工作：

- 准备移动侧环境
  - [Android 环境配置指南](docs/android_setup.md)
  - [iOS 环境配置指南](docs/ios_setup/ios_setup.md)
- 配置 PC 端环境与部署模型
  - [环境与模型部署指南](docs/environment.md)

## 使用 AutoGLM

### 命令行

根据你部署的模型，设置 `--base-url` 和 `--model` 参数，设置 `--device-type` 指定是安卓设备或鸿蒙设备 (默认值 adb 表示安卓设备，hdc 表示鸿蒙设备). 例如：

```bash
# Android 设备 - 交互模式
python main.py --base-url http://localhost:8000/v1 --model "autoglm-phone-9b"

# Android 设备 - 指定任务
python main.py --base-url http://localhost:8000/v1 "打开美团搜索附近的火锅店"

# 鸿蒙设备 - 交互模式
python main.py --device-type hdc --base-url http://localhost:8000/v1 --model "autoglm-phone-9b"

# 鸿蒙设备 - 指定任务
python main.py --device-type hdc --base-url http://localhost:8000/v1 "打开美团搜索附近的火锅店"

# 使用 API Key 进行认证
python main.py --apikey sk-xxxxx

# 使用英文 system prompt
python main.py --lang en --base-url http://localhost:8000/v1 "Open Chrome browser"

# 列出支持的应用（Android）
python main.py --list-apps

# 列出支持的应用（鸿蒙）
python main.py --device-type hdc --list-apps
```

### Python API

```python
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig

# Configure model
model_config = ModelConfig(
    base_url="http://localhost:8000/v1",
    model_name="autoglm-phone-9b",
)

# 创建 Agent
agent = PhoneAgent(model_config=model_config)

# 执行任务
result = agent.run("打开淘宝搜索无线耳机")
print(result)
```

### 远程调试

请参考 [远程调试指南](docs/remote_control.md)。

## 自定义配置

### 自定义 SYSTEM PROMPT

系统提供中英文两套 prompt，通过 `--lang` 参数切换：

- `--lang cn` - 中文 prompt(默认)，配置文件：`phone_agent/config/prompts_zh.py`
- `--lang en` - 英文 prompt，配置文件：`phone_agent/config/prompts_en.py`

可以直接修改对应的配置文件来增强模型在特定领域的能力，或通过注入 app 名称禁用某些 app。

### 环境变量

| 变量                          | 描述                     | 默认值                        |
|-----------------------------|------------------------|----------------------------|
| `PHONE_AGENT_BASE_URL`      | 模型 API 地址              | `http://localhost:8000/v1` |
| `PHONE_AGENT_MODEL`         | 模型名称                   | `autoglm-phone-9b`         |
| `PHONE_AGENT_API_KEY`       | 模型认证 API Key           | `EMPTY`                    |
| `PHONE_AGENT_MAX_STEPS`     | 每个任务最大步数               | `100`                      |
| `PHONE_AGENT_DEVICE_ID`     | ADB/HDC 设备 ID          | (自动检测)                     |
| `PHONE_AGENT_DEVICE_TYPE`   | 设备类型 (`adb` 或 `hdc`)   | `adb`                      |
| `PHONE_AGENT_LANG`          | 语言 (`cn` 或 `en`)       | `cn`                       |

### 模型配置

```python
from phone_agent.model import ModelConfig

config = ModelConfig(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",  # API 密钥 (如需要)
    model_name="autoglm-phone-9b",  # 模型名称
    max_tokens=3000,  # 最大输出 token 数
    temperature=0.1,  # 采样温度
    frequency_penalty=0.2,  # 频率惩罚
)
```

### Agent 配置

```python
from phone_agent.agent import AgentConfig

config = AgentConfig(
    max_steps=100,  # 每个任务最大步数
    device_id=None,  # ADB 设备 ID(None 为自动检测)
    lang="cn",  # 语言选择：cn(中文) 或 en(英文)
    verbose=True,  # 打印调试信息 (包括思考过程和执行动作)
)
```

### Verbose 模式输出

当 `verbose=True` 时，Agent 会在每一步输出详细信息：

```text
==================================================
💭 思考过程：
--------------------------------------------------
当前在系统桌面，需要先启动小红书应用
--------------------------------------------------
🎯 执行动作：
{
  "_metadata": "do",
  "action": "Launch",
  "app": "小红书"
}
==================================================

... (执行动作后继续下一步)

==================================================
💭 思考过程：
--------------------------------------------------
小红书已打开，现在需要点击搜索框
--------------------------------------------------
🎯 执行动作：
{
  "_metadata": "do",
  "action": "Tap",
  "element": [500, 100]
}
==================================================

🎉 ================================================
✅ 任务完成：已成功搜索美食攻略
==================================================
```

这样可以清楚地看到 AI 的推理过程和每一步的具体操作。

## 能力

### 支持 Android 应用

Phone Agent 支持 50+ 款主流中文应用：

| 分类   | 应用              |
|------|-----------------|
| 社交通讯 | 微信、QQ、微博        |
| 电商购物 | 淘宝、京东、拼多多       |
| 美食外卖 | 美团、饿了么、肯德基      |
| 出行旅游 | 携程、12306、滴滴出行   |
| 视频娱乐 | bilibili、抖音、爱奇艺 |
| 音乐音频 | 网易云音乐、QQ 音乐、喜马拉雅 |
| 生活服务 | 大众点评、高德地图、百度地图  |
| 内容社区 | 小红书、知乎、豆瓣       |

运行 `python main.py --list-apps` 查看完整列表。

### 支持鸿蒙应用

Phone Agent 支持 60+ 款鸿蒙原生应用和系统应用：

| 分类      | 应用                                       |
|---------|------------------------------------------|
| 社交通讯    | 微信、QQ、微博、飞书、企业微信                        |
| 电商购物    | 淘宝、京东、拼多多、唯品会、得物、闲鱼                     |
| 美食外卖    | 美团、美团外卖、大众点评、海底捞                        |
| 出行旅游    | 12306、滴滴出行、同程旅行、高德地图、百度地图               |
| 视频娱乐    | bilibili、抖音、快手、腾讯视频、爱奇艺、芒果 TV            |
| 音乐音频    | QQ 音乐、汽水音乐、喜马拉雅                           |
| 生活服务    | 小红书、知乎、今日头条、58 同城、中国移动                   |
| AI 与工具   | 豆包、WPS、UC 浏览器、扫描全能王、美图秀秀                 |
| 系统应用    | 浏览器、日历、相机、时钟、云空间、文件管理器、相册、联系人、短信、设置等   |
| 华为服务    | 应用市场、音乐、视频、阅读、主题、天气                     |

运行 `python main.py --device-type hdc --list-apps` 查看完整列表。

### 可用操作

Agent 可以执行以下操作：

| 操作           | 描述              |
|--------------|-----------------|
| `Launch`     | 启动应用            |  
| `Tap`        | 点击指定坐标          |
| `Type`       | 输入文本            |
| `Swipe`      | 滑动屏幕            |
| `Back`       | 返回上一页           |
| `Home`       | 返回桌面            |
| `Long Press` | 长按              |
| `Double Tap` | 双击              |
| `Wait`       | 等待页面加载          |
| `Take_over`  | 请求人工接管 (登录/验证码等) |

### 自定义回调

处理敏感操作确认和人工接管：

```python
def my_confirmation(message: str) -> bool:
    """敏感操作确认回调"""
    return input(f"确认执行 {message}？(y/n): ").lower() == "y"


def my_takeover(message: str) -> None:
    """人工接管回调"""
    print(f"请手动完成：{message}")
    input("完成后按回车继续...")


agent = PhoneAgent(
    confirmation_callback=my_confirmation,
    takeover_callback=my_takeover,
)
```

### 示例

查看 `examples/` 目录获取更多使用示例：

- `basic_usage.py` - 基础任务执行
- 单步调试模式
- 批量任务执行
- 自定义回调

## 二次开发

请参考 [二次开发指南](docs/development.md)。

## 常见问题

我们列举了一些常见的问题，以及对应的解决方案：

### 设备未找到

尝试通过重启 ADB 服务来解决：

```bash
adb kill-server
adb start-server
adb devices
```

如果仍然无法识别，请检查：

1. USB 调试是否已开启
2. 数据线是否支持数据传输 (部分数据线仅支持充电)
3. 手机上弹出的授权框是否已点击「允许」
4. 尝试更换 USB 接口或数据线

### 能打开应用，但无法点击

部分机型需要同时开启两个调试选项才能正常使用：

- **USB 调试**
- **USB 调试 (安全设置)**

请在 `设置 → 开发者选项` 中检查这两个选项是否都已启用。

### 文本输入不工作

1. 确保设备已安装 ADB Keyboard
2. 在设置 > 系统 > 语言和输入法 > 虚拟键盘 中启用
3. Agent 会在需要输入时自动切换到 ADB Keyboard

### 截图失败 (黑屏)

这通常意味着应用正在显示敏感页面 (支付、密码、银行类应用)。Agent 会自动检测并请求人工接管。

### windows 编码异常问题

报错信息形如 `UnicodeEncodeError gbk code`

解决办法：在运行代码的命令前面加上环境变量：`PYTHONIOENCODING=utf-8`

### 交互模式非 TTY 环境无法使用

报错形如：`EOF when reading a line`

解决办法：使用非交互模式直接指定任务，或者切换到 TTY 模式的终端应用。

### 引用

如果你觉得我们的工作有帮助，请引用以下论文：

```bibtex
@article{liu2024autoglm,
  title={Autoglm: Autonomous foundation agents for guis},
  author={Liu, Xiao and Qin, Bo and Liang, Dongzhu and Dong, Guang and Lai, Hanyu and Zhang, Hanchen and Zhao, Hanlin and Iong, Iat Long and Sun, Jiadai and Wang, Jiaqi and others},
  journal={arXiv preprint arXiv:2411.00820},
  year={2024}
}
@article{xu2025mobilerl,
  title={MobileRL: Online Agentic Reinforcement Learning for Mobile GUI Agents},
  author={Xu, Yifan and Liu, Xiao and Liu, Xinghan and Fu, Jiaqi and Zhang, Hanchen and Jing, Bohao and Zhang, Shudan and Wang, Yuting and Zhao, Wenyi and Dong, Yuxiao},
  journal={arXiv preprint arXiv:2509.18119},
  year={2025}
}
```

---

## 自动化部署指南 (面向 AI)

> **本章节专为 AI 助手 (如 Claude Code) 设计，用于自动化部署 Open-AutoGLM。**
>
> 如果你是人类读者，可以跳过本章节，按照上面的文档操作即可。

---

### 项目概述

Open-AutoGLM 是一个手机 Agent 框架：

- **输入**：用户的自然语言指令 (如"打开微信发消息给张三")
- **输出**：自动操作用户的安卓手机完成任务
- **原理**：截图 → 视觉模型理解界面 → 输出点击坐标 → ADB 执行操作 → 循环

架构分为两部分：

1. **Agent 代码**(本仓库)：运行在用户电脑上，负责调用模型、解析动作、控制手机
2. **视觉模型服务**：可以是远程 API，也可以本地部署

---

### 部署前置检查

在开始部署前，请逐项向用户确认以下内容：

#### 硬件环境

- [ ] 用户有一台安卓手机 (Android 7.0+)
- [ ] 用户有一根支持数据传输的 USB 数据线 (不是仅充电线)
- [ ] 手机和电脑可以通过数据线连接

#### 手机端配置

- [ ] 手机已开启「开发者模式」(设置 → 关于手机 → 连续点击版本号 7 次)
- [ ] 手机已开启「USB 调试」(设置 → 开发者选项 → USB 调试)
- [ ] 部分机型需要同时开启「USB 调试 (安全设置)」
- [ ] 手机已安装 ADB Keyboard 应用 (下载地址：<https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk>)
- [ ] ADB Keyboard 已在系统设置中启用 (设置 → 语言和输入法 → 启用 ADB Keyboard)

#### 模型服务确认 (二选一)

**请明确询问用户：你是否已有可用的 AutoGLM 模型服务？**

- **选项 A：使用已部署的模型服务 (推荐)**
  - 用户提供模型服务的 URL(如 `http://xxx.xxx.xxx.xxx:8000/v1`)
  - 无需本地 GPU，无需下载模型
  - 直接使用该 URL 作为 `--base-url` 参数

- **选项 B：本地部署模型 (高配置要求)**
  - 需要 NVIDIA GPU(建议 24GB+ 显存)
  - 需要安装 vLLM 或 SGLang
  - 需要下载约 20GB 的模型文件
  - **如果用户是新手或不确定，强烈建议选择选项 A**

---

### 部署流程

#### 阶段一：环境准备

```bash
# 1. 安装 ADB 工具
# MacOS:
brew install android-platform-tools
# 或手动下载：https://developer.android.com/tools/releases/platform-tools

# Windows: 下载后解压，添加到 PATH 环境变量

# 2. 验证 ADB 安装
adb version
# 应输出版本信息

# 3. 连接手机并验证
# 用数据线连接手机，手机上点击「允许 USB 调试」
adb devices
# 应输出设备列表，如：
# List of devices attached
# XXXXXXXX    device
```

**如果 `adb devices` 显示空列表或 unauthorized：**

1. 检查手机上是否弹出授权框，点击「允许」
2. 检查 USB 调试是否开启
3. 尝试更换数据线或 USB 接口
4. 执行 `adb kill-server && adb start-server` 后重试

#### 阶段二：安装 Agent

```bash
# 1. 克隆仓库(如果还没有克隆)
git clone https://github.com/zai-org/Open-AutoGLM.git
cd Open-AutoGLM

# 2. 创建虚拟环境(推荐)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
pip install -e .
```

**注意：不需要 clone 模型仓库，模型通过 API 调用。**

#### 阶段三：配置模型服务

**如果用户选择选项 A(使用已部署的模型)：**

你可以使用以下第三方模型服务：

1. **智谱 BigModel**
   - 文档：<https://docs.bigmodel.cn/cn/api/introduction>
   - `--base-url`：`https://open.bigmodel.cn/api/paas/v4`
   - `--model`：`autoglm-phone`
   - `--apikey`：在智谱平台申请你的 API Key

2. **ModelScope(魔搭社区)**
   - 文档：<https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B>
   - `--base-url`：`https://api-inference.modelscope.cn/v1`
   - `--model`：`ZhipuAI/AutoGLM-Phone-9B`
   - `--apikey`：在 ModelScope 平台申请你的 API Key

使用示例：

```bash
# 使用智谱 BigModel
python main.py --base-url https://open.bigmodel.cn/api/paas/v4 --model "autoglm-phone" --apikey "your-bigmodel-api-key" "打开美团搜索附近的火锅店"

# 使用 ModelScope
python main.py --base-url https://api-inference.modelscope.cn/v1 --model "ZhipuAI/AutoGLM-Phone-9B" --apikey "your-modelscope-api-key" "打开美团搜索附近的火锅店"
```

或者直接使用用户提供的其他模型服务 URL，跳过本地模型部署步骤。

**如果用户选择选项 B(本地部署模型)：**

```bash
# 1. 安装 vLLM
pip install vllm

# 2. 启动模型服务(会自动下载模型，约 20GB)
python3 -m vllm.entrypoints.openai.api_server \
  --served-model-name autoglm-phone-9b \
  --allowed-local-media-path / \
  --mm-encoder-tp-mode data \
  --mm_processor_cache_type shm \
  --mm_processor_kwargs "{\"max_pixels\":5000000}" \
  --max-model-len 25480 \
  --chat-template-content-format string \
  --limit-mm-per-prompt "{\"image\":10}" \
  --model zai-org/AutoGLM-Phone-9B \
  --port 8000

# 模型服务 URL 为：http://localhost:8000/v1
```

#### 阶段四：验证部署

```bash
# 在 Open-AutoGLM 目录下执行
# 将 {MODEL_URL} 替换为实际的模型服务地址

python main.py --base-url {MODEL_URL} --model "autoglm-phone-9b" "打开微信，对文件传输助手发送消息：部署成功"
```

**预期结果：**

- 手机自动打开微信
- 自动搜索「文件传输助手」
- 自动发送消息「部署成功」

---

### 异常处理

| 错误现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `adb devices` 无输出 | USB 调试未开启或数据线问题 | 检查开发者选项，更换数据线 |
| `adb devices` 显示 unauthorized | 手机未授权 | 手机上点击「允许 USB 调试」|
| 能打开应用但无法点击 | 缺少安全调试权限 | 开启「USB 调试 (安全设置)」|
| 中文输入变成乱码或无输入 | ADB Keyboard 未启用 | 在系统设置中启用 ADB Keyboard |
| 截图返回黑屏 | 敏感页面 (支付/银行) | 正常现象，系统会自动处理 |
| 连接模型服务失败 | URL 错误或服务未启动 | 检查 URL，确认服务正在运行 |
| `ModuleNotFoundError` | 依赖未安装 | 执行 `pip install -r requirements.txt` |

---

### 部署要点

1. **优先确认手机连接**：在安装任何代码之前，先确保 `adb devices` 能看到设备
2. **不要跳过 ADB Keyboard**：没有它，中文输入会失败
3. **模型服务是外部依赖**：Agent 代码本身不包含模型，需要单独的模型服务
4. **遇到权限问题先检查手机设置**：大部分问题都是手机端配置不完整
5. **部署完成后用简单任务测试**：建议用「打开微信发消息给文件传输助手」作为验收标准

---

### 命令速查

```bash
# 检查 ADB 连接
adb devices

# 重启 ADB 服务
adb kill-server && adb start-server

# 安装依赖
pip install -r requirements.txt && pip install -e .

# 运行 Agent(交互模式)
python main.py --base-url {MODEL_URL} --model "autoglm-phone-9b"

# 运行 Agent(单次任务)
python main.py --base-url {MODEL_URL} --model "autoglm-phone-9b" "你的任务描述"

# 查看支持的应用列表
python main.py --list-apps
```

---

**部署完成的标志：手机能自动执行用户的自然语言指令。**
