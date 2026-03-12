# 更新日志 - 新功能说明

本文档记录了 Open-AutoGLM 项目的最新功能更新和使用说明。

---

## 🆕 新增功能

### 1. 结果输出功能 (`--output`)

#### 功能说明
新增了 `--output`（或 `-o`）参数，可以将任务执行结果保存到指定的文件中。结果统一以 **JSON 数组** 格式保存。

#### 使用方法

**命令行方式：**
```bash
# 保存结果到 results/result.json 文件
python main.py --output ./results/result.json "打开微信并发送消息"

# 使用短参数
python main.py -o ./results/result.json "打开微信"
```

**编程方式：**
```python
from main import main_params

main_params(
    task="打开微信",
    output="./results/result.json"
)
```

#### 输出说明
- 结果会保存为指定路径的 JSON 文件
- 如果父级文件夹不存在，会自动创建
- 任务完成后会显示：`result保存到{output}文件`

#### 示例
```bash
$ python main.py --output ./results/result.json "打开微信"
Task: 打开微信

[执行过程...]

Result: 任务完成

result保存到./results/result.json文件
```

---

### 2. 结构化 JSON 输出与全量步骤保存 (`--all`)

#### 功能说明
现在结果统一以 **JSON 数组** 格式保存。
新增了 `--all` 参数，允许用户控制是仅保存最终结果，还是保存执行过程中的所有步骤结果。

#### 使用方法

**命令行方式：**
```bash
# 仅保存最后结果 (默认，输出为单元素 JSON 数组)
python main.py --output ./results/result.json "打开微信"

# 保存所有步骤的结果
python main.py --output ./results/all_steps.json --all "打开微信"
```

**编程方式：**
```python
from main import main_params

# 保存所有步骤的结果
main_params(
    task="打开微信",
    output="./results/all_steps.json",
    save_all=True
)
```

#### 输出格式示例

**仅保存最后结果时：**
```json
[
    "任务完成"
]
```

**保存所有步骤时 (`--all`)：**
```json
[
    "正在打开微信",
    "已进入微信主界面",
    "任务完成"
]
```

---

### 3. 编程接口 `main_params()` 函数

#### 功能说明
新增了 `main_params()` 函数，支持通过函数参数的方式调用主程序，方便从其他 Python 脚本中集成使用。

#### 函数签名
```python
def main_params(
    base_url: str = None,
    model: str = None,
    apikey: str = None,
    max_steps: int = None,
    device_id: str = None,
    connect: str = None,
    disconnect: str = None,
    list_devices: bool = False,
    enable_tcpip: int = None,
    wda_url: str = None,
    pair: bool = False,
    wda_status: bool = False,
    quiet: bool = False,
    list_apps: bool = False,
    lang: str = None,
    device_type: str = None,
    output: str = None,
    task: str = None,
    allow_all_apps: bool = False,
    save_all: bool = False,
) -> None
```

#### 使用方法

**基本示例：**
```python
from main import main_params

# 使用默认配置
main_params(task="打开微信")

# 自定义配置
main_params(
    base_url="http://localhost:8000/v1",
    model="autoglm-phone-9b",
    task="打开微信并发送消息",
    output="./results/result.json",
    device_type="adb"
)
```

