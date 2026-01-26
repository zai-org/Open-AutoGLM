# iOS Environment Setup Guide

This document describes how to configure iOS device environment for Open-AutoGLM.

## Requirements

- macOS operating system
- Xcode (latest version, download from App Store)
- Apple Developer Account (free account is sufficient, paid account not required)
- iOS device (iPhone/iPad)
- USB cable or same WiFi network


## WebDriverAgent Configuration

WebDriverAgent is the core component for iOS automation and needs to run on the iOS device.

### 1. Clone WebDriverAgent

```bash
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent
```

Simply click on `WebDriverAgent.xcodeproj` to open it in Xcode.

### 2. Configure Signing & Capabilities

1. Select `WebDriverAgent` in Xcode, and options like General, Signing&Capabilities will appear.
2. Go to the `Signing & Capabilities` tab
3. Check `Automatically manage signing`. Select your developer account in Team
4. Change Bundle ID to a unique identifier, for example: `com.yourname.WebDriverAgentRunner`
![Configure Signing 1](resources/ios0_WebDriverAgent0.png)

5. In TARGETS, it's recommended to configure `Signing & Capabilities` for WebDriverAgentLib, WebDriverAgentRunner, and IntegrationApp in the same way.
![Configure Signing 2](resources/ios0_WebDriverAgent1.png)

### 3. Test XCode GUI Mode and UI Automation Settings

It's recommended to first test whether GUI mode can successfully install WebDriverAgent before proceeding to subsequent steps.
Mac and iPhone have two connection methods: USB and WiFi. USB connection is recommended as it has a higher success rate.

#### Connect via WiFi

The following conditions must be met:
1. Connect via USB. Select the connected iPhone in Finder, and check "Show this iPhone when on WiFi" in "General"
2. Mac and iPhone are on the same WiFi network

#### Steps
1. Select `WebDriverAgentRunner` from project Target
2. Select your device

![Select Device](resources/select-your-iphone-device.png)

3. Long press the "▶️" run button, select "Test" to start compiling and deploying to your iPhone

![Start Testing](resources/start-wda-testing.png)

Signs of successful deployment: 1. XCode shows no errors. 2. You can find the app named WebDriverAgentRunner on your iPhone

#### Device Trust Configuration

On first run, you need to complete the following settings on iPhone, then recompile and redeploy:

1. **Enter unlock password**
2. **Trust developer app**
   - Go to: Settings → General → VPN & Device Management
   - Select the corresponding developer under "Developer App"
   - Tap Trust "XXX"

   ![Trust Device](resources/trust-dev-app.jpg)

3. **Enable UI Automation**
   - Go to: Settings → Developer
   - Turn on UI Automation settings

   ![Enable UI Automation](resources/enable-ui-automation.jpg)

### 4. XCode Command Line Deployment

1. Install libimobiledevice for establishing connection and communication with iPhone / iPad.

```
brew install libimobiledevice
# Check devices
idevice_id -ln
```
2. Use xcodebuild to install WebAgent. Command line also requires "Device Trust Configuration", refer to the GUI mode method.

```
cd WebDriverAgent

xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination 'platform=iOS,name=YOUR_PHONE_NAME' \
           test
```
Here, YOUR_ PHONE_NAME can be seen in the Xcode GUI.
After WebDriverAgent runs successfully, it will output information similar to the following in the console:

```
ServerURLHere->http://[Device_IP]:8100<-ServerURLHere
```

At the same time, you should observe that WebDriverAgentRunner is installed on the phone, and the screen displays "Automation Running".
Here, **http://[Device_IP]:8100** is the WDA_URL needed for WiFi connection.

## Using AutoGLM

After completing the above configuration, first open a new terminal and establish port mapping in the background (not needed for WiFi connection):

```bash
 iproxy 8100 8100
```

Then, open a new terminal and use AutoGLM with the following command (for WiFi, use the WDA_URL obtained above):

```bash
python ios.py --base-url "YOUR_BASE_URL" \
    --model  "autoglm-phone" \
    --api-key "YOUR_API_KEY" \
    --wda-url http://localhost:8100 \
    "TASK"
```

## References

- [WebDriverAgent Official Repository](https://github.com/appium/WebDriverAgent)
- [PR141](https://github.com/zai-org/Open-AutoGLM/pull/141)
- [iOS Solution by Gekowa](https://github.com/gekowa/Open-AutoGLM/tree/ios-support)

---

For other questions, please refer to the main project README or submit an Issue.
