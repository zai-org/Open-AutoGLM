# iOS 环境配置指南

本文档介绍如何为 Open-AutoGLM 配置 iOS 设备环境。

## 环境要求

- macOS 操作系统
- Xcode（最新版本，在 App store 中下载）
- 苹果开发者账号（免费账号即可，无需付费）
- iOS 设备（iPhone/iPad）
- USB 数据线或同一 WiFi 网络

## WebDriverAgent 配置

WebDriverAgent 是 iOS 自动化的核心组件，需要在 iOS 设备上运行。

### 1. 克隆 WebDriverAgent

```bash
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent
```

直接点击`WebDriverAgent.xcodeproj`即可使用 Xcode 打开。

### 2. 设置 Signing & Capabilities

1. 在 Xcode 中选中 `WebDriverAgent`，出现 General、Signing&Capabilities 等选项。
2. 进入 `Signing & Capabilities` 选项卡
3. 勾选 `Automatically manage signing`。在 Team 中选择自己的开发者账号
4. 将 Bundle ID 改为唯一标识符，例如：`com.yourname.WebDriverAgentRunner`
![设置签名 1](resources/ios0_WebDriverAgent0.png)

5. TARGETS 中，建议将 WebDriverAgentLib、WebDriverAgentRunner、IntegrationApp 的`Signing & Capabilities` 都按照相同方式设置。
![设置签名 1](resources/ios0_WebDriverAgent1.png)

### 3. 测试 XCode 的 GUI 模式和 UI 自动化设置

建议先测试 GUI 模式能否成功安装 WebDriverAgent，再进行后续步骤。
Mac 和 iPhone 有 USB 和 WiFi 两种连接方式，建议通过 USB 方式，成功率更高。

#### 通过 WiFi 连接

需要满足以下条件：

1. 通过 USB 连接。在 Finder 中选中连接的 IPhone，在“通用”中勾选"在 WiFi 中显示这台 iPhone"
2. Mac 与 iPhone 处于同一 WiFi 网络之下

#### 具体步骤

1. 从项目 Target 选择 `WebDriverAgentRunner`
2. 选择你的设备

   ![选择设备](resources/select-your-iphone-device.png)

3. 长按"▶️"运行按钮，选择 "Test" 后开始编译并部署到你的 iPhone 上

   ![开始测试](resources/start-wda-testing.png)

部署成功的标志：1. XCode 没有报错。2. 你可以在 iPhone 上找到名为 WebDriverAgentRunner 的 App

#### 设备信任配置

首次运行时，需要在 iPhone 上完成以下设置，然后重新编译和部署：

1. **输入解锁密码**
2. **信任开发者应用**
   - 进入：设置 → 通用 → VPN 与设备管理
   - 在“开发者 App”中选择对应开发者
   - 点击信任“XXX”

   ![信任设备](resources/trust-dev-app.jpg)

3. **启用 UI 自动化**
   - 进入：设置 → 开发者
   - 打开 UI 自动化设置

   ![启用 UI 自动化](resources/enable-ui-automation.jpg)

### 4. XCode 命令行模式部署

1.安装 libimobiledevice，用于与 iPhone / iPad 建立连接与通信。

   ```bash
   brew install libimobiledevice
   # 设备检查
   idevice_id -ln
   ```

2.使用 xcodebuild 安装 WebAgent。命令行也需要进行“设备信任配置”，参考 GUI 模式下的方法。

```bash
cd WebDriverAgent

xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination 'platform=iOS,name=YOUR_PHONE_NAME' \
           test
```

这里，YOUR_PHONE_NAME 可以在 xcode 的 GUI 中看到。
WebDriverAgent 成功运行后，会在 Xcode 控制台输出类似以下信息：

```text
ServerURLHere->http://[设备 IP]:8100<-ServerURLHere
```

同时，观察到手机上安装好了 WebDriverAgentRunner，屏幕显示 Automation Running 字样。
其中，**http://[设备 IP]:8100**为 WiFi 所需的 WDA_URL。

## 使用 AutoGLM

以上配置完成后，先打开一个新终端，在后台建立端口映射（使用 WiFi 连接则不需要）：

```bash
iproxy 8100 8100
```

之后，打开一个新终端，通过以下命令使用 AutoGLM（WiFi 则使用上述获得的 WDA_URL）：

```bash
python ios.py --base-url "YOUR_BASE_URL" \
    --model  "autoglm-phone" \
    --api-key "YOUR_API_KEY" \
    --wda-url http://localhost:8100 \
    "TASK"
```

## 参考资源

- [WebDriverAgent 官方仓库](https://github.com/appium/WebDriverAgent)
- [PR141](https://github.com/zai-org/Open-AutoGLM/pull/141)
- [Gekowa 提供的 ios 方案](https://github.com/gekowa/Open-AutoGLM/tree/ios-support)

---

如有其他问题，请参考主项目 README 或提交 Issue。
