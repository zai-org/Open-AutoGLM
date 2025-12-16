from environs import env
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig
from phone_agent.agent import AgentConfig
from phone_agent.adb import get_screenshot
from imgocr import ImgOcr
import base64


def 进入搜索结果界面(agent: PhoneAgent):
    agent.run(
        "点放大镜图标搜索“评论区找对象”，点漏斗图标把搜索条件设置为近1日。",
        "进入搜索结果界面",
    )


def 进入评论区界面(agent: PhoneAgent):
    agent.run("点进搜索结果里的第一个作品，点气泡图标打开评论区。", "进入评论区界面")


def 关注要男朋友的(agent: PhoneAgent) -> bool:
    screenshot = get_screenshot(agent.agent_config.device_id)
    for i in m.ocr(base64.b64decode(screenshot.base64_data)):
        if "男朋友" in i["text"]:
            x, y = i["box"][3]
            agent.action_handler._handle_tap(
                dict(element=[x - 100, y - 20]),
                screenshot.width,
                screenshot.height,
                False,
            )
            screenshot = get_screenshot(agent.agent_config.device_id)
            for j in m.ocr(base64.b64decode(screenshot.base64_data)):
                if j["text"] == "十关注" or j["text"] == "+关注":
                    agent.action_handler._handle_tap(
                        dict(element=j["box"][0]),
                        screenshot.width,
                        screenshot.height,
                        False,
                    )
                    for k in m.ocr(
                        base64.b64decode(
                            get_screenshot(agent.agent_config.device_id).base64_data
                        )
                    ):
                        if k["text"].startswith("关注失败"):
                            return True
                    break
            agent.action_handler._handle_back(dict(), 0, 0)
    return False


def 翻评论区(agent: PhoneAgent):
    agent.run(
        "仅在评论区向下滚动仅一次，然后什么都别做。警告：滑动的距离尽量小一点（从屏幕偏下较大的y值start，到屏幕中间较小的y值end，y轴之间相差300）。",
        "翻评论区",
    )


m = ImgOcr(is_efficiency_mode=True)


def 判断评论区有没有到底(agent: PhoneAgent) -> bool:
    result = m.ocr(
        base64.b64decode(get_screenshot(agent.agent_config.device_id).base64_data)
    )
    for i in result:
        text = i["text"]
        if text == "0条评论" or text == "评论0":
            agent.run("按一次返回键。", "按一次返回键")
            return True
        if "部分评论被折叠" in text or "没有更多评论" in text:
            return True
    return False


def 刷新搜索结果(agent: PhoneAgent) -> bool:
    agent.run(
        "按两次返回键回到到搜索结果界面，并下拉刷新搜索结果（从屏幕中间较小的y值start，到屏幕底部较大的y值end）。",
        "刷新搜索结果",
    )


def 用户获取(agent: PhoneAgent):
    进入搜索结果界面(agent)
    while True:
        进入评论区界面(agent)
        while True:
            if 关注要男朋友的(agent):
                agent.action_handler._handle_back(dict(), 0, 0)
                agent.action_handler._handle_back(dict(), 0, 0)
                agent.action_handler._handle_back(dict(), 0, 0)
                agent.action_handler._handle_back(dict(), 0, 0)
                agent.action_handler._handle_back(dict(), 0, 0)
                agent.action_handler._handle_back(dict(), 0, 0)
                return
            翻评论区(agent)
            if 判断评论区有没有到底(agent):
                break
        刷新搜索结果(agent)


def run():
    # Read .env into os.environ
    env.read_env()

    # Configure model
    model_config = ModelConfig(
        base_url=env("BASE_URL"),
        api_key=env("API_KEY"),
        model_name=env("MODEL_NAME"),
    )

    # Configure agent
    agent_config = AgentConfig(max_steps=10)

    # 创建 Agent
    agent = PhoneAgent(model_config, agent_config)

    # 执行任务
    关注要男朋友的(agent)
    # agent.action_handler._handle_launch(dict(app="快手"), 0, 0)
    # while True:
    #     try:
    #         用户获取(agent)
    #     except:
    #         while True:
    #             try:
    #                 agent.run("回到快手首页")
    #             except:
    #                 continue
    #             break
    #         continue
    #     break
    # agent.action_handler._handle_back(dict(), 0, 0)
    # agent.action_handler._handle_back(dict(), 0, 0)

if __name__ == "__main__":
    run()
