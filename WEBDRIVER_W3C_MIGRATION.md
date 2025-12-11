# WebDriver W3C 标准迁移

## 🎯 迁移原因

之前的实现使用了 WebDriverAgent 的自定义端点 (如 `wda/tap`, `wda/doubleTap`)，这些端点不是标准的 WebDriver W3C API。

正确的做法是使用标准的 **W3C WebDriver Actions API** (`/actions` 端点)，通过 JSON 描述触摸操作序列。

## ✅ 已迁移的函数

### 1. **tap()** - 单击/点击

**修改前 (❌ 非标准):**
```python
url = f"{wda_url}/session/{session_id}/wda/tap/0"
requests.post(url, json={"x": x, "y": y})
```

**修改后 (✅ W3C 标准):**
```python
url = f"{wda_url}/session/{session_id}/actions"
actions = {
    "actions": [{
        "type": "pointer",
        "id": "finger1",
        "parameters": {"pointerType": "touch"},
        "actions": [
            {"type": "pointerMove", "duration": 0, "x": x, "y": y},
            {"type": "pointerDown", "button": 0},
            {"type": "pause", "duration": 100},
            {"type": "pointerUp", "button": 0},
        ],
    }]
}
requests.post(url, json=actions)
```

### 2. **double_tap()** - 双击

**修改前 (❌ 非标准):**
```python
url = f"{wda_url}/session/{session_id}/wda/doubleTap"
requests.post(url, json={"x": x, "y": y})
```

**修改后 (✅ W3C 标准):**
```python
url = f"{wda_url}/session/{session_id}/actions"
actions = {
    "actions": [{
        "type": "pointer",
        "id": "finger1",
        "parameters": {"pointerType": "touch"},
        "actions": [
            {"type": "pointerMove", "duration": 0, "x": x, "y": y},
            {"type": "pointerDown", "button": 0},
            {"type": "pause", "duration": 100},
            {"type": "pointerUp", "button": 0},
            {"type": "pause", "duration": 100},
            {"type": "pointerDown", "button": 0},
            {"type": "pause", "duration": 100},
            {"type": "pointerUp", "button": 0},
        ],
    }]
}
requests.post(url, json=actions)
```

### 3. **long_press()** - 长按

**修改前 (❌ 非标准):**
```python
url = f"{wda_url}/session/{session_id}/wda/touchAndHold"
requests.post(url, json={"x": x, "y": y, "duration": duration})
```

**修改后 (✅ W3C 标准):**
```python
url = f"{wda_url}/session/{session_id}/actions"
duration_ms = int(duration * 1000)
actions = {
    "actions": [{
        "type": "pointer",
        "id": "finger1",
        "parameters": {"pointerType": "touch"},
        "actions": [
            {"type": "pointerMove", "duration": 0, "x": x, "y": y},
            {"type": "pointerDown", "button": 0},
            {"type": "pause", "duration": duration_ms},
            {"type": "pointerUp", "button": 0},
        ],
    }]
}
requests.post(url, json=actions)
```

### 4. **swipe()** - 滑动

**修改前 (❌ 非标准):**
```python
url = f"{wda_url}/session/{session_id}/wda/dragfromtoforduration"
requests.post(url, json={
    "fromX": start_x,
    "fromY": start_y,
    "toX": end_x,
    "toY": end_y,
    "duration": duration,
})
```

**修改后 (✅ W3C 标准):**
```python
url = f"{wda_url}/session/{session_id}/actions"
duration_ms = int(duration * 1000)
actions = {
    "actions": [{
        "type": "pointer",
        "id": "finger1",
        "parameters": {"pointerType": "touch"},
        "actions": [
            {"type": "pointerMove", "duration": 0, "x": start_x, "y": start_y},
            {"type": "pointerDown", "button": 0},
            {"type": "pause", "duration": 50},
            {"type": "pointerMove", "duration": duration_ms, "x": end_x, "y": end_y},
            {"type": "pointerUp", "button": 0},
        ],
    }]
}
requests.post(url, json=actions)
```

## 📚 W3C WebDriver Actions API 解释

### 基本结构

```json
{
  "actions": [
    {
      "type": "pointer",           // 输入源类型: pointer, key, wheel
      "id": "finger1",              // 唯一标识符
      "parameters": {
        "pointerType": "touch"     // 指针类型: touch, mouse, pen
      },
      "actions": [                 // 动作序列
        ...
      ]
    }
  ]
}
```

