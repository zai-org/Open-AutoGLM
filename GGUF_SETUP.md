# AutoGLM GGUF 使用指南

本项目已支持 GGUF 格式，以下是设置方法。

## 前置要求

- Python 3.10+
- CUDA 12.4+ (GPU 推理)
- ADB (手机控制)

## 快速设置

### 1. 克隆仓库
```bash
git clone https://github.com/your-org/Open-AutoGLM.git
cd Open-AutoGLM
pip install -r requirements.txt
```

### 2. 修改 llama.cpp（重要）⚠️

由于 llama.cpp 是子模块，需要手动应用以下修改以支持 GLM-4V：

#### 修改 1: `llama.cpp/tools/mtmd/clip.cpp`

在 `build_internvl` 函数中添加维度降维：

```cpp
// 在处理 merger 输出后，添加降维
// 约在第 1290 行附近
if (cur->ne[0] == 6144) {
    // GLM-4V 输出 6144 维，需要降维到 4096
    cur = ggml_view_2d(ctx, cur, 4096, cur->ne[1], 
                       cur->nb[1], 0);
}
```

#### 修改 2: `llama.cpp/convert_hf_to_gguf.py`

更新 merger 层映射（约在第 10366 行）：

```python
# GLM-4V merger 结构映射
if "merger" in name:
    if "layernorm" in name or "ln" in name:
        return f"mm.{bid}.mlp.0"  # norm
    elif "up_proj" in name:
        return f"mm.{bid}.mlp.1"  # up
    elif "down_proj" in name:
        return f"mm.{bid}.mlp.3"  # down
```

### 3. 重新编译 llama-server

```powershell
cd llama.cpp
mkdir build
cd build
cmake .. -DGGML_CUDA=ON
cmake --build . --config Release
cd ../..
```

### 4. 转换模型

```bash
# 下载原始模型
# HuggingFace: THUDM/AutoGLM-Phone-9B

# 转换语言模型
python llama.cpp/convert_hf_to_gguf.py models/AutoGLM-Phone-9B \
    --outtype q4_k_s \
    --outfile models/AutoGLM-Phone-9B-Q4_K_S.gguf

# 转换视觉编码器
python llama.cpp/convert_hf_to_gguf.py models/AutoGLM-Phone-9B \
    --mmproj \
    --outfile models/AutoGLM-Phone-9B-mmproj.gguf
```

### 5. 启动服务

```powershell
cd llama.cpp/build/bin/Release

.\llama-server.exe `
  --model ../../../../models/AutoGLM-Phone-9B-Q4_K_S.gguf `
  --mmproj ../../../../models/AutoGLM-Phone-9B-mmproj.gguf `
  --port 8080 `
  --ctx-size 16384 `
  --n-gpu-layers 99
```

### 6. 使用

```bash
# 连接手机
adb devices

# 执行任务
python main.py --base-url http://localhost:8080/v1 "打开微信"
```

## 关键修改说明

### clip.cpp 修改原因
GLM-4V 的视觉编码器输出 6144 维向量，而 llama.cpp 的标准 InternVL 实现期望 4096 维。需要添加降维操作。

### convert_hf_to_gguf.py 修改原因
GLM-4V 的 merger 层结构与标准 InternVL 略有不同，需要正确映射层名称。

## 性能指标

- **模型大小**: 5.35GB (Q4_K_S)
- **mmproj 大小**: 1.55GB
- **上下文**: 16,384 tokens
- **推理速度**: ~37 tokens/sec (RTX 4090)

## 已改进功能

### 模型客户端 (phone_agent/model/client.py)
- ✅ 使用 requests 替代 OpenAI 客户端
- ✅ 智能响应解析（支持多种格式）
- ✅ 改进的 Launch 操作（应用包名映射）

## 故障排除

### Q: llama-server 启动失败
```bash
# 确认 CUDA 可用
nvidia-smi

# 重新编译
cd llama.cpp
rm -rf build
mkdir build && cd build
cmake .. -DGGML_CUDA=ON
cmake --build . --config Release
```

### Q: 模型转换失败
确保原始模型下载完整，包含所有 safetensors 文件和 config.json。

### Q: 上下文溢出
增加上下文大小：`--ctx-size 32768`

## 已知限制

- llama.cpp 修改需手动应用（未包含在此提交中）
- 复杂 UI 导航准确性待提高
- 部分应用需手动添加包名映射

## 技术支持

- GitHub Issues: [提交问题](https://github.com/your-org/Open-AutoGLM/issues)
- 原始 AutoGLM: [THUDM/AutoGLM](https://github.com/THUDM/AutoGLM)
- llama.cpp: [ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)

## 贡献

欢迎提交 PR 改进 GGUF 支持！

## 许可证

MIT License
