# Remote Control Setup Guide (Tailscale + ADB)

This guide explains how to control your Android phone using Open-AutoGLM even when the phone is on a mobile network (4G/5G) and not on the same Wi-Fi as your PC.

## 1. Prerequisites (Tailscale VPN)

Since ADB (Android Debug Bridge) does not work over the public internet securely, we use **Tailscale** to create a private, secure link between your devices.

### Step 1: Install Tailscale
1.  **On PC**: Download and install [Tailscale for Windows](https://tailscale.com/download/windows).
2.  **On Phone**: Install the **Tailscale** app from the Google Play Store.

### Step 2: Configure Network
1.  Open Tailscale on **both** devices.
2.  Log in with the **same account** (e.g., your Google account) on both.
3.  Ensure Tailscale is **Active** (Connected) on both.
4.  On the phone app, find the **IP Address** assigned to your phone (it starts with `100.x.x.x`).

## 2. Connect ADB Remotely

To connect your PC to the phone securely over this new network:

1.  **Open Terminal** in the `Open-AutoGLM` directory.
2.  Run the connect command using the local `platform-tools`:

    ```powershell
    .\platform-tools\adb.exe connect <PHONE_TAILSCALE_IP>:5555
    ```
    *(Replace `<PHONE_TAILSCALE_IP>` with the address you found in Step 1, e.g., `100.76.226.33`)*

3.  **Verify Connection**:
    ```powershell
    .\platform-tools\adb.exe devices
    ```
    You should see your device IP listed as `device`.

## 3. Troubleshooting

**"Target machine actively refused it"**
*   This means ADB is not listening on port 5555 on the phone.
*   **Fix**: You must enable TCP/IP mode *once* via USB.
    1.  Plug phone into PC via USB.
    2.  Run: `.\platform-tools\adb.exe tcpip 5555`
    3.  Unplug phone.
    4.  Try connecting again via Tailscale IP.

**"Command not found"**
*   PowerShell doesn't know where `adb` is. Always use `.\platform-tools\adb.exe` instead of just `adb`.
