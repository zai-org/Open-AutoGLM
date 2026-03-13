# 用于演示Open-AutoGLM核心原理的可执行脚本，仅需输入API_KEY、任务描述即可运行
# author：fanbozhou
import time
import json
import ast
import base64
import io
import re
from datetime import datetime
from typing import Any, Dict, List
import adbutils
from openai import OpenAI

# ==========================================
# 1. 全局配置与状态 (还原原版 Config)
# ==========================================
API_KEY = "<输入智谱中申请的API_KEY>"
BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
MODEL_NAME = "autoglm-phone"  # 9b

# 采样与生成参数 (还原原版准确率参数)
GEN_PARAMS = {
    "temperature": 0.0,
    "top_p": 0.85,
    "frequency_penalty": 0.2,
    "max_tokens": 3000
}

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
device = adbutils.adb.device()


# ==========================================
# 2. 核心系统 Prompt (完整 18 条规则还原)
# ==========================================
def get_system_prompt():
    today = datetime.today()
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_str = today.strftime("%Y年%m月%d日") + " " + weekday_names[today.weekday()]

    return f"""今天的日期是: {date_str}
你是一个智能体分析专家，可以根据操作历史和当前状态图执行一系列操作来完成任务。
你必须严格按照要求输出以下格式：
<think>{{think}}</think>
<answer>{{action}}</answer>

操作指令定义：
1. do(action="Launch", app="xxx") : 启动APP。
2. do(action="Tap", element=[x,y]) : 点击坐标。
3. do(action="Type", text="xxx") : 输入文本（仅在焦点在输入框时使用）。
4. do(action="Swipe", start=[x1,y1], end=[x2,y2]) : 滑动。
5. do(action="Back") : 返回。
6. do(action="Home") : 回主页。
7. do(action="Wait", duration="x seconds") : 等待动画。
8. finish(message="xxx") : 任务完成。

执行原则：
1. 优先检查当前屏幕是否已达到目标。
2. 每次操作仅执行一步动作。
3. 如果遇到弹窗阻碍，应先处理弹窗。
4. 在输入文字前，确保已经点击了输入框。
5. 坐标系为相对坐标 [0, 1000]，左上角为 [0,0]，右下角为 [1000,1000]。
6. 尽量避免无效的重复点击。
7. 滑动操作要长，确保页面确实翻动。
8. 无法完成任务时，使用 finish 解释原因。
9. 严禁输出 <think> 和 <answer> 之外的任何字符。
10. 对于敏感操作（如支付、删除），请在 answer 中增加 message 说明。


必须遵循的规则：
1. 在执行任何操作前，先检查当前app是否是目标app，如果不是，先执行 Launch。
2. 如果进入到了无关页面，先执行 Back。如果执行Back后页面没有变化，请点击页面左上角的返回键进行返回，或者右上角的X号关闭。
3. 如果页面未加载出内容，最多连续 Wait 三次，否则执行 Back重新进入。
4. 如果页面显示网络问题，需要重新加载，请点击重新加载。
5. 如果当前页面找不到目标联系人、商品、店铺等信息，可以尝试 Swipe 滑动查找。
6. 遇到价格区间、时间区间等筛选条件，如果没有完全符合的，可以放宽要求。
7. 在做小红书总结类任务时一定要筛选图文笔记。
8. 购物车全选后再点击全选可以把状态设为全不选，在做购物车任务时，如果购物车里已经有商品被选中时，你需要点击全选后再点击取消全选，再去找需要购买或者删除的商品。
9. 在做外卖任务时，如果相应店铺购物车里已经有其他商品你需要先把购物车清空再去购买用户指定的外卖。
10. 在做点外卖任务时，如果用户需要点多个外卖，请尽量在同一店铺进行购买，如果无法找到可以下单，并说明某个商品未找到。
11. 请严格遵循用户意图执行任务，用户的特殊要求可以执行多次搜索，滑动查找。比如（i）用户要求点一杯咖啡，要咸的，你可以直接搜索咸咖啡，或者搜索咖啡后滑动查找咸的咖啡，比如海盐咖啡。（ii）用户要找到XX群，发一条消息，你可以先搜索XX群，找不到结果后，将"群"字去掉，搜索XX重试。（iii）用户要找到宠物友好的餐厅，你可以搜索餐厅，找到筛选，找到设施，选择可带宠物，或者直接搜索可带宠物，必要时可以使用AI搜索。
12. 在选择日期时，如果原滑动方向与预期日期越来越远，请向反方向滑动查找。
13. 执行任务过程中如果有多个可选择的项目栏，请逐个查找每个项目栏，直到完成任务，一定不要在同一项目栏多次查找，从而陷入死循环。
14. 在执行下一步操作前请一定要检查上一步的操作是否生效，如果点击没生效，可能因为app反应较慢，请先稍微等待一下，如果还是不生效请调整一下点击位置重试，如果仍然不生效请跳过这一步继续任务，并在finish message说明点击不生效。
15. 在执行任务中如果遇到滑动不生效的情况，请调整一下起始点位置，增大滑动距离重试，如果还是不生效，有可能是已经滑到底了，请继续向反方向滑动，直到顶部或底部，如果仍然没有符合要求的结果，请跳过这一步继续任务，并在finish message说明但没找到要求的项目。
16. 在做游戏任务时如果在战斗页面如果有自动战斗一定要开启自动战斗，如果多轮历史状态相似要检查自动战斗是否开启。
17. 如果没有合适的搜索结果，可能是因为搜索页面不对，请返回到搜索页面的上一级尝试重新搜索，如果尝试三次返回上一级搜索后仍然没有符合要求的结果，执行 finish(message="原因")。
18. 在结束任务前请一定要仔细检查任务是否完整准确的完成，如果出现错选、漏选、多选的情况，请返回之前的步骤进行纠正。
"""


