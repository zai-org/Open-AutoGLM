import subprocess

def check_adb_keyboard():
    try:
        output = subprocess.check_output(["adb", "shell", "ime", "list", "-s", "com.android.adbkeyboard/.AdbIME"])
        return output.decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Error checking ADB keyboard: {e}")
        # Provide guidance for OPPO users
        print("If you're using an OPPO device, please check ADB permissions.")
        return None