# Open-AutoGLM iOS 适配指南

本文档说明如何在 iOS 设备上运行 Open-AutoGLM Phone Agent。

## 📋 前置条件

1. **WebDriverAgent 已就绪**
   - 确保 WDA 已在 iOS 设备上启动（通过Xcode运行）
   - 获取 WDA URL，通常为 `http://localhost:8100`（通过USB转发）

2. **模型服务已启动**
   - 可以使用本地部署或第三方服务（智谱BigModel、Novita等）

## ⚠️ 重要：USB端口转发

由于iOS安全限制，WiFi直连WDA通常会被阻断。**推荐使用USB端口转发**：

```bash
# 安装 libimobiledevice（如未安装）
brew install libimobiledevice

# 启动端口转发（在单独的终端窗口运行，保持运行）
iproxy 8100 8100

# 现在可以通过 http://localhost:8100 访问WDA
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd Open-AutoGLM
pip install -r requirements.txt
pip install -e .
```

### 2. 启动USB端口转发

```bash
# 终端窗口1 - 保持运行
iproxy 8100 8100
```

### 3. 检查 WDA 连接

```bash
# 终端窗口2
python main_ios.py --check-only
# 或明确指定URL
python main_ios.py --wda-url http://localhost:8100 --check-only
```

### 4. 运行 iOS Agent

```bash
# 使用智谱BigModel
python main_ios.py \
    --base-url https://open.bigmodel.cn/api/paas/v4 \
    --model autoglm-phone \
    --apikey YOUR_API_KEY \
    "打开小红书搜索美食"

# 交互模式
python main_ios.py \
    --base-url https://open.bigmodel.cn/api/paas/v4 \
    --model autoglm-phone \
    --apikey YOUR_API_KEY
```

### 4. 查看支持的 iOS App

```bash
python main_ios.py --list-apps
```

## 📁 项目结构

```
phone_agent/
├── adb/              # Android ADB 实现（原有）
├── wda/              # iOS WebDriverAgent 实现（新增）
│   ├── __init__.py   # 导出接口
│   ├── client.py     # HTTP 客户端
│   ├── device.py     # 设备操作（tap/swipe/home等）
│   ├── input.py      # 文本输入
│   └── screenshot.py # 截图
├── actions/
│   ├── handler.py    # Android Action Handler
│   └── handler_ios.py # iOS Action Handler（新增）
├── agent.py          # Android Agent
├── agent_ios.py      # iOS Agent（新增）
└── config/
    └── apps_ios.py   # iOS App Bundle ID 映射（新增）
```

## 🔌 启动 WebDriverAgent

### 方法1: 通过 Xcode

```bash
xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination 'id=YOUR_DEVICE_UDID' \
           test
```

### 方法2: 查看设备 UDID

```bash
# 模拟器
xcrun simctl list devices available

# 真机
xcrun xctrace list devices
```

### 获取 WDA URL

启动后在日志中查找：
```
ServerURLHere->http://[DEVICE_IP]:8100<-ServerURLHere
```

## ⚠️ iOS 与 Android 的差异

| 功能 | Android | iOS |
|------|---------|-----|
| 返回 | 物理/虚拟Back键 | 左边缘滑动或点击左上角返回 |
| 键盘 | 需要ADB Keyboard | 使用原生键盘 |
| 启动App | 通过包名 | 通过Bundle ID |
| 截图 | ADB screencap | WDA /screenshot |

## 🛠️ 常见问题

### WDA 连接失败

1. 确保设备和电脑在同一网络
2. 检查 WDA 是否正常运行
3. 确认防火墙没有阻止 8100 端口

### 截图失败

1. 可能是敏感界面（如支付页面）
2. WDA 会返回黑色占位图

### App 启动失败

1. 检查 `apps_ios.py` 中是否有该 App 的 Bundle ID
2. 可以手动添加新 App 的映射

## 📝 添加新 App 支持

编辑 `phone_agent/config/apps_ios.py`：

```python
IOS_APP_PACKAGES = {
    # 添加新 App
    "新App中文名": "com.example.bundleid",
    "NewAppEnglish": "com.example.bundleid",
    ...
}
```

## 🔗 相关链接

- [WebDriverAgent GitHub](https://github.com/appium/WebDriverAgent)
- [Open-AutoGLM 主仓库](https://github.com/zai-org/Open-AutoGLM)
- [智谱AI API](https://open.bigmodel.cn)