# ==========================================
# 3. 消息构建与上下文管理 (核心准确率细节)
# ==========================================

def build_screen_info() -> str:
    """还原 MessageBuilder.build_screen_info"""
    app_info = device.app_current()
    w, h = device.window_size()
    data = {
        "current_app": app_info.package,
        "activity": app_info.activity,
        "screen_resolution": f"{w}x{h}"
    }
    return f"** Screen Info **\n{json.dumps(data, ensure_ascii=False, indent=2)}"


def get_screenshot_base64() -> str:
    """获取高清截图"""
    pil_img = device.screenshot()
    # 原版有时会做 resize 优化，这里保持高质量
    buffered = io.BytesIO()
    pil_img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def remove_images_from_context(context: List[Dict]):
    """核心细节：清理上下文中的图片以防止幻觉"""
    for msg in context:
        if isinstance(msg.get("content"), list):
            msg["content"] = [item for item in msg["content"] if item.get("type") == "text"]
    return context


# ==========================================
# 4. 指令解析引擎 (还原 Handler.py 的 AST 解析)
# ==========================================

def parse_action_from_response(response_text: str) -> Dict[str, Any]:
    """
    更强大的解析器：
    1. 优先找 <answer> 标签。
    2. 如果没标签，在全文中搜寻最后一个 do(...) 或 finish(...) 指令。
    3. 如果都找不到，将全文视为 finish 消息。
    """
    try:
        # 1. 提取 <answer> 内容
        pattern_xml = r"<answer>(.*?)</answer>"
        match_xml = re.search(pattern_xml, response_text, re.DOTALL)

        if match_xml:
            clean_text = match_xml.group(1).strip()
        else:
            # 2. 如果没标签，用正则在全文中寻找 do(xxx) 或 finish(xxx)
            # 我们寻找最后出现的一个指令，防止被开头的解释干扰
            action_matches = re.findall(r'(do\(.*?\)|finish\(.*?\))', response_text, re.DOTALL)
            if action_matches:
                clean_text = action_matches[-1].strip()
            else:
                clean_text = response_text.strip()

        # 3. 处理转义
        clean_text = clean_text.replace('\\n', '\n').replace('\\r', '\r')

        # 4. 尝试解析 do
        if "do(" in clean_text:
            # 提取 do(...) 内部的内容
            inner_content = clean_text.split("do(", 1)[1].rsplit(")", 1)[0]
            full_call = f"do({inner_content})"

            tree = ast.parse(full_call, mode="eval")
            action_data = {"_metadata": "do"}
            for kw in tree.body.keywords:
                action_data[kw.arg] = ast.literal_eval(kw.value)
            return action_data

        # 5. 尝试解析 finish
        elif "finish(" in clean_text:
            if "message=" in clean_text:
                msg = clean_text.split("message=")[1].rsplit(")", 1)[0].strip(" \"'")
            else:
                msg = clean_text
            return {"_metadata": "finish", "message": msg}

    except Exception as e:
        print(f"解析细节失败: {e}")

    # 最终兜底，确保永远不返回 None
    return {"_metadata": "finish", "message": response_text[:100]}


