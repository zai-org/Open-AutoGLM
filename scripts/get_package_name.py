#!/usr/bin/env python3
"""
工具脚本：查询Android应用的包名
"""

import subprocess
import sys
import re


def list_all_packages(device_id: str | None = None, third_party_only: bool = False) -> list[str]:
    """
    列出所有已安装应用的包名。
    
    Args:
        device_id: 可选的设备ID
        third_party_only: 是否只显示第三方应用
    
    Returns:
        包名列表
    """
    adb_prefix = ["adb"]
    if device_id:
        adb_prefix = ["adb", "-s", device_id]
    
    cmd = adb_prefix + ["shell", "pm", "list", "packages"]
    if third_party_only:
        cmd.append("-3")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return []
    
    packages = []
    for line in result.stdout.strip().split("\n"):
        if line.startswith("package:"):
            package = line.replace("package:", "").strip()
            packages.append(package)
    
    return packages


def get_current_package(device_id: str | None = None) -> str | None:
    """
    获取当前前台应用的包名。
    
    Args:
        device_id: 可选的设备ID
    
    Returns:
        包名，如果无法获取则返回None
    """
    adb_prefix = ["adb"]
    if device_id:
        adb_prefix = ["adb", "-s", device_id]
    
    result = subprocess.run(
        adb_prefix + ["shell", "dumpsys", "window"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return None
    
    output = result.stdout
    # 查找 mCurrentFocus 或 mFocusedApp
    for line in output.split("\n"):
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            # 提取包名，格式通常是 com.package.name/ActivityName
            match = re.search(r'([a-z][a-z0-9_]*\.)+[a-z][a-z0-9_]*', line)
            if match:
                return match.group(0)
    
    return None


def search_packages(keyword: str, device_id: str | None = None) -> list[str]:
    """
    搜索包含关键词的包名。
    
    Args:
        keyword: 搜索关键词
        device_id: 可选的设备ID
    
    Returns:
        匹配的包名列表
    """
    all_packages = list_all_packages(device_id, third_party_only=False)
    keyword_lower = keyword.lower()
    return [pkg for pkg in all_packages if keyword_lower in pkg.lower()]


def get_app_info(package_name: str, device_id: str | None = None) -> dict:
    """
    获取应用的详细信息。
    
    Args:
        package_name: 包名
        device_id: 可选的设备ID
    
    Returns:
        应用信息字典
    """
    adb_prefix = ["adb"]
    if device_id:
        adb_prefix = ["adb", "-s", device_id]
    
    # 获取应用信息
    result = subprocess.run(
        adb_prefix + ["shell", "dumpsys", "package", package_name],
        capture_output=True,
        text=True
    )
    
    info = {
        "package": package_name,
        "installed": False,
        "version": None,
        "label": None,
    }
    
    if result.returncode == 0:
        output = result.stdout
        info["installed"] = True
        
        # 提取版本信息
        version_match = re.search(r'versionName=([^\s]+)', output)
        if version_match:
            info["version"] = version_match.group(1)
        
        # 提取应用标签（需要从另一个命令获取）
        label_result = subprocess.run(
            adb_prefix + ["shell", "pm", "dump", package_name],
            capture_output=True,
            text=True
        )
        if label_result.returncode == 0:
            label_match = re.search(r'label=([^\s]+)', label_result.stdout)
            if label_match:
                info["label"] = label_match.group(1)
    
    return info


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python get_package_name.py list                    # 列出所有第三方应用")
        print("  python get_package_name.py list-all               # 列出所有应用（包括系统应用）")
        print("  python get_package_name.py current                # 显示当前前台应用的包名")
        print("  python get_package_name.py search <关键词>         # 搜索包含关键词的包名")
        print("  python get_package_name.py info <包名>             # 显示应用的详细信息")
        print("  python get_package_name.py device <设备ID> <命令>  # 指定设备ID")
        sys.exit(1)
    
    command = sys.argv[1]
    device_id = None
    
    # 检查是否有设备ID参数
    if command == "device" and len(sys.argv) >= 4:
        device_id = sys.argv[2]
        command = sys.argv[3]
        args = sys.argv[4:]
    else:
        args = sys.argv[2:]
    
    if command == "list":
        print("第三方应用包名列表:")
        print("-" * 60)
        packages = list_all_packages(device_id, third_party_only=True)
        for pkg in sorted(packages):
            print(f"  {pkg}")
        print(f"\n共 {len(packages)} 个应用")
    
    elif command == "list-all":
        print("所有应用包名列表:")
        print("-" * 60)
        packages = list_all_packages(device_id, third_party_only=False)
        for pkg in sorted(packages):
            print(f"  {pkg}")
        print(f"\n共 {len(packages)} 个应用")
    
    elif command == "current":
        package = get_current_package(device_id)
        if package:
            print(f"当前前台应用包名: {package}")
            info = get_app_info(package, device_id)
            if info.get("label"):
                print(f"应用名称: {info['label']}")
        else:
            print("无法获取当前应用的包名")
    
    elif command == "search":
        if not args:
            print("错误: 请提供搜索关键词")
            sys.exit(1)
        keyword = args[0]
        print(f"搜索包含 '{keyword}' 的包名:")
        print("-" * 60)
        packages = search_packages(keyword, device_id)
        if packages:
            for pkg in sorted(packages):
                print(f"  {pkg}")
            print(f"\n找到 {len(packages)} 个匹配的应用")
        else:
            print("未找到匹配的应用")
    
    elif command == "info":
        if not args:
            print("错误: 请提供包名")
            sys.exit(1)
        package = args[0]
        print(f"应用信息: {package}")
        print("-" * 60)
        info = get_app_info(package, device_id)
        if info["installed"]:
            print(f"包名: {info['package']}")
            if info.get("label"):
                print(f"应用名称: {info['label']}")
            if info.get("version"):
                print(f"版本: {info['version']}")
        else:
            print(f"错误: 未找到包名为 '{package}' 的应用")
    
    else:
        print(f"错误: 未知命令 '{command}'")
        sys.exit(1)


if __name__ == "__main__":
    main()

