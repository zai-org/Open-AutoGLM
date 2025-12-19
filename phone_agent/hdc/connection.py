"""HDC connection management for HarmonyOS devices."""

import os
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from phone_agent.config.timing import TIMING_CONFIG


# Global flag to control HDC command output
_HDC_VERBOSE = os.getenv("HDC_VERBOSE", "false").lower() in ("true", "1", "yes")


def _run_hdc_command(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    """
    Run HDC command with optional verbose output.

    Args:
        cmd: Command list to execute.
        **kwargs: Additional arguments for subprocess.run.

    Returns:
        CompletedProcess result.
    """
    if _HDC_VERBOSE:
        print(f"[HDC] Running command: {' '.join(cmd)}")

    result = subprocess.run(cmd, **kwargs)

    if _HDC_VERBOSE and result.returncode != 0:
        print(f"[HDC] Command failed with return code {result.returncode}")
        if hasattr(result, 'stderr') and result.stderr:
            print(f"[HDC] Error: {result.stderr}")

    return result


def set_hdc_verbose(verbose: bool):
    """Set HDC verbose mode globally."""
    global _HDC_VERBOSE
    _HDC_VERBOSE = verbose


class ConnectionType(Enum):
    """Type of HDC connection."""

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
    harmony_version: str | None = None


class HDCConnection:
    """
    Manages HDC connections to HarmonyOS devices.

    Supports USB, WiFi, and remote TCP/IP connections.

    Example:
        >>> conn = HDCConnection()
        >>> # Connect to remote device
        >>> conn.connect("192.168.1.100:5555")
        >>> # List devices
        >>> devices = conn.list_devices()
        >>> # Disconnect
        >>> conn.disconnect("192.168.1.100:5555")
    """

    def __init__(self, hdc_path: str = "hdc"):
        """
        Initialize HDC connection manager.

        Args:
            hdc_path: Path to HDC executable.
        """
        self.hdc_path = hdc_path

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
        """
        # Validate address format
        if ":" not in address:
            address = f"{address}:5555"  # Default HDC port

        try:
            result = _run_hdc_command(
                [self.hdc_path, "tconn", address],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            output = result.stdout + result.stderr

            if "Connect OK" in output or "connected" in output.lower():
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
            if address:
                cmd = [self.hdc_path, "tdisconn", address]
            else:
                # HDC doesn't have a "disconnect all" command, so we need to list and disconnect each
                devices = self.list_devices()
                for device in devices:
                    if ":" in device.device_id:  # Remote device
                        _run_hdc_command(
                            [self.hdc_path, "tdisconn", device.device_id],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                return True, "Disconnected all remote devices"

            result = _run_hdc_command(cmd, capture_output=True, text=True, encoding="utf-8", timeout=5)

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
            result = _run_hdc_command(
                [self.hdc_path, "list", "targets"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            devices = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue

                # HDC output format: device_id (status)
                # Example: "192.168.1.100:5555" or "FMR0223C13000649"
                device_id = line.strip()

                # Determine connection type
                if ":" in device_id:
                    conn_type = ConnectionType.REMOTE
                else:
                    conn_type = ConnectionType.USB

                # HDC doesn't provide detailed status in list command
                # We assume "Connected" status for devices that appear
                devices.append(
                    DeviceInfo(
                        device_id=device_id,
                        status="device",
                        connection_type=conn_type,
                        model=None,
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
            return len(devices) > 0

        return any(d.device_id == device_id for d in devices)

    def enable_tcpip(
        self, port: int = 5555, device_id: str | None = None
    ) -> tuple[bool, str]:
        """
        Enable TCP/IP debugging on a USB-connected device.

        This allows subsequent wireless connections to the device.

        Args:
            port: TCP port for HDC (default: 5555).
            device_id: Device ID. If None, uses first available device.

        Returns:
            Tuple of (success, message).

        Note:
            The device must be connected via USB first.
            After this, you can disconnect USB and connect via WiFi.
        """
        try:
            cmd = [self.hdc_path]
            if device_id:
                cmd.extend(["-t", device_id])
            cmd.extend(["tmode", "port", str(port)])

            result = _run_hdc_command(cmd, capture_output=True, text=True, encoding="utf-8", timeout=10)

            output = result.stdout + result.stderr

            if result.returncode == 0 or "success" in output.lower():
                time.sleep(TIMING_CONFIG.connection.adb_restart_delay)
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
            cmd = [self.hdc_path]
            if device_id:
                cmd.extend(["-t", device_id])
            cmd.extend(["shell", "ifconfig"])

            result = _run_hdc_command(cmd, capture_output=True, text=True, encoding="utf-8", timeout=5)

            # Parse IP from ifconfig output
            for line in result.stdout.split("\n"):
                if "inet addr:" in line or "inet " in line:
                    parts = line.strip().split()
                    for i, part in enumerate(parts):
                        if "addr:" in part:
                            ip = part.split(":")[1]
                            # Filter out localhost
                            if not ip.startswith("127."):
                                return ip
                        elif part == "inet" and i + 1 < len(parts):
                            ip = parts[i + 1].split("/")[0]
                            if not ip.startswith("127."):
                                return ip

            return None

        except Exception as e:
            print(f"Error getting device IP: {e}")
            return None

    def restart_server(self) -> tuple[bool, str]:
        """
        Restart the HDC server.

        Returns:
            Tuple of (success, message).
        """
        try:
            # Kill server
            _run_hdc_command(
                [self.hdc_path, "kill"], capture_output=True, timeout=5
            )

            time.sleep(TIMING_CONFIG.connection.server_restart_delay)

            # Start server (HDC auto-starts when running commands)
            _run_hdc_command(
                [self.hdc_path, "start", "-r"], capture_output=True, timeout=5
            )

            return True, "HDC server restarted"

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
    conn = HDCConnection()
    return conn.connect(address)


def list_devices() -> list[DeviceInfo]:
    """
    Quick helper to list connected devices.

    Returns:
        List of DeviceInfo objects.
    """
    conn = HDCConnection()
    return conn.list_devices()