**完整示例：**
```python
from main import main_params

# iOS 设备示例
main_params(
    base_url="http://localhost:8000/v1",
    model="autoglm-phone-9b",
    apikey="your-api-key",
    device_type="ios",
    wda_url="http://localhost:8100",
    task="打开Safari并搜索",
    output="./ios_results/search_res.json",
    max_steps=50,
    lang="cn",
    save_all=True
)
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | str | 环境变量或默认值 | 模型API基础URL |
| `model` | str | 环境变量或默认值 | 模型名称 |
| `apikey` | str | 环境变量或默认值 | API密钥 |
| `max_steps` | int | 100 | 最大执行步数 |
| `device_id` | str | None | 设备ID |
| `device_type` | str | "adb" | 设备类型：adb/hdc/ios |
| `output` | str | None | 输出文件路径 (JSON) |
| `task` | str | None | 要执行的任务 |
| `allow_all_apps` | bool | False | 是否允许启动所有应用 |
| `save_all` | bool | False | 是否保存所有中间步骤结果 |
| `lang` | str | "cn" | 语言：cn/en |
| `quiet` | bool | False | 是否静默模式 |
| `wda_url` | str | None | iOS WebDriverAgent URL |
| ... | ... | ... | 其他参数见函数文档 |

---

### 4. 允许所有应用功能 (`--allow-all-apps`)

#### 功能说明
新增了 `--allow-all-apps` 参数，允许启动任何应用，不再限制在配置的应用列表中。当启用此选项时，可以直接使用应用的包名（Android）、Bundle ID（iOS）或 Bundle Name（HarmonyOS）来启动应用。

#### 使用方法

**命令行方式：**
```bash
# 限制在应用列表中（默认行为）
python main.py "打开微信"

# 允许所有应用，直接使用包名
python main.py --allow-all-apps "打开com.example.myapp"
```

**编程方式：**
```python
from main import main_params

# 限制在应用列表中
main_params(task="打开微信", allow_all_apps=False)

# 允许所有应用
main_params(task="打开com.example.myapp", allow_all_apps=True)
```

#### 使用场景

1. **测试未配置的应用**
   ```bash
   python main.py --allow-all-apps "打开com.example.testapp"
   ```

2. **使用包名直接启动**
   ```bash
   # Android
   python main.py --allow-all-apps "打开com.android.chrome"
   
   # iOS
   python main.py --device-type ios --allow-all-apps "打开com.apple.Safari"
   ```

3. **动态应用管理**
   - 不需要修改配置文件即可启动新应用
   - 适合开发和测试环境

#### 注意事项

- 当 `allow_all_apps=True` 时，应用名称会被直接当作包名/Bundle ID使用
- 确保包名/Bundle ID正确，否则可能无法启动应用
- 建议在已知包名的情况下使用此功能

---

### 5. 应用包名查询工具 (`scripts/get_package_name.py`)

#### 功能说明
新增了一个实用的 Python 脚本工具，用于查询 Android 应用的包名。支持多种查询方式，方便开发者查找和添加新应用到配置中。

#### 安装要求
- 已安装 ADB 工具
- 设备已连接并启用 USB 调试

#### 使用方法

**1. 列出所有第三方应用**
```bash
python scripts/get_package_name.py list
```

**2. 列出所有应用（包括系统应用）**
```bash
python scripts/get_package_name.py list-all
```

**3. 查看当前前台应用的包名**
```bash
# 先打开你想查询的应用，然后运行：
python scripts/get_package_name.py current
```

**4. 搜索包含关键词的包名**
```bash
# 搜索微信相关应用
python scripts/get_package_name.py search wechat

# 搜索腾讯相关应用
python scripts/get_package_name.py search tencent
```

**5. 查看应用的详细信息**
```bash
python scripts/get_package_name.py info com.tencent.mm
```

**6. 指定设备ID（多设备时）**
```bash
python scripts/get_package_name.py device <设备ID> current
python scripts/get_package_name.py device emulator-5554 list
```

#### 使用示例

**示例1：查找微信包名**
```bash
$ python scripts/get_package_name.py search tencent
搜索包含 'tencent' 的包名:
------------------------------------------------------------
  com.tencent.mm
  com.tencent.mobileqq
  com.tencent.qqmusic
  com.tencent.qqlive
  com.tencent.androidqqmail
  com.tencent.news

