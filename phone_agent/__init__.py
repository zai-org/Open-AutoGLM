from .adb_manager import ADBManager

# Other imports...

class PhoneAgent:
    def __init__(self, device):
        self.adb_manager = ADBManager(device)

    def setup(self):
        if not self.adb_manager.check_adb_keyboard():
            print("Consider using another input method or check ADB permissions.")