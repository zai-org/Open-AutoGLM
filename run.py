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
result = agent.run("打开淘宝搜索无线耳机")
print(result)
