"""iOS device connection management via idevice tools and WebDriverAgent."""

import subprocess
import time
from dataclasses import dataclass
from enum import Enum


class ConnectionType(Enum):
    """Type of iOS connection."""

    USB = "usb"
    NETWORK = "network"


@dataclass
class DeviceInfo:
    """Information about a connected iOS device."""

    device_id: str  # UDID
    status: str
    connection_type: ConnectionType
    model: str | None = None
    ios_version: str | None = None
    device_name: str | None = None


class XCTestConnection:
    """
    Manages connections to iOS devices via libimobiledevice and WebDriverAgent.

    Requires:
        - libimobiledevice (idevice_id, ideviceinfo)
        - WebDriverAgent running on the iOS device
        - ios-deploy (optional, for app installation)

    Example:
        >>> conn = XCTestConnection()
        >>> # List connected devices
        >>> devices = conn.list_devices()
        >>> # Get device info
        >>> info = conn.get_device_info()
        >>> # Check if WDA is running
        >>> is_ready = conn.is_wda_ready()
    """

    def __init__(self, wda_url: str = "http://localhost:8100"):
        """
        Initialize iOS connection manager.

        Args:
            wda_url: WebDriverAgent URL (default: http://localhost:8100).
                     For network devices, use http://<device-ip>:8100
        """
        self.wda_url = wda_url.rstrip("/")

    def list_devices(self) -> list[DeviceInfo]:
        """
        List all connected iOS devices.

        Returns:
            List of DeviceInfo objects.

        Note:
            Requires libimobiledevice to be installed.
            Install on macOS: brew install libimobiledevice
        """
        try:
            # Get list of device UDIDs
            result = subprocess.run(
                ["idevice_id", "-ln"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            devices = []
            for line in result.stdout.strip().split("\n"):
                udid = line.strip()
                if not udid:
                    continue

                # Determine connection type (network devices have specific format)
                conn_type = (
                    ConnectionType.NETWORK
                    if "-" in udid and len(udid) > 40
                    else ConnectionType.USB
                )

                # Get detailed device info
                device_info = self._get_device_details(udid)

                devices.append(
                    DeviceInfo(
                        device_id=udid,
                        status="connected",
                        connection_type=conn_type,
                        model=device_info.get("model"),
                        ios_version=device_info.get("ios_version"),
                        device_name=device_info.get("name"),
                    )
                )

            return devices

        except FileNotFoundError:
            print(
                "Error: idevice_id not found. Install libimobiledevice: brew install libimobiledevice"
            )
            return []
        except Exception as e:
            print(f"Error listing devices: {e}")
            return []

    def _get_device_details(self, udid: str) -> dict[str, str]:
        """
        Get detailed information about a specific device.

        Args:
            udid: Device UDID.

        Returns:
            Dictionary with device details.
        """
        try:
            result = subprocess.run(
                ["ideviceinfo", "-u", udid],
                capture_output=True,
                text=True,
                timeout=5,
            )

            info = {}
            for line in result.stdout.split("\n"):
                if ": " in line:
                    key, value = line.split(": ", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "ProductType":
                        info["model"] = value
                    elif key == "ProductVersion":
                        info["ios_version"] = value
                    elif key == "DeviceName":
                        info["name"] = value

            return info

        except Exception:
            return {}

    def get_device_info(self, device_id: str | None = None) -> DeviceInfo | None:
        """
        Get detailed information about a device.

        Args:
            device_id: Device UDID. If None, uses first available device.

        Returns:
            DeviceInfo or None if not found.
        """
        devices = self.list_devices()

        if not devices:
            return None

        if device_id is None:
            return devices[0]

        for device in devices:
            if device.device_id == device_id:
                return device

        return None

    def is_connected(self, device_id: str | None = None) -> bool:
        """
        Check if a device is connected.

        Args:
            device_id: Device UDID to check. If None, checks if any device is connected.

        Returns:
            True if connected, False otherwise.
        """
        devices = self.list_devices()

        if not devices:
            return False

        if device_id is None:
            return len(devices) > 0

        return any(d.device_id == device_id for d in devices)

    def is_wda_ready(self, timeout: int = 2) -> bool:
        """
        Check if WebDriverAgent is running and accessible.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if WDA is ready, False otherwise.
        """
        try:
            import requests

            response = requests.get(
                f"{self.wda_url}/status", timeout=timeout, verify=False
            )
            return response.status_code == 200
        except ImportError:
            print(
                "Error: requests library not found. Install it: pip install requests"
            )
            return False
        except Exception:
            return False

    def start_wda_session(self) -> tuple[bool, str]:
        """
        Start a new WebDriverAgent session.

        Returns:
            Tuple of (success, session_id or error_message).
        """
        try:
            import requests

            response = requests.post(
                f"{self.wda_url}/session",
                json={"capabilities": {}},
                timeout=30,
                verify=False,
            )

            if response.status_code in (200, 201):
                data = response.json()
                session_id = data.get("sessionId") or data.get("value", {}).get(
                    "sessionId"
                )
                return True, session_id or "session_started"
            else:
                return False, f"Failed to start session: {response.text}"

        except ImportError:
            return (
                False,
                "requests library not found. Install it: pip install requests",
            )
        except Exception as e:
            return False, f"Error starting WDA session: {e}"

    def get_wda_status(self) -> dict | None:
        """
        Get WebDriverAgent status information.

        Returns:
            Status dictionary or None if not available.
        """
        try:
            import requests

            response = requests.get(f"{self.wda_url}/status", timeout=5, verify=False)

            if response.status_code == 200:
                return response.json()
            return None

        except Exception:
            return None

    def pair_device(self, device_id: str | None = None) -> tuple[bool, str]:
        """
        Pair with an iOS device (required for some operations).

        Args:
            device_id: Device UDID. If None, uses first available device.

        Returns:
            Tuple of (success, message).
        """
        try:
            cmd = ["idevicepair"]
            if device_id:
                cmd.extend(["-u", device_id])
            cmd.append("pair")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            output = result.stdout + result.stderr

            if "SUCCESS" in output or "already paired" in output.lower():
                return True, "Device paired successfully"
            else:
                return False, output.strip()

        except FileNotFoundError:
            return (
                False,
                "idevicepair not found. Install libimobiledevice: brew install libimobiledevice",
            )
        except Exception as e:
            return False, f"Error pairing device: {e}"

    def get_device_name(self, device_id: str | None = None) -> str | None:
        """
        Get the device name.

        Args:
            device_id: Device UDID. If None, uses first available device.

        Returns:
            Device name string or None if not found.
        """
        try:
            cmd = ["ideviceinfo"]
            if device_id:
                cmd.extend(["-u", device_id])
            cmd.extend(["-k", "DeviceName"])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            return result.stdout.strip() or None

        except Exception as e:
            print(f"Error getting device name: {e}")
            return None

    def restart_wda(self) -> tuple[bool, str]:
        """
        Restart WebDriverAgent (requires manual restart on device).

        Returns:
            Tuple of (success, message).

        Note:
            This method only checks if WDA needs restart.
            Actual restart requires re-running WDA on the device via Xcode or other means.
        """
        if self.is_wda_ready():
            return True, "WDA is already running"
        else:
            return (
                False,
                "WDA is not running. Please start it manually on the device.",
            )


def quick_connect(wda_url: str = "http://localhost:8100") -> tuple[bool, str]:
    """
    Quick helper to check iOS device connection and WDA status.

    Args:
        wda_url: WebDriverAgent URL.

    Returns:
        Tuple of (success, message).
    """
    conn = XCTestConnection(wda_url=wda_url)

    # Check if device is connected
    if not conn.is_connected():
        return False, "No iOS device connected"

    # Check if WDA is ready
    if not conn.is_wda_ready():
        return False, "WebDriverAgent is not running"

    return True, "iOS device connected and WDA ready"


def list_devices() -> list[DeviceInfo]:
    """
    Quick helper to list connected iOS devices.

    Returns:
        List of DeviceInfo objects.
    """
    conn = XCTestConnection()
    return conn.list_devices()
