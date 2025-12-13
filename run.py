from environs import env
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig
from phone_agent.agent import AgentConfig


# 翻找对象评论区，关注要男朋友的
def acquisition(agent: PhoneAgent):
    while True:
        try:
            print("正在进入搜索结果界面……")
            result = agent.run(
                "打开快手搜索“评论区找对象”，点漏斗图标把搜索条件设置为7日内、未看过。若成功完成任务，仅输出“成功”，其他什么都不要输出，严格按照这个格式来。"
            )
            if result != "成功":
                raise Exception(result)
        except Exception as e:
            print("进入搜索结果界面失败：", e)
            continue
        while True:
            try:
                print("正在进入作品界面……")
                result = agent.run(
                    "点进搜索结果中的第一个作品。若成功完成任务，仅输出“成功”，其他什么都不要输出，严格按照这个格式来。"
                )
                if result != "成功":
                    raise Exception(result)
            except Exception as e:
                print("进入作品界面失败：", e)
                continue
            try:
                print("正在判断评论条数……")
                result = agent.run(
                    "判断评论数量有没有达到一百（显示抢首评说明一个评论都没有），若达到则仅输出“y”，若没有达到则仅输出“n”，其他什么都不要输出，严格按照这个格式来。"
                )
                if result == "y":
                    print("正在进入评论区界面……")
                    try:
                        result = agent.run(
                            "点视频右侧气泡图标打开评论区。若成功完成任务，仅输出“成功”，其他什么都不要输出，严格按照这个格式来。"
                        )
                        if result != "成功":
                            raise Exception(result)
                    except Exception as e:
                        print("进入评论区界面失败")
                    while True:
                        print("正在点关注……")
                        try:
                            result = agent.run(
                                "下翻评论区找到第一个发“我要这个——男朋友”的绿色表情包（而不是“女朋友”的红色表情包）的人，点她的头像（头像在昵称的左侧）进入她的主页点关注（如果是已经关注过的人或者朋友也忽略，显示“相互关注”也说明已经关注过了）。若已到当日关注上限则仅输出“y”，没达到输出“n”，其他什么都不要输出，严格按照这个格式来。警告：滑动的距离尽量小一点，起点y轴与终点y轴的差距不要超过300。"
                            )
                            if result == "y":
                                print("哈哈哈，已达当日关注上限，用户获取任务完成")
                                return
                            elif result == "n":
                                pass
                            else:
                                raise Exception(result)
                        except Exception as e:
                            print("点关注失败：", e)
                        print("正在翻评论区……")
                        try:
                            result = agent.run(
                                "确保你在评论区界面，如果不在则尝试返回。在评论区的情况下向下滚动仅一次。警告：滑动的距离尽量小一点，起点y轴与终点y轴的差距不要超过300。"
                            )
                            if result != "成功":
                                raise Exception(result)
                        except Exception as e:
                            print("翻评论区失败：", e)
                        print("正在判断到底提示……")
                        try:
                            result = agent.run(
                                "判断：若看到“部分评论被折叠”字样，则仅输出“y”，若没看到则仅输出“n”，其他什么都不要输出，严格按照这个格式来。"
                            )
                            if result == "y":
                                break
                            elif result == "n":
                                pass
                            else:
                                raise Exception(result)
                        except Exception as e:
                            print("判断到底提示失败：", e)
                elif result == "n":
                    pass
                else:
                    raise Exception(result)
                try:
                    print("正在刷新搜索结果界面……")
                    result = agent.run(
                        "返回到上一页的搜索结果界面（而不是作品界面），并下拉刷新搜索结果（从屏幕中间较小的y值start，到屏幕底部较大的y值end）。若成功完成任务，仅输出“成功”，其他什么都不要输出，严格按照这个格式来。"
                    )
                except Exception as e:
                    print("刷新搜索界面失败：", e)
            except Exception as e:
                print("判断评论条数失败：", e)
                continue


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
        max_steps=10,
    )

    # 创建 Agent
    agent = PhoneAgent(model_config=model_config, agent_config=agent_config)

    # 用户获取
    # acquisition(agent)
    while True:
        print("正在点关注……")
        try:
            result = agent.run(
                "下翻评论区找到第一个发“我要这个——男朋友”的绿色表情包（而不是“女朋友”的红色表情包）的人，点她的头像（头像在昵称的左侧）进入她的主页点关注（如果是已经关注过的人或者朋友也忽略，显示“相互关注”也说明已经关注过了）。若已到当日关注上限则仅输出“y”，没达到输出“n”，其他什么都不要输出，严格按照这个格式来。警告：滑动的距离尽量小一点，起点y轴与终点y轴的差距不要超过300。"
            )
            if result == "y":
                print("哈哈哈，已达当日关注上限，用户获取任务完成")
                return
            elif result == "n":
                pass
            else:
                raise Exception(result)
        except Exception as e:
            print("点关注失败：", e)
        print("正在翻评论区……")
        try:
            result = agent.run(
                "确保你在评论区界面，如果不在则尝试返回。在评论区的情况下向下滚动仅一次。警告：滑动的距离尽量小一点，起点y轴与终点y轴的差距不要超过300。"
            )
            if result != "成功":
                raise Exception(result)
        except Exception as e:
            print("翻评论区失败：", e)
        print("正在判断到底提示……")
        try:
            result = agent.run(
                "判断：若看到“部分评论被折叠”字样，则仅输出“y”，若没看到则仅输出“n”，其他什么都不要输出，严格按照这个格式来。"
            )
            if result == "y":
                break
            elif result == "n":
                pass
            else:
                raise Exception(result)
        except Exception as e:
            print("判断到底提示失败：", e)


if __name__ == "__main__":
    run()
