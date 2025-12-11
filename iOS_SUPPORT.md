# iOS 设备支持

Open-AutoGLM 现在支持 iOS 设备自动化!通过 `phone_agent.xctest` 模块,您可以像控制 Android 设备一样控制 iPhone 和 iPad。

## 🆕 新功能

- ✅ iOS 设备连接管理 (USB / WiFi)
- ✅ 屏幕截图
- ✅ 触控操作 (点击、滑动、长按、双击)
- ✅ 文本输入
- ✅ 应用启动
- ✅ 主屏幕和导航控制

## 快速开始

### 1. 安装依赖

#### macOS

```bash
# 安装 libimobiledevice (iOS 设备通信工具)
brew install libimobiledevice

# 安装 Python 依赖
pip install requests Pillow

# 验证安装
idevice_id -l
```

#### Linux (Ubuntu/Debian)

```bash
# 安装 libimobiledevice
sudo apt-get install libimobiledevice-utils

# 安装 Python 依赖
pip install requests Pillow
```

### 2. 设置 WebDriverAgent

WebDriverAgent 是 iOS 自动化的核心组件,需要在 iOS 设备上运行。

#### 下载并配置

```bash
# 1. 克隆 WebDriverAgent
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent

# 2. 安装依赖
./Scripts/bootstrap.sh

# 3. 在 Xcode 中打开
open WebDriverAgent.xcodeproj
```

#### 配置签名

1. 选择 `WebDriverAgentRunner` target
2. 在 "Signing & Capabilities" 中选择你的开发团队
3. 修改 Bundle Identifier (例如: `com.yourname.WebDriverAgentRunner`)

#### 运行 WebDriverAgent

1. 连接 iOS 设备
2. 在 Xcode 中选择你的设备
3. 运行 WebDriverAgentRunner scheme (`Product > Test` 或 `Cmd+U`)
4. 在设备上信任开发者证书: `设置 > 通用 > VPN与设备管理`

#### 设置端口转发 (USB 连接)

```bash
# 安装 iproxy
brew install libusbmuxd

# 转发端口 8100
iproxy 8100 8100
```

### 3. 运行示例

```bash
# 运行 iOS 基础示例
python examples/ios_basic_usage.py
```

## 使用示例

### Python API

```python
from phone_agent.xctest import (
    XCTestConnection,
    list_devices,
    get_screenshot,
    tap,
    swipe,
    home,
    launch_app,
)
from phone_agent.xctest.input import type_text, hide_keyboard

# 1. 列出设备
devices = list_devices()
for device in devices:
    print(f"{device.device_name} - iOS {device.ios_version}")

# 2. 检查 WebDriverAgent
conn = XCTestConnection(wda_url="http://localhost:8100")
if conn.is_wda_ready():
    print("WebDriverAgent 就绪!")

# 3. 设备控制
home()  # 返回主屏幕
tap(100, 200)  # 点击
swipe(100, 500, 100, 100)  # 向上滑动

# 4. 截图
screenshot = get_screenshot()
print(f"Screenshot: {screenshot.width}x{screenshot.height}")

# 5. 启动应用
launch_app("Safari")

# 6. 文本输入
tap(200, 100)  # 点击输入框
type_text("Hello, iPhone!")
hide_keyboard()
```

## 配置 iOS 应用

要使用 `launch_app()` 功能,需要在 `phone_agent/config/apps.py` 中添加 iOS 应用的 Bundle ID:

```python
APP_PACKAGES: dict[str, str] = {
    # iOS 系统应用
    "Safari": "com.apple.mobilesafari",
    "Settings": "com.apple.Preferences",
    "Photos": "com.apple.mobileslideshow",
    "Camera": "com.apple.camera",
    "Notes": "com.apple.mobilenotes",
    "Maps": "com.apple.Maps",
    "Music": "com.apple.Music",
    "AppStore": "com.apple.AppStore",

    # 第三方应用 (示例)
    "WeChat": "com.tencent.xin",
    "Chrome": "com.google.chrome.ios",
    "YouTube": "com.google.ios.youtube",
    "Twitter": "com.atebits.Tweetie2",
    # ... 更多应用
}
```

### 如何查找 Bundle ID?

**方法 1: 通过 WebDriverAgent**

```python
from phone_agent.xctest import XCTestConnection

conn = XCTestConnection()
status = conn.get_wda_status()
if status:
    current_app = status.get("value", {}).get("currentApp", {})
    print(f"当前应用 Bundle ID: {current_app.get('bundleId')}")
```

**方法 2: 通过 ideviceinstaller**

```bash
# 安装工具
brew install ideviceinstaller

# 列出所有已安装应用
ideviceinstaller -l

# 输出示例:
# com.apple.mobilesafari - Safari
# com.tencent.xin - WeChat
```

## 网络调试 (WiFi)

如果设备和电脑在同一 WiFi 网络中,可以无线连接:

