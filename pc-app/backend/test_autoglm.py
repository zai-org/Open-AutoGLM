# -*- coding: utf-8 -*-
import sys
import io

# 强制设置stdout为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig

# 配置模型
model_config = ModelConfig(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model_name="autoglm-phone",
    api_key="ce41396d8f44415eb3bff547e12d21f3.qNXajSi820CAHv0J"
)

# 创建 Agent
agent = PhoneAgent(model_config=model_config)

# 执行任务
print("正在使用汽水音乐搜索《平凡之路》...")
try:
    result = agent.run("打开汽水音乐搜索平凡之路")
    print("任务完成！")
    print(f"执行结果: {result}")
except Exception as e:
    print(f"任务失败: {e}")
    import traceback
    traceback.print_exc()
