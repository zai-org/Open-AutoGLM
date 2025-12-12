# -*- coding: utf-8 -*-
"""
AutoGLM Web Control Platform - Production Ready
完整的产品级手机控制平台，支持任务队列、历史搜索、高频推荐等
"""

import io
import sys
import json
import threading
import re
import time
from datetime import datetime
from pathlib import Path
from collections import Counter

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, render_template, request, jsonify
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig

app = Flask(__name__)

# 配置
CONFIG = {
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "model_name": "autoglm-phone",
    "api_key": "change your api key"
}

# 文件路径
HISTORY_FILE = Path("task_history.json")
QUEUE_FILE = Path("task_queue.json")
STATS_FILE = Path("task_stats.json")

# 全局变量
current_task = {
    "running": False,
    "task": "",
    "result": "",
    "status": "idle",
    "steps": [],
    "current_step": 0,
    "can_stop": False,
    "task_id": None,
    "logs": []  # 原始日志
}

task_queue = []
task_thread = None
stop_flag = False


class CustomPhoneAgent(PhoneAgent):
    """自定义Agent，捕获详细执行信息"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steps_callback = None
        self.should_stop = False

    def set_steps_callback(self, callback):
        self.steps_callback = callback

    def set_stop_flag(self, flag):
        self.should_stop = flag

    def run(self, task):
        if self.steps_callback:
            self.steps_callback({
                "type": "start",
                "task": task,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })

        original_stdout = sys.stdout
        captured_output = io.StringIO()

        try:
            sys.stdout = captured_output
            result = super().run(task)
            sys.stdout = original_stdout

            output = captured_output.getvalue()

            # 保存原始日志
            if self.steps_callback:
                self.steps_callback({
                    "type": "raw_log",
                    "content": output,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })

            self._parse_and_send_steps(output)

            if self.steps_callback:
                self.steps_callback({
                    "type": "complete",
                    "result": result,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })

            return result

        except Exception as e:
            sys.stdout = original_stdout
            if self.steps_callback:
                self.steps_callback({
                    "type": "error",
                    "error": str(e),
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
            raise

    def _parse_and_send_steps(self, output):
        if not self.steps_callback:
            return

        steps = output.split("=" * 50)

        for step_text in steps:
            # 检查停止标志
            if self.should_stop:
                if self.steps_callback:
                    self.steps_callback({
                        "type": "error",
                        "error": "任务已被用户停止",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                raise Exception("任务已被用户停止")

            step_text = step_text.strip()
            if not step_text:
                continue

            think_match = re.search(r'💭 思考过程:.*?-{50}(.*?)-{50}', step_text, re.DOTALL)
            if think_match:
                thinking = think_match.group(1).strip()
                self.steps_callback({
                    "type": "thinking",
                    "content": thinking,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })

            action_match = re.search(r'🎯 执行动作:(.*?)(?=={50}|$)', step_text, re.DOTALL)
            if action_match:
                action = action_match.group(1).strip()
                try:
                    action_clean = re.sub(r'^```json\n|```$', '', action, flags=re.MULTILINE).strip()
                    action_json = json.loads(action_clean)
                    self.steps_callback({
                        "type": "action",
                        "content": action_json,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                except:
                    self.steps_callback({
                        "type": "action",
                        "content": action,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })

            if "✅ 任务完成:" in step_text:
                complete_match = re.search(r'✅ 任务完成:(.*?)(?=={50}|$)', step_text, re.DOTALL)
                if complete_match:
                    message = complete_match.group(1).strip()
                    self.steps_callback({
                        "type": "success",
                        "message": message,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })


# ========== 文件操作 ==========

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_history(task, result, status, steps):
    history = load_history()
    history.insert(0, {
        "id": str(int(time.time() * 1000)),
        "task": task,
        "result": result,
        "status": status,
        "steps": steps,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    history = history[:100]

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    # 更新统计
    update_stats(task, status)


def load_queue():
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_queue(queue):
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def load_stats():
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"task_count": {}, "total_executions": 0}
    return {"task_count": {}, "total_executions": 0}


def save_stats(stats):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def update_stats(task, status):
    stats = load_stats()
    stats["total_executions"] = stats.get("total_executions", 0) + 1

    if "task_count" not in stats:
        stats["task_count"] = {}

    stats["task_count"][task] = stats["task_count"].get(task, 0) + 1
    save_stats(stats)


def get_popular_tasks(limit=10):
    stats = load_stats()
    task_count = stats.get("task_count", {})

    # 排序并返回
    sorted_tasks = sorted(task_count.items(), key=lambda x: x[1], reverse=True)
    return [{"task": task, "count": count} for task, count in sorted_tasks[:limit]]


# ========== 任务执行 ==========

def steps_callback(step_data):
    global current_task
    current_task["steps"].append(step_data)
    current_task["current_step"] = len(current_task["steps"])

    # 处理原始日志
    if step_data.get("type") == "raw_log":
        if "logs" not in current_task:
            current_task["logs"] = []
        current_task["logs"].append({
            "content": step_data["content"],
            "timestamp": step_data["timestamp"]
        })


def execute_task(task, task_id):
    global current_task, stop_flag

    try:
        current_task["running"] = True
        current_task["task"] = task
        current_task["status"] = "running"
        current_task["steps"] = []
        current_task["current_step"] = 0
        current_task["can_stop"] = True
        current_task["task_id"] = task_id
        stop_flag = False

        model_config = ModelConfig(
            base_url=CONFIG["base_url"],
            model_name=CONFIG["model_name"],
            api_key=CONFIG["api_key"]
        )

        agent = CustomPhoneAgent(model_config=model_config)
        agent.set_steps_callback(steps_callback)
        agent.set_stop_flag(stop_flag)

        result = agent.run(task)

        current_task["result"] = result
        current_task["status"] = "success"
        save_history(task, result, "success", current_task["steps"])

    except Exception as e:
        error_msg = f"执行失败: {str(e)}"
        current_task["result"] = error_msg
        current_task["status"] = "error"
        current_task["steps"].append({
            "type": "error",
            "content": error_msg,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        save_history(task, error_msg, "error", current_task["steps"])

    finally:
        current_task["running"] = False
        current_task["can_stop"] = False
        current_task["task_id"] = None


def process_queue():
    """后台线程处理队列"""
    global task_queue, current_task

    while True:
        if not current_task["running"] and len(task_queue) > 0:
            # 取出队列第一个任务
            next_task = task_queue.pop(0)
            save_queue(task_queue)

            # 执行任务
            execute_task(next_task["task"], next_task["id"])

        time.sleep(1)


# ========== API路由 ==========

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/execute', methods=['POST'])
def api_execute():
    """立即执行任务"""
    data = request.json
    task = data.get('task', '').strip()

    if not task:
        return jsonify({"success": False, "message": "任务不能为空"})

    if current_task["running"]:
        return jsonify({"success": False, "message": "当前有任务正在执行，请添加到队列"})

    task_id = str(int(time.time() * 1000))
    thread = threading.Thread(target=execute_task, args=(task, task_id))
    thread.daemon = True
    thread.start()

    return jsonify({"success": True, "message": "任务已开始执行", "task_id": task_id})


@app.route('/api/queue/add', methods=['POST'])
def api_queue_add():
    """添加任务到队列"""
    global task_queue

    data = request.json
    task = data.get('task', '').strip()

    if not task:
        return jsonify({"success": False, "message": "任务不能为空"})

    task_id = str(int(time.time() * 1000))
    task_queue.append({
        "id": task_id,
        "task": task,
        "added_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_queue(task_queue)

    return jsonify({"success": True, "message": "任务已添加到队列", "queue_length": len(task_queue)})


@app.route('/api/queue/list', methods=['GET'])
def api_queue_list():
    """获取队列列表"""
    return jsonify({"success": True, "queue": task_queue})


@app.route('/api/queue/remove', methods=['POST'])
def api_queue_remove():
    """从队列移除任务"""
    global task_queue

    data = request.json
    task_id = data.get('task_id')

    task_queue = [t for t in task_queue if t["id"] != task_id]
    save_queue(task_queue)

    return jsonify({"success": True, "message": "任务已移除"})


@app.route('/api/queue/clear', methods=['POST'])
def api_queue_clear():
    """清空队列"""
    global task_queue
    task_queue = []
    save_queue(task_queue)
    return jsonify({"success": True, "message": "队列已清空"})


@app.route('/api/stop', methods=['POST'])
def api_stop():
    """停止当前任务"""
    global stop_flag, current_task

    if not current_task["running"]:
        return jsonify({"success": False, "message": "当前没有正在执行的任务"})

    stop_flag = True
    return jsonify({"success": True, "message": "停止信号已发送"})


@app.route('/api/status', methods=['GET'])
def api_status():
    """获取当前任务状态"""
    return jsonify({
        "running": current_task["running"],
        "task": current_task["task"],
        "result": current_task["result"],
        "status": current_task["status"],
        "steps": current_task["steps"],
        "current_step": current_task["current_step"],
        "can_stop": current_task["can_stop"],
        "queue_length": len(task_queue)
    })


@app.route('/api/history', methods=['GET'])
def api_history():
    """获取历史记录"""
    search = request.args.get('search', '').strip()
    history = load_history()

    if search:
        history = [h for h in history if search.lower() in h["task"].lower()]

    return jsonify({"success": True, "history": history})


@app.route('/api/history/clear', methods=['POST'])
def api_history_clear():
    """清空历史记录"""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    return jsonify({"success": True, "message": "历史记录已清空"})


@app.route('/api/popular', methods=['GET'])
def api_popular():
    """获取高频任务"""
    popular = get_popular_tasks(20)
    return jsonify({"success": True, "popular": popular})


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """获取统计信息"""
    stats = load_stats()
    return jsonify({
        "success": True,
        "total_executions": stats.get("total_executions", 0),
        "unique_tasks": len(stats.get("task_count", {}))
    })


@app.route('/guide')
def guide():
    """安装指南页面"""
    return render_template('guide.html')


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 AutoGLM - 智能手机控制平台")
    print("=" * 70)
    print(f"🌐 Web界面: http://localhost:5000")
    print(f"📖 安装指南: http://localhost:5000/guide")
    print(f"🔧 模型: {CONFIG['model_name']}")
    print(f"📡 API: {CONFIG['base_url']}")
    print("=" * 70)
    print("\n✨ 产品功能:")
    print("  • 任务队列管理")
    print("  • 实时停止任务")
    print("  • 历史记录搜索")
    print("  • 高频任务推荐")
    print("  • 详细执行日志")
    print("  • 新手安装指南")
    print("\n⌨️  按 Ctrl+C 停止服务\n")

    # 启动队列处理线程
    queue_thread = threading.Thread(target=process_queue)
    queue_thread.daemon = True
    queue_thread.start()

    # 加载现有队列
    task_queue = load_queue()

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