# ==========================================
# 5. 设备执行层 (还原 ADB 细节)
# ==========================================

def setup_adb_keyboard():
    """解决中文输入问题 (原版 Handler 隐藏逻辑)"""
    adb_k = "com.android.adbkeyboard/.ADBKeyboard"
    try:
        device.shell(f"ime set {adb_k}")
    except:
        print("提示：未安装 ADBKeyboard，中文输入可能失败")


def perform_adb_action(action: Dict):
    """执行底层动作，带坐标转换"""
    w, h = device.window_size()
    op = action.get("action")

    print(f"➡️ 执行动作: {op}")

    if op == "Tap":
        rel_x, rel_y = action["element"]
        abs_x, abs_y = int(rel_x / 1000 * w), int(rel_y / 1000 * h)
        device.click(abs_x, abs_y)

    elif op == "Type":
        text = action.get("text", "")
        setup_adb_keyboard()
        cmd = f"am broadcast -a ADB_INPUT_TEXT --es msg {text}"
        device.shell(cmd)

    elif op == "Swipe":
        s, e = action["start"], action["end"]
        x1, y1 = int(s[0] / 1000 * w), int(s[1] / 1000 * h)
        x2, y2 = int(e[0] / 1000 * w), int(e[1] / 1000 * h)
        device.swipe(x1, y1, x2, y2, duration=0.5)

    elif op == "Back":
        device.keyevent("BACK")

    elif op == "Home":
        device.keyevent("HOME")

    elif op == "Launch":
        device.app_start(action.get("app"))

    elif op == "Wait":
        time.sleep(2)


# ==========================================
# 6. 主循环引擎 (完全还原 _execute_step 逻辑)
# ==========================================

def run_agent_loop(user_goal: str):
    context = []
    step_count = 0
    max_steps = 33

    print(f"🎯 任务启动: {user_goal}")

    while step_count < max_steps:
        step_count += 1
        is_first = (step_count == 1)
        print(f"\n--- STEP {step_count} ---")

        # 1. 采集当前环境
        screenshot_b64 = get_screenshot_base64()
        screen_info = build_screen_info()

        # 2. 构建消息流 (区分 is_first)
        if is_first:
            # 细节：第一步才注入系统 Prompt 和 任务目标
            context.append({"role": "system", "content": get_system_prompt()})
            user_content = f"{user_goal}\n\n{screen_info}"
        else:
            # 细节：后续步骤只传屏幕变化
            user_content = f"** Screen Info **\n\n{screen_info}"

        context.append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}},
                {"type": "text", "text": user_content}
            ]
        })

        # 3. 获取模型决策 (流式演示)
        try:
            print("💭 正在思考...")
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=context,
                **GEN_PARAMS
            )
            full_resp = response.choices[0].message.content
            print(f"🤖 模型输出:\n{full_resp}")
        except Exception as e:
            print(f"请求失败: {e}")
            break

        # 4. 解析与执行前的“内存管理”
        # 细节：在解析完之后，立刻把 context 里最后一条消息的图片删掉
        # 这样下次循环时，模型只能看到“最新”的图，不会被历史图干扰
        context[-1]["content"] = [item for item in context[-1]["content"] if item["type"] == "text"]

        # 5. 解析指令
        action_dict = parse_action_from_response(full_resp)

        # 6. 记录助手消息
        context.append({"role": "assistant", "content": full_resp})

        # 7. 判断结束
        if action_dict.get("_metadata") == "finish":
            print(f"🎉 任务终点: {action_dict.get('message')}")
            break

        # 8. 执行物理动作
        try:
            perform_adb_action(action_dict)
        except Exception as e:
            print(f"执行出错: {e}")
            # 出错后给模型一个反馈
            context.append({"role": "user", "content": f"执行失败，错误原因: {str(e)}"})

        time.sleep(2)  # 等待页面加载


if __name__ == "__main__":
    task = "<输入你的任务描述>"
    run_agent_loop(task)
