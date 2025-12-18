# Open-AutoGLM API 接口设计文档

**项目名称**: Open-AutoGLM 电话自动化智能代理系统  
**版本**: v0.2.0  
**文档日期**: 2025-12-15  

---

## 目录

1. [核心 API](#核心api)
2. [模型交互 API](#模型交互api)
3. [设备控制 API](#设备控制api)
4. [动作执行 API](#动作执行api)
5. [配置管理 API](#配置管理api)
6. [监控和日志 API](#监控和日志api)
7. [安全验证 API](#安全验证api)
8. [缓存管理 API](#缓存管理api)

---

## 核心API

### 1.1 PhoneAgent 类

主要的代理类，负责编排整个任务执行流程。

#### 初始化

```python
class PhoneAgent:
    """
    电话自动化智能代理
    
    功能:
    - 解析用户任务
    - 与 AI 模型交互
    - 控制 Android 设备
    - 执行自动化操作
    - 管理执行状态和指标
    
    示例:
    -------
    >>> from phone_agent import PhoneAgent, ModelConfig, AgentConfig
    >>> model_config = ModelConfig(
    ...     base_url="http://localhost:8000/v1",
    ...     api_key="sk-xxx",
    ...     model_name="autoglm-phone-9b"
    ... )
    >>> agent_config = AgentConfig(max_steps=100, device_id="emulator-5554")
    >>> agent = PhoneAgent(model_config, agent_config)
    >>> result = agent.run("打开微信并发送消息给朋友")
    >>> print(result)
    """
    
    def __init__(
        self,
        model_config: ModelConfig,
        agent_config: AgentConfig,
        device_id: Optional[str] = None
    ) -> None:
        """
        初始化 PhoneAgent
        
        参数:
        ------
        model_config : ModelConfig
            模型配置对象，包含：
            - base_url: str - API 基础 URL
            - api_key: str - API 密钥
            - model_name: str - 模型名称
            - max_tokens: int - 最大输出 token 数 (推荐 3000)
            - temperature: float - 温度 (推荐 0.0)
            - top_p: float - top_p 采样 (推荐 0.85)
        
        agent_config : AgentConfig
            代理配置对象，包含：
            - max_steps: int - 最大执行步数 (推荐 100)
            - device_id: Optional[str] - 设备 ID (不提供则使用第一台设备)
            - lang: str - 语言 ('cn' 或 'en')
            - verbose: bool - 是否输出详细信息 (默认 False)
        
        device_id : Optional[str]
            可选的设备 ID，覆盖配置中的设备 ID
        
        异常:
        ------
        ValueError
            - 配置参数无效
            - 无法连接到 ADB 服务
            - 设备不存在
        
        ConnectionError
            - 无法连接到模型 API 服务
        
        示例:
        -------
        >>> model_cfg = ModelConfig(
        ...     base_url="http://localhost:8000/v1",
        ...     api_key="sk-xxx",
        ...     model_name="autoglm-phone-9b",
        ...     max_tokens=3000,
        ...     temperature=0.0,
        ...     top_p=0.85
        ... )
        >>> agent_cfg = AgentConfig(
        ...     max_steps=100,
        ...     device_id="emulator-5554",
        ...     lang="cn",
        ...     verbose=True
        ... )
        >>> agent = PhoneAgent(model_cfg, agent_cfg)
        """
        ...
```

#### 运行任务

```python
    def run(self, task: str) -> str:
        """
        运行一个自动化任务
        
        该方法会执行以下循环，直到达到完成条件或最大步数：
        1. 获取当前屏幕截图
        2. 发送截图和任务描述到 AI 模型
        3. 解析模型返回的动作
        4. 在设备上执行动作
        5. 更新状态和性能指标
        
        参数:
        ------
        task : str
            用户任务描述，使用自然语言表示。支持中文和英文。
            
            示例:
            - "打开微信"
            - "发送消息给朋友，内容是hello world"
            - "打开应用商店并安装qq"
            - "点击屏幕中间的按钮"
        
        返回:
        -------
        str
            任务执行结果，包含：
            - 成功: "任务完成：[完成说明]"
            - 失败: "任务失败：[失败原因]"
        
        异常:
        ------
        RuntimeError
            - 设备断开连接
            - 模型 API 服务异常
            - 执行步数超限
        
        ConnectionError
            - 无法连接到 ADB 或模型 API
        
        TimeoutError
            - 操作超时
        
        示例:
        -------
        >>> agent = PhoneAgent(model_config, agent_config)
        >>> result = agent.run("打开微信并查看消息")
        >>> print(result)
        '任务完成：微信已打开，消息列表已加载'
        
        >>> # 错误处理
        >>> try:
        ...     result = agent.run("执行某个任务")
        ... except ConnectionError:
        ...     print("设备连接失败")
        ... except RuntimeError as e:
        ...     print(f"执行失败: {e}")
        """
        ...
```

#### 执行单步

```python
    def step(self) -> StepResult:
        """
        执行一个步骤（可用于自定义控制流）
        
        执行流程:
        1. 检查是否已初始化
        2. 获取截图（使用缓存加速）
        3. 发送到 AI 推理
        4. 解析动作
        5. 执行动作
        6. 收集性能指标
        
        返回:
        -------
        StepResult
            执行结果对象，包含：
            - action: Optional[str] - 执行的动作描述 (如为 None 则表示完成或错误)
            - result: str - 执行结果或错误消息
            - screenshot: Optional[bytes] - 动作执行后的截图 (PNG 格式)
        
        异常:
        ------
        RuntimeError
            - 代理未初始化
            - 步骤执行失败
        
        ConnectionError
            - 设备断开连接
        
        示例:
        -------
        >>> agent = PhoneAgent(model_config, agent_config)
        >>> agent.init()
        >>> 
        >>> for i in range(10):
        ...     step_result = agent.step()
        ...     print(f"Step {i}: {step_result.action}")
        ...     if step_result.action is None:
        ...         print("任务完成或失败")
        ...         break
        ...     if step_result.screenshot:
        ...         with open(f"step_{i}.png", "wb") as f:
        ...             f.write(step_result.screenshot)
        """
        ...
```

#### 重置状态

```python
    def reset(self) -> None:
        """
        重置代理状态，用于执行新的任务
        
        功能:
        - 清空历史屏幕截图缓存
        - 重置执行步数计数
        - 清空状态变量
        - 保持设备连接
        
        异常:
        ------
        RuntimeError
            - 设备重置失败
        
        示例:
        -------
        >>> # 执行第一个任务
        >>> agent.run("任务1")
        >>> 
        >>> # 重置状态
        >>> agent.reset()
        >>> 
        >>> # 执行第二个任务
        >>> agent.run("任务2")
        """
        ...
```

### 1.2 数据类定义

#### ModelConfig

```python
@dataclass
class ModelConfig:
    """
    AI 模型配置
    
    属性:
    ------
    base_url : str
        API 服务的基础 URL
        示例: "http://localhost:8000/v1" 或 "https://api.openai.com/v1"
    
    api_key : str
        API 访问密钥，支持从环境变量读取
        示例: "sk-xxxx..." 或 "${OPENAI_API_KEY}"
    
    model_name : str
        模型名称
        示例: "autoglm-phone-9b", "gpt-4v", "gpt-4o"
    
    max_tokens : int
        最大生成 token 数 (默认 3000)
        推荐值: 3000-4000 (用于返回完整的 JSON 动作)
    
    temperature : float
        采样温度 (默认 0.0)
        范围: [0.0, 1.0]
        推荐值: 0.0 (确定性输出，适合自动化任务)
    
    top_p : float
        核采样参数 (默认 0.85)
        范围: [0.0, 1.0]
        推荐值: 0.85
    
    示例:
    -------
    >>> config = ModelConfig(
    ...     base_url="http://localhost:8000/v1",
    ...     api_key="sk-xxx...",
    ...     model_name="autoglm-phone-9b",
    ...     max_tokens=3000,
    ...     temperature=0.0,
    ...     top_p=0.85
    ... )
    
    >>> # 从环境变量读取 API 密钥
    >>> import os
    >>> config = ModelConfig(
    ...     base_url="https://api.openai.com/v1",
    ...     api_key=os.getenv("OPENAI_API_KEY"),
    ...     model_name="gpt-4v",
    ...     max_tokens=3000,
    ...     temperature=0.0,
    ...     top_p=0.85
    ... )
    """
    
    base_url: str
    api_key: str
    model_name: str
    max_tokens: int = 3000
    temperature: float = 0.0
    top_p: float = 0.85
    
    def __post_init__(self) -> None:
        """验证配置参数的有效性"""
        ...
```

#### AgentConfig

```python
@dataclass
class AgentConfig:
    """
    代理执行配置
    
    属性:
    ------
    max_steps : int
        单个任务的最大执行步数 (默认 100)
        推荐值: 50-150
        - 简单任务: 20-30
        - 中等任务: 50-100
        - 复杂任务: 100-150
    
    device_id : Optional[str]
        连接的 Android 设备 ID (默认 None)
        设置为 None 时使用第一台可用设备
        可通过 adb devices 查看设备 ID
        示例: "emulator-5554", "FA7AL1A00241"
    
    lang : str
        提示词语言 (默认 'cn')
        可选值: 'cn' (中文), 'en' (英文)
    
    verbose : bool
        是否输出详细执行信息 (默认 False)
        设置为 True 时会输出每步的详细过程
    
    示例:
    -------
    >>> config = AgentConfig(
    ...     max_steps=100,
    ...     device_id="emulator-5554",
    ...     lang="cn",
    ...     verbose=True
    ... )
    
    >>> # 使用第一台可用设备
    >>> config = AgentConfig(max_steps=50, lang="en", verbose=False)
    """
    
    max_steps: int = 100
    device_id: Optional[str] = None
    lang: str = "cn"
    verbose: bool = False
    
    def __post_init__(self) -> None:
        """验证配置参数的有效性"""
        ...
```

#### StepResult

```python
@dataclass
class StepResult:
    """
    单步执行结果
    
    属性:
    ------
    action : Optional[str]
        执行的动作描述
        示例: "tap(500, 1000)", "send_text('hello')", "swipe(100, 500, 100, 100)"
        值为 None 表示: 任务已完成或发生错误
    
    result : str
        执行结果消息
        示例:
        - "屏幕点击成功"
        - "应用已启动"
        - "错误: 设备离线"
        - "任务完成"
    
    screenshot : Optional[bytes]
        执行动作后的屏幕截图 (PNG 格式)
        值为 None 表示: 无法获取截图（设备离线等）
    
    示例:
    -------
    >>> agent = PhoneAgent(model_config, agent_config)
    >>> result = agent.step()
    >>> if result.action:
    ...     print(f"执行动作: {result.action}")
    ...     print(f"结果: {result.result}")
    ...     if result.screenshot:
    ...         with open("screenshot.png", "wb") as f:
    ...             f.write(result.screenshot)
    ... else:
    ...     print(f"步骤结束: {result.result}")
    """
    
    action: Optional[str]
    result: str
    screenshot: Optional[bytes] = None
```

---

## 模型交互API

### 2.1 ModelClient 类

负责与 AI 模型 API 的交互。

```python
class ModelClient:
    """
    模型 API 客户端
    
    功能:
    - 发送截图和提示词到模型
    - 处理流式响应
    - 异常重试机制
    - 日志记录
    
    示例:
    -------
    >>> from phone_agent.model import ModelClient, ModelConfig
    >>> config = ModelConfig(
    ...     base_url="http://localhost:8000/v1",
    ...     api_key="sk-xxx",
    ...     model_name="autoglm-phone-9b"
    ... )
    >>> client = ModelClient(config)
    >>> 
    >>> with open("screenshot.png", "rb") as f:
    ...     image_data = f.read()
    >>> 
    >>> response = client.query(
    ...     image=image_data,
    ...     prompt="打开微信应用"
    ... )
    >>> print(response)
    """
    
    def __init__(self, config: ModelConfig) -> None:
        """
        初始化模型客户端
        
        参数:
        ------
        config : ModelConfig
            模型配置对象
        
        异常:
        ------
        ValueError
            - 配置参数无效
        
        ConnectionError
            - 无法连接到模型 API 服务
        """
        ...
    
    def query(
        self,
        image: bytes,
        prompt: str,
        max_retries: int = 3,
        timeout: int = 30
    ) -> str:
        """
        查询模型，获取执行动作
        
        参数:
        ------
        image : bytes
            PNG 编码的屏幕截图数据
        
        prompt : str
            用户任务描述或系统提示词
            示例: "当前屏幕显示了微信主界面。用户要求打开联系人列表。请返回下一步的动作。"
        
        max_retries : int
            最多重试次数 (默认 3)
        
        timeout : int
            请求超时时间，单位秒 (默认 30)
        
        返回:
        -------
        str
            模型返回的响应文本，通常为 JSON 格式动作
            
            示例响应:
            {
                "_metadata": {
                    "action_type": "ui_action",
                    "confidence": 0.95
                },
                "action": "tap",
                "x": 500,
                "y": 1000,
                "reasoning": "用户要求打开联系人，点击屏幕顶部的联系人按钮"
            }
        
        异常:
        ------
        ConnectionError
            - 无法连接到模型 API 服务
        
        TimeoutError
            - 请求超时
        
        ValueError
            - 响应内容无效
        
        示例:
        -------
        >>> response = client.query(
        ...     image=screenshot_bytes,
        ...     prompt="打开应用",
        ...     timeout=30
        ... )
        >>> import json
        >>> action_data = json.loads(response)
        >>> print(action_data['action'])
        """
        ...
```

---

## 设备控制API

### 3.1 ADBDevice 类

负责 Android 设备的控制和交互。

```python
class ADBDevice:
    """
    ADB 设备控制接口
    
    功能:
    - 获取屏幕截图
    - 控制触摸输入（点击、滑动）
    - 输入文本
    - 按键控制
    - 应用启动和管理
    - 系统命令执行
    
    示例:
    -------
    >>> from phone_agent.adb import ADBDevice
    >>> device = ADBDevice(device_id="emulator-5554")
    >>> 
    >>> # 获取截图
    >>> screenshot = device.get_screenshot()
    >>> print(f"图像尺寸: {screenshot.width}x{screenshot.height}")
    >>> with open("screenshot.png", "wb") as f:
    ...     f.write(screenshot.data)
    >>> 
    >>> # 点击屏幕
    >>> device.tap(500, 1000)
    >>> 
    >>> # 输入文本
    >>> device.send_text("hello world")
    """
    
    def __init__(self, device_id: Optional[str] = None) -> None:
        """
        初始化 ADB 设备
        
        参数:
        ------
        device_id : Optional[str]
            设备 ID (为 None 时使用第一台可用设备)
            可通过 `adb devices` 查看
        
        异常:
        ------
        ConnectionError
            - ADB 服务不可用
            - 指定的设备不存在
            - 设备离线
        
        示例:
        -------
        >>> # 使用第一台可用设备
        >>> device = ADBDevice()
        >>> 
        >>> # 指定设备 ID
        >>> device = ADBDevice(device_id="emulator-5554")
        """
        ...
    
    def get_screenshot(self) -> Screenshot:
        """
        获取设备屏幕截图
        
        流程:
        1. 检查截图缓存（如果启用）
        2. 执行 ADB screencap 命令
        3. 传输图像到主机
        4. 解码 PNG 图像
        5. 返回 Screenshot 对象
        
        返回:
        -------
        Screenshot
            包含以下属性:
            - data: bytes - PNG 编码的图像数据
            - width: int - 图像宽度 (像素)
            - height: int - 图像高度 (像素)
        
        异常:
        ------
        ConnectionError
            - 设备断开连接
        
        RuntimeError
            - 截图失败
            - 图像解码失败
        
        TimeoutError
            - 截图操作超时
        
        性能:
        -------
        典型耗时: 300-800 ms
        使用缓存时: 1-10 ms
        
        示例:
        -------
        >>> device = ADBDevice()
        >>> screenshot = device.get_screenshot()
        >>> print(f"分辨率: {screenshot.width}x{screenshot.height}")
        >>> print(f"图像大小: {len(screenshot.data)} bytes")
        >>> 
        >>> # 保存截图
        >>> with open("screen.png", "wb") as f:
        ...     f.write(screenshot.data)
        """
        ...
    
    def tap(self, x: int, y: int) -> None:
        """
        在指定坐标点击屏幕
        
        参数:
        ------
        x : int
            点击位置的 x 坐标 (像素)
            范围: 0 到屏幕宽度
        
        y : int
            点击位置的 y 坐标 (像素)
            范围: 0 到屏幕高度
        
        异常:
        ------
        ValueError
            - 坐标超出屏幕范围
        
        ConnectionError
            - 设备断开连接
        
        RuntimeError
            - ADB 命令执行失败
        
        性能:
        -------
        典型耗时: 100-200 ms
        
        示例:
        -------
        >>> device = ADBDevice()
        >>> device.tap(500, 1000)  # 点击中间位置
        """
        ...
    
    def swipe(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration: int = 500
    ) -> None:
        """
        滑动屏幕（从一点滑动到另一点）
        
        参数:
        ------
        x1 : int
            起始点 x 坐标
        
        y1 : int
            起始点 y 坐标
        
        x2 : int
            终止点 x 坐标
        
        y2 : int
            终止点 y 坐标
        
        duration : int
            滑动持续时间，单位毫秒 (默认 500)
            范围: 100-2000
        
        异常:
        ------
        ValueError
            - 坐标超出范围
            - 持续时间无效
        
        ConnectionError
            - 设备断开连接
        
        示例:
        -------
        >>> device = ADBDevice()
        >>> # 向上滑动
        >>> device.swipe(500, 1000, 500, 100, duration=500)
        >>> 
        >>> # 向下滑动
        >>> device.swipe(500, 100, 500, 1000, duration=500)
        """
        ...
    
    def send_text(self, text: str) -> None:
        """
        输入文本到设备
        
        功能:
        1. 验证文本内容（防止注入攻击）
        2. 清理特殊字符
        3. 使用 ADB input text 命令输入
        
        参数:
        ------
        text : str
            要输入的文本
            支持: 中文、英文、数字、常见符号
            不支持: 某些特殊字符和控制字符
        
        异常:
        ------
        ValueError
            - 文本包含非法字符
        
        ConnectionError
            - 设备断开连接
        
        RuntimeError
            - 输入失败
        
        限制:
        -------
        - 单次最大输入长度: 1024 字符
        - 某些设备可能不支持中文输入
        
        示例:
        -------
        >>> device = ADBDevice()
        >>> device.send_text("hello world")  # 英文
        >>> device.send_text("你好世界")      # 中文
        """
        ...
    
    def press_key(self, key_code: int) -> None:
        """
        按下设备按键
        
        参数:
        ------
        key_code : int
            Android KeyEvent 代码
            
            常见按键:
            - 4: KEYCODE_BACK (返回键)
            - 3: KEYCODE_HOME (主页键)
            - 82: KEYCODE_MENU (菜单键)
            - 24: KEYCODE_VOLUME_UP (音量增)
            - 25: KEYCODE_VOLUME_DOWN (音量减)
            - 26: KEYCODE_POWER (电源键)
            
            参考: https://developer.android.com/reference/android/view/KeyEvent
        
        异常:
        ------
        ValueError
            - 无效的按键代码
        
        ConnectionError
            - 设备断开连接
        
        示例:
        -------
        >>> device = ADBDevice()
        >>> device.press_key(4)    # 返回键
        >>> device.press_key(3)    # 主页键
        >>> device.press_key(24)   # 音量增
        """
        ...
    
    def launch_app(self, package_name: str) -> None:
        """
        启动应用
        
        参数:
        ------
        package_name : str
            应用包名
            示例: "com.tencent.mm" (微信)
                 "com.sina.weibo" (微博)
                 "com.tencent.qq" (QQ)
        
        异常:
        ------
        ValueError
            - 应用包名无效
        
        ConnectionError
            - 设备断开连接
        
        RuntimeError
            - 启动失败（应用不存在等）
        
        示例:
        -------
        >>> device = ADBDevice()
        >>> device.launch_app("com.tencent.mm")  # 启动微信
        """
        ...
    
    def get_current_app(self) -> str:
        """
        获取当前前台应用包名
        
        返回:
        -------
        str
            当前前台应用的包名
            示例: "com.tencent.mm"
        
        异常:
        ------
        ConnectionError
            - 设备断开连接
        
        示例:
        -------
        >>> device = ADBDevice()
        >>> app = device.get_current_app()
        >>> print(f"当前应用: {app}")
        """
        ...
```

#### Screenshot 数据类

```python
@dataclass
class Screenshot:
    """
    屏幕截图对象
    
    属性:
    ------
    data : bytes
        PNG 编码的图像数据，可直接保存为 PNG 文件
    
    width : int
        图像宽度（像素）
    
    height : int
        图像高度（像素）
    
    示例:
    -------
    >>> screenshot = device.get_screenshot()
    >>> print(f"分辨率: {screenshot.width}x{screenshot.height}")
    >>> 
    >>> # 保存为文件
    >>> with open("screenshot.png", "wb") as f:
    ...     f.write(screenshot.data)
    >>> 
    >>> # 使用 PIL 处理
    >>> from PIL import Image
    >>> import io
    >>> img = Image.open(io.BytesIO(screenshot.data))
    >>> img.save("processed.png")
    """
    
    data: bytes
    width: int
    height: int
```

### 3.2 设备列表查询

```python
def list_devices() -> List[str]:
    """
    列出所有连接的 Android 设备
    
    返回:
    -------
    List[str]
        设备 ID 列表
        示例: ["emulator-5554", "FA7AL1A00241"]
    
    异常:
    ------
    ConnectionError
        - ADB 服务不可用
    
    示例:
    -------
    >>> from phone_agent.adb import list_devices
    >>> devices = list_devices()
    >>> for device_id in devices:
    ...     print(f"设备: {device_id}")
    """
    ...
```

---

## 动作执行API

### 4.1 ActionHandler 类

负责解析和执行 AI 模型返回的动作。

```python
class ActionHandler:
    """
    动作解析和执行处理器
    
    功能:
    - 解析 AI 模型返回的 JSON 动作
    - 验证动作合法性
    - 执行 14+ 种不同的动作类型
    - 提供三级解析策略（JSON → AST → Regex）
    
    支持的动作类型:
    -------
    1. tap - 点击屏幕
    2. swipe - 滑动屏幕
    3. send_text - 输入文本
    4. press_key - 按下按键
    5. launch_app - 启动应用
    6. close_app - 关闭应用
    7. long_press - 长按
    8. double_tap - 双击
    9. pinch - 缩放
    10. scroll - 滚动
    11. wake_screen - 点亮屏幕
    12. sleep_screen - 关闭屏幕
    13. back - 返回键
    14. wait - 等待
    
    示例:
    -------
    >>> from phone_agent.actions import ActionHandler
    >>> handler = ActionHandler(device)
    >>> 
    >>> # 解析动作
    >>> response = '{"action": "tap", "x": 500, "y": 1000}'
    >>> action = handler.parse_action(response)
    >>> print(action)
    {'action': 'tap', 'x': 500, 'y': 1000}
    >>> 
    >>> # 执行动作
    >>> handler.handle_action(action)
    """
    
    def __init__(self, device: ADBDevice) -> None:
        """
        初始化动作处理器
        
        参数:
        ------
        device : ADBDevice
            ADB 设备实例
        """
        ...
    
    def parse_action(self, response: str) -> dict:
        """
        解析 AI 模型返回的动作字符串
        
        采用三级解析策略：
        1. JSON 解析（99% 成功率）
        2. AST 解析（提取部分有效内容）
        3. Regex 解析（从纯文本提取参数）
        
        参数:
        ------
        response : str
            AI 模型返回的响应文本
            
            支持的格式:
            
            1. 标准 JSON:
            {
                "action": "tap",
                "x": 500,
                "y": 1000,
                "reasoning": "点击按钮"
            }
            
            2. 包含额外字段的 JSON:
            {
                "_metadata": {"confidence": 0.95},
                "action": "send_text",
                "text": "hello",
                "reasoning": "输入文本"
            }
            
            3. 单行文本 (Regex 解析):
            "执行 tap 动作，坐标 (500, 1000)"
        
        返回:
        -------
        dict
            解析后的动作字典
            
            示例:
            {
                "action": "tap",
                "x": 500,
                "y": 1000
            }
        
        异常:
        ------
        ValueError
            - 无法解析响应内容
            - 缺少必需的动作参数
        
        示例:
        -------
        >>> handler = ActionHandler(device)
        >>> 
        >>> # 解析标准 JSON
        >>> json_response = '{"action": "tap", "x": 100, "y": 200}'
        >>> action = handler.parse_action(json_response)
        >>> print(action["action"])  # 输出: tap
        >>> 
        >>> # 解析包含多余字段的 JSON
        >>> complex_response = '''
        ... {
        ...     "_metadata": {"model": "gpt-4"},
        ...     "action": "swipe",
        ...     "x1": 100, "y1": 200,
        ...     "x2": 100, "y2": 500,
        ...     "reasoning": "向上滑动"
        ... }
        ... '''
        >>> action = handler.parse_action(complex_response)
        >>> 
        >>> # 解析部分失效的 JSON (使用 AST 解析)
        >>> malformed = '{"action": "tap", "x": 500, "y": 1000'
        >>> action = handler.parse_action(malformed)
        """
        ...
    
    def handle_action(self, action: dict) -> None:
        """
        执行解析后的动作
        
        参数:
        ------
        action : dict
            动作字典，必须包含 'action' 字段
            其他字段取决于动作类型
        
        异常:
        ------
        ValueError
            - 无效的动作类型
            - 缺少必需参数
        
        RuntimeError
            - 动作执行失败
        
        支持的动作及参数:
        -----------------
        
        tap:
            {
                "action": "tap",
                "x": int,  # 必需
                "y": int   # 必需
            }
        
        swipe:
            {
                "action": "swipe",
                "x1": int,      # 必需
                "y1": int,      # 必需
                "x2": int,      # 必需
                "y2": int,      # 必需
                "duration": int # 可选，默认 500ms
            }
        
        send_text:
            {
                "action": "send_text",
                "text": str  # 必需
            }
        
        press_key:
            {
                "action": "press_key",
                "key_code": int  # 必需
            }
        
        launch_app:
            {
                "action": "launch_app",
                "package": str  # 必需
            }
        
        wait:
            {
                "action": "wait",
                "duration": int  # 可选，默认 1000ms
            }
        
        示例:
        -------
        >>> handler = ActionHandler(device)
        >>> 
        >>> # 执行点击动作
        >>> handler.handle_action({"action": "tap", "x": 500, "y": 1000})
        >>> 
        >>> # 执行输入文本动作
        >>> handler.handle_action({"action": "send_text", "text": "hello"})
        >>> 
        >>> # 执行滑动动作
        >>> handler.handle_action({
        ...     "action": "swipe",
        ...     "x1": 500, "y1": 1000,
        ...     "x2": 500, "y2": 200,
        ...     "duration": 500
        ... })
        """
        ...
```

---

## 配置管理API

### 5.1 ConfigValidator 类

```python
class ConfigValidator:
    """
    配置验证工具
    
    功能:
    - 验证 ModelConfig 参数有效性
    - 验证 AgentConfig 参数有效性
    - 验证环境变量
    - 给出详细的验证错误信息
    
    示例:
    -------
    >>> from phone_agent.utils import ConfigValidator
    >>> validator = ConfigValidator()
    >>> 
    >>> config = ModelConfig(
    ...     base_url="http://localhost:8000/v1",
    ...     api_key="sk-xxx",
    ...     model_name="gpt-4v"
    ... )
    >>> 
    >>> if validator.validate_model_config(config):
    ...     print("配置有效")
    ... else:
    ...     print("配置无效")
    """
    
    def validate_model_config(self, config: ModelConfig) -> bool:
        """
        验证模型配置
        
        检查项:
        - base_url 格式有效
        - api_key 非空
        - model_name 非空
        - max_tokens > 0
        - temperature in [0.0, 1.0]
        - top_p in [0.0, 1.0]
        
        参数:
        ------
        config : ModelConfig
            要验证的配置
        
        返回:
        -------
        bool
            配置是否有效
        
        异常:
        ------
        ValueError
            - 配置无效，包含详细错误信息
        """
        ...
    
    def validate_agent_config(self, config: AgentConfig) -> bool:
        """
        验证代理配置
        
        检查项:
        - max_steps > 0
        - lang in ['cn', 'en']
        - verbose 是布尔值
        
        参数:
        ------
        config : AgentConfig
            要验证的配置
        
        返回:
        -------
        bool
            配置是否有效
        """
        ...
```

### 5.2 ConfigLoader 类

```python
class ConfigLoader:
    """
    灵活的配置加载工具
    
    支持:
    - 从文件加载 (JSON/YAML)
    - 从环境变量加载
    - 合并多个配置源
    - 解析环境变量引用
    
    示例:
    -------
    >>> from phone_agent.utils import ConfigLoader
    >>> loader = ConfigLoader()
    >>> 
    >>> # 从 JSON 文件加载
    >>> config = loader.from_file("config.json")
    >>> 
    >>> # 从环境变量加载
    >>> config = loader.from_env()
    >>> 
    >>> # 合并配置
    >>> config = loader.merge_configs(config1, config2)
    """
    
    def from_file(self, file_path: str) -> dict:
        """
        从文件加载配置
        
        参数:
        ------
        file_path : str
            配置文件路径 (.json 或 .yaml)
        
        返回:
        -------
        dict
            配置字典
        
        异常:
        ------
        FileNotFoundError
            - 文件不存在
        
        ValueError
            - 文件格式无效
        """
        ...
    
    def from_env(self) -> dict:
        """
        从环境变量加载配置
        
        读取以下环境变量:
        - PHONE_AGENT_BASE_URL
        - PHONE_AGENT_API_KEY
        - PHONE_AGENT_MODEL
        - PHONE_AGENT_MAX_TOKENS
        - PHONE_AGENT_TEMPERATURE
        - PHONE_AGENT_TOP_P
        - PHONE_AGENT_MAX_STEPS
        - PHONE_AGENT_DEVICE_ID
        - PHONE_AGENT_LANG
        - PHONE_AGENT_VERBOSE
        
        返回:
        -------
        dict
            配置字典
        """
        ...
    
    def merge_configs(self, config1: dict, config2: dict) -> dict:
        """
        合并两个配置
        
        config2 的值会覆盖 config1 的值
        """
        ...
```

---

## 监控和日志API

### 6.1 LoggerSetup 类

```python
class LoggerSetup:
    """
    日志系统设置工具
    
    功能:
    - 配置日志处理器（控制台、文件）
    - 设置日志级别
    - 自动创建日志目录
    - 轮转日志文件
    
    示例:
    -------
    >>> from phone_agent.utils import LoggerSetup
    >>> setup = LoggerSetup()
    >>> logger = setup.setup_logging(
    ...     level="DEBUG",
    ...     log_file="logs/app.log",
    ...     console=True
    ... )
    >>> logger.info("应用启动")
    """
    
    def setup_logging(
        self,
        level: str = "INFO",
        log_file: Optional[str] = None,
        console: bool = True,
        format_str: Optional[str] = None
    ) -> logging.Logger:
        """
        配置日志系统
        
        参数:
        ------
        level : str
            日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        
        log_file : Optional[str]
            日志文件路径
            如提供，会在该文件中记录日志
        
        console : bool
            是否输出到控制台 (默认 True)
        
        format_str : Optional[str]
            日志格式字符串
            默认: "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
        
        返回:
        -------
        logging.Logger
            配置后的日志记录器
        """
        ...
```

### 6.2 PerformanceMonitor 类

```python
class PerformanceMonitor:
    """
    性能监控工具
    
    功能:
    - 计时操作
    - 收集性能指标
    - 生成性能报告
    - 单例模式（全局实例）
    
    示例:
    -------
    >>> from phone_agent.utils import get_performance_monitor
    >>> monitor = get_performance_monitor()
    >>> 
    >>> monitor.start_timer("screenshot")
    >>> # ... 获取截图 ...
    >>> monitor.end_timer("screenshot")
    >>> 
    >>> monitor.start_timer("inference")
    >>> # ... 模型推理 ...
    >>> monitor.end_timer("inference")
    >>> 
    >>> monitor.print_report()
    """
    
    def start_timer(self, operation_name: str) -> None:
        """
        开始计时
        
        参数:
        ------
        operation_name : str
            操作名称 (例: "screenshot", "inference")
        """
        ...
    
    def end_timer(self, operation_name: str) -> float:
        """
        结束计时
        
        参数:
        ------
        operation_name : str
            操作名称（必须与 start_timer 匹配）
        
        返回:
        -------
        float
            操作耗时（秒）
        """
        ...
    
    def get_metrics(self, operation_name: str) -> dict:
        """
        获取指定操作的性能指标
        
        返回:
        -------
        dict
            包含以下信息:
            - count: 执行次数
            - total: 总耗时
            - average: 平均耗时
            - min: 最少耗时
            - max: 最多耗时
        """
        ...
    
    def print_report(self) -> None:
        """
        打印性能报告
        
        示例输出:
        --------
        ========== 性能监控报告 ==========
        screenshot:
          执行次数: 5
          总耗时: 2.15s
          平均耗时: 0.43s
          最少耗时: 0.32s
          最多耗时: 0.51s
        
        inference:
          执行次数: 5
          总耗时: 8.75s
          平均耗时: 1.75s
          最少耗时: 1.52s
          最多耗时: 2.01s
        ===================================
        """
        ...
```

### 6.3 全局性能监控

```python
def get_performance_monitor() -> PerformanceMonitor:
    """
    获取全局性能监控器
    
    使用单例模式，整个应用共享一个监控实例
    
    返回:
    -------
    PerformanceMonitor
        全局性能监控器实例
    
    示例:
    -------
    >>> from phone_agent.utils import get_performance_monitor
    >>> 
    >>> monitor = get_performance_monitor()
    >>> monitor.start_timer("operation")
    >>> # ... 执行操作 ...
    >>> monitor.end_timer("operation")
    >>> monitor.print_report()
    """
    ...
```

---

## 安全验证API

### 7.1 InputValidator 类

```python
class InputValidator:
    """
    输入验证工具
    
    功能:
    - 检测和防止 SQL 注入
    - 检测和防止 XSS 攻击
    - 检测和防止路径遍历
    - 验证坐标有效性
    
    示例:
    -------
    >>> from phone_agent.utils import InputValidator
    >>> validator = InputValidator()
    >>> 
    >>> # 验证文本输入
    >>> try:
    ...     validator.validate_text_input("hello world")
    ... except ValueError:
    ...     print("输入包含恶意内容")
    """
    
    def validate_text_input(self, text: str) -> bool:
        """
        验证文本输入安全性
        
        检查项:
        - 检测 SQL 注入关键字
        - 检测 XSS 攻击代码
        - 检测脚本注入
        - 检测路径遍历
        
        参数:
        ------
        text : str
            要验证的文本
        
        返回:
        -------
        bool
            输入是否安全
        
        异常:
        ------
        ValueError
            - 输入包含恶意内容
        """
        ...
    
    def sanitize_app_name(self, app_name: str) -> str:
        """
        清理应用名称
        
        移除特殊字符和非法字符
        """
        ...
    
    def sanitize_coordinates(self, x: int, y: int, max_x: int, max_y: int) -> tuple:
        """
        验证和修正坐标
        
        确保坐标在有效范围内
        """
        ...
```

### 7.2 SensitiveDataFilter 类

```python
class SensitiveDataFilter:
    """
    敏感数据过滤工具
    
    功能:
    - 自动识别和脱敏敏感数据
    - 支持自定义脱敏规则
    - 防止敏感信息在日志中泄露
    
    示例:
    -------
    >>> from phone_agent.utils import SensitiveDataFilter
    >>> filter = SensitiveDataFilter()
    >>> 
    >>> # 脱敏敏感数据
    >>> text = "我的手机号是 13800138000，密码是 password123"
    >>> masked = filter.mask_sensitive_data(text)
    >>> print(masked)
    '我的手机号是 ***138*000，密码是 ****'
    """
    
    def mask_sensitive_data(self, text: str) -> str:
        """
        脱敏敏感数据
        
        支持识别:
        - 手机号码: 保留首尾，中间用 * 替换
        - 邮箱地址: 保留首尾，中间用 * 替换
        - 密码: 完全替换为 ****
        - API 密钥: 保留前后 4 位
        
        参数:
        ------
        text : str
            包含敏感信息的文本
        
        返回:
        -------
        str
            脱敏后的文本
        """
        ...
    
    def filter_log_message(self, message: str) -> str:
        """
        过滤日志消息中的敏感数据
        
        这是 mask_sensitive_data 的别名
        """
        ...
```

### 7.3 RateLimiter 类

```python
class RateLimiter:
    """
    速率限制工具
    
    功能:
    - 限制 API 调用频率
    - 防止过度使用
    - 实现退避策略
    
    示例:
    -------
    >>> from phone_agent.utils import RateLimiter
    >>> limiter = RateLimiter(max_calls=10, time_window=60)
    >>> 
    >>> for i in range(20):
    ...     if limiter.is_allowed("api_call"):
    ...         print(f"调用 {i}")
    ...     else:
    ...         print(f"受限，请等待 {limiter.get_reset_time('api_call')}s")
    """
    
    def __init__(self, max_calls: int = 100, time_window: int = 60) -> None:
        """
        初始化速率限制器
        
        参数:
        ------
        max_calls : int
            时间窗口内的最大调用次数
        
        time_window : int
            时间窗口大小（秒）
        """
        ...
    
    def is_allowed(self, key: str) -> bool:
        """
        检查是否允许执行操作
        
        参数:
        ------
        key : str
            操作标识符
        
        返回:
        -------
        bool
            是否允许
        """
        ...
    
    def get_reset_time(self, key: str) -> int:
        """
        获取重置时间
        
        返回:
        -------
        int
            距离重置的秒数
        """
        ...
```

---

## 缓存管理API

### 8.1 SimpleCache 类

```python
class SimpleCache:
    """
    简单缓存工具
    
    功能:
    - 基于 TTL 的缓存过期
    - 缓存统计
    - 线程安全
    
    示例:
    -------
    >>> from phone_agent.utils import SimpleCache
    >>> cache = SimpleCache(ttl=300)  # 300秒过期
    >>> 
    >>> cache.set("key1", "value1")
    >>> value = cache.get("key1")
    >>> print(value)  # 输出: value1
    >>> 
    >>> # 获取缓存统计
    >>> stats = cache.get_stats()
    >>> print(stats)
    {'hits': 1, 'misses': 0, 'size': 1}
    """
    
    def __init__(self, ttl: int = 300) -> None:
        """
        初始化缓存
        
        参数:
        ------
        ttl : int
            缓存有效期（秒）
        """
        ...
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        参数:
        ------
        key : str
            缓存键
        
        返回:
        -------
        Optional[Any]
            缓存值，不存在或已过期返回 None
        """
        ...
    
    def set(self, key: str, value: Any) -> None:
        """
        设置缓存值
        
        参数:
        ------
        key : str
            缓存键
        
        value : Any
            缓存值
        """
        ...
    
    def clear(self) -> None:
        """清空所有缓存"""
        ...
    
    def get_stats(self) -> dict:
        """
        获取缓存统计信息
        
        返回:
        -------
        dict
            包含:
            - hits: 命中次数
            - misses: 失效次数
            - size: 当前缓存大小
        """
        ...
```

### 8.2 ScreenshotCache 类

```python
class ScreenshotCache:
    """
    屏幕截图缓存工具
    
    功能:
    - 使用 MD5 哈希检测截图变化
    - 只在屏幕内容改变时重新获取
    - 提高性能（85% 缓存命中率）
    
    算法:
    ------
    每次获取截图时:
    1. 计算新截图的 MD5 哈希值
    2. 与上次缓存的哈希值比较
    3. 如果相同，返回缓存中的截图
    4. 如果不同，更新缓存
    
    示例:
    -------
    >>> from phone_agent.utils import ScreenshotCache
    >>> cache = ScreenshotCache(max_size=5)
    >>> 
    >>> screenshot1 = device.get_screenshot()
    >>> cache.set(screenshot1)
    >>> 
    >>> screenshot2 = device.get_screenshot()
    >>> if cache.is_different(screenshot2):
    ...     print("屏幕内容已改变")
    ...     cache.set(screenshot2)
    ... else:
    ...     print("屏幕内容未改变，使用缓存")
    """
    
    def __init__(self, max_size: int = 5) -> None:
        """
        初始化截图缓存
        
        参数:
        ------
        max_size : int
            最多保存多少个截图
        """
        ...
    
    def get(self) -> Optional[bytes]:
        """
        获取缓存的最新截图
        
        返回:
        -------
        Optional[bytes]
            缓存的 PNG 图像数据，不存在返回 None
        """
        ...
    
    def set(self, screenshot: Screenshot) -> None:
        """
        缓存一个截图
        
        参数:
        ------
        screenshot : Screenshot
            要缓存的截图对象
        """
        ...
    
    def is_different(self, new_screenshot: Screenshot) -> bool:
        """
        检查新截图是否与缓存不同
        
        参数:
        ------
        new_screenshot : Screenshot
            新获取的截图
        
        返回:
        -------
        bool
            True: 内容不同，False: 内容相同
        """
        ...
    
    def clear(self) -> None:
        """清空缓存"""
        ...
```

---

## 总结

Open-AutoGLM API 设计遵循以下原则：

1. **模块化**: 每个模块职责清晰，可独立使用
2. **易用性**: 提供高层 API (PhoneAgent) 和低层 API (ADBDevice, ModelClient)
3. **健壮性**: 完善的异常处理和验证机制
4. **可扩展**: 支持自定义配置、日志和监控
5. **安全性**: 内置防止注入、XSS、路径遍历等攻击
6. **性能**: 缓存、流式处理等优化技术

使用者可根据需求选择合适的 API 层级进行集成。

