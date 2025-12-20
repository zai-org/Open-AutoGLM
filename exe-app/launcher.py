# -*- coding: utf-8 -*-
"""
AutoGLM Windows Application Launcher
双击启动后端服务并自动打开浏览器
用户无需任何配置，API Key 在软件内设置
"""

import io
import os
import sys
import time
import threading
import webbrowser
import logging
from pathlib import Path


class SafeWriter:
    """
    Safe writer that handles I/O errors gracefully.
    Always catches exceptions and never crashes.
    """

    def __init__(self, original_stream=None, log_file=None):
        self._original = original_stream
        self._log_file = log_file
        self._use_console = original_stream is not None

    def write(self, s):
        if not s:
            return
        # Try original stream first
        if self._use_console and self._original:
            try:
                self._original.write(s)
                self._original.flush()
                return
            except:
                self._use_console = False

        # Fall back to log file
        if self._log_file:
            try:
                with open(self._log_file, "a", encoding="utf-8") as f:
                    f.write(s)
            except:
                pass

    def flush(self):
        if self._use_console and self._original:
            try:
                self._original.flush()
            except:
                pass

    def isatty(self):
        return False

    # Add encoding attribute for compatibility
    @property
    def encoding(self):
        return "utf-8"

    # Add buffer property for compatibility (returns self as we handle binary data the same way)
    @property
    def buffer(self):
        return self


def get_app_dir():
    """获取应用程序目录（支持 PyInstaller 打包后的路径）"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


def setup_safe_io():
    """
    Set up safe I/O that won't crash on Windows console issues.
    This must be called before any print statements.
    """
    if sys.platform != "win32":
        return

    app_dir = get_app_dir()
    log_file = app_dir / "autoglm.log"

    # Clear old log file
    try:
        if log_file.exists():
            log_file.unlink()
    except:
        pass

    # Store original streams (might be None or invalid)
    orig_stdout = None
    orig_stderr = None

    # Test if stdout is usable
    try:
        if sys.__stdout__ is not None:
            sys.__stdout__.write("")
            sys.__stdout__.flush()
            orig_stdout = sys.__stdout__
    except:
        pass

    try:
        if sys.__stderr__ is not None:
            sys.__stderr__.write("")
            sys.__stderr__.flush()
            orig_stderr = sys.__stderr__
    except:
        pass

    # Always wrap with SafeWriter
    sys.stdout = SafeWriter(orig_stdout, log_file)
    sys.stderr = SafeWriter(orig_stderr, log_file)

    # Set environment variables
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUNBUFFERED"] = "1"

    # Disable werkzeug logging to avoid console issues
    logging.getLogger("werkzeug").disabled = True


# Apply safe I/O immediately at module load time
setup_safe_io()


def setup_environment():
    """设置运行环境"""
    app_dir = get_app_dir()

    # 切换到应用目录
    os.chdir(app_dir)

    # 添加应用目录到 Python 路径
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

    # 设置数据目录环境变量（用于存储 config.json 等）
    os.environ["AUTOGLM_DATA_DIR"] = str(app_dir)

    return app_dir


def open_browser_delayed(url, delay=1.5):
    """延迟打开浏览器"""

    def _open():
        time.sleep(delay)
        try:
            print(f"🌐 正在打开浏览器: {url}")
            webbrowser.open(url)
        except:
            pass

    thread = threading.Thread(target=_open, daemon=True)
    thread.start()


def main():
    """主入口"""
    print("=" * 60)
    print("🚀 AutoGLM - 智能手机控制平台")
    print("=" * 60)

    # 设置环境
    app_dir = setup_environment()
    print(f"📁 应用目录: {app_dir}")

    # 延迟打开浏览器
    url = "http://localhost:5000"
    open_browser_delayed(url)

    print(f"\n🌐 Web界面: {url}")
    print("💡 提示: 首次使用请在「设置」中配置 API Key")
    print("⌨️  按 Ctrl+C 停止服务\n")
    print("=" * 60)

    # 启动 Flask 服务器
    try:
        # 导入并运行 web_server
        from web_server import app, process_queue, load_queue, task_queue
        import threading

        # 启动队列处理线程
        queue_thread = threading.Thread(target=process_queue, daemon=True)
        queue_thread.start()

        # 加载现有队列
        loaded_queue = load_queue()
        task_queue.extend(loaded_queue)

        # 使用 werkzeug 直接运行服务器，绕过 Flask CLI 的 click 模块
        from werkzeug.serving import make_server

        server = make_server("0.0.0.0", 5000, app, threaded=True)
        print("✅ 服务器已启动，正在监听...")
        server.serve_forever()

    except KeyboardInterrupt:
        print("\n\n👋 正在退出...")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        try:
            import traceback

            traceback.print_exc()
        except:
            pass
        try:
            # 尝试等待用户输入
            input("按回车键退出...")
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
