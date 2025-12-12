from environs import env
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig

# Read .env into os.environ
env.read_env()

# Configure model
model_config = ModelConfig(
    base_url=env("BASE_URL"),
    api_key=env("API_KEY")
    model_name=env("MODEL_NAME"),
)

# 创建 Agent
agent = PhoneAgent(model_config=model_config)

# 执行任务
while(True):
    try:
        print("正在寻找作品")
        agent.run("打开快手搜索找对象，点漏斗图标把筛选条件设置为7日内、未看过。若成功完成任务，仅输出“成功”这两个字。")
    except:
        print("寻找作品失败")
        continue
