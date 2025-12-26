# Connecting a Setup-Ready iPhone

This guide explains how to connect your iPhone to Phone Agent after WebDriverAgent has been installed and configured.

## Prerequisites

Before proceeding, ensure:
- ✅ WebDriverAgent is installed on your iPhone (see [iOS Setup Guide](ios_setup.md))
- ✅ Your iPhone is trusted by your Mac
- ✅ UI Automation is enabled on your iPhone (Settings → Developer → UI Automation)
- ✅ `libimobiledevice` is installed on your Mac: `brew install libimobiledevice`

## Step 1: Check Device Connection

First, verify that your iPhone is connected and recognized:

```bash
# List connected iOS devices
idevice_id -l

# Or use Phone Agent to list devices
python ios.py --list-devices
```

You should see your device's UDID. If not:
1. Connect your iPhone via USB
2. Unlock your iPhone
3. Tap "Trust This Computer" if prompted
4. Try the command again

## Step 2: Start WebDriverAgent

WebDriverAgent must be running on your iPhone. You have two options:

### Option A: Start via Xcode (Recommended for first-time setup)

1. Open `WebDriverAgent.xcodeproj` in Xcode
2. Select your iPhone as the target device
3. Select `WebDriverAgentRunner` scheme
4. Press `Cmd+U` (or Product → Test) to run
5. Wait for "Automation Running" to appear on your iPhone screen
6. Note the WDA URL from Xcode console: `ServerURLHere->http://[IP]:8100<-ServerURLHere`

### Option B: Start via Command Line

```bash
cd WebDriverAgent

xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination 'platform=iOS,name=YOUR_PHONE_NAME' \
           test
```

Replace `YOUR_PHONE_NAME` with your device name (visible in Xcode).

## Step 3: Choose Connection Method

You can connect via USB or WiFi. Choose based on your setup:

### USB Connection (Recommended)

1. **Set up port forwarding** (in a separate terminal):
   ```bash
   iproxy 8100 8100
   ```
   Keep this terminal running while using Phone Agent.

2. **Use default WDA URL**:
   ```bash
   python ios.py --wda-url http://localhost:8100 "Your task here"
   ```

### WiFi Connection

1. **Get your iPhone's IP address**:
   - Settings → Wi-Fi → Tap the (i) next to your network
   - Note the IP address (e.g., `192.168.1.100`)

2. **Ensure iPhone is on the same WiFi network as your Mac**

3. **Use the device IP in WDA URL**:
   ```bash
   python ios.py --wda-url http://192.168.1.100:8100 "Your task here"
   ```

   Replace `192.168.1.100` with your iPhone's actual IP address.

## Step 4: Verify Connection

Before running tasks, verify everything is working:

```bash
# Check WebDriverAgent status
python ios.py --wda-status

# Or check with a specific WDA URL
python ios.py --wda-url http://localhost:8100 --wda-status
```

You should see:
```
✓ WebDriverAgent is running
Status details:
  Session ID: [some-id]
  Build: [timestamp]
```

If you see an error:
- **"WebDriverAgent is not running"**: Go back to Step 2 and start WebDriverAgent
- **"Connection refused"**: Check your port forwarding (USB) or IP address (WiFi)
- **"Cannot connect"**: Verify your iPhone and Mac are on the same network (WiFi) or USB is connected

## Step 5: Run Phone Agent

Once everything is verified, you can run Phone Agent:

```bash
# Basic usage with USB connection
python ios.py \
    --base-url "YOUR_BASE_URL" \
    --model "autoglm-phone-9b" \
    --api-key "YOUR_API_KEY" \
    --wda-url http://localhost:8100 \
    "Open Safari and search for iPhone tips"

# With WiFi connection
python ios.py \
    --base-url "YOUR_BASE_URL" \
    --model "autoglm-phone-9b" \
    --api-key "YOUR_API_KEY" \
    --wda-url http://192.168.1.100:8100 \
    "Open Safari and search for iPhone tips"
```

## Troubleshooting

### Device Not Found

```bash
# Check if device is connected
idevice_id -l

# If empty, try:
# 1. Unplug and replug USB cable
# 2. Unlock iPhone
# 3. Trust computer again
# 4. Restart libimobiledevice services
```

### WebDriverAgent Not Accessible

**For USB:**
```bash
# Check if iproxy is running
ps aux | grep iproxy

# If not, start it:
iproxy 8100 8100

# Test connection
curl http://localhost:8100/status
```

**For WiFi:**
```bash
# Test connection directly
curl http://192.168.1.100:8100/status

# If fails, check:
# 1. iPhone and Mac are on same WiFi network
# 2. iPhone IP address is correct
# 3. Firewall isn't blocking port 8100
```

### WebDriverAgent Crashes or Stops

1. Restart WebDriverAgent via Xcode (Cmd+U)
2. Check iPhone screen for error messages
3. Verify UI Automation is still enabled (Settings → Developer)
4. Re-trust the developer certificate if needed

### Port Already in Use

```bash
# Find process using port 8100
lsof -i :8100

# Kill the process if needed
kill -9 [PID]

# Or use a different port
iproxy 8101 8100
python ios.py --wda-url http://localhost:8101
```

## Quick Reference

| Connection Type | WDA URL | Port Forwarding Required |
|----------------|---------|-------------------------|
| USB | `http://localhost:8100` | Yes (`iproxy 8100 8100`) |
| WiFi | `http://[iPhone-IP]:8100` | No |

## Environment Variables

You can set these to avoid typing them every time:

```bash
export PHONE_AGENT_WDA_URL="http://localhost:8100"
export PHONE_AGENT_BASE_URL="http://localhost:8000/v1"
export PHONE_AGENT_MODEL="autoglm-phone-9b"
export PHONE_AGENT_API_KEY="your-api-key"
```

Then simply run:
```bash
python ios.py "Your task here"
```

## Next Steps

- See [iOS Setup Guide](ios_setup.md) for initial WebDriverAgent installation
- Check [Main README](../../README.md) for more usage examples
- Run `python ios.py --list-apps` to see supported apps

