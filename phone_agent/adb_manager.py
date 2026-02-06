import subprocess

class ADBManager:
    def __init__(self, device):
        self.device = device
    
    def check_adb_keyboard(self):
        try:
            output = subprocess.check_output(['adb', '-s', self.device, 'shell', 'ime', 'list', '-s', 'com.android.adbkeyboard/.AdbIME'])
            return 'adbkeyboard' in output.decode()
        except subprocess.CalledProcessError as e:
            if 'SecurityException' in str(e):
                print("Permission denied. Please ensure ADB permissions are set correctly.")
                return False
            raise e