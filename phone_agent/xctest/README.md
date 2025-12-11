# XCTest - iOS 设备自动化

这个模块为 Phone Agent 提供 iOS 设备的自动化控制能力,类似于 Android 的 ADB 功能。

## 架构说明

XCTest 模块通过以下工具与 iOS 设备交互:

1. **WebDriverAgent (WDA)**: 主要的自动化引擎,提供 HTTP API 来控制 iOS 设备
2. **libimobiledevice**: 用于设备连接管理和截图备用方案
3. **idevice tools**: 命令行工具集 (`idevice_id`, `ideviceinfo`, `idevicescreenshot` 等)

## 前置要求

### 1. 安装 libimobiledevice

```bash
# macOS
brew install libimobiledevice

# Linux (Ubuntu/Debian)
sudo apt-get install libimobiledevice-utils

# 验证安装
idevice_id -l
```

### 2. 安装 WebDriverAgent

WebDriverAgent 是 iOS 自动化的核心组件,需要在 iOS 设备上运行。

#### 方式一: 使用 Appium WebDriverAgent (推荐)

```bash
# 1. 克隆 WebDriverAgent
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent

# 2. 安装依赖
./Scripts/bootstrap.sh

# 3. 在 Xcode 中打开项目
open WebDriverAgent.xcodeproj

# 4. 配置签名
# - 选择 WebDriverAgentRunner target
# - 在 Signing & Capabilities 中选择你的开发团队
# - 修改 Bundle Identifier (例如: com.yourname.WebDriverAgentRunner)

# 5. 连接 iOS 设备并运行
# - 选择你的设备作为目标
# - 运行 WebDriverAgentRunner scheme (Product > Test 或 Cmd+U)

# 6. 设置端口转发 (如果通过 USB 连接)
iproxy 8100 8100
```

#### 方式二: 使用 facebook-wda (Python 库)

```bash
pip install facebook-wda

# 使用 wda 命令行工具
python -m wda.cli --list  # 列出设备
python -m wda.cli --port 8100  # 启动 WDA 代理
```

### 3. 安装 Python 依赖

```bash
pip install requests Pillow
```

## 使用示例

### 基础连接测试

```python
from phone_agent.xctest import XCTestConnection, list_devices

# 列出所有连接的 iOS 设备
devices = list_devices()
for device in devices:
    print(f"{device.device_id} - {device.model} - iOS {device.ios_version}")

# 检查 WebDriverAgent 状态
conn = XCTestConnection(wda_url="http://localhost:8100")
if conn.is_wda_ready():
    print("WebDriverAgent is ready!")
else:
    print("WebDriverAgent is not running. Please start it first.")
```

### 设备控制

```python
from phone_agent.xctest import tap, swipe, home, launch_app

# 点击屏幕坐标
tap(100, 200)

# 滑动屏幕
swipe(100, 500, 100, 100)  # 向上滑动

# 返回主屏幕
home()

# 启动应用 (需要在 apps.py 中配置 bundle ID)
launch_app("Safari")
```

### 截图

```python
from phone_agent.xctest import get_screenshot
from phone_agent.xctest.screenshot import save_screenshot

# 获取截图
screenshot = get_screenshot()
print(f"Screenshot size: {screenshot.width}x{screenshot.height}")

# 保存截图
save_screenshot(screenshot, "screenshot.png")
```

### 文本输入

```python
from phone_agent.xctest import tap, type_text, clear_text

# 1. 点击输入框以获得焦点
tap(200, 400)

# 2. 输入文本
type_text("Hello, iPhone!")

# 3. 清除文本
clear_text()

# 4. 隐藏键盘
from phone_agent.xctest.input import hide_keyboard
hide_keyboard()
```

## 完整示例

```python
from phone_agent.xctest import (
    XCTestConnection,
    get_screenshot,
    tap,
    type_text,
    home,
    launch_app,
)

# 1. 检查连接
conn = XCTestConnection(wda_url="http://localhost:8100")

if not conn.is_connected():
    print("No iOS device connected!")
    exit(1)

if not conn.is_wda_ready():
    print("WebDriverAgent is not running!")
    exit(1)

# 2. 获取设备信息
device = conn.get_device_info()
print(f"Connected to: {device.device_name} (iOS {device.ios_version})")

# 3. 返回主屏幕
home()

# 4. 启动应用
launch_app("Safari")

# 5. 等待应用启动并截图
import time
time.sleep(2)
screenshot = get_screenshot()
print(f"Screenshot captured: {screenshot.width}x{screenshot.height}")

# 6. 点击地址栏
tap(200, 100)

# 7. 输入 URL
type_text("https://www.apple.com")
```

## 支持的操作

