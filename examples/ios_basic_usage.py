#!/usr/bin/env python3
"""
iOS 设备基础使用示例

演示如何使用 phone_agent.xctest 模块控制 iOS 设备。

前置要求:
1. 安装 libimobiledevice: brew install libimobiledevice
2. 在 iOS 设备上运行 WebDriverAgent
3. 设置端口转发 (如果通过 USB): iproxy 8100 8100
4. 安装 requests: pip install requests
"""

import time

from phone_agent.xctest import (
    XCTestConnection,
    get_screenshot,
    home,
    launch_app,
    list_devices,
    tap,
)
from phone_agent.xctest.input import hide_keyboard, type_text
from phone_agent.xctest.screenshot import save_screenshot


def main():
    print("=" * 50)
    print("iOS 设备自动化示例")
    print("=" * 50)

    # 1. 检查设备连接
    print("\n1. 检查连接的 iOS 设备...")
    devices = list_devices()

    if not devices:
        print("❌ 未找到 iOS 设备!")
        print("请确保:")
        print("  - iOS 设备已通过 USB 连接")
        print("  - 已安装 libimobiledevice")
        print("  - 设备已解锁并信任此电脑")
        return

    for device in devices:
        print(f"✅ 找到设备: {device.device_name}")
        print(f"   UDID: {device.device_id}")
        print(f"   型号: {device.model}")
        print(f"   iOS 版本: {device.ios_version}")
        print(f"   连接类型: {device.connection_type.value}")

    # 2. 检查 WebDriverAgent 状态
    print("\n2. 检查 WebDriverAgent 状态...")
    wda_url = "http://localhost:8100"
    conn = XCTestConnection(wda_url=wda_url)

    if not conn.is_wda_ready():
        print("❌ WebDriverAgent 未运行!")
        print("请确保:")
        print("  - 在 Xcode 中运行了 WebDriverAgentRunner")
        print("  - 如果是 USB 连接,运行了端口转发: iproxy 8100 8100")
        print("  - 如果是 WiFi 连接,修改 wda_url 为设备 IP")
        return

    print(f"✅ WebDriverAgent 正常运行: {wda_url}")

    # 获取 WDA 状态信息
    status = conn.get_wda_status()
    if status:
        print(f"   Session ID: {status.get('sessionId', 'N/A')}")

    # 3. 返回主屏幕
    print("\n3. 返回主屏幕...")
    home(wda_url=wda_url)
    time.sleep(1)

    # 4. 截图
    print("\n4. 截取主屏幕...")
    screenshot = get_screenshot(wda_url=wda_url)
    print(f"✅ 截图成功: {screenshot.width}x{screenshot.height}")

    # 保存截图
    screenshot_path = "ios_home_screen.png"
    if save_screenshot(screenshot, screenshot_path):
        print(f"   已保存到: {screenshot_path}")

    # 5. 启动应用示例 (需要在 apps.py 中配置)
    print("\n5. 尝试启动应用...")
    app_name = "Safari"  # 可以改为其他已配置的应用

    if launch_app(app_name, wda_url=wda_url):
        print(f"✅ 成功启动应用: {app_name}")
        time.sleep(2)

        # 截图应用界面
        screenshot = get_screenshot(wda_url=wda_url)
        app_screenshot_path = f"ios_{app_name.lower()}.png"
        save_screenshot(screenshot, app_screenshot_path)
        print(f"   已保存应用截图: {app_screenshot_path}")
    else:
        print(f"❌ 应用 {app_name} 未配置或未安装")
        print("   请在 phone_agent/config/apps.py 中添加应用的 Bundle ID")

    # 6. 交互示例 (如果启动了 Safari)
    if app_name == "Safari":
        print("\n6. Safari 交互示例...")

        # 点击地址栏 (坐标需根据实际屏幕调整)
        print("   点击地址栏...")
        tap(200, 100, wda_url=wda_url)
        time.sleep(1)

        # 输入 URL
        print("   输入 URL...")
        type_text("https://www.apple.com", wda_url=wda_url)
        time.sleep(1)

        # 隐藏键盘 (按回车或点击其他区域)
        print("   隐藏键盘...")
        hide_keyboard(wda_url=wda_url)

        print("✅ 交互完成")

    # 7. 返回主屏幕
    print("\n7. 返回主屏幕...")
    home(wda_url=wda_url)
    time.sleep(1)

    print("\n" + "=" * 50)
    print("示例执行完成!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n中断执行")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()
