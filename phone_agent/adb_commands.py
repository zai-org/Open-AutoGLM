import subprocess

def check_adb_permissions():
    try:
        # Attempting to list input methods
        result = subprocess.run(['adb', 'shell', 'ime', 'list', '-s'], capture_output=True, text=True)
        if 'java.lang.SecurityException' in result.stderr:
            raise PermissionError("Permission denied: ADB commands cannot be executed due to device restrictions.")
        return result.stdout
    except Exception as e:
        return str(e)

def execute_adb_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stderr}")
        return result.stdout
    except PermissionError as pe:
        print(pe)
        return None