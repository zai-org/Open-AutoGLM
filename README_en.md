# Open-AutoGLM

[中文阅读.](./README.md)

<div align="center">
<img src=resources/logo.svg width="20%"/>
</div>
<p align="center">
    👋 Join our <a href="resources/WECHAT.md" target="_blank">WeChat</a> community
</p>

## Project Introduction

Phone Agent is a mobile intelligent assistant framework built on AutoGLM. It understands phone screen content in a multimodal manner and helps users complete tasks through automated operations. The system controls devices via ADB (Android Debug Bridge), perceives screens using vision-language models, and generates and executes operation workflows through intelligent planning. Users simply describe their needs in natural language, such as "Open Xiaohongshu and search for food," and Phone Agent will automatically parse the intent, understand the current interface, plan the next action, and complete the entire workflow. The system also includes a sensitive operation confirmation mechanism and supports manual takeover during login or verification code scenarios. Additionally, it provides remote ADB debugging capabilities, allowing device connection via WiFi or network for flexible remote control and development.

> ⚠️ This project is for research and learning purposes only. It is strictly prohibited to use for illegal information acquisition, system interference, or any illegal activities. Please carefully review the [Terms of Use](resources/privacy_policy_en.txt).

## Model Download Links

| Model             | Download Links                                                                                                                                             |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| AutoGLM-Phone-9B  | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B)<br>[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B)               |
| AutoGLM-Phone-9B-Multilingual | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B-Multilingual)<br>[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B-Multilingual) |

`AutoGLM-Phone-9B` is optimized for Chinese mobile applications, while `AutoGLM-Phone-9B-Multilingual` supports English scenarios and is suitable for applications containing English or other language content.

## Environment Setup

### 1. Python Environment

Python from 3.10 to 3.12 is recommended.

### 2. ADB (Android Debug Bridge)

