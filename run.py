from environs import env
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig
from phone_agent.agent import AgentConfig
from phone_agent.adb import get_screenshot
from imgocr import ImgOcr
import base64


def 进入搜索结果界面(agent: PhoneAgent):
    agent.run(
        "搜索“评论区找对象”，点漏斗图标把搜索条件设置为7日内、未看过。",
        "进入搜索结果界面",
    )


def 进入评论区界面(agent: PhoneAgent):
    agent.run("点进搜索结果里的第一个作品，点气泡图标打开评论区。", "进入评论区界面")


def 关注要男朋友的(agent: PhoneAgent) -> bool:
    return (
        agent.run(
            "评论区找到第一个发“我要这个——男朋友”的绿色表情包（而不是“女朋友”的红色表情包）的人，点她的头像（头像在昵称的左侧）进入她的主页点关注（如果是已经关注过的人或者朋友也忽略，显示“相互关注”也说明已经关注过了）。若已到当日关注上限则仅输出“蒟蒻”，其他什么都不要输出，严格按照这个格式来。警告：滑动的距离尽量小一点，起点y轴比终点y轴大288左右。"
        )
        == "蒟蒻"
    )


def 翻评论区(agent: PhoneAgent):
    agent.run(
        "按返回键回到评论区，向下滚动仅一次。警告：滑动的距离尽量小一点，起点y轴比终点y轴大288左右。",
        "翻评论区",
    )


m = ImgOcr(is_efficiency_mode=True)


def 判断评论区有没有到底(agent: PhoneAgent) -> bool:
    result = m.ocr(
        base64.b64decode(get_screenshot(agent.agent_config.device_id).base64_data)
    )
    for i in result:
        text = i["text"]
        if (
            "快来发布首条评论吧" in text
            or "部分评论被折叠" in text
            or "没有更多评论" in text
        ):
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
    agent_config = AgentConfig(
        max_steps=12
    )

    # 创建 Agent
    agent = PhoneAgent(model_config, agent_config)

    # 执行任务
    agent.action_handler._handle_launch(dict(app="快手"), 0, 0)
    用户获取(agent)
    agent.action_handler._handle_back(dict(), 0, 0)
    agent.action_handler._handle_back(dict(), 0, 0)


if __name__ == "__main__":
    run()
