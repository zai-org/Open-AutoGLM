#!/usr/bin/env python3
"""
Telegram Bot for Open-AutoGLM
Controls the phone agent via Telegram messages.
"""

import logging
import os
import subprocess
import shlex
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ======================================================================================
# CONFIGURATION
# ======================================================================================
# 1. Get token from @BotFather
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

# 2. Get your User ID from @userinfobot (to prevent others from controlling your phone)
ALLOWED_USER_ID = 0  # Replace with your numeric user ID (e.g., 123456789)

# 3. Path to your agent script (using the PowerShell wrapper for Windows)
AGENT_SCRIPT = "start_agent.ps1"
# ======================================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /start command."""
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Unauthorized access.")
        return

    await update.message.reply_text(
        "🤖 **AutoGLM Bot Ready!**\n\n"
        "Send me any text like \"Open Chrome\" and I will execute it on your phone.\n"
        "Make sure your laptop is running and phone is connected!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Passes the message text to the AutoGLM agent."""
    user_id = update.effective_user.id
    message_text = update.message.text

    # Security check
    if ALLOWED_USER_ID != 0 and user_id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Unauthorized access.")
        return
    
    # Notify user we are starting
    status_msg = await update.message.reply_text(f"⏳ Executing: _{message_text}_ ...", parse_mode='Markdown')

    try:
        # Construct the task prompt with safety/navigation wrappers
        full_task = (
            "First, go to the home screen. "
            f"Then, {message_text}. "
            "Finally, go to the home screen, open the Telegram app, and then open the chat with 'AutoGLM_bot'."
        )

        # Construct the command
        # We use the powershell script to handle environment setup
        # Add --auto-confirm to prevent blocking on user interaction
        command = [
            "powershell", 
            "-ExecutionPolicy", "Bypass", 
            "-File", f".\\{AGENT_SCRIPT}", 
            "--auto-confirm",
            full_task
        ]
        
        logging.info(f"Running command: {command}")

        # Run with Popen to stream output to console (for debugging)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1  # Line buffered
        )

        output_buffer = []
        
        # Stream output
        try:
            for line in process.stdout:
                print(line, end='', flush=True)  # Stream to bot console
                output_buffer.append(line)
        except Exception as e:
            logging.error(f"Error reading output: {e}")
            
        process.wait()
        
        full_output = "".join(output_buffer)
        
        if process.returncode == 0:
            final_response = f"yo, we did it.\n\nOutput:\n```\n{full_output[-2000:]}\n```" # Telegram max message is 4096 chars
        else:
            final_response = f"❌ **Error** (Exit Code {process.returncode})\n\nOutput:\n```\n{full_output[-2000:]}\n```"

        await status_msg.edit_text(final_response, parse_mode='Markdown')

    except Exception as e:
        await status_msg.edit_text(f"💥 **Internal Bot Error**:\n{str(e)}")

if __name__ == '__main__':
    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        print("❌ Error: You must set the BOT_TOKEN in telegram_bot.py")
        exit(1)

    print("🤖 Bot is starting...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 Polling for messages...")
    application.run_polling()
