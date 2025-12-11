# Open-AutoGLM

[中文阅读.](./README.md)

<div align="center">
<img src=resources/logo.svg width="20%"/>
</div>
<p align="center">
    👋 Join our <a href="resources/WECHAT.md" target="_blank">WeChat</a> and <a href="https://discord.gg/QR7SARHRxK" target="_blank">Discord</a> communities
</p>

## Project Introduction

Phone Agent is a mobile intelligent assistant framework built on AutoGLM. It understands phone screen content in a multimodal manner and helps users complete tasks through automated operations. The system controls devices via ADB (Android Debug Bridge), perceives screens using vision-language models, and generates and executes operation workflows through intelligent planning. Users simply describe their needs in natural language, such as "Open eBay and search for wireless earphones." and Phone Agent will automatically parse the intent, understand the current interface, plan the next action, and complete the entire workflow. The system also includes a sensitive operation confirmation mechanism and supports manual takeover during login or verification code scenarios. Additionally, it provides remote ADB debugging capabilities, allowing device connection via WiFi or network for flexible remote control and development.
> ⚠️ This project is for research and learning purposes only. It is strictly prohibited to use for illegal information acquisition, system interference, or any illegal activities. Please carefully review the [Terms of Use](resources/privacy_policy_en.txt).

## Model Download Links

| Model             | Download Links                                                                                                                                             |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| AutoGLM-Phone-9B  | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B)<br>[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B)               |
| AutoGLM-Phone-9B-Multilingual | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B-Multilingual)<br>[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B-Multilingual) |

`AutoGLM-Phone-9B` is optimized for Chinese mobile applications, while `AutoGLM-Phone-9B-Multilingual` supports English scenarios and is suitable for applications containing English or other language content.

## Environment Setup

### 1. Python Environment

Python 3.10 or higher is recommended.

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

![Permissions](resources/screenshot-20251210-120416.png)

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

You can choose to deploy the model service yourself or use a third-party model service provider.

#### Option A: Use Third-Party Model Services

If you don't want to deploy the model yourself, you can use the following third-party services that have already deployed our model:

**1. z.ai**

- Documentation: https://docs.z.ai/api-reference/introduction
- `--base-url`: `https://api.z.ai/api/paas/v4`
- `--model`: `autoglm-phone-multilingual`
- `--apikey`: Apply for your own API key on the z.ai platform

**2. Novita AI**

- Documentation: https://novita.ai/models/model-detail/zai-org-autoglm-phone-9b-multilingual
- `--base-url`: `https://api.novita.ai/openai`
- `--model`: `zai-org/autoglm-phone-9b-multilingual`
- `--apikey`: Apply for your own API key on the Novita AI platform

**3. Parasail**

- Documentation: https://www.saas.parasail.io/serverless?name=auto-glm-9b-multilingual
- `--base-url`: `https://api.parasail.io/v1`
- `--model`: `parasail-auto-glm-9b-multilingual`
- `--apikey`: Apply for your own API key on the Parasail platform

Example usage with third-party services:

```bash
# Using z.ai
python main.py --base-url https://api.z.ai/api/paas/v4 --model "autoglm-phone-multilingual" --apikey "your-z-ai-api-key" "Open Chrome browser"

# Using Novita AI
python main.py --base-url https://api.novita.ai/openai --model "zai-org/autoglm-phone-9b-multilingual" --apikey "your-novita-api-key" "Open Chrome browser"

# Using Parasail
python main.py --base-url https://api.parasail.io/v1 --model "parasail-auto-glm-9b-multilingual" --apikey "your-parasail-api-key" "Open Chrome browser"
```

#### Option B: Deploy Model Yourself

If you prefer to deploy the model locally or on your own server:

1. Download the model and install the inference engine framework according to the `For Model Deployment` section in `requirements.txt`.
2. Start via SGlang / vLLM to get an OpenAI-format service. Here's a vLLM deployment solution; please strictly follow the startup parameters we provide:

- vLLM:

```shell
python3 -m vllm.entrypoints.openai.api_server \
 --served-model-name autoglm-phone-9b-multilingual \
 --allowed-local-media-path /   \
 --mm-encoder-tp-mode data \
 --mm_processor_cache_type shm \
 --mm_processor_kwargs "{\"max_pixels\":5000000}" \
 --max-model-len 25480  \
 --chat-template-content-format string \
 --limit-mm-per-prompt "{\"image\":10}" \
 --model zai-org/AutoGLM-Phone-9B-Multilingual \
 --port 8000
```

