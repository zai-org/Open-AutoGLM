# AutoGLM Windows 应用

AutoGLM 智能手机控制平台的 Windows 可执行程序版本。

## 快速开始

### 使用便携版

1. **解压文件**  
   将 `AutoGLM-Portable-*.zip` 解压到任意目录

2. **启动应用**  
   双击 `AutoGLM.exe` 运行

3. **配置 API Key**  
   - 浏览器会自动打开 http://localhost:5000
   - 点击右上角「设置」图标
   - 输入你的智谱 API Key（必需）
   - 输入 SiliconFlow API Key（可选，用于聊天功能）
   - 点击保存

4. **开始使用**  
   配置完成后即可开始使用手机控制功能

## 功能特性

- ✅ **零依赖安装** - 无需安装 Python、Node.js 等任何环境
- ✅ **双击即用** - 解压后直接运行
- ✅ **UI 配置** - 在网页界面中配置 API Key，无需编辑文件
- ✅ **数据持久化** - 配置和历史记录自动保存
- ✅ **完全便携** - 可以放在 U 盘中随身携带

## 系统要求

- Windows 10/11 (64-bit)
- 至少 200MB 磁盘空间
- ADB 工具（用于手机控制）

## 常见问题

### 如何获取 API Key？

**智谱 API Key**（必需）:

1. 访问 https://open.bigmodel.cn/
2. 注册并登录
3. 在控制台创建 API Key

**SiliconFlow API Key**（可选）:

1. 访问 https://siliconflow.cn/
2. 注册并登录
3. 创建 API Key

### ADB 工具如何安装？

1. 下载 Android Platform Tools
2. 解压到任意目录
3. 将 adb.exe 所在目录添加到系统 PATH

或者将 adb.exe 放在 AutoGLM.exe 同一目录下。

### 配置保存在哪里？

所有配置和数据保存在 AutoGLM.exe 所在目录：

- `config.json` - API Key 等配置
- `task_history.json` - 任务历史
- `task_queue.json` - 任务队列
- `task_stats.json` - 统计数据

### 如何更新版本？

1. 备份旧版本目录中的 `config.json` 和其他 JSON 文件
2. 解压新版本到新目录
3. 将备份的文件复制到新目录
4. 运行新版本的 AutoGLM.exe

## 技术支持

如遇问题，请检查：

1. 是否已正确配置 API Key
2. ADB 是否正常工作（运行 `adb devices` 测试）
3. 防火墙是否允许应用访问网络
4. 控制台窗口中的错误信息