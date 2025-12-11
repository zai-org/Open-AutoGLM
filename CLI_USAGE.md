# 命令行使用指南

Open-AutoGLM 提供两个 CLI 入口:

- **`main.py`** - Android 设备自动化
- **`ios.py`** - iOS 设备自动化 (新增)

## 快速对比

| 功能 | Android (main.py) | iOS (ios.py) |
|------|-------------------|--------------|
| 设备通信 | ADB (Android Debug Bridge) | libimobiledevice + WebDriverAgent |
| 连接方式 | USB / WiFi | USB / WiFi |
| 列出设备 | `python main.py --list-devices` | `python ios.py --list-devices` |
| 指定设备 | `--device-id <device_id>` | `--device-id <UDID>` |
| 远程连接 | `--connect <ip>:5555` | `--wda-url http://<ip>:8100` |
| 启用远程 | `--enable-tcpip` | (在设备上配置 WDA) |
| 应用标识 | Package name | Bundle ID |

## Android 设备使用 (main.py)

### 基础命令

```bash
# 检查系统要求
python main.py --list-devices

# 列出支持的应用
python main.py --list-apps

# 交互模式
python main.py

# 执行单个任务
python main.py "打开美团搜索附近的火锅店"

# 使用英文模式
python main.py --lang en "Open Chrome browser"
```

### 设备管理

```bash
# 列出所有设备
python main.py --list-devices

# 使用特定设备
python main.py --device-id emulator-5554 "打开淘宝"

# 连接远程设备
python main.py --connect 192.168.1.100:5555

# 断开远程设备
python main.py --disconnect 192.168.1.100:5555
python main.py --disconnect all  # 断开所有

# 启用 TCP/IP 模式
python main.py --enable-tcpip
python main.py --enable-tcpip 5555
```

### 模型配置

```bash
# 指定模型服务器
python main.py --base-url http://localhost:8000/v1 --model autoglm-phone-9b

# 设置最大步数
python main.py --max-steps 50 "复杂任务"

# 静默模式
python main.py --quiet "任务"
```

### 环境变量

```bash
export PHONE_AGENT_BASE_URL="http://localhost:8000/v1"
export PHONE_AGENT_MODEL="autoglm-phone-9b"
export PHONE_AGENT_MAX_STEPS="100"
export PHONE_AGENT_DEVICE_ID="emulator-5554"
export PHONE_AGENT_LANG="cn"

python main.py "任务"
```

## iOS 设备使用 (ios.py)

### 基础命令

```bash
# 检查系统要求
python ios.py --list-devices

# 列出支持的应用
python ios.py --list-apps

# 交互模式
python ios.py

# 执行单个任务
python ios.py "Open Safari and search for Apple"

# 使用中文模式
python ios.py --lang cn "打开设置"
```

### 设备管理

```bash
# 列出所有 iOS 设备
python ios.py --list-devices

# 使用特定设备 (UDID)
python ios.py --device-id 00008030-001A2C8A3A92802E "打开相机"

# 配对设备
python ios.py --pair

# 检查 WebDriverAgent 状态
python ios.py --wda-status

# WiFi 连接 (使用设备 IP)
python ios.py --wda-url http://192.168.1.100:8100 "打开地图"
```

### 模型配置

```bash
# 指定模型服务器
python ios.py --base-url http://localhost:8000/v1 --model autoglm-phone-9b

# 设置 WebDriverAgent URL
python ios.py --wda-url http://localhost:8100

# 设置最大步数
python ios.py --max-steps 50 "复杂任务"

# 静默模式
python ios.py --quiet "任务"
```

### 环境变量

```bash
export PHONE_AGENT_BASE_URL="http://localhost:8000/v1"
export PHONE_AGENT_MODEL="autoglm-phone-9b"
export PHONE_AGENT_MAX_STEPS="100"
export PHONE_AGENT_WDA_URL="http://localhost:8100"
export PHONE_AGENT_DEVICE_ID="00008030-001A2C8A3A92802E"
export PHONE_AGENT_LANG="en"

python ios.py "任务"
```

## 完整示例

### Android 场景

```bash
# 1. 检查设备连接
python main.py --list-devices

# 2. 确认模型服务运行
curl http://localhost:8000/v1/models

# 3. 运行任务
python main.py "打开小红书搜索美食攻略"

# 4. 远程调试
python main.py --enable-tcpip
# 记下输出的 IP 地址
python main.py --connect 192.168.1.100:5555
python main.py "打开抖音刷视频"
```

### iOS 场景