找到 6 个匹配的应用
```

**示例2：查看当前应用**
```bash
$ python scripts/get_package_name.py current
当前前台应用包名: com.tencent.mm
应用名称: 微信
```

**示例3：获取应用详细信息**
```bash
$ python scripts/get_package_name.py info com.tencent.mm
应用信息: com.tencent.mm
------------------------------------------------------------
包名: com.tencent.mm
应用名称: 微信
版本: 8.0.xx
```

#### 添加到配置文件

找到包名后，可以添加到 `phone_agent/config/apps.py`：

```python
APP_PACKAGES: dict[str, str] = {
    # ... 现有应用 ...
    "新应用名称": "com.example.newapp",  # 添加新应用
    "新应用英文名": "com.example.newapp",  # 支持多个名称映射到同一包名
}
```

#### 其他查询方法

**使用 ADB 命令直接查询：**
```bash
# 列出所有第三方应用
adb shell pm list packages -3

# 搜索特定应用
adb shell pm list packages | grep wechat

# 查看当前前台应用
adb shell dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'
```

---

## 📝 配置说明

### 环境变量支持

所有参数都支持通过环境变量设置：

```bash
# 设置模型API地址
export PHONE_AGENT_BASE_URL="http://localhost:8000/v1"

# 设置模型名称
export PHONE_AGENT_MODEL="autoglm-phone-9b"

# 设置API密钥
export PHONE_AGENT_API_KEY="your-api-key"

# 设置最大步数
export PHONE_AGENT_MAX_STEPS="100"

# 设置设备ID
export PHONE_AGENT_DEVICE_ID="emulator-5554"

# 设置设备类型
export PHONE_AGENT_DEVICE_TYPE="adb"

# 设置语言
export PHONE_AGENT_LANG="cn"

# iOS WebDriverAgent URL
export PHONE_AGENT_WDA_URL="http://localhost:8100"
```

---

## 🔧 完整使用示例

### 示例1：基本使用
```bash
python main.py "打开微信并发送消息给张三"
```

### 示例2：保存结果到文件
```bash
python main.py --output ./results/result.json "打开微信"
```

### 示例3：允许所有应用
```bash
python main.py --allow-all-apps "打开com.example.myapp"
```

### 示例4：iOS设备使用
```bash
python main.py \
  --device-type ios \
  --wda-url http://localhost:8100 \
  --output ./ios_results/res.json \
  "打开Safari并搜索"
```

### 示例5：编程集成
```python
from main import main_params

def my_automation_task():
    result = main_params(
        base_url="http://localhost:8000/v1",
        model="autoglm-phone-9b",
        task="打开微信并发送消息",
        output="./results/result.json",
        allow_all_apps=False,
        max_steps=50
    )
    return result

if __name__ == "__main__":
    my_automation_task()
```

---

## 🐛 故障排除

### 问题1：无法保存结果文件
**解决方案：**
- 确保有写入权限
- 检查输出路径是否正确
- 确保磁盘空间充足

### 问题2：无法启动未配置的应用
**解决方案：**
- 使用 `--allow-all-apps` 参数
- 或先使用 `scripts/get_package_name.py` 查找包名，然后添加到配置

### 问题3：包名查询工具无法使用
**解决方案：**
- 确保 ADB 已安装并在 PATH 中
- 确保设备已连接：`adb devices`
- 确保已启用 USB 调试

---

## 📚 相关文件

- `main.py` - 主程序文件，包含所有新功能
- `phone_agent/config/apps.py` - 应用配置映射
- `scripts/get_package_name.py` - 包名查询工具
- `phone_agent/agent.py` - Android/HarmonyOS Agent
- `phone_agent/agent_ios.py` - iOS Agent

---

## 🔄 更新历史

### 最新更新
- ✅ 修改 `output` 参数为具体文件路径，支持 JSON 数组格式
- ✅ 添加 `--output` 参数支持结果保存
- ✅ 新增 `main_params()` 编程接口
- ✅ 添加 `--allow-all-apps` 参数支持所有应用
- ✅ 创建包名查询工具脚本

---

## 💡 提示

1. **结果保存**：现在支持指定具体 JSON 文件路径
2. **应用配置**：优先使用配置列表中的应用，更稳定可靠
3. **包名查询**：使用工具脚本可以快速找到应用的包名
4. **编程集成**：使用 `main_params()` 可以更好地集成到其他项目中