### 动作类型

1. **pointerMove** - 移动指针
   ```json
   {"type": "pointerMove", "duration": 0, "x": 100, "y": 200}
   ```

2. **pointerDown** - 按下
   ```json
   {"type": "pointerDown", "button": 0}
   ```

3. **pointerUp** - 抬起
   ```json
   {"type": "pointerUp", "button": 0}
   ```

4. **pause** - 暂停
   ```json
   {"type": "pause", "duration": 100}
   ```

### 时间单位

- **duration**: 所有时长都以**毫秒 (ms)** 为单位
- Python 中的秒需要转换: `duration_ms = int(duration * 1000)`

### 触摸手势模式

#### 单击 (Tap)
```
Move → Down → Pause(100ms) → Up
```

#### 双击 (Double Tap)
```
Move → Down → Pause → Up → Pause → Down → Pause → Up
```

#### 长按 (Long Press)
```
Move → Down → Pause(duration) → Up
```

#### 滑动 (Swipe)
```
Move(start) → Down → Pause(50ms) → Move(end, duration) → Up
```

## 🔄 其他 WebDriverAgent 端点状态

以下端点**保持不变**,因为它们使用的是 WDA 特定功能,没有标准 WebDriver 等价物:

### ✅ 保留的 WDA 特定端点

1. **launch_app()** - 启动应用
   ```python
   url = f"{wda_url}/session/{session_id}/wda/apps/launch"
   ```

2. **home()** - 主屏幕
   ```python
   url = f"{wda_url}/wda/homescreen"
   ```

3. **hide_keyboard()** - 隐藏键盘
   ```python
   url = f"{wda_url}/wda/keyboard/dismiss"
   ```

4. **is_keyboard_shown()** - 键盘状态
   ```python
   url = f"{wda_url}/session/{session_id}/wda/keyboard/shown"
   ```

5. **type_text()** - 文本输入
   ```python
   url = f"{wda_url}/session/{session_id}/wda/keys"
   ```

6. **set_pasteboard()/get_pasteboard()** - 剪贴板
   ```python
   url = f"{wda_url}/wda/setPasteboard"
   url = f"{wda_url}/wda/getPasteboard"
   ```

### ✅ 使用标准 WebDriver 端点

1. **get_screen_size()** - 屏幕尺寸
   ```python
   url = f"{wda_url}/session/{session_id}/window/size"  # 标准端点
   ```

2. **get_screenshot()** - 截图
   ```python
   url = f"{wda_url}/session/{session_id}/screenshot"  # 标准端点
   ```

## 📊 迁移对比总结

| 函数 | 旧端点 | 新端点 | 状态 |
|------|--------|--------|------|
| tap() | `wda/tap/0` | `actions` | ✅ 已迁移 |
| double_tap() | `wda/doubleTap` | `actions` | ✅ 已迁移 |
| long_press() | `wda/touchAndHold` | `actions` | ✅ 已迁移 |
| swipe() | `wda/dragfromtoforduration` | `actions` | ✅ 已迁移 |
| launch_app() | `wda/apps/launch` | - | ⚪ WDA 特定 |
| home() | `wda/homescreen` | - | ⚪ WDA 特定 |
| type_text() | `wda/keys` | - | ⚪ WDA 特定 |
| get_screen_size() | `window/size` | - | ✅ 已是标准 |

## 🎯 迁移优势

1. **标准兼容性**: 符合 W3C WebDriver 规范,与其他自动化工具一致
2. **更好的兼容性**: 可能在不同版本的 WebDriverAgent 上有更好的兼容性
3. **更精确的控制**: Actions API 提供更细粒度的触摸控制
4. **未来兼容**: 基于标准规范,未来更新更稳定

## 🧪 验证

所有迁移后的函数已通过导入测试:

```bash
python -c "from phone_agent.xctest import tap, double_tap, long_press, swipe; print('✅ OK')"
```

## 📖 参考资料

- [W3C WebDriver Specification - Actions](https://www.w3.org/TR/webdriver/#actions)
- [WebDriverAgent GitHub](https://github.com/appium/WebDriverAgent)
- [Appium Touch Actions](https://appium.io/docs/en/commands/interactions/touch/touch-perform/)

## 🎉 完成

所有主要的触摸操作函数已成功迁移到 W3C WebDriver Actions API 标准! 🚀
