import os
import sys
import requests
from datetime import datetime

def send_discord_notification(webhook_url, message):
    data = {
        "content": message
    }
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        print("Discord notification sent.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord notification: {e}")
        if response is not None:
             print(f"Response status: {response.status_code}")
             print(f"Response body: {response.text}")

def send_telegram_notification(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print("Telegram notification sent.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram notification: {e}")

import json
from datetime import datetime, timedelta

# ... (Previous notification functions remain the same, but I will include them to be safe if I need to change message format)
# Actually, I'll just rewrite the check_uptime function and helper imports/loading.

STATUS_FILE = "uptime_status.json"

def load_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_status(status):
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f)

def check_uptime():
    target_url = os.environ.get("TARGET_URL")
    if not target_url:
        print("Error: TARGET_URL environment variable not set.")
        sys.exit(1)

    discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    print(f"Checking {target_url} at {datetime.now()}...")

    # Load previous state
    state = load_status()
    was_down = state.get("is_down", False)
    down_start_time_str = state.get("down_start_time")
    
    is_currently_down = False
    status_code = None
    error_details = ""

    try:
        response = requests.get(target_url, timeout=30)
        status_code = response.status_code
        
        if status_code == 200:
            print(f"Status OK (200).")
            is_currently_down = False
        else:
            is_currently_down = True
            error_details = f"Status code {status_code}"

    except requests.exceptions.RequestException as e:
        is_currently_down = True
        error_details = str(e)

    # Logic for notifications and state update
    if is_currently_down:
        if not was_down:
            # IT JUST WENT DOWN
            msg = f"⚠️ **DOWN ALERT**: {target_url} is DOWN! ({error_details})."
            print(msg)
            if discord_webhook: send_discord_notification(discord_webhook, msg)
            if telegram_token and telegram_chat_id: send_telegram_notification(telegram_token, telegram_chat_id, msg)
            
            # Save state
            state["is_down"] = True
            state["down_start_time"] = datetime.now().isoformat()
            save_status(state)
        else:
            print("Still down... no new notification.")

    else:
        # IT IS UP
        if was_down:
            # IT JUST RECOVERED
            down_start = datetime.fromisoformat(down_start_time_str) if down_start_time_str else None
            duration_str = "unknown duration"
            if down_start:
                duration = datetime.now() - down_start
                # Format duration nicely
                total_seconds = int(duration.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                duration_str = f"{hours}h {minutes}m {seconds}s"

            msg = f"✅ **RECOVERED**: {target_url} is back UP! It was down for **{duration_str}**."
            print(msg)
            if discord_webhook: send_discord_notification(discord_webhook, msg)
            if telegram_token and telegram_chat_id: send_telegram_notification(telegram_token, telegram_chat_id, msg)
            
            # Reset state
            state["is_down"] = False
            state["down_start_time"] = None
            save_status(state)
        else:
            print("Status is normal.")

    return True # Always return true so workflow doesn't fail unless script crashes

if __name__ == "__main__":
    check_uptime()
