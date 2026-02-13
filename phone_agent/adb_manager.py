import subprocess

class AdbManager:
    def __init__(self, device_id):
        self.device_id = device_id

    def run_command(self, command):
        try:
            result = subprocess.run(['adb', '-s', self.device_id] + command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            if 'SecurityException' in e.stderr:
                return "Permission denied. Please ensure that ADB debugging is enabled and permissions are granted."
            return f"Error: {e.stderr}"

    def check_adb_keyboard(self):
        output = self.run_command(['shell', 'ime', 'list', '-s', 'com.android.adbkeyboard/.AdbIME'])
        if "Permission denied" in output:
            print("Please grant the necessary permissions for ADB.")
        return output