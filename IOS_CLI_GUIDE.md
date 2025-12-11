# iOS CLI 使用指南 (ios.py)

`ios.py` 是专门为 iOS 设备自动化设计的命令行入口,功能类似于 Android 的 `main.py`,但使用 WebDriverAgent 和 libimobiledevice 与 iOS 设备交互。

## 🚀 快速开始

### 1. 安装依赖

```bash
# macOS
brew install libimobiledevice

# 安装 Python 依赖
pip install -r requirements.txt

# 验证安装
idevice_id -l
```

### 2. 设置 WebDriverAgent

```bash
# 克隆并设置 WebDriverAgent
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent
./Scripts/bootstrap.sh

# 在 Xcode 中打开并配置签名
open WebDriverAgent.xcodeproj

# 配置完成后,在 Xcode 中运行 WebDriverAgentRunner (Cmd+U)
```

### 3. 设置端口转发 (USB 连接)

```bash
# 安装 libusbmuxd
brew install libusbmuxd

# 转发端口
iproxy 8100 8100
```

### 4. 运行 ios.py

```bash
# 检查设备
python ios.py --list-devices

# 检查 WebDriverAgent
python ios.py --wda-status

# 运行任务
python ios.py "Open Safari"
```

## 📋 命令行选项

### 基本选项

```bash
python ios.py [OPTIONS] [TASK]
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--base-url URL` | 模型 API 地址 | `http://localhost:8000/v1` |
| `--model NAME` | 模型名称 | `autoglm-phone-9b` |
| `--max-steps N` | 最大步数 | `100` |
| `--device-id UDID` | iOS 设备 UDID | 自动检测 |
| `--wda-url URL` | WebDriverAgent URL | `http://localhost:8100` |
| `--lang cn\|en` | 系统提示语言 | `cn` |
| `--quiet, -q` | 静默模式 | `False` |

### 设备管理选项

| 选项 | 说明 |
|------|------|
| `--list-devices` | 列出所有连接的 iOS 设备 |
| `--pair` | 与 iOS 设备配对 |
| `--wda-status` | 显示 WebDriverAgent 状态 |
| `--list-apps` | 列出支持的应用 |

## 🔧 使用示例

### 设备管理

```bash
# 列出所有 iOS 设备
python ios.py --list-devices

# 输出示例:
# Connected iOS devices:
# ----------------------------------------------------------------------
#   ✓ My iPhone
#     UDID: 00008030-001A2C8A3A92802E
#     Model: iPhone14,5
#     OS: iOS 17.2
#     Connection: usb
# ----------------------------------------------------------------------

# 配对设备 (首次使用)
python ios.py --pair

# 检查 WebDriverAgent 状态
python ios.py --wda-status

# 输出示例:
# Checking WebDriverAgent status at http://localhost:8100...
# --------------------------------------------------
# ✓ WebDriverAgent is running
#
# Status details:
#   Session ID: ABC123-DEF456-GHI789
#   Build: 2024.01.01
#
# Current App:
#   Bundle ID: com.apple.springboard
#   Process ID: 54321
```

### 使用特定设备

```bash
# 通过 UDID 指定设备
python ios.py --device-id 00008030-001A2C8A3A92802E "Open Camera"

# WiFi 连接 (使用设备 IP)
python ios.py --wda-url http://192.168.1.100:8100 "Open Photos"
```

### 执行任务

