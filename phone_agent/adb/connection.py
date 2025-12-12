"""ADB connection management for local and remote devices."""

import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ConnectionType(Enum):
    """Type of ADB connection."""

    USB = "usb"
    WIFI = "wifi"
    REMOTE = "remote"


@dataclass
class DeviceInfo:
    """Information about a connected device."""

    device_id: str
    status: str
    connection_type: ConnectionType
    model: str | None = None
    android_version: str | None = None


class ADBConnection:
    """
    Manages ADB connections to Android devices.

    Supports USB, WiFi, and remote TCP/IP connections.

    Example:
        >>> conn = ADBConnection()
        >>> # Connect to remote device
        >>> conn.connect("192.168.1.100:5555")
        >>> # List devices
        >>> devices = conn.list_devices()
        >>> # Disconnect
        >>> conn.disconnect("192.168.1.100:5555")
    """

    def __init__(self, adb_path: str = "adb"):
        """
        Initialize ADB connection manager.

        Args:
            adb_path: Path to ADB executable.
        """
        self.adb_path = adb_path

    def connect(self, address: str, timeout: int = 10) -> tuple[bool, str]:
        """
        Connect to a remote device via TCP/IP.

        Args:
            address: Device address in format "host:port" (e.g., "192.168.1.100:5555").
            timeout: Connection timeout in seconds.

        Returns:
            Tuple of (success, message).

        Note:
            The remote device must have TCP/IP debugging enabled.
            On the device, run: adb tcpip 5555
        """
        # Validate address format
        if ":" not in address:
            address = f"{address}:5555"  # Default ADB port

        try:
            result = subprocess.run(
                [self.adb_path, "connect", address],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            output = result.stdout + result.stderr

            if "connected" in output.lower():
                return True, f"Connected to {address}"
            elif "already connected" in output.lower():
                return True, f"Already connected to {address}"
            else:
                return False, output.strip()

        except subprocess.TimeoutExpired:
            return False, f"Connection timeout after {timeout}s"
        except Exception as e:
            return False, f"Connection error: {e}"

    def disconnect(self, address: str | None = None) -> tuple[bool, str]:
        """
        Disconnect from a remote device.

        Args:
            address: Device address to disconnect. If None, disconnects all.

        Returns:
            Tuple of (success, message).
        """
        try:
            cmd = [self.adb_path, "disconnect"]
            if address:
                cmd.append(address)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            output = result.stdout + result.stderr
            return True, output.strip() or "Disconnected"

        except Exception as e:
            return False, f"Disconnect error: {e}"

    def list_devices(self) -> list[DeviceInfo]:
        """
        List all connected devices.

        Returns:
            List of DeviceInfo objects.
        """
        try:
            result = subprocess.run(
                [self.adb_path, "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            devices = []
            for line in result.stdout.strip().split("\n")[1:]:  # Skip header
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    status = parts[1]

                    # Determine connection type
                    if ":" in device_id:
                        conn_type = ConnectionType.REMOTE
                    elif "emulator" in device_id:
                        conn_type = ConnectionType.USB  # Emulator via USB
                    else:
                        conn_type = ConnectionType.USB

                    # Parse additional info
                    model = None
                    for part in parts[2:]:
                        if part.startswith("model:"):
                            model = part.split(":", 1)[1]
                            break

                    devices.append(
                        DeviceInfo(
                            device_id=device_id,
                            status=status,
                            connection_type=conn_type,
                            model=model,
                        )
                    )

            return devices

        except Exception as e:
            print(f"Error listing devices: {e}")
            return []

    def get_device_info(self, device_id: str | None = None) -> DeviceInfo | None:
        """
        Get detailed information about a device.

        Args:
            device_id: Device ID. If None, uses first available device.

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
            device_id: Device ID to check. If None, checks if any device is connected.

        Returns:
            True if connected, False otherwise.
        """
        devices = self.list_devices()

        if not devices:
            return False

        if device_id is None:
            return any(d.status == "device" for d in devices)

        return any(d.device_id == device_id and d.status == "device" for d in devices)

    def enable_tcpip(
        self, port: int = 5555, device_id: str | None = None
    ) -> tuple[bool, str]:
        """
        Enable TCP/IP debugging on a USB-connected device.

        This allows subsequent wireless connections to the device.

        Args:
            port: TCP port for ADB (default: 5555).
            device_id: Device ID. If None, uses first available device.

        Returns:
            Tuple of (success, message).

        Note:
            The device must be connected via USB first.
            After this, you can disconnect USB and connect via WiFi.
        """
        try:
            cmd = [self.adb_path]
            if device_id:
                cmd.extend(["-s", device_id])
            cmd.extend(["tcpip", str(port)])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            output = result.stdout + result.stderr

            if "restarting" in output.lower() or result.returncode == 0:
                time.sleep(2)  # Wait for ADB to restart
                return True, f"TCP/IP mode enabled on port {port}"
            else:
                return False, output.strip()

        except Exception as e:
            return False, f"Error enabling TCP/IP: {e}"

    def get_device_ip(self, device_id: str | None = None) -> str | None:
        """
        Get the IP address of a connected device.

        Args:
            device_id: Device ID. If None, uses first available device.

        Returns:
            IP address string or None if not found.
        """
        try:
            cmd = [self.adb_path]
            if device_id:
                cmd.extend(["-s", device_id])
            cmd.extend(["shell", "ip", "route"])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            # Parse IP from route output
            for line in result.stdout.split("\n"):
                if "src" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "src" and i + 1 < len(parts):
                            return parts[i + 1]

            # Alternative: try wlan0 interface
            cmd[-1] = "ip addr show wlan0"
            result = subprocess.run(
                cmd[:-1] + ["shell", "ip", "addr", "show", "wlan0"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            for line in result.stdout.split("\n"):
                if "inet " in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        return parts[1].split("/")[0]

            return None

        except Exception as e:
            print(f"Error getting device IP: {e}")
            return None

    def restart_server(self) -> tuple[bool, str]:
        """
        Restart the ADB server.

        Returns:
            Tuple of (success, message).
        """
        try:
            # Kill server
            subprocess.run(
                [self.adb_path, "kill-server"], capture_output=True, timeout=5
            )

            time.sleep(1)

            # Start server
            subprocess.run(
                [self.adb_path, "start-server"], capture_output=True, timeout=5
            )

            return True, "ADB server restarted"

        except Exception as e:
            return False, f"Error restarting server: {e}"


def quick_connect(address: str) -> tuple[bool, str]:
    """
    Quick helper to connect to a remote device.

    Args:
        address: Device address (e.g., "192.168.1.100" or "192.168.1.100:5555").

    Returns:
        Tuple of (success, message).
    """
    conn = ADBConnection()
    return conn.connect(address)


def list_devices() -> list[DeviceInfo]:
    """
    Quick helper to list connected devices.

    Returns:
        List of DeviceInfo objects.
    """
    conn = ADBConnection()
    return conn.list_devices()
