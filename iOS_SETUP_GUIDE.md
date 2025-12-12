# Open-AutoGLM iOS 完整部署指南

**最后更新**: 2025年12月13日

本指南详细记录了 Open-AutoGLM 在 iOS 平台的完整适配过程，包括遇到的所有问题和解决方案。

---

## 📋 目录

- [1. 概述](#1-概述)
- [2. 环境准备](#2-环境准备)
- [3. WebDriverAgent 部署](#3-webdriveragent-部署)
- [4. USB 端口转发](#4-usb-端口转发)
- [5. 安装 Open-AutoGLM](#5-安装-open-autoglm)
- [6. 运行测试](#6-运行测试)
- [7. 核心技术问题与解决方案](#7-核心技术问题与解决方案)
- [8. 常见问题](#8-常见问题)
- [9. 弹窗处理](#9-弹窗处理)

---

## 1. 概述

### 1.1 项目背景

Open-AutoGLM 是基于 AutoGLM-Phone-9B 视觉-语言模型的智能手机自动化框架。本项目成功将其从 Android (ADB) 适配到 iOS (WebDriverAgent)。

### 1.2 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                  AutoGLM-Phone-9B 模型                   │
│              (视觉-语言模型，理解屏幕并决策)              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Open-AutoGLM Agent                     │
│        agent_ios.py + handler_ios.py (任务执行器)        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   WDA Python 封装层                      │
│     phone_agent/wda/ (HTTP 客户端 + 坐标转换)           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              WebDriverAgent (HTTP Server)                │
│            运行在 iOS 设备上，监听 8100 端口             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│            iproxy (USB 端口转发工具)                     │
│         将 Mac 的 8100 转发到 iPhone 的 8100            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   iOS 设备 (真机)                        │
│                   执行实际操作                           │
└─────────────────────────────────────────────────────────┘
```

### 1.3 iOS vs Android 差异

| 特性 | Android (ADB) | iOS (WDA) |
|------|---------------|-----------|
| **通信协议** | ADB Shell 命令 | HTTP REST API |
| **坐标系统** | Pixels (像素) | **Points (逻辑点)** ⚠️ |
| **缩放因子** | 1x | 2x/3x (Retina) |
| **截图** | `adb shell screencap` | `GET /screenshot` |
| **点击** | `input tap x y` | `POST /wda/tap` |
| **文字输入** | ADB Keyboard | 原生键盘 + `/wda/keys` |
| **返回键** | 物理 Back 键 | 左边缘滑动手势 |
| **连接方式** | USB 直连 | **USB + iproxy 转发** ⚠️ |

---

## 2. 环境准备

### 2.1 系统要求

- **操作系统**: macOS 10.14+ (建议 macOS 12+)
- **Xcode**: 14.0+ (需要从 App Store 安装)
- **iOS 设备**: iOS 13.0+ (建议 iOS 14+)
- **Python**: 3.10+
- **网络**: 稳定的互联网连接（用于 AI 模型 API）

### 2.2 安装必要工具

#### 2.2.1 安装 Homebrew（如未安装）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2.2.2 安装 libimobiledevice

```bash
brew install libimobiledevice
```

**作用**: 提供 `iproxy` 等工具，用于 USB 端口转发。

#### 2.2.3 验证安装

```bash
# 验证 iproxy
which iproxy
# 应输出: /usr/local/bin/iproxy 或 /opt/homebrew/bin/iproxy

# 检查连接的 iOS 设备
idevice_id -l
# 应输出设备的 UDID
```

---

## 3. WebDriverAgent 部署

### 3.1 克隆 WebDriverAgent

本项目已包含 WebDriverAgent，位于：
```
/path/to/Open-AutoGLM/WebDriverAgent/
```

如果需要单独安装：
```bash
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent
./Scripts/bootstrap.sh
```

### 3.2 配置 Xcode 项目

#### 步骤 1: 打开项目

```bash
open WebDriverAgent/WebDriverAgent.xcodeproj
```

#### 步骤 2: 配置签名

1. 在 Xcode 左侧项目导航器中，选择 **WebDriverAgent** 项目
2. 选择 **WebDriverAgentLib** target
3. 点击 **Signing & Capabilities** 标签
4. 勾选 **Automatically manage signing**
5. 选择你的 **Team**（需要 Apple Developer 账号）

**重要**: 重复上述步骤为以下 targets 配置签名：
- WebDriverAgentLib
- WebDriverAgentRunner
- IntegrationApp

#### 步骤 3: 修改 Bundle ID（如果遇到冲突）

如果出现 "Failed to register bundle identifier" 错误：

1. 选择 **WebDriverAgentRunner** target
2. 修改 **Bundle Identifier**，例如：
   ```
   com.yourname.WebDriverAgentRunner
   ```

### 3.3 部署到设备

#### 步骤 1: 连接 iOS 设备

1. 使用 USB 线连接 iPhone/iPad 到 Mac
2. 在设备上**信任**此电脑
3. 在 Xcode 顶部工具栏，选择你的真机设备

#### 步骤 2: 运行 WebDriverAgent

1. 选择 **Product → Scheme → WebDriverAgentRunner**
2. 按 **⌘+U** 或点击 **Product → Test**

#### 步骤 3: 信任开发者（首次运行）

如果设备上出现"不受信任的开发者"警告：

1. 在 iOS 设备上打开 **设置 → 通用 → VPN与设备管理**
2. 找到你的开发者账号
3. 点击**信任**

#### 步骤 4: 验证 WDA 启动

在 Xcode Console 中查找以下日志：

```
ServerURLHere->http://192.168.x.x:8100<-ServerURLHere
```

记下这个 IP 地址（但我们会使用 USB 转发，不直接使用 WiFi IP）。

---

## 4. USB 端口转发

### 4.1 为什么需要 iproxy？

**核心问题**: iOS 的安全限制使得 WiFi 直连 WDA 不稳定且经常被阻断。

**解决方案**: 使用 USB 端口转发，将 Mac 的本地端口映射到 iPhone 的端口。

### 4.2 启动 iproxy

在**单独的终端窗口**运行（需要保持运行）：

```bash
iproxy 8100 8100
```

**输出示例**：
```
Creating listening port 8100 for device port 8100
waiting for connection
```

**关键点**：
- ✅ 此命令需要**持续运行**，不要关闭终端
- ✅ 如果看到 "waiting for connection"，说明正常
- ✅ 建议在 tmux/screen 中运行，或使用后台进程

### 4.3 验证连接

在另一个终端运行：

```bash
curl http://localhost:8100/status
```

**成功输出**（JSON格式）：
```json
{
  "value": {
    "message": "WebDriverAgent is ready to accept commands",
    "state": "success",
    ...
  },
  "sessionId": "...",
  "status": 0
}
```

**失败情况**：
```
curl: (7) Failed to connect to localhost port 8100: Connection refused
```

**解决方法**：
1. 确认 iproxy 正在运行
2. 确认 WDA 在 Xcode 中正在运行（Test 状态）
3. 检查设备是否通过 USB 连接

---

## 5. 安装 Open-AutoGLM

### 5.1 克隆仓库

```bash
git clone https://github.com/Rocke1001feller/Open-AutoGLM.git
cd Open-AutoGLM
git checkout iOS-iPhone
```

### 5.2 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5.3 安装依赖

```bash
pip install -r requirements.txt
pip install -e .
```

### 5.4 验证安装

```bash
python main_ios.py --check-only
```

**成功输出**：
```
🔍 Checking iOS device connection...
--------------------------------------------------
1. Checking WDA connectivity (http://localhost:8100)... ✅ OK
2. Checking screenshot capability... ✅ OK (1170x2532)
3. Checking active app detection... ✅ OK (Current: SpringBoard)
--------------------------------------------------
✅ iOS device connection OK!
```

---

## 6. 运行测试

### 6.1 配置 API Key

获取智谱 AI API Key：https://open.bigmodel.cn

### 6.2 运行基础任务

```bash
python main_ios.py \
    --base-url https://open.bigmodel.cn/api/paas/v4 \
    --model autoglm-phone \
    --apikey "YOUR_API_KEY" \
    "打开美团搜索附近的火锅"
```

### 6.3 查看支持的 App

```bash
python main_ios.py --list-apps
```

### 6.4 交互模式

```bash
python main_ios.py \
    --base-url https://open.bigmodel.cn/api/paas/v4 \
    --model autoglm-phone \
    --apikey "YOUR_API_KEY"
```

然后输入任务，例如：
- "打开微信发送一个笑话给文件传输助手"
- "打开淘宝搜索 iPhone 15"
- "打开美团搜索附近的刀削面馆并作推荐"

---

## 7. 核心技术问题与解决方案

### 7.1 坐标系统问题（最关键！）

#### 问题描述

在初始实现中，点击位置严重偏移（通常偏移 3 倍距离）。

#### 根本原因

WDA 使用 **Points（逻辑点）** 坐标系统，而不是 Pixels（像素）。

**iOS 坐标系统详解**：

```
iPhone 设备示例：iPhone 14 Pro

物理屏幕分辨率（Pixels）: 1179 × 2556
逻辑分辨率（Points）:      393 × 852
缩放因子（Scale）:          3.0x

关系: Pixels = Points × Scale
```

**错误的实现**：
```python
# ❌ 直接发送像素坐标
client.post("/wda/tap", {"x": 589, "y": 1278})  # 像素坐标

# WDA 理解为: 589 points = 1767 pixels
# 实际想点击的位置: 589 pixels = 196 points
# 结果: 点击位置偏移 3 倍！
```

**正确的实现**：
```python
# ✅ 转换为点坐标
SCALE_FACTOR = 3.0  # iPhone @3x

x_pixels = 589
y_pixels = 1278

x_points = x_pixels / SCALE_FACTOR  # 196.3
y_points = y_pixels / SCALE_FACTOR  # 426.0

client.post("/wda/tap", {"x": x_points, "y": y_points})
```

#### 解决方案

**文件**: `phone_agent/wda/device.py`

```python
# 添加动态获取 scale factor
def _get_scale_factor(device_id: str | None = None) -> float:
    """动态获取设备的 scale factor"""
    try:
        client = get_client(device_id)
        resp = client.get("/wda/screen", use_session=False)
        value = resp.get("value", {})
        return float(value.get("scale", 3.0))
    except:
        return 3.0  # 默认 @3x

# 添加坐标转换函数
def _pixels_to_points(x: int, y: int, device_id: str | None = None) -> tuple[float, float]:
    """将像素坐标转换为点坐标"""
    scale = _get_scale_factor(device_id)
    return x / scale, y / scale

# 修改所有坐标相关函数
def tap(x: int, y: int, device_id: str | None = None, delay: float = 0.5) -> None:
    client = get_client(device_id)
    x_pt, y_pt = _pixels_to_points(x, y, device_id)
    client.post("/wda/tap", {"x": x_pt, "y": y_pt})
    time.sleep(delay)
```

**修改涉及的函数**：
- `tap()` - 点击
- `double_tap()` - 双击
- `long_press()` - 长按
- `swipe()` - 滑动
- `back()` - 返回手势

#### 参考资料

- **权威来源**: WebDriverAgent 源码
  - 文件: `WebDriverAgentLib/Commands/FBElementCommands.m`
  - 行号: 658-685
  - 关键代码: `coordinateWithOffset:` 使用的是 Points

- **成功案例**: gekowa/Open-AutoGLM ios-support-3 分支
  - 使用 `SCALE_FACTOR = 3` 进行转换
  - 所有坐标操作都除以 scale factor

### 7.2 文字输入问题

#### 问题描述

初期文字输入无效，键盘弹出后无法输入文字。

#### 根本原因

1. iOS 不需要像 Android 那样安装 ADB Keyboard
2. 需要使用全局 `/wda/keys` 端点，而不是元素特定的输入
3. 文本格式需要是字符数组 `list(text)`

#### 解决方案

**文件**: `phone_agent/wda/input.py`

```python
def type_text(text: str, device_id: str | None = None, frequency: int = 60) -> None:
    """使用全局键盘输入文本"""
    if not text:
        return
    
    client = get_client(device_id)
    
    # 发送字符数组 + frequency 参数
    client.post("/wda/keys", {
        "value": list(text),  # 转换为字符数组
        "frequency": frequency  # 打字速度
    }, use_session=True)

def clear_text(device_id: str | None = None) -> None:
    """清除输入框文本"""
    client = get_client(device_id)
    
    try:
        # 尝试获取激活的元素
        resp = client.get("/element/active", use_session=True)
        if "value" in resp:
            element_id = resp["value"].get("ELEMENT")
            if element_id:
                # 清除元素
                client.post(f"/element/{element_id}/clear", use_session=True)
                return
    except:
        pass
    
    # 备选方案：发送退格键
    backspace = "\u0008"
    client.post("/wda/keys", {
        "value": [backspace] * 100
    }, use_session=True)

def hide_keyboard(device_id: str | None = None) -> None:
    """隐藏键盘"""
    client = get_client(device_id)
    
    try:
        # 需要使用 session
        client.post("/wda/keyboard/dismiss", use_session=True)
    except:
        pass  # 忽略错误（键盘可能已关闭）
```

**三步输入法** (`handler_ios.py`):

```python
def _handle_type(self, action: dict, width: int, height: int) -> ActionResult:
    """处理文字输入"""
    text = action.get("text", "")
    
    # 1. 清除现有文本
    clear_text(self.device_id)
    time.sleep(0.5)
    
    # 2. 输入新文本
    type_text(text, self.device_id, frequency=60)
    time.sleep(0.5)
    
    # 3. 隐藏键盘
    hide_keyboard(self.device_id)
    time.sleep(0.5)
    
    return ActionResult(True, False)
```

### 7.3 键盘隐藏 404 错误

#### 问题描述

```
WDA POST /wda/keyboard/dismiss error: 404 Client Error
```

#### 根本原因

`/wda/keyboard/dismiss` 端点**需要 session**，但初始实现使用了 `use_session=False`。

#### 证据

WebDriverAgent 源码 `FBCustomCommands.m` 第 43 行：

```objective-c
[[FBRoute POST:@"/wda/keyboard/dismiss"] respondWithTarget:self 
    action:@selector(handleDismissKeyboardCommand:)],
```

**注意**: 没有 `.withoutSession` 修饰符，说明需要 session。

#### 解决方案

1. **修改 input.py**:
   ```python
   # 改为使用 session
   client.post("/wda/keyboard/dismiss", use_session=True)
   ```

2. **修改 client.py** - 添加到需要 session 的路径列表:
   ```python
   session_required_prefixes = [
       "/wda/tap", "/wda/keys", "/wda/swipe", 
       "/wda/keyboard",  # 新增
       # ...
   ]
   ```

### 7.4 Session 管理

#### 问题描述

某些操作返回 404 错误，因为 session 过期。

#### 解决方案

**文件**: `phone_agent/wda/client.py`

```python
def post(self, path: str, data: dict = None, use_session: bool = True, **kwargs) -> dict:
    """发送 POST 请求，自动处理 session 过期"""
    original_path = path
    if use_session:
        path = self._session_path(path)
    url = f"{self.base_url}{path}"
    
    for attempt in range(2):  # 最多重试 2 次
        try:
            resp = self._session.post(url, json=data or {}, timeout=self.timeout)
            
            # 检查 404（可能是 session 过期）
            if resp.status_code == 404 and "/session/" in path and attempt == 0:
                # Session 过期，重新创建
                self._invalidate_session()
                path = self._session_path(original_path)
                url = f"{self.base_url}{path}"
                continue  # 重试
            
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == 0 and "/session/" in path:
                # 重试一次
                self._invalidate_session()
                continue
            return {"error": str(e)}
    
    return {"error": "Request failed after retry"}
```

---

## 8. 常见问题

### Q1: WDA 连接失败

**错误信息**:
```
Error: Cannot connect to WebDriverAgent.
```

**解决步骤**:

1. **检查 iproxy 是否运行**:
   ```bash
   pgrep -f iproxy
   # 如果没有输出，说明未运行
   ```

2. **启动 iproxy**:
   ```bash
   iproxy 8100 8100
   ```

3. **检查 WDA 是否在 Xcode 中运行**:
   - 确认 Xcode Console 显示 "ServerURLHere"
   - 确认设备未锁屏

4. **测试连接**:
   ```bash
   curl http://localhost:8100/status
   ```

### Q2: 坐标点击不准确

**症状**: 点击位置偏移，通常偏移 3 倍

**原因**: 坐标转换问题

**检查**:
```bash
# 运行测试脚本
python test_wda_coordinates.py
```

**验证修复**:
```python
# 查看 device.py 是否有坐标转换
grep "_pixels_to_points" phone_agent/wda/device.py
```

### Q3: 文字输入无效

**症状**: 输入框聚焦但无文字输出

**检查清单**:
- [ ] 键盘是否弹出？
- [ ] `/wda/keys` 端点是否使用 session？
- [ ] 文本格式是否为 `list(text)`？

**调试**:
```bash
# 查看日志中是否有 keyboard 相关错误
python main_ios.py ... 2>&1 | grep -i keyboard
```

### Q4: 应用启动失败

**错误**: `App not found: xxx`

**原因**: Bundle ID 未配置

**解决**:

编辑 `phone_agent/config/apps_ios.py`:
```python
IOS_APP_PACKAGES = {
    "你的App名称": "com.example.bundleid",
    # ...
}
```

**查找 Bundle ID**:
```bash
# 方法1: 通过 WDA 查看当前应用
curl http://localhost:8100/wda/activeAppInfo

# 方法2: 使用 ideviceinstaller
ideviceinstaller -l
```

### Q5: 截图失败或黑屏

**原因**: 敏感界面（支付、密码等）

**解决**: 这是 iOS 安全特性，无法绕过。系统会返回黑色占位图。

### Q6: USB 连接不稳定

**症状**: iproxy 频繁断开

**解决**:
1. 使用原装 USB 线
2. 更换 USB 端口（避免 USB hub）
3. 禁用设备自动锁屏
4. 在 iOS 设置中启用"保持连接"

### Q7: Xcode 签名问题

**错误**: "Failed to create provisioning profile"

**解决**:
1. 确保登录 Apple ID（Xcode → Preferences → Accounts）
2. 修改 Bundle ID 为唯一值
3. 使用免费开发者账号（7 天有效期）

---

## 9. 弹窗处理

### 9.1 弹窗识别能力

AutoGLM-Phone-9B 是视觉-语言模型，**可以识别和处理弹窗**：

✅ **可以识别**:
- 广告弹窗
- 权限请求（定位、通知、相机等）
- 更新提示
- 活动推广
- 引导页

✅ **可以执行**:
- 点击"关闭"、"X"按钮
- 点击"取消"、"稍后再说"
- 点击"跳过"、"我知道了"
- 点击弹窗外区域关闭

### 9.2 系统提示优化

已在系统提示词中添加**弹窗优先处理**规则（`prompts_zh.py` 第 1 条）：

```python
"1. **弹窗处理（重要）**：在执行任务过程中，如果屏幕上出现弹窗、广告、"
"通知请求、权限请求等干扰性界面，应该优先关闭它们。常见的关闭方式："
"点击"关闭"、"X"、"取消"、"稍后再说"、"跳过"等按钮，或点击弹窗外的区域。"
"关闭弹窗后再继续执行主任务。"
```

### 9.3 测试弹窗处理

```bash
# 测试淘宝/京东等常见弹窗
python main_ios.py \
    --base-url https://open.bigmodel.cn/api/paas/v4 \
    --model autoglm-phone \
    --apikey "YOUR_KEY" \
    "打开淘宝搜索 iPhone 15"

# 观察模型是否先关闭弹窗再执行搜索
```

### 9.4 弹窗处理流程

```
┌─────────────────────────────────────┐
│ 1. 模型看到屏幕（包括弹窗）          │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ 2. 判断：是否有干扰性弹窗？          │
│    - 检查是否有"关闭"按钮            │
│    - 是否遮挡主要内容                │
│    - 是否与任务无关                  │
└─────────────────────────────────────┘
                  ↓
         ┌────────┴────────┐
         │                 │
    【是】              【否】
         │                 │
         ↓                 ↓
┌─────────────────┐  ┌─────────────────┐
│ 3. 点击关闭按钮 │  │ 继续执行主任务  │
└─────────────────┘  └─────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│ 4. 验证弹窗是否关闭                  │
└─────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│ 5. 继续执行主任务                    │
└─────────────────────────────────────┘
```

---

## 10. 总结

### 10.1 关键成就

✅ **成功适配 iOS 平台** - 从 Android ADB 迁移到 WebDriverAgent  
✅ **解决坐标系统问题** - Points vs Pixels，scale factor 转换  
✅ **实现文字输入** - 全局 `/wda/keys` + 字符数组格式  
✅ **修复 Session 管理** - 自动重试和 session 恢复  
✅ **优化弹窗处理** - 系统提示词优先级调整  

### 10.2 核心技术决策

| 决策点 | Android 方案 | iOS 方案 | 理由 |
|--------|-------------|----------|------|
| **连接方式** | ADB USB 直连 | USB + iproxy 转发 | iOS 安全限制 WiFi 不稳定 |
| **坐标系统** | 像素坐标 | 点坐标（÷scale） | WDA 使用 Points 坐标系 |
| **文字输入** | ADB Keyboard | 原生键盘 + `/wda/keys` | iOS 不支持虚拟键盘 |
| **返回操作** | 物理 Back 键 | 左边缘滑动手势 | iOS 无返回键 |

### 10.3 踩过的坑

| # | 问题 | 初期错误 | 正确方案 |
|---|------|----------|----------|
| 1 | **坐标偏移** | 直接传像素坐标 | 除以 scale factor |
| 2 | **文字输入失败** | 尝试查找元素输入 | 使用全局 `/wda/keys` |
| 3 | **键盘隐藏 404** | `use_session=False` | `use_session=True` |
| 4 | **WiFi 连接不稳定** | 直接连设备 IP | 使用 iproxy USB 转发 |
| 5 | **Session 过期** | 单次请求无重试 | 自动检测并重建 session |

### 10.4 工具软件依赖

| 工具 | 作用 | 安装命令 | 必需性 |
|------|------|----------|--------|
| **iproxy** | USB 端口转发 | `brew install libimobiledevice` | ✅ 必需 |
| **Xcode** | 编译运行 WDA | App Store 安装 | ✅ 必需 |
| **WebDriverAgent** | iOS 自动化服务 | 已包含在项目中 | ✅ 必需 |
| **Python 3.10+** | 运行 AutoGLM | `brew install python@3.10` | ✅ 必需 |

### 10.5 下一步优化方向

- [ ] 支持多设备并行控制
- [ ] 优化截图性能（当前每步都截图）
- [ ] 增强弹窗识别准确率
- [ ] 支持模拟器（当前仅真机）
- [ ] 添加录屏功能（用于调试）
- [ ] 支持更多 iOS 专属手势（3D Touch、Control Center 等）

---

## 附录

### A. 完整测试清单

```bash
# 1. 检查环境
which iproxy           # 应有输出
which python3          # 应有输出
xcodebuild -version    # 应显示 Xcode 版本

# 2. 启动 iproxy
iproxy 8100 8100 &

# 3. 启动 WDA（在 Xcode 中）

# 4. 验证连接
curl http://localhost:8100/status

# 5. 运行测试
python main_ios.py --check-only
python test_wda_coordinates.py
python main_ios.py --list-apps

# 6. 执行任务
python main_ios.py \
    --base-url https://open.bigmodel.cn/api/paas/v4 \
    --model autoglm-phone \
    --apikey "YOUR_KEY" \
    "打开微信发送消息给文件传输助手"
```

### B. 参考资料

- [WebDriverAgent GitHub](https://github.com/appium/WebDriverAgent)
- [iOS 坐标系统文档](https://developer.apple.com/documentation/uikit/uiview/1622580-bounds)
- [gekowa iOS 实现](https://github.com/gekowa/Open-AutoGLM/tree/ios-support-3)
- [AutoGLM 论文](https://arxiv.org/abs/2411.00820)

### C. 联系方式

- **Issues**: https://github.com/zai-org/Open-AutoGLM/issues
- **Pull Request**: #143

---

**文档版本**: 1.0  
**作者**: iOS 适配团队  
**最后更新**: 2025年12月13日