```bash
# 交互模式
python ios.py

# 输出:
# 🔍 Checking system requirements...
# --------------------------------------------------
# 1. Checking libimobiledevice installation... ✅ OK
# 2. Checking connected iOS devices... ✅ OK (1 device(s): My iPhone)
# 3. Checking WebDriverAgent (http://localhost:8100)... ✅ OK
#    Session ID: ABC123...
# --------------------------------------------------
# ✅ All system checks passed!
#
# 🔍 Checking model API...
# --------------------------------------------------
# 1. Checking API connectivity (http://localhost:8000/v1)... ✅ OK
# 2. Checking model 'autoglm-phone-9b'... ✅ OK
# --------------------------------------------------
# ✅ Model API checks passed!
#
# ==================================================
# Phone Agent iOS - AI-powered iOS automation
# ==================================================
# Model: autoglm-phone-9b
# Base URL: http://localhost:8000/v1
# WDA URL: http://localhost:8100
# Max Steps: 100
# Language: cn
# Device: My iPhone
#         iPhone14,5, iOS 17.2
# ==================================================
#
# Entering interactive mode. Type 'quit' to exit.
#
# Enter your task:

# 单次执行
python ios.py "Open Safari and search for Apple"

# 使用中文
python ios.py --lang cn "打开设置"

# 静默模式
python ios.py --quiet "Open Camera"
```

### 应用管理

```bash
# 列出支持的应用
python ios.py --list-apps

# 输出:
# Supported apps:
#
# Note: For iOS apps, ensure the Bundle IDs are configured in:
#   phone_agent/config/apps.py
#
# Currently configured apps:
#   - AppStore
#   - Camera
#   - Chrome
#   - Maps
#   - Music
#   - Notes
#   - Photos
#   - Safari
#   - Settings
#   - WeChat
#   - ...
#
# To add iOS apps, find the Bundle ID and add to APP_PACKAGES dictionary.
```

## 🌐 WiFi 连接

### 方法 1: 在设备上启动 WDA

1. 确保 iOS 设备和电脑在同一 WiFi 网络
2. 在 Xcode 中运行 WebDriverAgentRunner
3. 记下设备的 IP 地址 (设置 > WiFi > 详细信息)
4. 使用设备 IP 连接

```bash
python ios.py --wda-url http://192.168.1.100:8100 "打开相机"
```

### 方法 2: 使用环境变量

```bash
export PHONE_AGENT_WDA_URL="http://192.168.1.100:8100"
python ios.py "任务"
```

## 🔐 环境变量配置

```bash
# 创建配置文件
cat > ~/.phone_agent_ios << 'EOF'
export PHONE_AGENT_BASE_URL="http://localhost:8000/v1"
export PHONE_AGENT_MODEL="autoglm-phone-9b"
export PHONE_AGENT_MAX_STEPS="100"
export PHONE_AGENT_WDA_URL="http://localhost:8100"
export PHONE_AGENT_DEVICE_ID="00008030-001A2C8A3A92802E"
export PHONE_AGENT_LANG="cn"
EOF

# 使用配置
source ~/.phone_agent_ios
python ios.py "任务"
```

## 🐛 故障排查

### 设备未找到

```bash
# 检查设备连接
idevice_id -l

# 如果没有输出,尝试:
# 1. 重新插拔 USB 线
# 2. 在设备上点击"信任此电脑"
# 3. 重启 usbmuxd
sudo killall usbmuxd

# 4. 验证配对
idevicepair pair
```

### WebDriverAgent 无法访问

```bash
# 检查 WDA 是否运行
curl http://localhost:8100/status

# 如果失败:
# 1. 确认在 Xcode 中运行了 WebDriverAgentRunner
# 2. 检查端口转发
ps aux | grep iproxy
killall iproxy
iproxy 8100 8100

# 3. 在浏览器中测试
open http://localhost:8100/status
```

### libimobiledevice 问题

```bash
# 重新安装 libimobiledevice
brew uninstall --ignore-dependencies libimobiledevice
brew install libimobiledevice

# 验证安装
idevice_id --version
```

### 配对问题

```bash
# 取消配对并重新配对
idevicepair unpair
idevicepair pair

# 如果要求输入密码,在设备上输入
# 然后重新运行配对命令
```

## 📝 完整示例

### 日常任务自动化

