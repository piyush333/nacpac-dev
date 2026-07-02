# Getting Discord Credentials

Complete guide to set up Discord bot and extract required credentials.

---

## What You Need

For the agentic system, you need:

| Credential | What it is | Where to find |
|-----------|-----------|---------------|
| `DISCORD_TOKEN` | Bot authentication token | Developer Portal → Bot |
| `DISCORD_GUILD_ID` | Your Discord server ID | Right-click server → Copy ID |
| `DISCORD_GENERAL_CHANNEL_ID` | #general channel ID | Right-click #general → Copy ID |
| `DISCORD_BUILDS_CHANNEL_ID` | #builds channel ID | Create channel, copy ID |
| `DISCORD_DEPLOYS_CHANNEL_ID` | #deploys channel ID | Create channel, copy ID |
| `ALLOWED_USER_ID` | Your Discord user ID | Right-click your name → Copy ID |

---

## Step 1: Create Discord Bot (if needed)

### Option A: You already have a bot from jico-system

If you already set up a Discord bot for the old system:
- Skip to **Step 2: Get DISCORD_TOKEN**
- Reuse same bot and token

### Option B: Create a new bot

1. Go to https://discord.com/developers/applications
2. Click **New Application**
3. Enter name: `jico-agentic` (or any name)
4. Click **Create**
5. Go to **Bot** (left sidebar)
6. Click **Add Bot**
7. Confirm "Yes, do it!"

You now have a bot! Continue to Step 2.

---

## Step 2: Get DISCORD_TOKEN

1. In Discord Developer Portal, click **Bot** (left sidebar)
2. Under **TOKEN** section, click **Copy**
3. This is your `DISCORD_TOKEN`

**Example:**
```
DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE_LONG_STRING
```

**⚠️ IMPORTANT:** Keep this secret! Never share or commit to git.

**In your .env:**
```
DISCORD_TOKEN=YOUR_ACTUAL_BOT_TOKEN_HERE
```

---

## Step 3: Add Bot to Your Server

1. In Developer Portal, go to **OAuth2** (left sidebar)
2. Select **URL Generator**
3. Under **SCOPES**, check:
   - ✅ `bot`
4. Under **PERMISSIONS**, check:
   - ✅ `Send Messages`
   - ✅ `Use Slash Commands`
   - ✅ `Read Messages/View Channels`
5. Copy the generated URL at bottom
6. Open URL in browser
7. Select your Discord server
8. Click **Authorize**

Done! Bot is now in your server.

---

## Step 4: Get DISCORD_GUILD_ID

1. Open your Discord server
2. Right-click on the server name (top-left)
3. Click **Copy Server ID**
4. This is your `DISCORD_GUILD_ID`

**Example:**
```
DISCORD_GUILD_ID=123456789012345678
```

**In your .env:**
```
DISCORD_GUILD_ID=123456789012345678
```

---

## Step 5: Create Channels (if needed)

The bot posts results to 3 channels. Create them:

1. In Discord, right-click server → **Create Channel**
2. Create these channels:
   - `#general` (usually exists)
   - `#builds` (new)
   - `#deploys` (new)
3. Make sure bot has permission to see and post in all 3

---

## Step 6: Get Channel IDs

