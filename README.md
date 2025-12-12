# AutoGLM-TGLinked: The "Cloud Native" AI Phone Agent

> **Status**: **Public Alpha v0.1**  
> **"Control your phone, from your phone... via your computer."**

Open-AutoGLM is a Windows-based AI agent that uses the Z.ai Vision Model to autonomously control your Android device. It is designed to be **"Cloud Native"**, meaning you can control your phone from anywhere in the world using Telegram, with your laptop acting as the brain at home.

---

## The Architecture

### 1. What We Did
We integrated **Tailscale** (a Mesh VPN) and **Telegram** to decouple the physical link between PC and Phone.

### 2. Why We Did It
*   **Problem**: Standard ADB requires USB or local Wi-Fi. You can't use the agent if you are at a cafe and your laptop is at home.
*   **Solution**: Tailscale creates a virtual tunnel. Your laptop sees your phone as "local" even if it's on 5G. Telegram provides the UI to trigger commands remotely.

### 3. How It Works
1.  **Tunnel**: Tailscale connects PC & Phone over the internet.
2.  **Control**: Telegram Bot on PC receives your command.
3.  **Action**: PC sends ADB commands through the tunnel to the phone.

---

## Quick Start Guide

Want to run this on your own laptop? Follow these steps.

### Prerequisites
*   Windows PC (The Brain)
*   Android Phone (The Hand)
*   Python 3.10+
*   [Tailscale](https://tailscale.com/) installed on both devices.

### Installation

1.  **Clone the Repo**:
    ```powershell
    git clone https://github.com/YourUsername/Open-AutoGLM.git
    cd Open-AutoGLM
    ```

2.  **Install Dependencies**:
    ```powershell
    pip install python-telegram-bot openai
    ```

3.  **Setup ADB**:
    *   Enable **Developer Options** & **USB Debugging** on your phone.
    *   Install **[ADB Keyboard](https://github.com/senzhk/ADBKeyBoard)** on your phone and set it as default.
    *   Connect via USB and run `.\platform-tools\adb.exe tcpip 5555` once to enable wireless mode.

---

## Configuration (IMPORTANT)

You must add your own API keys for this to work.

### 1. Z.ai Vision Model Key
*   Open `start_agent.ps1`
*   Find `$ApiKey` line.
*   Paste your Z.ai API key:
    ```powershell
    $ApiKey = "sk-..."
    ```

### 2. Telegram Bot Token
*   Talk to **@BotFather** on Telegram to create a new bot.
*   Open `telegram_bot.py`.
*   Paste your Token:
    ```python
    BOT_TOKEN = "123456:ABC-..."
    ```

### 3. Security (User ID)
*   To prevent strangers from controlling your phone, set your Telegram User ID.
*   Talk to **@userinfobot** to get your numeric ID.
*   Update `telegram_bot.py`:
    ```python
    ALLOWED_USER_ID = 123456789
    ```

---

## Usage

### 1. Connect Devices
Ensure Tailscale is ON for both devices. Get your phone's Tailscale IP (e.g., `100.x.x.x`).
```powershell
.\platform-tools\adb.exe connect 100.x.x.x:5555
```

### 2. Start the Bot
Run the bot listener on your PC:
```powershell
python telegram_bot.py
```

### 3. Control Remotely
Open your Bot in Telegram and send a command:
> *"Open Instagram and find a picture of a cat"*

The bot will execute the script, connect to your phone, and send you back a screenshot of the result!

---

## Future Roadmap

We are moving towards a computer-less future where the agent lives entirely in the cloud.

### 1. Phase I: Whisper Protocol (Voice Control)
**Goal**: Stop typing commands.
*   **Plan**: Integrate OpenAI Whisper into the Telegram bot.
*   **Experience**: Send a voice note -> Bot transcribes -> Agent executes.

### 2. Phase II: Headless Accessibility (Action Button)
**Goal**: Stop opening Telegram.
*   **Plan**: Use Android Accessibility Services to map a physical button to trigger the agent.
*   **Experience**: Press Action Button -> Speak command -> Done.

### 3. Phase III: True Cloud Autonomy (AWS / Railway)
**Goal**: Stop using the laptop.
*   **Plan**: Dockerize the agent and deploy to the cloud.
*   **Experience**: Your personal AI agent runs 24/7 on a server, always connected to your phone via Tailscale.

---

## Troubleshooting

*   **"Target machine actively refused it"**: Re-enable TCP/IP mode via USB (`adb tcpip 5555`).
*   **"Device Offline"**: Disconnect and reconnect ADB using the new IP.