| 操作 | 函数 | 说明 |
|------|------|------|
| 点击 | `tap(x, y)` | 点击指定坐标 |
| 双击 | `double_tap(x, y)` | 双击指定坐标 |
| 长按 | `long_press(x, y, duration)` | 长按指定坐标 |
| 滑动 | `swipe(x1, y1, x2, y2)` | 从起点滑动到终点 |
| 返回 | `back()` | 模拟返回手势 (从左边缘滑动) |
| 主屏幕 | `home()` | 返回主屏幕 |
| 启动应用 | `launch_app(app_name)` | 启动指定应用 |
| 截图 | `get_screenshot()` | 获取屏幕截图 |
| 输入文本 | `type_text(text)` | 输入文本到焦点输入框 |
| 清除文本 | `clear_text()` | 清除焦点输入框的文本 |
| 隐藏键盘 | `hide_keyboard()` | 隐藏屏幕键盘 |

## 配置应用 Bundle ID

要支持 `launch_app()` 功能,需要在 `phone_agent/config/apps.py` 中添加 iOS 应用的 Bundle ID:

```python
APP_PACKAGES: dict[str, str] = {
    # iOS apps
    "Safari": "com.apple.mobilesafari",
    "Settings": "com.apple.Preferences",
    "Photos": "com.apple.mobileslideshow",
    "Camera": "com.apple.camera",
    "Notes": "com.apple.mobilenotes",

    # 第三方应用示例
    "WeChat": "com.tencent.xin",
    "Chrome": "com.google.chrome.ios",
    # ... 更多应用
}
```

### 如何找到应用的 Bundle ID?

```python
from phone_agent.xctest import XCTestConnection

conn = XCTestConnection()
status = conn.get_wda_status()
if status:
    current_app = status.get("value", {}).get("currentApp", {})
    print(f"Bundle ID: {current_app.get('bundleId')}")
```

## 网络调试

如果设备和电脑在同一 WiFi 网络中,可以直接通过 IP 地址连接:

```python
# 1. 在 iOS 设备上运行 WebDriverAgent,记下设备 IP (例如: 192.168.1.100)

# 2. 使用设备 IP 连接
conn = XCTestConnection(wda_url="http://192.168.1.100:8100")

# 3. 后续操作与 USB 连接相同
screenshot = get_screenshot(wda_url="http://192.168.1.100:8100")
```

## 常见问题

### 1. idevice_id 找不到设备

**解决方案:**
```bash
# 重启 usbmuxd 服务
sudo killall usbmuxd

# 重新插拔 USB 线
# 在 iOS 设备上点击"信任此电脑"

# 验证配对
idevicepair pair
```

### 2. WebDriverAgent 无法启动

**可能原因:**
- 未在 Xcode 中配置签名
- Bundle ID 冲突
- 设备未信任开发者证书

**解决方案:**
1. 在 iOS 设备上: 设置 > 通用 > VPN与设备管理 > 信任开发者
2. 确保 Xcode 中选择了正确的开发团队
3. 修改 Bundle Identifier 为唯一值

### 3. 截图返回黑屏

**原因:** 某些系统界面或敏感内容可能无法截图

**解决方案:** 使用 `is_sensitive` 标志判断,并请求人工确认

### 4. 文本输入不工作

**解决方案:**
1. 确保先点击输入框获得焦点
2. 使用 `is_keyboard_shown()` 检查键盘是否已显示
3. 如果键盘未显示,可能需要调整点击位置

### 5. requests 库 SSL 警告

WebDriverAgent 使用自签名证书,会产生 SSL 警告。代码中已使用 `verify=False` 忽略这些警告。

如果希望消除警告信息:
```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

## 性能优化

1. **复用 WDA Session**: 创建一次 session 并重复使用
2. **批量操作**: 减少 HTTP 请求次数
3. **调整延迟**: 根据设备性能调整 `delay` 参数
4. **使用网络连接**: WiFi 连接通常比 USB 更稳定

## 与 Android ADB 的对比

| 功能 | Android (ADB) | iOS (XCTest) |
|------|---------------|--------------|
| 连接方式 | USB / WiFi | USB / WiFi |
| 核心工具 | adb | libimobiledevice + WDA |
| 文本输入 | ADB Keyboard | WDA 键盘 API |
| 截图 | screencap | WDA screenshot API |
| 应用标识 | Package name | Bundle ID |
| 返回按钮 | 系统按钮 | 左边缘滑动手势 |

## 参考资源

- [WebDriverAgent GitHub](https://github.com/appium/WebDriverAgent)
- [libimobiledevice](https://libimobiledevice.org/)
- [Appium iOS Documentation](https://appium.io/docs/en/drivers/ios-xcuitest/)
- [facebook-wda](https://github.com/openatx/facebook-wda)
