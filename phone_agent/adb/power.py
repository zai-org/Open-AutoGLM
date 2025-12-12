import subprocess
import time


def is_screen_on(device_id: str | None = None) -> bool:
    adb_prefix = _get_adb_prefix(device_id)

    try:
        result = subprocess.run(
            adb_prefix + ["shell", "dumpsys", "power"],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = result.stdout.lower()
        return "display power: state=on" in output
    except:
        return True


def wake_screen_if_needed(device_id: str | None = None) -> bool:
    if not is_screen_on(device_id):
        adb_prefix = _get_adb_prefix(device_id)
        subprocess.run(
            adb_prefix + ["shell", "input", "keyevent", "KEYCODE_WAKEUP"],
            capture_output=True
        )
        time.sleep(0.5)

        if not is_screen_on(device_id):
            return False

    return True


def _get_adb_prefix(device_id: str | None) -> list:
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]
