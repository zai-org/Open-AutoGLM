# Connecting iPhone to Phone Agent - Complete Setup Guide

This guide covers the complete setup process for connecting your iPhone to Phone Agent, including cross-computer setups (iPhone on Mac, Phone Agent on Windows).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup (Mac)](#initial-setup-mac)
3. [Connection Methods](#connection-methods)
4. [Cross-Computer Setup (Windows PC)](#cross-computer-setup-windows-pc)
5. [Model Service Setup](#model-service-setup)
6. [Running Phone Agent](#running-phone-agent)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### On Your Mac:
- ✅ macOS with Xcode installed
- ✅ Apple Developer account (free account works)
- ✅ iPhone connected via USB or on same WiFi network
- ✅ `libimobiledevice` installed: `brew install libimobiledevice`

### On Your Windows PC (if using cross-computer setup):
- ✅ Python 3.10+ installed
- ✅ Phone Agent repository cloned
- ✅ SSH client (built into Windows 10/11)

### On Your iPhone:
- ✅ Developer mode enabled
- ✅ UI Automation enabled (Settings → Developer → UI Automation)
- ✅ Device trusted by your Mac

## Initial Setup (Mac)

### Step 1: Install WebDriverAgent

1. **Clone WebDriverAgent:**
   ```bash
   git clone https://github.com/appium/WebDriverAgent.git
   cd WebDriverAgent
   ```

2. **Open in Xcode:**
   ```bash
   open WebDriverAgent.xcodeproj
   ```

3. **Configure Signing:**
   - Select `WebDriverAgent` in the project navigator
   - Go to **Signing & Capabilities**
   - Check **Automatically manage signing**
   - Select your Team (Apple Developer account)
   - Change Bundle ID to something unique (e.g., `com.yourname.WebDriverAgentRunner`)
   - Repeat for `WebDriverAgentLib`, `WebDriverAgentRunner`, and `IntegrationApp` targets

### Step 2: Start WebDriverAgent

**Option A: Via Xcode (Recommended)**
1. Select `WebDriverAgentRunner` scheme
2. Select your iPhone as the target device
3. Press `Cmd+U` (or Product → Test)
4. Wait for "Automation Running" to appear on your iPhone
5. Check Xcode console for the server URL: `ServerURLHere->http://[IP]:8100<-ServerURLHere`

**Option B: Via Command Line**
```bash
cd WebDriverAgent
xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination 'platform=iOS,name=YOUR_PHONE_NAME' \
           test
```

### Step 3: Device Trust Configuration

On your iPhone, complete these steps (first time only):

1. **Trust Developer App:**
   - Settings → General → VPN & Device Management
   - Tap your developer account
   - Tap "Trust [Your Name]"

2. **Enable UI Automation:**
   - Settings → Developer → UI Automation
   - Toggle it ON

3. **Re-run WebDriverAgent** after completing these steps

## Connection Methods

### Method 1: USB Connection (Same Computer)

**On your Mac:**

1. **Set up port forwarding:**
   ```bash
   iproxy 8100 8100
   ```
   Keep this terminal running.

2. **Use Phone Agent:**
   ```bash
   python ios.py --wda-url http://localhost:8100 --base-url YOUR_MODEL_URL --model YOUR_MODEL "Your task"
   ```

### Method 2: WiFi Connection (Same Computer)

1. **Get iPhone's IP address:**
   - Settings → Wi-Fi → Tap (i) next to your network
   - Note the IP address (e.g., `192.168.86.249`)

2. **Ensure Mac and iPhone are on the same WiFi network**

3. **Use Phone Agent:**
   ```bash
   python ios.py --wda-url http://192.168.86.249:8100 --base-url YOUR_MODEL_URL --model YOUR_MODEL "Your task"
   ```

## Cross-Computer Setup (Windows PC)

If your iPhone is connected to a Mac, but you want to run Phone Agent on Windows:

### Step 1: Find Your Mac's Information

**On your Mac:**

1. **Find your Mac username:**
   ```bash
   whoami
   ```
   Example output: `john`

2. **Find your Mac's IP address:**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
   Or: System Settings → Network → Wi-Fi → Details → IP Address
   Example: `192.168.86.100`

### Step 2: Enable SSH on Mac

**On your Mac:**
1. System Settings → General → Sharing → Remote Login
2. Enable Remote Login
3. Or via command line:
   ```bash
   sudo systemsetup -setremotelogin on
   ```

### Step 3: Set Up SSH Port Forwarding

**On your Mac:**
1. Start WebDriverAgent (see [Initial Setup](#initial-setup-mac))
2. If using USB, run port forwarding:
   ```bash
   iproxy 8100 8100
   ```
   Keep this terminal running.

**On your Windows PC:**

1. **Open PowerShell and create SSH tunnel:**
   ```powershell
   ssh -L 8100:localhost:8100 YOUR_MAC_USERNAME@YOUR_MAC_IP
   ```
   
   Example:
   ```powershell
   ssh -L 8100:localhost:8100 john@192.168.86.100
   ```

2. **Enter your Mac password when prompted**

3. **Keep this PowerShell window open** - the SSH tunnel must stay active

### Step 4: Verify Connection from Windows

**On your Windows PC:**

```powershell
# Test WebDriverAgent connection
python ios.py --wda-url http://localhost:8100 --wda-status
```

You should see:
```
✓ WebDriverAgent is running
Status details:
  Session ID: [some-id]
  Build: [timestamp]
```

## Model Service Setup

You need a model API service to run Phone Agent. Choose one option:

### Option 1: Cloud Model Services (Easiest - Recommended)

No local installation needed. Sign up for one of these services:

**z.ai:**
- Sign up: https://docs.z.ai/api-reference/introduction
- Get your API key
- Use: `--base-url https://api.z.ai/api/paas/v4 --model "autoglm-phone-multilingual" --api-key "your-key"`

**Novita AI:**
- Sign up: https://novita.ai/models/model-detail/zai-org-autoglm-phone-9b-multilingual
- Get your API key
- Use: `--base-url https://api.novita.ai/openai --model "zai-org/autoglm-phone-9b-multilingual" --api-key "your-key"`

**Parasail:**
- Sign up: https://www.saas.parasail.io/serverless?name=auto-glm-9b-multilingual
- Get your API key
- Use: `--base-url https://api.parasail.io/v1 --model "parasail-auto-glm-9b-multilingual" --api-key "your-key"`

### Option 2: Local Model Server (WSL2 on Windows)

If you have a local model and want to run it on Windows:

**Prerequisites:**
- WSL2 installed (Windows Subsystem for Linux)
- NVIDIA GPU (recommended) or CPU (slower)

**Setup Steps:**

1. **Install WSL2 (if not installed):**
   ```powershell
   wsl --install
   ```
   Restart your computer after installation.

2. **Open WSL2 and set up environment:**
   ```powershell
   wsl
   ```

3. **In WSL2, install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv -y
   
   # Create virtual environment
   cd ~
   python3 -m venv vllm-env
   source vllm-env/bin/activate
   
   # Install PyTorch (for CUDA support)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   
   # Install vLLM
   pip install vllm
   pip install transformers>=5.0.0rc0
   ```

4. **Start model server in WSL2:**
   ```bash
   source ~/vllm-env/bin/activate
   
   python3 -m vllm.entrypoints.openai.api_server \
       --served-model-name autoglm-phone-9b \
       --allowed-local-media-path / \
       --mm-encoder-tp-mode data \
       --mm_processor_cache_type shm \
       --mm_processor_kwargs '{"max_pixels":5000000}' \
       --max-model-len 25480 \
       --chat-template-content-format string \
       --limit-mm-per-prompt '{"image":10}' \
       --model /mnt/b/huggingface_cache/AutoGLM-Phone-9B \
       --port 8000 \
       --host 0.0.0.0
   ```
   
   **Important:** Replace `/mnt/b/huggingface_cache/AutoGLM-Phone-9B` with your actual model path.
   The `--host 0.0.0.0` flag allows Windows to access the server.

5. **Keep WSL2 terminal running** - the model server must stay active

6. **From Windows PowerShell, use:**
   ```powershell
   python ios.py --wda-url http://localhost:8100 --base-url http://localhost:8000/v1 --model "autoglm-phone-9b" "Your task"
   ```

### Option 3: Run Model Server on Mac

If your Mac has a GPU, you can run the model server there:

**On your Mac:**
```bash
pip install vllm

python3 -m vllm.entrypoints.openai.api_server \
    --served-model-name autoglm-phone-9b \
    --allowed-local-media-path / \
    --mm-encoder-tp-mode data \
    --mm_processor_cache_type shm \
    --mm_processor_kwargs '{"max_pixels":5000000}' \
    --max-model-len 25480 \
    --chat-template-content-format string \
    --limit-mm-per-prompt '{"image":10}' \
    --model /path/to/AutoGLM-Phone-9B \
    --port 8000 \
    --host 0.0.0.0
```

**On Windows, use Mac's IP:**
```powershell
python ios.py --wda-url http://localhost:8100 --base-url http://YOUR_MAC_IP:8000/v1 --model "autoglm-phone-9b" "Your task"
```

## Running Phone Agent

### Complete Setup Checklist

Before running, ensure:

- ✅ WebDriverAgent is running on iPhone (Xcode shows "Automation Running")
- ✅ SSH tunnel is active (if using cross-computer setup)
- ✅ Model server is running (if using local model)
- ✅ All terminal windows are kept open

### Basic Usage

**With cloud service:**
```powershell
python ios.py `
    --wda-url http://localhost:8100 `
    --base-url https://api.z.ai/api/paas/v4 `
    --model "autoglm-phone-multilingual" `
    --api-key "your-api-key" `
    "Open Chrome and search for iPhone tips"
```

**With local model (WSL2):**
```powershell
python ios.py `
    --wda-url http://localhost:8100 `
    --base-url http://localhost:8000/v1 `
    --model "autoglm-phone-9b" `
    "Open Chrome and search for iPhone tips"
```

**Interactive mode:**
```powershell
python ios.py --wda-url http://localhost:8100 --base-url YOUR_MODEL_URL --model YOUR_MODEL --api-key YOUR_KEY
```

### Environment Variables (Optional)

Set these to avoid typing parameters every time:

**PowerShell:**
```powershell
$env:PHONE_AGENT_WDA_URL = "http://localhost:8100"
$env:PHONE_AGENT_BASE_URL = "http://localhost:8000/v1"
$env:PHONE_AGENT_MODEL = "autoglm-phone-9b"
$env:PHONE_AGENT_API_KEY = "your-api-key"
```

Then simply run:
```powershell
python ios.py "Your task here"
```

## Troubleshooting

### WebDriverAgent Not Accessible

**Symptoms:** Connection refused or timeout errors

**Solutions:**
1. Verify WebDriverAgent is running on iPhone (check Xcode console)
2. Check iPhone shows "Automation Running" on screen
3. For USB: Ensure `iproxy 8100 8100` is running on Mac
4. For SSH: Verify SSH tunnel is active (`ssh -L 8100:localhost:8100 ...`)
5. Test connection:
   ```powershell
   python ios.py --wda-url http://localhost:8100 --wda-status
   ```

### SSH Connection Fails

**Symptoms:** Cannot connect to Mac via SSH

**Solutions:**
1. Verify SSH is enabled on Mac (System Settings → Sharing → Remote Login)
2. Check Mac's IP address is correct
3. Ensure both computers are on the same network
4. Test SSH connection:
   ```powershell
   ssh YOUR_USERNAME@MAC_IP
   ```

### Model Server Not Accessible

**Symptoms:** Connection errors when calling model API

**Solutions:**
1. **For WSL2:** Ensure model server is running and using `--host 0.0.0.0`
2. **For cloud services:** Verify API key is correct
3. Test model API:
   ```powershell
   python -c "import requests; r = requests.get('YOUR_BASE_URL/models'); print(r.status_code)"
   ```

### App Launch Fails

**Symptoms:** Agent keeps trying to launch the same app repeatedly

**Solutions:**
1. Verify app is installed on iPhone
2. Check app name is correct (use `python ios.py --list-apps` to see supported apps)
3. Common aliases work: "chrome" → "Google Chrome", "safari" → "Safari"
4. If app launch fails, the agent will show error messages - check those for details

### libimobiledevice Not Found (Windows)

**Symptoms:** Warning about libimobiledevice not being installed

**Note:** This is **normal and safe to ignore** on Windows when using SSH port forwarding or WiFi connections. libimobiledevice is only needed for direct USB device detection, which isn't required for cross-computer setups.

### Port Already in Use

**Symptoms:** Port 8100 or 8000 already in use

**Solutions:**
```powershell
# Find process using port (Windows)
netstat -ano | findstr :8100

# Kill process if needed
taskkill /PID [PID] /F

# Or use different port
# For SSH: ssh -L 8101:localhost:8100 ...
# For Phone Agent: --wda-url http://localhost:8101
```

### Agent Stuck in Loop

**Symptoms:** Agent keeps repeating the same action

**Solutions:**
1. Check error messages - they will indicate what's failing
2. Verify WebDriverAgent is responding (test with `--wda-status`)
3. Check model API is working
4. Try a simpler task first to verify setup
5. Press Ctrl+C to stop and restart

## Quick Reference

### Connection Types

| Setup | WDA URL | Requirements |
|-------|---------|--------------|
| USB (Mac only) | `http://localhost:8100` | `iproxy 8100 8100` running |
| WiFi (Mac only) | `http://[iPhone-IP]:8100` | Same WiFi network |
| SSH (Mac → Windows) | `http://localhost:8100` | SSH tunnel active |
| Direct Network | `http://[Mac-IP]:8100` | WDA listening on network |

### Required Running Processes

For cross-computer setup, you need **3 terminals/processes running**:

1. **Terminal 1 (Mac):** WebDriverAgent (Xcode or command line)
2. **Terminal 2 (Mac):** Port forwarding (`iproxy 8100 8100` if using USB)
3. **Terminal 3 (Windows):** SSH tunnel (`ssh -L 8100:localhost:8100 ...`)
4. **Terminal 4 (Optional):** Model server (if using local model)

### Common Commands

```powershell
# Check WebDriverAgent status
python ios.py --wda-url http://localhost:8100 --wda-status

# List supported apps
python ios.py --list-apps

# List connected devices (requires libimobiledevice on Mac)
python ios.py --list-devices

# Run a task
python ios.py --wda-url http://localhost:8100 --base-url YOUR_URL --model YOUR_MODEL "Your task"
```

## Next Steps

- See [iOS Setup Guide](ios_setup.md) for initial WebDriverAgent installation details
- Check [Main README](../../README.md) for more usage examples and features
- Run `python ios.py --list-apps` to see all supported iOS apps