- This model has the same architecture as `GLM-4.1V-9B-Thinking`. For detailed information about model deployment, you can also check [GLM-V](https://github.com/zai-org/GLM-V) for model deployment and usage guides.

- After successful startup, the model service will be accessible at `http://localhost:8000/v1`. If you deploy the model on a remote server, access it using that server's IP address.

## Using AutoGLM

### Command Line

Set the `--base-url` and `--model` parameters according to your deployed model. For example:

```bash
# Interactive mode
python main.py --base-url http://localhost:8000/v1 --model "autoglm-phone-9b-multilingual"

# Specify model endpoint
python main.py --base-url http://localhost:8000/v1 "Open Maps and search for nearby coffee shops"

# Use API key for authentication
python main.py --apikey sk-xxxxx

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
    model_name="autoglm-phone-9b-multilingual",
)

# Create Agent
agent = PhoneAgent(model_config=model_config)

# Execute task
result = agent.run("Open eBay and search for wireless earphones")
print(result)
```

## Remote Debugging

Phone Agent supports remote ADB debugging via WiFi/network, allowing device control without a USB connection.

### Configure Remote Debugging

#### Enable Wireless Debugging on Phone

Ensure the phone and computer are on the same WiFi network, as shown below:

![Enable Wireless Debugging](resources/screenshot-20251210-120630.png)

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
python main.py --device-id 192.168.1.100:5555 --base-url http://localhost:8000/v1 --model "autoglm-phone-9b-multilingual" "Open TikTok and browse videos"
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

| Variable                  | Description               | Default Value              |
|---------------------------|---------------------------|----------------------------|
| `PHONE_AGENT_BASE_URL`    | Model API URL             | `http://localhost:8000/v1` |
| `PHONE_AGENT_MODEL`       | Model name                | `autoglm-phone-9b`         |
| `PHONE_AGENT_API_KEY`     | API key for authentication| `EMPTY`                    |
| `PHONE_AGENT_MAX_STEPS`   | Maximum steps per task    | `100`                      |
| `PHONE_AGENT_DEVICE_ID`   | ADB device ID             | (auto-detect)              |
| `PHONE_AGENT_LANG`        | Language (`cn` or `en`)   | `en`                       |

### Model Configuration

```python
from phone_agent.model import ModelConfig

config = ModelConfig(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",  # API key (if required)
    model_name="autoglm-phone-9b-multilingual",  # Model name
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
    lang="en",  # Language: cn (Chinese) or en (English)
    verbose=True,  # Print debug info (including thinking process and actions)
)
```

### Verbose Mode Output

When `verbose=True`, the Agent outputs detailed information at each step:

```
==================================================
💭 Thinking Process:
--------------------------------------------------
Currently on the system desktop, need to launch eBay app first
--------------------------------------------------
🎯 Executing Action:
{
  "_metadata": "do",
  "action": "Launch",
  "app": "eBay"
}
==================================================

... (continues to next step after executing action)

==================================================
💭 Thinking Process:
--------------------------------------------------
eBay is now open, need to tap the search box
--------------------------------------------------
🎯 Executing Action:
{
  "_metadata": "do",
  "action": "Tap",
  "element": [499, 182]
}
==================================================

🎉 ================================================
✅ Task Completed: Successfully opened eBay and searched for 'wireless earphones'
==================================================
```

This allows you to clearly see the AI's reasoning process and specific operations at each step.

## Supported Apps

Phone Agent supports 50+ mainstream Chinese applications:

| Category                 | Apps                                                                                   |
|--------------------------|----------------------------------------------------------------------------------------|
| Social & Messaging       | X, Tiktok, WhatsApp, Telegram, FacebookMessenger, GoogleChat, Quora, Reddit, Instagram |
| Productivity & Office    | Gmail, GoogleCalendar, GoogleDrive, GoogleDocs, GoogleTasks, Joplin                    |
| Life, Shopping & Finance | Amazon shopping, Temu, Bluecoins, Duolingo, GoogleFit, ebay                            |
| Utilities & Media        | GoogleClock, Chrome, GooglePlayStore, GooglePlayBooks, FilesbyGoogle                   |
| Travel & Navigation      | GoogleMaps, Booking.com, Trip.com, Expedia, OpenTracks                                 |

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

If the device is still not recognized, please check:
1. Whether USB debugging is enabled
2. Whether the USB cable supports data transfer (some cables only support charging)
3. Whether you have tapped "Allow" on the authorization popup on your phone
4. Try a different USB port or cable

### Can Open Apps but Cannot Tap

Some devices require both debugging options to be enabled:
- **USB Debugging**
- **USB Debugging (Security Settings)**

Please check in `Settings → Developer Options` that both options are enabled.

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

---

## Automated Deployment Guide (For AI Assistants)

> **This section is specifically designed for AI assistants (such as Claude Code) to automate the deployment of Open-AutoGLM.**
>
> If you are a human reader, you can skip this section and follow the documentation above.

---

### Project Overview

Open-AutoGLM is a phone agent framework:
- **Input**: User's natural language instructions (e.g., "Open WhatsApp and send a message to John")
- **Output**: Automatically operates the user's Android phone to complete tasks
- **Mechanism**: Screenshot → Vision model understands interface → Outputs tap coordinates → ADB executes actions → Loop

The architecture consists of two parts:
1. **Agent Code** (this repository): Runs on the user's computer, responsible for calling models, parsing actions, and controlling the phone
2. **Vision Model Service**: Can be a remote API or deployed locally

---

### Pre-Deployment Checklist

Before starting deployment, confirm the following items with the user:

#### Hardware Requirements
- [ ] User has an Android phone (Android 7.0+)
- [ ] User has a USB cable that supports data transfer (not just charging)
- [ ] Phone and computer can be connected via USB cable

#### Phone Configuration
- [ ] Phone has Developer Mode enabled (Settings → About Phone → Tap Build Number 7 times)
- [ ] Phone has USB Debugging enabled (Settings → Developer Options → USB Debugging)
- [ ] Some models require enabling "USB Debugging (Security Settings)" as well
- [ ] ADB Keyboard app is installed (Download: https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk)
- [ ] ADB Keyboard is enabled in system settings (Settings → Language & Input → Enable ADB Keyboard)

#### Model Service Confirmation (Choose One)

**Ask the user explicitly: Do you already have access to an AutoGLM model service?**

- **Option A: Use an already-deployed model service (Recommended)**
  - User provides the model service URL (e.g., `http://xxx.xxx.xxx.xxx:8000/v1`)
  - No local GPU required, no model download needed
  - Use this URL directly as the `--base-url` parameter

- **Option B: Deploy model locally (High system requirements)**
  - Requires NVIDIA GPU (24GB+ VRAM recommended)
  - Requires installation of vLLM or SGLang
  - Requires downloading approximately 20GB of model files
  - **If the user is a beginner or unsure, strongly recommend Option A**

---

### Deployment Process

#### Phase 1: Environment Setup

```bash
# 1. Install ADB tools
# MacOS:
brew install android-platform-tools
# Or download manually: https://developer.android.com/tools/releases/platform-tools

# Windows: Download, extract, and add to PATH environment variable

# 2. Verify ADB installation
adb version
# Should output version information

# 3. Connect phone and verify
# Connect phone via USB cable, tap "Allow USB debugging" on phone
adb devices
# Should output device list, e.g.:
# List of devices attached
# XXXXXXXX    device
```

**If `adb devices` shows empty list or unauthorized:**
1. Check if authorization popup appeared on phone, tap "Allow"
2. Check if USB debugging is enabled
3. Try a different cable or USB port
4. Run `adb kill-server && adb start-server` and retry

#### Phase 2: Install Agent

```bash
# 1. Clone repository (if not already cloned)
git clone https://github.com/zai-org/Open-AutoGLM.git
cd Open-AutoGLM

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -e .
```

**Note: No need to clone model repository; models are called via API.**

#### Phase 3: Configure Model Service

**If user chooses Option A (using already-deployed model):**

You can use the following third-party model services:

1. **z.ai**
   - Documentation: https://docs.z.ai/api-reference/introduction
   - `--base-url`: `https://api.z.ai/api/paas/v4`
   - `--model`: `autoglm-phone-multilingual`
   - `--apikey`: Apply for your own API key on the z.ai platform

2. **Novita AI**
   - Documentation: https://novita.ai/models/model-detail/zai-org-autoglm-phone-9b-multilingual
   - `--base-url`: `https://api.novita.ai/openai`
   - `--model`: `zai-org/autoglm-phone-9b-multilingual`
   - `--apikey`: Apply for your own API key on the Novita AI platform

3. **Parasail**
   - Documentation: https://www.saas.parasail.io/serverless?name=auto-glm-9b-multilingual
   - `--base-url`: `https://api.parasail.io/v1`
   - `--model`: `parasail-auto-glm-9b-multilingual`
   - `--apikey`: Apply for your own API key on the Parasail platform

Example usage:

```bash
# Using z.ai
python main.py --base-url https://api.z.ai/api/paas/v4 --model "autoglm-phone-multilingual" --apikey "your-z-ai-api-key" "Open Chrome browser"

# Using Novita AI
python main.py --base-url https://api.novita.ai/openai --model "zai-org/autoglm-phone-9b-multilingual" --apikey "your-novita-api-key" "Open Chrome browser"

# Using Parasail
python main.py --base-url https://api.parasail.io/v1 --model "parasail-auto-glm-9b-multilingual" --apikey "your-parasail-api-key" "Open Chrome browser"
```

Or use the URL provided by the user directly and skip local model deployment steps.

**If user chooses Option B (deploy model locally):**

```bash
# 1. Install vLLM
pip install vllm

# 2. Start model service (will auto-download model, ~20GB)
python3 -m vllm.entrypoints.openai.api_server \
  --served-model-name autoglm-phone-9b-multilingual \
  --allowed-local-media-path / \
  --mm-encoder-tp-mode data \
  --mm_processor_cache_type shm \
  --mm_processor_kwargs "{\"max_pixels\":5000000}" \
  --max-model-len 25480 \
  --chat-template-content-format string \
  --limit-mm-per-prompt "{\"image\":10}" \
  --model zai-org/AutoGLM-Phone-9B-Multilingual \
  --port 8000

# Model service URL: http://localhost:8000/v1
```

#### Phase 4: Verify Deployment

```bash
# Execute in the Open-AutoGLM directory
# Replace {MODEL_URL} with the actual model service address

python main.py --base-url {MODEL_URL} --model "autoglm-phone-9b-multilingual" "Open Gmail and send an email to File Transfer Assistant: Deployment successful"
```

**Expected Result:**
- Phone automatically opens Gmail
- Automatically searches for recipient
- Automatically sends the message "Deployment successful"

---

### Troubleshooting

| Error Symptom | Possible Cause | Solution |
|---------------|----------------|----------|
| `adb devices` shows nothing | USB debugging not enabled or cable issue | Check developer options, replace cable |
| `adb devices` shows unauthorized | Phone not authorized | Tap "Allow USB debugging" on phone |
| Can open apps but cannot tap | Missing security debugging permission | Enable "USB Debugging (Security Settings)" |
| Chinese/text input corrupted or missing | ADB Keyboard not enabled | Enable ADB Keyboard in system settings |
| Screenshot returns black screen | Sensitive page (payment/banking) | Normal behavior, system will handle automatically |
| Cannot connect to model service | Wrong URL or service not running | Check URL, confirm service is running |
| `ModuleNotFoundError` | Dependencies not installed | Run `pip install -r requirements.txt` |

---

### Deployment Key Points

1. **Prioritize confirming phone connection**: Before installing any code, ensure `adb devices` can see the device
2. **Don't skip ADB Keyboard**: Without it, text input will fail
3. **Model service is an external dependency**: Agent code doesn't include the model; a separate model service is required
4. **Check phone settings first for permission issues**: Most problems are due to incomplete phone-side configuration
5. **Test with simple tasks after deployment**: Recommend using "Open Gmail and send message to File Transfer Assistant" as acceptance criteria

---

### Command Quick Reference

```bash
# Check ADB connection
adb devices

# Restart ADB service
adb kill-server && adb start-server

# Install dependencies
pip install -r requirements.txt && pip install -e .

# Run Agent (interactive mode)
python main.py --base-url {MODEL_URL} --model "autoglm-phone-9b-multilingual"

# Run Agent (single task)
python main.py --base-url {MODEL_URL} --model "autoglm-phone-9b-multilingual" "your task description"

# View supported apps list
python main.py --list-apps
```

---

**Deployment success indicator: The phone can automatically execute user's natural language instructions.**
