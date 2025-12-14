#!/usr/bin/env python3
"""
Gradio Web UI for Phone Agent - AI-powered phone automation.

This provides a user-friendly web interface for controlling and monitoring
the phone agent assistant.
"""

import base64
import json
import os
import shutil
import subprocess
import tempfile
import time
import traceback
from datetime import datetime
from typing import Generator, List, Tuple

import gradio as gr
from openai import OpenAI

from phone_agent import PhoneAgent
from phone_agent.adb import get_screenshot, list_devices
from phone_agent.agent import AgentConfig, StepResult
from phone_agent.model import ModelConfig


# ============================================================================
# System Check Functions
# ============================================================================

def check_adb_installation() -> Tuple[bool, str]:
    """Check if ADB is installed and accessible."""
    if shutil.which("adb") is None:
        return False, "❌ ADB未安装或不在PATH中"

    try:
        result = subprocess.run(
            ["adb", "version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.strip().split("\n")[0]
            return True, f"✅ {version_line}"
        else:
            return False, "❌ ADB命令运行失败"
    except Exception as e:
        return False, f"❌ ADB检查失败: {str(e)}"


def check_device_connection() -> Tuple[bool, str, List[str]]:
    """Check connected devices."""
    try:
        devices = list_devices()
        if not devices:
            return False, "❌ 没有连接的设备", []

        device_list = [f"{d.device_id} ({d.model or 'Unknown'})" for d in devices]
        device_ids = [d.device_id for d in devices]
        return True, f"✅ 找到 {len(devices)} 个设备", device_ids
    except Exception as e:
        return False, f"❌ 设备检查失败: {str(e)}", []


def check_adb_keyboard(device_id: str = None) -> Tuple[bool, str]:
    """Check if ADB Keyboard is installed on the device."""
    try:
        cmd = ["adb"]
        if device_id:
            cmd.extend(["-s", device_id])
        cmd.extend(["shell", "ime", "list", "-s"])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        ime_list = result.stdout.strip()

        if "com.android.adbkeyboard/.AdbIME" in ime_list:
            return True, "✅ ADB Keyboard已安装"
        else:
            return False, "❌ ADB Keyboard未安装"
    except Exception as e:
        return False, f"❌ ADB Keyboard检查失败: {str(e)}"


def check_model_api(base_url: str, model_name: str, api_key: str = "EMPTY") -> Tuple[bool, str]:
    """Check if the model API is accessible."""
    try:
        client = OpenAI(base_url=base_url, api_key=api_key, timeout=10.0)
        models_response = client.models.list()
        available_models = [model.id for model in models_response.data]
        return True, f"✅ API连接成功 ({len(available_models)} 个可用模型)"
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg or "Connection error" in error_msg:
            return False, f"❌ 无法连接到 {base_url}"
        elif "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
            return False, f"❌ 连接超时: {base_url}"
        else:
            return False, f"❌ API错误: {error_msg}"


def run_full_system_check(base_url: str, model_name: str, api_key: str, device_id: str = None) -> str:
    """Run comprehensive system check."""
    report = ["# 系统环境检查报告", ""]
    report.append(f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # Check 1: ADB Installation
    report.append("## 1. ADB安装检查")
    adb_ok, adb_msg = check_adb_installation()
    report.append(adb_msg)
    report.append("")

    if not adb_ok:
        report.append("**提示**: 请先安装ADB工具")
        report.append("- macOS: `brew install android-platform-tools`")
        report.append("- Linux: `sudo apt install android-tools-adb`")
        report.append("- Windows: 从 [官网](https://developer.android.com/studio/releases/platform-tools) 下载")
        return "\n".join(report)

    # Check 2: Device Connection
    report.append("## 2. 设备连接检查")
    dev_ok, dev_msg, device_list = check_device_connection()
    report.append(dev_msg)
    if dev_ok:
        for dev in device_list:
            report.append(f"  - {dev}")
    report.append("")

    if not dev_ok:
        report.append("**提示**: 请连接Android设备并启用USB调试")
        return "\n".join(report)

    # Check 3: ADB Keyboard
    report.append("## 3. ADB Keyboard检查")
    kbd_ok, kbd_msg = check_adb_keyboard(device_id)
    report.append(kbd_msg)
    report.append("")

    if not kbd_ok:
        report.append("**提示**: 请在设备上安装ADB Keyboard")
        report.append("  1. 下载: [ADBKeyboard.apk](https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk)")
        report.append("  2. 安装: `adb install ADBKeyboard.apk`")
        report.append("  3. 在设置中启用该输入法")
        report.append("")

    # Check 4: Model API
    report.append("## 4. 模型API检查")
    api_ok, api_msg = check_model_api(base_url, model_name, api_key)
    report.append(api_msg)
    report.append("")

    if not api_ok:
        report.append("**提示**: 请检查模型服务器是否运行，并确认URL和API Key正确")
        report.append("")

    # Summary
    report.append("## 检查总结")
    all_ok = adb_ok and dev_ok and kbd_ok and api_ok
    if all_ok:
        report.append("✅ **所有检查通过！可以开始使用Phone Agent**")
    else:
        report.append("❌ **部分检查未通过，请根据上述提示修复问题**")

    return "\n".join(report)


# ============================================================================
# Agent Management
# ============================================================================

class AgentSession:
    """Manages a phone agent session."""

    def __init__(self, base_url: str, model_name: str, api_key: str,
                 max_steps: int, device_id: str, lang: str):
        self.model_config = ModelConfig(
            base_url=base_url,
            model_name=model_name,
            api_key=api_key,
        )

        self.agent_config = AgentConfig(
            max_steps=max_steps,
            device_id=device_id if device_id else None,
            lang=lang,
            verbose=True,
        )

        self.agent = PhoneAgent(
            model_config=self.model_config,
            agent_config=self.agent_config,
        )

        self.current_task = None
        self.should_stop = False

    def stop_task(self):
        """Stop the current running task."""
        self.should_stop = True


    def run_task_stream(self, task: str) -> Generator[Tuple[str, str], None, None]:
        """Run a task and yield updates for streaming display."""
        self.current_task = task
        self.should_stop = False
        self.agent.reset()

        # Yield initial message
        initial_output = self._format_step_output("开始执行任务", task, "info")
        yield initial_output, None

        # First step
        try:
            result = self.agent.step(task)
            step_output = self._format_step_result(result, 1)
            screenshot_path = self._get_screenshot()
            yield step_output, screenshot_path

            if result.finished:
                final_msg = result.message or "任务完成"
                final_output = self._format_step_output("任务完成", final_msg, "success")
                yield final_output, screenshot_path
                return
        except Exception as e:
            error_msg = f"错误: {str(e)}\n{traceback.format_exc()}"
            error_output = self._format_step_output("执行错误", error_msg, "error")
            yield error_output, None
            return

        # Continue steps
        while self.agent.step_count < self.agent_config.max_steps:
            # Check if task should be stopped
            if self.should_stop:
                screenshot_path = self._get_screenshot()
                stop_output = self._format_step_output("任务终止", "任务已被用户手动终止", "warning")
                yield stop_output, screenshot_path
                return

            try:
                result = self.agent.step()
                step_output = self._format_step_result(result, self.agent.step_count)
                screenshot_path = self._get_screenshot()
                yield step_output, screenshot_path

                if result.finished:
                    final_msg = result.message or "任务完成"
                    final_output = self._format_step_output("任务完成", final_msg, "success")
                    yield final_output, screenshot_path
                    return

            except Exception as e:
                error_msg = f"错误: {str(e)}\n{traceback.format_exc()}"
                error_output = self._format_step_output("执行错误", error_msg, "error")
                yield error_output, None
                return

        # Max steps reached
        screenshot_path = self._get_screenshot()
        warning_output = self._format_step_output("任务终止", "达到最大步数限制", "warning")
        yield warning_output, screenshot_path

    def _format_step_result(self, result: StepResult, step_num: int) -> str:
        """Format a step result for display."""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"📍 **步骤 {step_num}**")
        lines.append(f"{'='*60}\n")

        lines.append(f"### 💭 思考过程:")
        lines.append(f"```\n{result.thinking}\n```\n")

        if result.action:
            lines.append(f"### 🎯 执行动作:")
            lines.append(f"```json\n{json.dumps(result.action, ensure_ascii=False, indent=2)}\n```\n")

        if result.message:
            lines.append(f"### 📝 消息:")
            lines.append(f"> {result.message}\n")

        return "\n".join(lines)

    def _format_step_output(self, title: str, content: str, level: str = "info") -> str:
        """Format a step output message."""
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
        }
        icon = icons.get(level, "ℹ️")

        lines = [f"\n{'='*60}", f"{icon} **{title}**", f"{'='*60}\n"]
        lines.append(content)
        return "\n".join(lines)

    def _get_screenshot(self) -> str:
        """Get current device screenshot and save to temp file."""
        try:
            import base64
            from io import BytesIO
            from PIL import Image

            screenshot = get_screenshot(self.agent_config.device_id)
            # Convert base64 data back to image
            img_data = base64.b64decode(screenshot.base64_data)
            img = Image.open(BytesIO(img_data))

            # Save to temporary file
            temp_path = os.path.join(tempfile.gettempdir(), f"phone_agent_screenshot_{int(time.time())}.png")
            img.save(temp_path)
            return temp_path
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None



# Global session storage
sessions = {}
current_session_id = 0


def get_or_create_session(base_url: str, model_name: str, api_key: str,
                          max_steps: int, device_id: str, lang: str,
                          session_id: int = None) -> Tuple[AgentSession, int]:
    """Get existing session or create new one."""
    global current_session_id

    if session_id is None or session_id not in sessions:
        current_session_id += 1
        session_id = current_session_id
        sessions[session_id] = AgentSession(
            base_url, model_name, api_key, max_steps, device_id, lang
        )

    return sessions[session_id], session_id


# ============================================================================
# Gradio Interface Functions
# ============================================================================

def refresh_devices():
    """Refresh and return device list."""
    try:
        devices = list_devices()
        if not devices:
            return gr.Dropdown(choices=[], value=None, label="可用设备 (无设备)")

        device_choices = [f"{d.device_id} ({d.model or 'Unknown'})" for d in devices]
        device_ids = [d.device_id for d in devices]

        return gr.Dropdown(
            choices=list(zip(device_choices, device_ids)),
            value=device_ids[0] if device_ids else None,
            label=f"可用设备 ({len(devices)} 个)"
        )
    except Exception as e:
        return gr.Dropdown(choices=[], value=None, label=f"设备检查失败: {str(e)}")


def run_system_check(base_url, model_name, api_key, device_id):
    """Run system check and return report."""
    return run_full_system_check(base_url, model_name, api_key, device_id)


def execute_task(task, base_url, model_name, api_key, max_steps, device_id, lang, session_id):
    """Execute a task with streaming output."""
    if not task or not task.strip():
        yield "请输入任务内容", None, session_id
        return

    session, new_session_id = get_or_create_session(
        base_url, model_name, api_key, max_steps, device_id, lang, session_id
    )

    for output, screenshot in session.run_task_stream(task.strip()):
        yield output, screenshot, new_session_id


def new_conversation(base_url, model_name, api_key, max_steps, device_id, lang):
    """Start a new conversation."""
    global current_session_id
    current_session_id += 1
    session_id = current_session_id

    sessions[session_id] = AgentSession(
        base_url, model_name, api_key, max_steps, device_id, lang
    )

    return "开始新对话", None, session_id


def get_current_screenshot(device_id):
    """Get and display current device screenshot."""
    try:
        import base64
        from io import BytesIO
        from PIL import Image

        screenshot = get_screenshot(device_id)
        # Convert base64 data back to image
        img_data = base64.b64decode(screenshot.base64_data)
        img = Image.open(BytesIO(img_data))

        # Save to temp path
        temp_path = os.path.join(tempfile.gettempdir(), f"phone_agent_screenshot_current_{int(time.time())}.png")
        img.save(temp_path)
        return temp_path
    except Exception as e:
        print(f"Screenshot error: {e}")
        return None


def stop_current_task(session_id):
    """Stop the current running task."""
    if session_id and session_id in sessions:
        sessions[session_id].stop_task()
        return "正在终止任务..."
    return "没有运行中的任务"




# ============================================================================
# Gradio UI
# ============================================================================

def create_ui():
    """Create the Gradio interface."""

    with gr.Blocks(title="Phone Agent 手机助手", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🤖 Phone Agent 手机助手

        基于AI的智能手机自动化助手 - 通过自然语言控制您的Android设备
        """)

        # Session state
        session_state = gr.State(None)

        with gr.Tabs():

            # ================================================================
            # Tab 1: Device Management
            # ================================================================
            with gr.Tab("📱 设备管理"):
                gr.Markdown("""
                ### 设备连接管理
                查看和管理已连接的Android设备
                """)

                with gr.Row():
                    list_devices_btn = gr.Button("📋 列出设备", size="lg")
                    connect_ip = gr.Textbox(
                        label="远程设备地址",
                        placeholder="例如: 192.168.1.100:5555"
                    )
                    connect_btn = gr.Button("🔗 连接设备", size="lg")

                device_output = gr.Markdown("点击上方按钮查看设备信息")
            # ================================================================
            # Tab 2: System Check
            # ================================================================
            with gr.Tab("🔍 系统检查"):
                gr.Markdown("""
                ### 环境配置检查
                点击下方按钮检查系统环境是否满足运行要求
                """)

                check_btn = gr.Button("▶️ 运行系统检查", variant="primary", size="lg")
                check_output = gr.Markdown("点击上方按钮开始检查")


            # ================================================================
            # Tab 3: Main Interface
            # ================================================================
            with gr.Tab("💬 对话控制"):
                with gr.Row():
                    with gr.Column(scale=2):
                        # Configuration Section
                        with gr.Accordion("⚙️ 配置", open=False):
                            with gr.Row():
                                base_url = gr.Textbox(
                                    label="模型API地址",
                                    value=os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1"),
                                    placeholder="http://localhost:8000/v1"
                                )
                                model_name = gr.Textbox(
                                    label="模型名称",
                                    value=os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b"),
                                    placeholder="autoglm-phone-9b"
                                )

                            with gr.Row():
                                api_key = gr.Textbox(
                                    label="API Key",
                                    value=os.getenv("PHONE_AGENT_API_KEY", "EMPTY"),
                                    placeholder="EMPTY",
                                    type="password"
                                )
                                max_steps = gr.Number(
                                    label="最大步数",
                                    value=int(os.getenv("PHONE_AGENT_MAX_STEPS", "100")),
                                    precision=0
                                )

                            with gr.Row():
                                device_dropdown = gr.Dropdown(
                                    label="选择设备",
                                    choices=[],
                                    value=None,
                                    interactive=True
                                )
                                refresh_btn = gr.Button("🔄 刷新设备", size="sm")
                                lang = gr.Radio(
                                    choices=[("中文", "cn"), ("English", "en")],
                                    value="cn",
                                    label="语言"
                                )

                        # Task Input
                        task_input = gr.Textbox(
                            label="📝 输入任务",
                            placeholder="例如: 打开微信，给张三发送一条消息'你好'",
                            lines=3
                        )

                        with gr.Row():
                            submit_btn = gr.Button("🚀 执行任务", variant="primary", size="lg")
                            stop_btn = gr.Button("⏹️ 终止任务", variant="stop", size="lg")
                            new_chat_btn = gr.Button("➕ 新对话", size="lg")

                        # Output Display
                        output_display = gr.Markdown(
                            label="📤 执行输出",
                            value="等待任务输入..."
                        )

                    with gr.Column(scale=1):
                        # Screenshot Display
                        screenshot_display = gr.Image(
                            label="📱 设备截图",
                            type="filepath",
                            height=800,
                            width=360
                    
                        )

                        auto_refresh_checkbox = gr.Checkbox(
                            label="自动刷新(0.5s)",
                            value=False
                        )

                        # Auto-refresh timer
                        screenshot_timer = gr.Timer(value=0.5, active=False)

            # ================================================================
            # Tab 4: Help
            # ================================================================
            with gr.Tab("❓ 帮助"):
                gr.Markdown("""
                ## 📖 使用指南

                ### 快速开始

                1. **检查环境**: 前往"系统检查"标签页，运行系统检查确保环境配置正确
                2. **配置设置**: 在"配置"区域设置模型API地址和API Key
                3. **选择设备**: 点击"刷新设备"按钮，从下拉列表中选择目标设备
                4. **输入任务**: 在任务输入框中用自然语言描述您的需求
                5. **执行任务**: 点击"执行任务"按钮，系统会自动控制手机完成任务

                ### 功能说明

                #### 💬 对话控制
                - **任务执行**: 支持流式输出，实时显示AI的思考过程和执行动作
                - **截图显示**: 右侧实时显示设备当前屏幕状态
                - **新对话**: 清空当前上下文，开始全新的任务会话

                #### 🔍 系统检查
                - 检查ADB工具安装状态
                - 检查设备连接状态
                - 检查ADB Keyboard安装状态
                - 检查模型API连接状态

                #### 📱 设备管理
                - 查看所有已连接设备
                - 支持USB和WiFi连接
                - 远程设备连接功能

                ### 任务示例

                ```
                # 消息发送
                打开微信，给张三发送消息"晚上一起吃饭吗?"

                # 应用操作
                打开抖音，搜索"美食教程"，点赞第一个视频

                # 购物任务
                打开淘宝，搜索"机械键盘"，按价格从低到高排序，加购第一个商品

                # 信息查询
                打开小红书，搜索"成都旅游攻略"，总结前5篇笔记的内容
                ```

                ### 注意事项

                - 首次使用请确保已安装ADB Keyboard并在设备设置中启用
                - 执行任务前请确保设备已解锁
                - 某些敏感操作(如支付)可能需要人工确认
                - 建议在WiFi环境下使用以获得更好的响应速度

                ### 常见问题

                **Q: 无法检测到设备?**
                A: 确保已启用USB调试，并在设备上授权计算机的调试请求

                **Q: 任务执行失败?**
                A: 检查网络连接，确认模型API服务正常运行

                **Q: 输入文本没有反应?**
                A: 确保已安装并启用ADB Keyboard

                ### 技术支持

                - GitHub: [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM)
                - 文档: 查看项目README获取更多信息
                """)

        # ================================================================
        # Event Handlers
        # ================================================================

        # Refresh devices
        refresh_btn.click(
            fn=refresh_devices,
            inputs=[],
            outputs=[device_dropdown]
        )

        # System check
        check_btn.click(
            fn=run_system_check,
            inputs=[base_url, model_name, api_key, device_dropdown],
            outputs=[check_output]
        )

        # Execute task
        submit_btn.click(
            fn=execute_task,
            inputs=[task_input, base_url, model_name, api_key, max_steps,
                   device_dropdown, lang, session_state],
            outputs=[output_display, screenshot_display, session_state]
        )

        # New conversation
        new_chat_btn.click(
            fn=new_conversation,
            inputs=[base_url, model_name, api_key, max_steps, device_dropdown, lang],
            outputs=[output_display, screenshot_display, session_state]
        )

        # Stop task
        stop_btn.click(
            fn=stop_current_task,
            inputs=[session_state],
            outputs=[output_display]
        )

        # List devices
        def list_devices_info():
            try:
                devices = list_devices()
                if not devices:
                    return "## 设备列表\n\n❌ 没有检测到连接的设备"

                lines = ["## 设备列表\n"]
                for i, device in enumerate(devices, 1):
                    lines.append(f"### {i}. {device.device_id}")
                    lines.append(f"- **型号**: {device.model or 'Unknown'}")
                    lines.append(f"- **状态**: {device.status}")
                    lines.append(f"- **连接类型**: {device.connection_type.value}")
                    lines.append("")

                return "\n".join(lines)
            except Exception as e:
                return f"## 设备列表\n\n❌ 错误: {str(e)}"

        list_devices_btn.click(
            fn=list_devices_info,
            inputs=[],
            outputs=[device_output]
        )

        # Connect device
        def connect_device(address):
            if not address:
                return "❌ 请输入设备地址"

            try:
                from phone_agent.adb import ADBConnection
                conn = ADBConnection()
                success, message = conn.connect(address)
                if success:
                    return f"✅ {message}"
                else:
                    return f"❌ {message}"
            except Exception as e:
                return f"❌ 连接失败: {str(e)}"

        connect_btn.click(
            fn=connect_device,
            inputs=[connect_ip],
            outputs=[device_output]
        )

        # Auto-refresh screenshot
        # Toggle timer active state based on checkbox
        auto_refresh_checkbox.change(
            fn=lambda checked: gr.Timer(active=checked),
            inputs=[auto_refresh_checkbox],
            outputs=[screenshot_timer]
        )

        # Update screenshot on timer tick
        screenshot_timer.tick(
            fn=get_current_screenshot,
            inputs=[device_dropdown],
            outputs=[screenshot_display]
        )

    return app


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Launch the Gradio app."""
    app = create_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=False,
        quiet=False,
    )


if __name__ == "__main__":
    main()
