# 环境与模型部署指南

## 1. 克隆仓库

```bash
git clone https://github.com/zai-org/Open-AutoGLM.git
cd Open-AutoGLM
```

## 2. 安装依赖

```bash
pip install -r requirements.txt 
pip install -e .
```

## 3. 配置与手机的连接

根据你的设备类型选择相应的工具：

### 对于 Android 设备 - 使用 ADB

1. 下载官方 ADB [安装包](https://developer.android.com/tools/releases/platform-tools?hl=zh-cn)，并解压到自定义路径。
2. 配置环境变量。
   - MacOS 配置方法：在 `Terminal` 或者任何命令行工具里

      ```bash
      # 假设解压后的目录为 ~/Downloads/platform-tools。如果不是请自行调整命令。
      export PATH=${PATH}:~/Downloads/platform-tools
      ```

   - Windows 配置方法：可参考 [第三方教程](https://blog.csdn.net/x2584179909/article/details/108319973) 进行配置。
3. 确认 **USB 数据线具有数据传输功能**, 而不是仅有充电功能。
4. 确保已安装 ADB 并使用 **USB 数据线** 连接设备。
5. 检查已连接的设备。

    ```bash
    # 检查已连接的设备
    adb devices

    # 输出结果应显示你的设备，如：
    # List of devices attached
    # emulator-5554   device
    ```

### 对于鸿蒙设备 (HarmonyOS NEXT 版本以上) - 使用 HDC

1. 下载 HDC 工具：
   - 从 [HarmonyOS SDK](https://developer.huawei.com/consumer/cn/download/) 下载
2. 配置环境变量
   - MacOS/Linux 配置方法：

     ```bash
     # 假设解压后的目录为 ~/Downloads/harmonyos-sdk/toolchains。请根据实际路径调整。
     export PATH=${PATH}:~/Downloads/harmonyos-sdk/toolchains
     ```

   - Windows 配置方法：将 HDC 工具所在目录添加到系统 PATH 环境变量
3. 确认 **USB 数据线具有数据传输功能**, 而不是仅有充电功能
4. 确保已安装 HDC 并使用 **USB 数据线** 连接设备
5. 检查已连接的设备。

    ```bash
    # 检查已连接的设备
    hdc list targets

    # 输出结果应显示你的设备，如：
    # 7001005458323933328a01bce01c2500
    ```

### 对于 iOS 设备（WebDriverAgent）

请参考 [iOS 环境配置指南](ios_setup.md) 进行配置。

## 4. 启动模型服务

你可以选择自行部署模型服务，或使用第三方模型服务商。

### 选项 A: 使用第三方模型服务

如果你不想自行部署模型，可以使用以下已部署我们模型的第三方服务：

1. 智谱 BigModel
   - [智谱 BigModel 文档](https://docs.bigmodel.cn/cn/api/introduction)
   - 参数说明：
     - `--base-url`: `https://open.bigmodel.cn/api/paas/v4`
     - `--model`: `autoglm-phone`
     - `--apikey`: 在智谱平台申请你的 API Key
   - 使用示例：

     ```bash
     python main.py --base-url https://open.bigmodel.cn/api/paas/v4 --model "autoglm-phone" --apikey "your-bigmodel-api-key" "打开美团搜索附近的火锅店"
     ```

2. ModelScope(魔搭社区)
   - [ModelScope 文档](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B)
   - 参数说明：
     - `--base-url`: `https://api-inference.modelscope.cn/v1`
     - `--model`: `ZhipuAI/AutoGLM-Phone-9B`
     - `--apikey`: 在 ModelScope 平台申请你的 API Key
   - 使用示例：

     ```bash
     python main.py --base-url https://api-inference.modelscope.cn/v1 --model "ZhipuAI/AutoGLM-Phone-9B" --apikey "your-modelscope-api-key" "打开美团搜索附近的火锅店"
     ```

### 选项 B: 自行部署模型

如果你希望在本地或自己的服务器上部署模型，可以选择 vLLM 或 SGLang 两种主流推理框架。

注意：无论选择哪种推理引擎，**安装或升级 transformers** 至 `5.0.0rc0` 或更高 (`pip install -U transformers --pre`)。

#### vLLM 部署流程

1. **安装 vLLM 和 transformers**
   - 直接用 pip 安装（如本地 GPU 环境）：

     ```bash
     pip install "vllm>=0.12.0"
     pip install -U transformers --pre
     ```

   - 或使用官方 Docker 镜像：

     ```bash
     docker pull vllm/vllm-openai:v0.12.0
     ```

     进入容器后同样执行：

     ```bash
     pip install -U transformers --pre
     ```

2. 下载模型（如：zai-org/AutoGLM-Phone-9B）
3. 启动 vLLM OpenAI 接口服务，**务必严格按参数设置**：

   ```bash
   python3 -m vllm.entrypoints.openai.api_server \
     --served-model-name autoglm-phone-9b \
     --allowed-local-media-path / \
     --mm-encoder-tp-mode data \
     --mm_processor_cache_type shm \
     --mm_processor_kwargs "{\"max_pixels\":5000000}" \
     --max-model-len 25480 \
     --chat-template-content-format string \
     --limit-mm-per-prompt "{\"image\":10}" \
     --model zai-org/AutoGLM-Phone-9B \
     --port 8000
   ```

#### SGLang 部署流程

1. **安装 SGLang 和 transformers**
   - 通过 pip 安装（需按依赖处理 CUDA/cudnn 环境）：

     ```bash
     pip install "sglang>=0.5.6.post1"
     pip install -U transformers --pre
     ```

   - 或使用官方 Docker 镜像（如无需本地编译）：

     ```bash
     docker pull lmsysorg/sglang:v0.5.6.post1
     ```

     进入容器后，如需可选多模态功能，还需安装 CUDNN：

     ```bash
     pip install nvidia-cudnn-cu12==9.16.0.29
     pip install -U transformers --pre
     ```

2. 下载模型（如：`zai-org/AutoGLM-Phone-9B`）

3. 启动 SGLang OpenAI 格式服务，**务必严格按参数设置**：

   ```bash
   python3 -m sglang.launch_server \
     --model-path zai-org/AutoGLM-Phone-9B \
     --served-model-name autoglm-phone-9b \
     --context-length 25480 \
     --mm-enable-dp-encoder \
     --mm-process-config '{"image":{"max_pixels":5000000}}' \
     --port 8000
   ```

---

- 该模型结构与 `GLM-4.1V-9B-Thinking` 相同，详细部署流程可参考 [GLM-V](https://github.com/zai-org/GLM-V) 仓库。
- 启动成功后，可通过 `http://localhost:8000/v1` 访问模型 OpenAI 接口。如果在远程服务器上运行，请用对应服务器的 IP 地址替换 `localhost`。

## 5. 检查模型部署

模型服务启动后，可以使用检查脚本验证部署是否成功：

```bash
python scripts/check_deployment_cn.py --base-url http://你的IP:你的端口/v1 --model 模型名称
```

脚本将发送测试请求并展示模型的推理结果，你可以根据输出判断模型部署是否正常工作。

基于给定的任务，预期输出如下。**如果思维链长度很短，或者出现了乱码，很可能是模型部署失败**, 请仔细检查文档要求的配置和依赖。

```text
<think>用户想要比较这个洗发水在京东和淘宝上的价格，然后选择最便宜的平台下单。当前在小红书 app 上，显示的是一个关于 LUMMI MOOD 洗发水的帖子。

我需要：
1. 先启动京东 app，搜索这个洗发水
2. 查看京东的价格
3. 再启动淘宝 app，搜索这个洗发水
4. 查看淘宝的价格
5. 比较价格后，选择最便宜的京东或淘宝下单

首先，我需要从当前的小红书界面退出，然后启动京东 app。</think>
<answer>do(action="Launch", app="京东")
```

参数说明：

- `--base-url`: 模型服务地址 (根据实际部署地址修改)
- `--model`: 模型名称
- `--messages-file`: 可选，指定自定义测试消息文件 (默认使用 `scripts/sample_messages.json`)
