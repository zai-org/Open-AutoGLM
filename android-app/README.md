# AutoGLM Android App

独立运行在手机上的 AutoGLM 控制应用，无需 PC 和 ADB 连接。

## 功能

- ✅ 直接在手机上配置 API Key
- ✅ 使用无障碍服务控制手机
- ✅ 支持截图、点击、滑动、文字输入
- ✅ 实时日志显示
- ✅ Material3 现代 UI

## 系统要求

- Android 11 (API 30) 或更高版本
- 需要启用无障碍服务权限

## 编译方法

### 方法一：一键安装（推荐，Windows）

自动检测设备、编译并安装 Debug 包。

1. 手机连接电脑，开启 **USB 调试**。
2. 双击运行 `android-app/install_app.bat`。

### 方法二：使用 Android Studio

1. 用 Android Studio 打开 `android-app` 目录
2. 等待 Gradle 同步完成
3. 点击 Build > Build Bundle(s) / APK(s) > Build APK(s)
4. APK 生成在 `app/build/outputs/apk/debug/`

### 方法三：使用命令行

```bash
cd android-app

# Windows
.\gradlew.bat assembleDebug

# macOS/Linux
./gradlew assembleDebug
```

## 使用方法

1. 安装 APK 到手机
2. 打开应用，点击设置图标
3. 配置 API Base URL、API Key 和模型名称
4. 返回主页，在系统设置中启用 AutoGLM 无障碍服务
5. 输入任务描述，点击"开始任务"

## API 配置

**智谱 BigModel:**
- Base URL: `https://open.bigmodel.cn/api/paas/v4`
- Model: `autoglm-phone`
- API Key: 在智谱平台申请

**ModelScope:**
- Base URL: `https://api-inference.modelscope.cn/v1`
- Model: `ZhipuAI/AutoGLM-Phone-9B`
- API Key: 在 ModelScope 平台申请

## 注意事项

⚠️ 部分国产手机对无障碍服务有额外限制，可能需要在系统设置中额外开启权限。