```bash
#!/bin/bash

# 设置环境
export PHONE_AGENT_WDA_URL="http://localhost:8100"
export PHONE_AGENT_BASE_URL="http://localhost:8000/v1"

# 检查设备
echo "检查设备连接..."
python ios.py --list-devices || exit 1

# 检查 WDA
echo "检查 WebDriverAgent..."
python ios.py --wda-status || exit 1

# 执行任务序列
TASKS=(
    "Open Safari and go to apple.com"
    "Open Photos and view recent photos"
    "Open Settings and check battery"
)

for task in "${TASKS[@]}"; do
    echo "执行任务: $task"
    python ios.py "$task"
    sleep 5
done

echo "所有任务完成!"
```

### Python 脚本集成

```python
#!/usr/bin/env python3
"""iOS 自动化脚本示例"""

import subprocess
import sys
import os

# 配置
os.environ["PHONE_AGENT_WDA_URL"] = "http://localhost:8100"
os.environ["PHONE_AGENT_BASE_URL"] = "http://localhost:8000/v1"

def run_task(task: str) -> bool:
    """运行单个任务"""
    result = subprocess.run(
        ["python", "ios.py", "--quiet", task],
        capture_output=True,
        text=True,
        cwd="/path/to/Open-AutoGLM"
    )

    if result.returncode == 0:
        print(f"✓ {task}")
        return True
    else:
        print(f"✗ {task}")
        print(result.stderr)
        return False

def main():
    """主函数"""
    tasks = [
        "Open Camera",
        "Take a photo",
        "Open Photos",
        "View latest photo",
    ]

    print("开始执行 iOS 自动化任务...")

    for task in tasks:
        if not run_task(task):
            print(f"任务失败,停止执行: {task}")
            sys.exit(1)

    print("所有任务执行成功!")

if __name__ == "__main__":
    main()
```

## 🎯 与 main.py 的对比

| 特性 | main.py (Android) | ios.py (iOS) |
|------|-------------------|--------------|
| 设备检测 | `adb devices` | `idevice_id -l` |
| 设备通信 | ADB | libimobiledevice + WDA |
| 远程连接 | `--connect <ip>:5555` | `--wda-url http://<ip>:8100` |
| 启用远程 | `--enable-tcpip` | (需在设备上配置) |
| 特殊工具 | ADB Keyboard | WDA 键盘 API |
| 应用标识 | Package Name | Bundle ID |
| 系统检查 | ADB + ADB Keyboard | libimobiledevice + WDA |

## 📚 相关资源

- [iOS 支持文档](iOS_SUPPORT.md)
- [XCTest 模块文档](phone_agent/xctest/README.md)
- [命令行使用对比](CLI_USAGE.md)
- [iOS 基础示例](examples/ios_basic_usage.py)
- [WebDriverAgent 项目](https://github.com/appium/WebDriverAgent)

## ⚠️ 重要说明

当前 `ios.py` 是 iOS 自动化的命令行入口,它提供了:

✅ **完整的系统检查** - 设备、libimobiledevice、WebDriverAgent
✅ **设备管理功能** - 列出设备、配对、WDA 状态检查
✅ **模型 API 验证** - 连接性和模型可用性检查
✅ **环境变量支持** - 灵活的配置选项

⚠️ **正在开发中的功能**:

- PhoneAgent 主类的 iOS 后端集成 (当前使用 ADB 后端)
- 完整的任务执行流程 (需要扩展 ActionHandler 支持 xctest)

**临时解决方案**: 使用 `phone_agent.xctest` 模块直接控制 iOS 设备,参考 `examples/ios_basic_usage.py`

## 🔜 后续改进计划

1. **扩展 PhoneAgent 类** - 支持 iOS 后端选择
2. **统一 ActionHandler** - 自动检测并使用 ADB 或 XCTest
3. **改进错误处理** - 更详细的 iOS 特定错误提示
4. **添加手势支持** - iOS 特有的手势操作
5. **完善文档** - 更多使用示例和最佳实践

欢迎贡献代码和反馈! 🎉