For each channel (#general, #builds, #deploys):

1. Right-click channel name
2. Click **Copy Channel ID**
3. Save these IDs

**Example:**
```
DISCORD_GENERAL_CHANNEL_ID=123456789012345679
DISCORD_BUILDS_CHANNEL_ID=123456789012345680
DISCORD_DEPLOYS_CHANNEL_ID=123456789012345681
```

**In your .env:**
```
DISCORD_GENERAL_CHANNEL_ID=123456789012345679
DISCORD_BUILDS_CHANNEL_ID=123456789012345680
DISCORD_DEPLOYS_CHANNEL_ID=123456789012345681
```

---

## Step 7: Get Your User ID

1. In Discord, right-click on your name (anywhere)
2. Click **Copy User ID**
3. This is your `ALLOWED_USER_ID`

**Example:**
```
ALLOWED_USER_ID=987654321098765432
```

**In your .env:**
```
ALLOWED_USER_ID=987654321098765432
```

This ensures only YOU can use the `/task` command (safety gate).

---

## Troubleshooting

### "I don't see Copy Server ID option"

Make sure **Developer Mode** is enabled:
1. Discord Settings → **Advanced**
2. Toggle **Developer Mode** ON
3. Now right-click options will show IDs

### "Bot is in server but not responding"

Check permissions:
1. Server Settings → **Roles**
2. Find your bot role
3. Make sure it has:
   - ✅ Send Messages
   - ✅ Use Application Commands (Slash Commands)
   - ✅ Embed Links
   - ✅ Attach Files

### "Slash commands not showing up"

- Bot needs `applications.commands` scope
- Re-generate OAuth2 URL with correct scopes
- Re-invite bot to server

### "Token is invalid"

- Make sure you copied entire token (no spaces)
- Make sure you copied from **Bot** section, not **OAuth2**
- If unsure, regenerate token:
  - Developer Portal → Bot → Click **Regenerate** under TOKEN
  - Copy new token

---

## Quick Copy-Paste Template

Once you have all IDs, fill this in:

```
# Discord bot token (from Developer Portal → Bot)
DISCORD_TOKEN=YOUR_ACTUAL_BOT_TOKEN_HERE

# Your Discord server ID (right-click server → Copy Server ID)
DISCORD_GUILD_ID=YOUR_GUILD_ID_HERE

# Channel IDs (right-click each channel → Copy Channel ID)
DISCORD_GENERAL_CHANNEL_ID=YOUR_GENERAL_CHANNEL_ID
DISCORD_BUILDS_CHANNEL_ID=YOUR_BUILDS_CHANNEL_ID
DISCORD_DEPLOYS_CHANNEL_ID=YOUR_DEPLOYS_CHANNEL_ID

# Your Discord user ID (right-click your name → Copy User ID)
ALLOWED_USER_ID=YOUR_USER_ID_HERE
```

---

## Test Discord Connection

Once you have credentials and bot is in your server:

```bash
cd agentic

# Copy and fill .env
cp .env.template .env
nano .env  # Add all Discord IDs + token

# Create Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run bot (this starts it, watch for login message)
python3 main.py

# In another terminal, test in Discord:
# /task brand:nacpac request:Test connection
```

Expected:
- Bot shows approval buttons
- You can click ✅ Approve
- Bot responds with success message

---

## Visual Walkthrough

### Discord Server Setup

```
Your Discord Server
├── #general ← Bot posts here
├── #builds ← Build logs posted here
├── #deploys ← Deploy logs posted here
└── Bot role with permissions
    ├── ✅ Send Messages
    ├── ✅ Use Slash Commands
    ├── ✅ Embed Links
    └── ✅ Attach Files
```

### Developer Portal

```
Discord Developer Portal
├── Applications
│   └── [jico-agentic]
│       ├── Bot ← Get TOKEN here
│       ├── OAuth2
│       │   └── URL Generator ← Generate invite URL
│       └── Integration
```

---

## Summary

| Credential | Format | Length | Where |
|-----------|--------|--------|-------|
| DISCORD_TOKEN | Long string | 50+ chars | Developer Portal → Bot |
| DISCORD_GUILD_ID | Numbers | 18 digits | Right-click server |
| DISCORD_GENERAL_CHANNEL_ID | Numbers | 18 digits | Right-click #general |
| DISCORD_BUILDS_CHANNEL_ID | Numbers | 18 digits | Right-click #builds |
| DISCORD_DEPLOYS_CHANNEL_ID | Numbers | 18 digits | Right-click #deploys |
| ALLOWED_USER_ID | Numbers | 18 digits | Right-click your name |

---

## Next Steps

1. ✅ Get all 6 credentials above
2. ✅ Add to `.env` file
3. ✅ Continue with Supabase setup (see SUPABASE_CREDENTIALS_GUIDE.md)
4. ✅ Run deployment script

You're almost there! 🎉
