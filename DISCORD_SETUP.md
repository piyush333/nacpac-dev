# Discord Setup Guide

Quick start to set up Discord channels and test the JICO Manager system.

## Step 1: Create Discord Bot (if you don't have one)

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name it "JICO Manager"
4. Go to "Bot" section
5. Click "Add Bot"
6. Copy the **TOKEN** → paste into `.env` as `DISCORD_TOKEN`
7. Enable these **Intents**:
   - ✅ Message Content Intent
   - ✅ Server Members Intent (optional)
   - ✅ Guild Members Intent (optional)
8. Click "OAuth2" → "URL Generator"
9. Select scopes: `bot`
10. Select permissions:
    - ✅ Read Messages/View Channels
    - ✅ Send Messages
    - ✅ Add Reactions
    - ✅ Manage Channels
11. Copy generated URL and open in browser to add bot to your server

## Step 2: Get Your Guild ID

1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click your server name → "Copy Server ID"
3. Paste into `.env` as `DISCORD_GUILD_ID`

## Step 3: Update .env

```env
DISCORD_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
```

## Step 4: Create Channels Automatically

Run the setup script:

```bash
cd /home/user/nacpac-dev/jico-system
python setup_discord_channels.py
```

**Expected output:**
```
🚀 JICO Discord Channel Setup
==================================================

Starting setup...
(This will create channels in your Discord server)

✅ Bot logged in as JICO Manager#1234
📍 Setting up channels in guild: Your Server Name

✅ #general - Already exists
✅ #nacpac-dev - Created
✅ #jico-dev - Created
✅ #logs - Created
✅ #reports - Created

🎉 Channel setup complete!
```

## Step 5: Test the System

### Option A: Run Locally (Fast)

```bash
cd /home/user/nacpac-dev/jico-system
python main.py
```

You'll see:
```
2026-06-30 15:15:00 - INFO - 🤖 Discord Manager online as JICO Manager#1234
2026-06-30 15:15:01 - INFO - ✅ Channels initialized: general=True, nacpac-dev=True, jico-dev=True
2026-06-30 15:15:02 - INFO - 🤖 Auto mode started - listening for tasks in #general
```

### Option B: Run in Background

```bash
nohup python main.py > /tmp/jico-bot.log 2>&1 &
tail -f /tmp/jico-bot.log
```

## Step 6: Send Test Messages

In Discord, go to **#general** and try:

```
Add dark mode to mobile app
```

**Expected responses:**

In #general:
```
📱 NACPAC task queued
ID: `task_abc123`
Action: Add dark mode to mobile app
Updates → #nacpac-dev
```

In #nacpac-dev:
```
📋 Task task_abc123 started
Action: Add dark mode to mobile app
Target: dev
Priority: normal
```

Then bot processes it, and results appear in #nacpac-dev:
```
✅ Task task_abc123 success
Action: Add dark mode to mobile app
Target: dev
📦 APK: https://...apk...
📦 EXE: https://...exe...
```

## Step 7: Try More Commands

In #general:

```
Build APK
```
→ Routes to Nacpac build worker

```
Add a new color variant for Shopify
```
→ Routes to Jico (AR) worker

```
!status
```
→ System status in same channel

```
!auto_mode status
```
→ Show pending/executing tasks

```
!help_jico
```
→ Show help (channel architecture)

## Troubleshooting

### Bot doesn't respond

1. **Check bot is in server:**
   - Go to Server Settings → Roles → Check if JICO Manager is listed

2. **Check permissions:**
   - Right-click bot role → Check permissions
   - Need: Read Messages, Send Messages, Add Reactions, Manage Channels

3. **Check token:**
   - Make sure DISCORD_TOKEN in .env is correct
   - No spaces or newlines

4. **Check guild ID:**
   - Make sure DISCORD_GUILD_ID in .env is correct
   - Should be numeric, like: `123456789`

5. **Check logs:**
   ```bash
   tail -f /tmp/jico-system.log
   grep ERROR /tmp/jico-system.log
   ```

### Bot in server but doesn't see channels

1. Make sure channels were created (run setup script again)
2. Make sure bot has permission to see channels
3. Check DISCORD_GUILD_ID is correct

### Channels created but bot doesn't post results

1. Check #logs for errors
2. Make sure bot has "Send Messages" permission in each channel
3. Check compression layer is working (logs should show "classification_method")

## Monitoring

### Watch logs in real-time
```bash
tail -f /tmp/jico-system.log
```

### Check what's running
```bash
ps aux | grep "python main.py"
```

### Stop the bot
```bash
pkill -f "python main.py"
```

### Restart the bot
```bash
pkill -f "python main.py"
sleep 2
python main.py &
```

## Channel Reference

Once running, you'll see:

| Channel | Purpose |
|---------|---------|
| **#general** | You talk here → Manager routes |
| **#nacpac-dev** | Nacpac task updates |
| **#jico-dev** | Jico task updates |
| **#logs** | Errors and debugging |
| **#reports** | Scheduled reports |

## Next: Full Testing

See `DISCORD_ARCHITECTURE.md` for complete workflow examples.

## Quick Commands

```bash
# Setup
python setup_discord_channels.py

# Run
python main.py

# Test
# (in Discord #general)
# "Add dark mode to home screen"

# Monitor
tail -f /tmp/jico-system.log

# Stop
pkill -f "python main.py"
```

---

**You're ready to test! Set up the bot and send a message in #general.**