```python
# 使用设备 IP 地址
wda_url = "http://192.168.1.100:8100"  # 替换为你的设备 IP

conn = XCTestConnection(wda_url=wda_url)

# 所有操作都使用这个 URL
screenshot = get_screenshot(wda_url=wda_url)
tap(100, 200, wda_url=wda_url)
```

## 支持的操作对照表

| 操作 | Android (ADB) | iOS (XCTest) |
|------|---------------|--------------|
| 点击 | `tap(x, y)` | `tap(x, y, wda_url=...)` |
| 双击 | `double_tap(x, y)` | `double_tap(x, y, wda_url=...)` |
| 长按 | `long_press(x, y, duration_ms)` | `long_press(x, y, duration, wda_url=...)` |
| 滑动 | `swipe(x1, y1, x2, y2)` | `swipe(x1, y1, x2, y2, wda_url=...)` |
| 返回 | `back()` | `back(wda_url=...)` (左边缘滑动) |
| 主屏幕 | `home()` | `home(wda_url=...)` |
| 启动应用 | `launch_app(name)` | `launch_app(name, wda_url=...)` |
| 截图 | `get_screenshot()` | `get_screenshot(wda_url=...)` |
| 文本输入 | `type_text(text)` | `type_text(text, wda_url=...)` |
| 清除文本 | `clear_text()` | `clear_text(wda_url=...)` |

## 常见问题

### 1. idevice_id 找不到设备

```bash
# 重启 usbmuxd 服务
sudo killall usbmuxd

# 重新插拔 USB 线
# 在 iOS 设备上点击"信任此电脑"

# 验证配对
idevicepair pair
```

### 2. WebDriverAgent 无法启动

**检查清单:**
- [ ] 在 Xcode 中配置了开发团队签名
- [ ] Bundle Identifier 是唯一的
- [ ] 在 iOS 设备上信任了开发者证书
- [ ] 设备已解锁

**信任开发者证书:**
`设置 > 通用 > VPN与设备管理 > 开发者App > 信任`

### 3. 端口 8100 无法访问

**USB 连接:**
```bash
# 检查 iproxy 是否运行
ps aux | grep iproxy

# 重启端口转发
killall iproxy
iproxy 8100 8100
```

**WiFi 连接:**
- 确保设备和电脑在同一网络
- 使用设备 IP 地址: `http://<device-ip>:8100`
- 检查防火墙设置

### 4. 截图返回黑屏

尝试使用 idevicescreenshot 备用方案:

```bash
# 测试 idevicescreenshot
idevicescreenshot test.png

# 如果失败,检查设备配对
idevicepair validate
```

### 5. 文本输入无响应

```python
# 1. 先点击输入框
tap(x, y, wda_url=wda_url)
time.sleep(0.5)

# 2. 检查键盘是否显示
from phone_agent.xctest.input import is_keyboard_shown
if is_keyboard_shown(wda_url=wda_url):
    type_text("your text", wda_url=wda_url)
else:
    print("键盘未显示,请调整点击位置")
```

## 性能优化建议

1. **使用 WiFi 连接**: 通常比 USB 更稳定
2. **复用 WDA Session**: 减少 HTTP 请求
3. **调整延迟参数**: 根据设备性能调整 `delay`
4. **批量操作**: 减少网络往返

## 已知限制

1. **需要 macOS 或 Linux**: Windows 对 libimobiledevice 支持有限
2. **需要 Xcode**: 用于编译和运行 WebDriverAgent (仅 macOS)
3. **需要开发者证书**: 免费的也可以,但每 7 天需要重新签名
4. **某些系统界面**: 可能无法截图或交互(如系统设置的某些页面)
5. **后台应用**: WebDriverAgent 可能会在后台被 iOS 挂起

## 更多资源

- [XCTest 模块详细文档](phone_agent/xctest/README.md)
- [iOS 示例代码](examples/ios_basic_usage.py)
- [WebDriverAgent 官方文档](https://github.com/appium/WebDriverAgent)
- [libimobiledevice 项目](https://libimobiledevice.org/)

## 技术架构

```
iOS 设备
    ↓ (USB / WiFi)
libimobiledevice (idevice_id, idevicepair, etc.)
    ↓
WebDriverAgent (在 iOS 设备上运行)
    ↓ (HTTP REST API)
phone_agent.xctest 模块
    ↓
Phone Agent 核心
```

## 贡献

欢迎贡献 iOS 相关的改进:

- 添加更多 iOS 应用的 Bundle ID 映射
- 优化 WebDriverAgent 交互逻辑
- 改进错误处理和重连机制
- 添加更多自动化操作

## 致谢

iOS 支持基于以下开源项目:

- [WebDriverAgent](https://github.com/appium/WebDriverAgent) - iOS 自动化引擎
- [libimobiledevice](https://libimobiledevice.org/) - iOS 设备通信库
- [facebook-wda](https://github.com/openatx/facebook-wda) - Python WebDriverAgent 客户端参考
