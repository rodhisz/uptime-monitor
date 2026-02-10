# 24/7 Uptime Monitor (No Server Required)

This is a simple system to monitor your website/API status using GitHub Actions. It runs every 1 minute and sends a notification if your system is down.

## How it works
1.  **GitHub Actions Runner** wakes up every 1 minute.
2.  Runs the `check_uptime.py` Python script.
3.  The script tries to reach your `TARGET_URL`.
4.  It saves the status to `uptime_status.json` and commits it back to the repo.
    -   If status changes from DOWN to UP, it calculates downtime duration and alerts you.
5.  If the response code is not 200 (OK), it sends an alert to Discord or Telegram.

## Setup Instructions

### 1. Upload to GitHub
Upload this entire folder to a new GitHub repository (can be Private or Public).

### 2. Configure Secrets
Go to your Repository **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.

Add the following secrets:

-   `TARGET_URL` (Required): The URL you want to monitor (e.g., `https://mysystem.com/health`).

**For Discord Notifications (Optional):**
-   `DISCORD_WEBHOOK_URL`: Your Discord Webhook URL.
    -   *How to get:*
        1.  Open Discord and go to the server where you want notifications.
        2.  Go to **Server Settings** -> **Integrations** -> **Webhooks**.
        3.  Click **New Webhook**.
        4.  Give it a name (e.g., "Uptime Bot") and choose a channel.
        5.  Click **Copy Webhook URL**.

**For Telegram Notifications (Optional):**
-   `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token.
    -   *How to get:* Message @BotFather on Telegram to create a new bot.
-   `TELEGRAM_CHAT_ID`: Your Chat ID.
    -   *How to get:* Message @userinfobot to get your ID.

### 3. That's it!
The action is configured to run automatically.
-   You can verify it works by going to the **Actions** tab in your repo.
-   You can manually trigger a check by selecting the "Uptime Monitor" workflow and clicking **Run workflow**.

## Customize Frequency
To change how often it runs, edit `.github/workflows/uptime.yml`:
```yaml
on:
  schedule:
    - cron: '*/1 * * * *' # Change 1 to your desired minutes
```
*Note: GitHub Actions free tier has plenty of minutes, but don't set it too frequent (e.g. every 1 minute) to avoid hitting limits or getting flagged.*