1. Download the official ADB [installation package](https://developer.android.com/tools/releases/platform-tools) and extract it to a custom path
2. Configure environment variables

- MacOS configuration: In `Terminal` or any command line tool

  ```bash
  # Assuming the extracted directory is ~/Downloads/platform-tools. Adjust the command if different.
  export PATH=${PATH}:~/Downloads/platform-tools
  ```

- Windows configuration: Refer to [third-party tutorials](https://blog.csdn.net/x2584179909/article/details/108319973) for configuration.

### 3. Android 7.0+ Device or Emulator with `Developer Mode` and `USB Debugging` Enabled

1. Enable Developer Mode: The typical method is to find `Settings > About Phone > Build Number` and tap it rapidly about 10 times until a popup shows "Developer mode has been enabled." This may vary slightly between phones; search online for tutorials if you can't find it.
2. Enable USB Debugging: After enabling Developer Mode, go to `Settings > Developer Options > USB Debugging` and enable it
3. Some devices may require a restart after setting developer options for them to take effect. You can test by connecting your phone to your computer via USB cable and running `adb devices` to see if device information appears. If not, the connection has failed.

**Please carefully check the relevant permissions**

![Permissions](resources/screenshot-20251209-181423.png)

### 4. Install ADB Keyboard (for Text Input)

Download the [installation package](https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk) and install it on the corresponding Android device.
Note: After installation, you need to enable `ADB Keyboard` in `Settings > Input Method` or `Settings > Keyboard List` for it to work.

## Deployment Preparation

### 1. Install Dependencies

```bash
pip install -r requirements.txt 
pip install -e .
```

### 2. Configure ADB

Make sure your **USB cable supports data transfer**, not just charging.

Ensure ADB is installed and connect the device via **USB cable**:

```bash
# Check connected devices
adb devices

# Output should show your device, e.g.:
# List of devices attached
# emulator-5554   device
```

### 3. Start Model Service

1. Download the model and install the inference engine framework according to the `For Model Deployment` section in `requirements.txt`.
2. Start via SGlang / vLLM to get an OpenAI-format service. Here's a vLLM deployment solution; please strictly follow the startup parameters we provide:

- vLLM:

```shell
python3 -m vllm.entrypoints.openai.api_server \
 --served-model-name autoglm-phone-9b \
 --allowed-local-media-path /   \
 --mm-encoder-tp-mode data \
 --mm_processor_cache_type shm \
 --mm_processor_kwargs "{\"max_pixels\":5000000}" \
 --max-model-len 25480  \
 --chat-template-content-format string \
 --limit-mm-per-prompt "{\"image\":10}" \
 --model zai-org/AutoGLM-Phone-9B \
 --port 8000
```

- This model has the same architecture as `GLM-4.1V-9B-Thinking`. For detailed information about model deployment, you can also check [GLM-V](https://github.com/zai-org/GLM-V) for model deployment and usage guides.

- After successful startup, the model service will be accessible at `http://localhost:8000/v1`. If you deploy the model on a remote server, access it using that server's IP address.

## Using AutoGLM

### Command Line

Set the `--base-url` and `--model` parameters according to your deployed model. For example:

```bash
# Interactive mode
python main.py --base-url http://localhost:8000/v1 --model "autoglm-phone-9b"

# Specify model endpoint
python main.py --base-url http://localhost:8000/v1 "Open Meituan and search for nearby hotpot restaurants"

# Use English system prompt
python main.py --lang en --base-url http://localhost:8000/v1 "Open Chrome browser"

# List supported apps
python main.py --list-apps
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

# Create Agent
agent = PhoneAgent(model_config=model_config)

# Execute task
result = agent.run("Open Taobao and search for wireless earbuds")
print(result)
```

## Remote Debugging

Phone Agent supports remote ADB debugging via WiFi/network, allowing device control without a USB connection.

### Configure Remote Debugging

#### Enable Wireless Debugging on Phone

Ensure the phone and computer are on the same WiFi network, as shown below:

![Enable Wireless Debugging](resources/setting.png)

#### Use Standard ADB Commands on Computer

```bash
# Connect via WiFi, replace with the IP address and port shown on your phone
adb connect 192.168.1.100:5555

# Verify connection
adb devices
# Should show: 192.168.1.100:5555    device
```

### Device Management Commands

```bash
# List all connected devices
adb devices

# Connect to remote device
adb connect 192.168.1.100:5555

# Disconnect specific device
adb disconnect 192.168.1.100:5555

# Execute task on specific device
python main.py --device-id 192.168.1.100:5555 --base-url http://localhost:8000/v1 --model "autoglm-phone-9b" "Open TikTok and browse videos"
```

### Python API Remote Connection

```python
from phone_agent.adb import ADBConnection, list_devices

# Create connection manager
conn = ADBConnection()

# Connect to remote device
success, message = conn.connect("192.168.1.100:5555")
print(f"Connection status: {message}")

# List connected devices
devices = list_devices()
for device in devices:
    print(f"{device.device_id} - {device.connection_type.value}")

# Enable TCP/IP on USB device
success, message = conn.enable_tcpip(5555)
ip = conn.get_device_ip()
print(f"Device IP: {ip}")

# Disconnect
conn.disconnect("192.168.1.100:5555")
```

### Remote Connection Troubleshooting

**Connection Refused:**

- Ensure the device and computer are on the same network
- Check if the firewall is blocking port 5555
- Confirm TCP/IP mode is enabled: `adb tcpip 5555`

**Connection Dropped:**

- WiFi may have disconnected; use `--connect` to reconnect
- Some devices disable TCP/IP after restart; re-enable via USB

**Multiple Devices:**

- Use `--device-id` to specify which device to use
- Or use `--list-devices` to view all connected devices

## Configuration

### Custom SYSTEM PROMPT

The system provides both Chinese and English prompts, switchable via the `--lang` parameter:

- `--lang cn` - Chinese prompt (default), config file: `phone_agent/config/prompts_zh.py`
- `--lang en` - English prompt, config file: `phone_agent/config/prompts_en.py`

You can directly modify the corresponding config files to enhance model capabilities in specific domains or disable certain apps by injecting app names.

### Environment Variables

| Variable                  | Description               | Default Value                |
|---------------------------|---------------------------|------------------------------|
| `PHONE_AGENT_BASE_URL`    | Model API URL             | `http://localhost:8000/v1`   |
| `PHONE_AGENT_MODEL`       | Model name                | `autoglm-phone-9b`           |
| `PHONE_AGENT_MAX_STEPS`   | Maximum steps per task    | `100`                        |
| `PHONE_AGENT_DEVICE_ID`   | ADB device ID             | (auto-detect)                |
| `PHONE_AGENT_LANG`        | Language (`cn` or `en`)   | `cn`                         |

### Model Configuration

```python
from phone_agent.model import ModelConfig

config = ModelConfig(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",  # API key (if required)
    model_name="autoglm-phone-9b",  # Model name
    max_tokens=3000,  # Maximum output tokens
    temperature=0.1,  # Sampling temperature
    frequency_penalty=0.2,  # Frequency penalty
)
```

### Agent Configuration

```python
from phone_agent.agent import AgentConfig

config = AgentConfig(
    max_steps=100,  # Maximum steps per task
    device_id=None,  # ADB device ID (None for auto-detect)
    lang="cn",  # Language: cn (Chinese) or en (English)
    verbose=True,  # Print debug info (including thinking process and actions)
)
```

### Verbose Mode Output

When `verbose=True`, the Agent outputs detailed information at each step:

```
==================================================
💭 Thinking Process:
--------------------------------------------------
Currently on the system desktop, need to launch Xiaohongshu app first
--------------------------------------------------
🎯 Executing Action:
{
  "_metadata": "do",
  "action": "Launch",
  "app": "Xiaohongshu"
}
==================================================

... (continues to next step after executing action)

==================================================
💭 Thinking Process:
--------------------------------------------------
Xiaohongshu is now open, need to tap the search box
--------------------------------------------------
🎯 Executing Action:
{
  "_metadata": "do",
  "action": "Tap",
  "element": [500, 100]
}
==================================================

🎉 ================================================
✅ Task Complete: Successfully searched for food guides
==================================================
```

This allows you to clearly see the AI's reasoning process and specific operations at each step.

## Supported Apps

Phone Agent supports 50+ mainstream Chinese applications:

| Category          | Apps                                    |
|-------------------|-----------------------------------------|
| Social & Messaging| WeChat, QQ, Weibo                       |
| E-commerce        | Taobao, JD.com, Pinduoduo              |
| Food & Delivery   | Meituan, Ele.me, KFC                   |
| Travel            | Ctrip, 12306, Did                     |
| Video & Entertainment | Bilibili, TikTok, iQiyi            |
| Music & Audio     | NetEase Music, QQ Music, Ximalaya      |
| Life Services     | Dianping, Amap, Baidu Maps             |
| Content Communities| Xiaohongshu, Zhihu, Douban            |

Run `python main.py --list-apps` to see the complete list.

## Available Actions

The Agent can perform the following actions:

| Action         | Description                              |
|----------------|------------------------------------------|
| `Launch`       | Launch an app                            |  
| `Tap`          | Tap at specified coordinates             |
| `Type`         | Input text                               |
| `Swipe`        | Swipe the screen                         |
| `Back`         | Go back to previous page                 |
| `Home`         | Return to home screen                    |
| `Long Press`   | Long press                               |
| `Double Tap`   | Double tap                               |
| `Wait`         | Wait for page to load                    |
| `Take_over`    | Request manual takeover (login/captcha)  |

## Custom Callbacks

Handle sensitive operation confirmation and manual takeover:

```python
def my_confirmation(message: str) -> bool:
    """Sensitive operation confirmation callback"""
    return input(f"Confirm execution of {message}? (y/n): ").lower() == "y"


def my_takeover(message: str) -> None:
    """Manual takeover callback"""
    print(f"Please complete manually: {message}")
    input("Press Enter after completion...")


agent = PhoneAgent(
    confirmation_callback=my_confirmation,
    takeover_callback=my_takeover,
)
```

## Examples

Check the `examples/` directory for more usage examples:

- `basic_usage.py` - Basic task execution
- Single-step debugging mode
- Batch task execution
- Custom callbacks

## Development

### Set Up Development Environment

Development requires dev dependencies:

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Complete Project Structure

```
phone_agent/
├── __init__.py          # Package exports
├── agent.py             # PhoneAgent main class
├── adb/                 # ADB utilities
│   ├── connection.py    # Remote/local connection management
│   ├── screenshot.py    # Screen capture
│   ├── input.py         # Text input (ADB Keyboard)
│   └── device.py        # Device control (tap, swipe, etc.)
├── actions/             # Action handling
│   └── handler.py       # Action executor
├── config/              # Configuration
│   ├── apps.py          # Supported app mappings
│   ├── prompts_zh.py    # Chinese system prompts
│   └── prompts_en.py    # English system prompts
└── model/               # AI model client
    └── client.py        # OpenAI-compatible client
```

## FAQ

Here are some common issues and their solutions:

### Device Not Found

Try resolving by restarting the ADB service:

```bash
adb kill-server
adb start-server
adb devices
```

### Text Input Not Working

1. Ensure ADB Keyboard is installed on the device
2. Enable it in Settings > System > Language & Input > Virtual Keyboard
3. The Agent will automatically switch to ADB Keyboard when input is needed

### Screenshot Failed (Black Screen)

This usually means the app is displaying a sensitive page (payment, password, banking apps). The Agent will automatically detect this and request manual takeover.

### Windows Encoding Issues
Error message like `UnicodeEncodeError gbk code`

Solution: Add the environment variable before running the code: `PYTHONIOENCODING=utf-8`

### Interactive Mode Not Working in Non-TTY Environment
Error like: `EOF when reading a line`

Solution: Use non-interactive mode to specify tasks directly, or switch to a TTY-mode terminal application.

### Citation

If you find our work helpful, please cite the following papers:

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