```bash
# 1. 检查设备连接
python ios.py --list-devices

# 2. 配对设备 (首次使用)
python ios.py --pair

# 3. 启动 WebDriverAgent (在 Xcode 中)
# - 打开 WebDriverAgent.xcodeproj
# - 选择设备
# - Product > Test (Cmd+U)

# 4. 设置端口转发 (USB 连接)
iproxy 8100 8100

# 5. 检查 WDA 状态
python ios.py --wda-status

# 6. 确认模型服务运行
curl http://localhost:8000/v1/models

# 7. 运行任务
python ios.py "Open Camera app"

# 8. WiFi 调试 (可选)
# 在设备上记下 IP 地址
python ios.py --wda-url http://192.168.1.100:8100 "Open Photos"
```

## 常见命令速查

### 设备检查

```bash
# Android
adb devices
python main.py --list-devices

# iOS
idevice_id -l
python ios.py --list-devices
```

### 截图测试

```bash
# Android
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png

# iOS
idevicescreenshot screenshot.png
# 或通过 WDA: open http://localhost:8100/screenshot
```

### 应用启动

```bash
# Android
adb shell monkey -p com.taobao.taobao 1
python main.py "打开淘宝"

# iOS
# 需要先配置 Bundle ID
python ios.py "打开 Safari"
```

### 端口转发

```bash
# Android (ADB over WiFi)
adb tcpip 5555
adb connect 192.168.1.100:5555

# iOS (WebDriverAgent)
iproxy 8100 8100  # USB
# 或直接使用 WiFi: http://device-ip:8100
```

## 故障排查

### Android 常见问题

```bash
# 设备未找到
adb kill-server && adb start-server
adb devices

# ADB Keyboard 问题
adb shell ime list -s
adb install ADBKeyboard.apk
adb shell ime set com.android.adbkeyboard/.AdbIME

# 权限问题
adb shell pm grant com.android.adbkeyboard android.permission.SYSTEM_ALERT_WINDOW
```

### iOS 常见问题

```bash
# 设备未找到
sudo killall usbmuxd
idevice_id -l
idevicepair pair

# WebDriverAgent 无法访问
iproxy 8100 8100
curl http://localhost:8100/status

# 配对问题
idevicepair unpair
idevicepair pair
```

## 进阶用法

### 批量任务

```bash
# 创建任务列表
cat > tasks.txt << EOF
打开淘宝搜索耳机
打开美团搜索火锅
打开抖音刷视频
EOF

# 执行任务列表
while read task; do
    python main.py "$task"
    sleep 5
done < tasks.txt
```

### 脚本集成

```python
#!/usr/bin/env python3
import subprocess
import sys

tasks = [
    "打开小红书",
    "搜索美食攻略",
    "点赞第一条笔记",
]

for task in tasks:
    print(f"执行任务: {task}")
    result = subprocess.run(
        ["python", "main.py", task],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"任务失败: {task}", file=sys.stderr)
        break
```

### 定时任务

```bash
# 使用 cron (Linux/macOS)
# 每天早上 9 点执行任务
0 9 * * * cd /path/to/Open-AutoGLM && python main.py "打开微信查看消息"

# 使用 launchd (macOS)
# 创建 ~/Library/LaunchAgents/com.autoglm.task.plist
```

## 性能优化建议

1. **使用静默模式减少输出**: `--quiet`
2. **调整最大步数**: `--max-steps 50`
3. **WiFi 连接更稳定**: Android 使用 `--connect`, iOS 使用 `--wda-url`
4. **模型服务本地部署**: 降低延迟
5. **设备保持唤醒**: 避免锁屏中断

## 开发调试

### 查看详细日志

```bash
# Android
python main.py "任务"  # verbose 模式默认开启

# iOS
python ios.py "任务"  # verbose 模式默认开启
```

### 测试模型连接

```bash
# 使用 curl
curl http://localhost:8000/v1/models

# 使用 Python
python -c "from openai import OpenAI; print(OpenAI(base_url='http://localhost:8000/v1', api_key='EMPTY').models.list())"
```

### 测试设备操作

```bash
# Android
python -c "from phone_agent.adb import tap, get_screenshot; tap(100, 200); print(get_screenshot())"

# iOS
python -c "from phone_agent.xctest import tap, get_screenshot; tap(100, 200, wda_url='http://localhost:8100'); print(get_screenshot(wda_url='http://localhost:8100'))"
```

## 更多资源

- [Android ADB 文档](https://developer.android.com/tools/adb)
- [iOS WebDriverAgent 文档](https://github.com/appium/WebDriverAgent)
- [libimobiledevice 项目](https://libimobiledevice.org/)
- [项目 README](README.md)
- [iOS 支持文档](iOS_SUPPORT.md)
