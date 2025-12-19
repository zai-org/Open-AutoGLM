"""ADB Keyboard Auto-Installation and Enablement Tool.

This module provides automatic installation, configuration, and enabling of ADB Keyboard,
without requiring users to manually download and install APK.
"""

import subprocess
import urllib.request
from pathlib import Path
from typing import Optional

ADB_KEYBOARD_PACKAGE = "com.android.adbkeyboard/.AdbIME"
ADB_KEYBOARD_APK_URL = "https://github.com/senzhk/ADBKeyBoard/raw/master/ADBKeyboard.apk"

# APK file within the project (highest priority)
PROJECT_APK_PATH = Path(__file__).parent.parent.parent / "resources" / "apks" / "ADBKeyboard.apk"

# APK file in user cache directory (fallback)
USER_CACHE_APK_PATH = Path.home() / ".cache" / "autoglm" / "ADBKeyboard.apk"


class ADBKeyboardInstaller:
    """ADB Keyboard Auto-Installer."""

    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize the installer.

        Args:
            device_id: Optional ADB device ID for multi-device scenarios.
        """
        self.device_id = device_id
        self.adb_prefix = ["adb"]
        if device_id:
            self.adb_prefix.extend(["-s", device_id])

    def is_installed(self) -> bool:
        """
        Check if ADB Keyboard is installed (via package name).

        Returns:
            bool: True if installed, False otherwise.
        """
        try:
            result = subprocess.run(
                self.adb_prefix + ["shell", "pm", "list", "packages"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            package_list = result.stdout.strip()
            return "com.android.adbkeyboard" in package_list
        except Exception as e:
            print(f"Error checking keyboard installation status: {e}")
            return False

    def is_enabled(self) -> bool:
        """
        Check if ADB Keyboard is enabled (usable).

        Determined by checking the list of enabled input methods.

        Returns:
            bool: True if enabled, False otherwise.
        """
        try:
            # Use ime list -s to check only enabled input methods
            result = subprocess.run(
                self.adb_prefix + ["shell", "ime", "list", "-s"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            ime_list_enabled = result.stdout.strip()
            return ADB_KEYBOARD_PACKAGE in ime_list_enabled
        except Exception as e:
            print(f"Error checking keyboard enable status: {e}")
            return False

    def get_apk_path(self) -> Optional[Path]:
        """
        Get APK file path.

        Prioritizes returning the APK file within the project, falls back to user cache if not exists.

        Returns:
            Optional[Path]: APK file path, or None if neither exists.
        """
        # Prioritize APK within the project
        if PROJECT_APK_PATH.exists():
            return PROJECT_APK_PATH

        # Fallback: APK in user cache directory
        if USER_CACHE_APK_PATH.exists():
            return USER_CACHE_APK_PATH

        return None

    def download_apk(self, force: bool = False) -> bool:
        """
        Get or download ADB Keyboard APK.

        Prioritizes using the APK file within the project, downloads from GitHub if not exists.

        Args:
            force: Whether to force re-download even if file already exists.

        Returns:
            bool: True if APK is successfully obtained, False otherwise.
        """
        # If project has APK and no force download needed, use directly
        if PROJECT_APK_PATH.exists() and not force:
            return True

        # Check user cache
        if USER_CACHE_APK_PATH.exists() and not force:
            return True

        # Download from GitHub
        # Ensure cache directory exists
        USER_CACHE_APK_PATH.parent.mkdir(parents=True, exist_ok=True)

        try:
            urllib.request.urlretrieve(ADB_KEYBOARD_APK_URL, USER_CACHE_APK_PATH)
            return True
        except Exception:
            # Clean up incomplete file
            if USER_CACHE_APK_PATH.exists():
                USER_CACHE_APK_PATH.unlink()
            return False

    def install(self) -> bool:
        """
        Install ADB Keyboard APK.

        Returns:
            bool: True if installation successful, False otherwise.
        """
        apk_path = self.get_apk_path()
        if not apk_path or not apk_path.exists():
            return False

        try:
            result = subprocess.run(
                self.adb_prefix + ["install", "-r", str(apk_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if "Success" in result.stdout or result.returncode == 0:
                return True
            else:
                return False

        except Exception:
            return False

    def enable(self) -> bool:
        """
        Enable ADB Keyboard (enable only, do not modify default input method).

        Note: This only enables ADB Keyboard, does not set it as default input method.
        In actual usage, Phone Agent will temporarily switch via detect_and_set_adb_keyboard().

        Returns:
            bool: True if enable successful, False otherwise.
        """
        try:
            # Enable keyboard
            result = subprocess.run(
                self.adb_prefix
                + ["shell", "ime", "enable", ADB_KEYBOARD_PACKAGE],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return result.returncode == 0

        except Exception:
            return False

    def auto_setup(self) -> bool:
        """
        Automatically complete installation and enablement process.

        Intelligent handling:
        1. Installed and enabled - skip, return True
        2. Installed but not enabled - enable only, return result
        3. Not installed - install+enable, return result

        Note: This method does not interact with users, all user prompts should be handled by the caller.

        Returns:
            bool: True if all successful, False otherwise.
        """
        # Check current status
        installed = self.is_installed()
        enabled = self.is_enabled()

        # Status 1: Installed and enabled
        if installed and enabled:
            return True

        # Status 2: Installed but not enabled
        if installed and not enabled:
            return self.enable()

        # Status 3: Not installed
        if not installed:
            # Step 1: Download APK
            if not self.download_apk():
                return False

            # Step 2: Install
            if not self.install():
                return False

            # Step 3: Enable
            if not self.enable():
                return False

            # Verify
            return self.is_installed() and self.is_enabled()

        # Default return failure
        return False

    def get_status(self) -> dict:
        """
        Get detailed status of ADB Keyboard.

        Returns:
            dict: Dictionary containing installation and enablement status.
        """
        apk_path = self.get_apk_path()
        installed = self.is_installed()
        enabled = self.is_enabled()

        # Determine current status
        if installed and enabled:
            status = "ready"  # Ready
        elif installed and not enabled:
            status = "installed_but_disabled"  # Installed but not enabled
        elif not installed:
            status = "not_installed"  # Not installed
        else:
            status = "unknown"  # Unknown

        return {
            "installed": installed,
            "enabled": enabled,
            "status": status,
            "status_text": {
                "ready": "Installed and enabled",
                "installed_but_disabled": "Installed but not enabled",
                "not_installed": "Not installed",
                "unknown": "Unknown status"
            }.get(status, "Unknown"),
            "apk_exists": apk_path is not None and apk_path.exists(),
            "apk_path": str(apk_path) if apk_path else "N/A",
            "project_apk_exists": PROJECT_APK_PATH.exists(),
            "project_apk_path": str(PROJECT_APK_PATH),
            "cache_apk_exists": USER_CACHE_APK_PATH.exists(),
            "cache_apk_path": str(USER_CACHE_APK_PATH),
        }


def auto_setup_adb_keyboard(device_id: Optional[str] = None) -> bool:
    """
    Convenience function: One-click auto-install and enable ADB Keyboard.

    Args:
        device_id: Optional device ID.

    Returns:
        bool: True on success, False on failure.
    """
    installer = ADBKeyboardInstaller(device_id)
    return installer.auto_setup()


def check_and_suggest_installation() -> bool:
    """
    Check if ADB Keyboard needs installation.

    Note: This function does not interact with users, only returns boolean value.
    All user prompts should be handled by the caller.

    Returns:
        bool: True if not installed, False otherwise.
    """
    installer = ADBKeyboardInstaller()
    return not installer.is_installed()
