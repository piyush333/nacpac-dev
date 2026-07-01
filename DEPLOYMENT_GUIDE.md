# Complete Deployment Guide

This guide explains how to deploy the Nacpac Discord Bot system to Oracle Cloud for 24/7 autonomous operation.

## Overview

The system consists of:
1. **Discord Bot** (`discord_manager.py`) - Handles user requests in #general channel
2. **Nacpac Manager** (`nacpac_manager.py`) - Orchestrates builds (APK via EAS, EXE via npm)
3. **Build Backup** (`build_backup.py`) - Tracks and allows rollback to last 2 builds
4. **Google Drive Backup** (`google_drive_backup.py`) - Auto-backups codebase after successful builds
5. **Systemd Service** - Auto-restarts bot on failure

## System Architecture

```
Discord User in #general
    ↓
Discord Bot (discord_manager.py)
    ├─ Greeting recognition
    ├─ Task screening (keyword-based, no API)
    ├─ Approval buttons [✅ Yes] [❌ No]
    ├─ Optional preview generation [✅ Generate] [⏭️ Skip]
    ├─ Build type selection [📱 APK] [🖥️ EXE] [📦 BOTH]
    └─ Queue task to Nacpac Manager
        ↓
Nacpac Manager (nacpac_manager.py)
    ├─ APK Build (if mobile exists)
    │   └─ eas build --platform android --profile preview
    ├─ EXE Build (if npm exists)
    │   └─ npm run build in desktop/
    ├─ Upload to Cloudflare R2
    ├─ Save to Build Backup (keep last 2)
    └─ Auto-backup to Google Drive
        ↓
Download Links Posted to #nacpac-dev
```

## Pre-Deployment Checklist

- [ ] All credentials gathered (see CREDENTIALS_REFERENCE.md)
- [ ] Google Drive OAuth credentials obtained
- [ ] EAS token acquired and verified
- [ ] Oracle Cloud instance running and accessible via SSH
- [ ] Nacpac codebase cloned (mobile + desktop folders ready)
- [ ] Git branch `claude/new-session-dxi5li` pulled to local machine

## Deployment Steps

### Step 1: Prepare Credentials

Read `CREDENTIALS_REFERENCE.md` and gather:
- Discord Token & Guild ID
- Anthropic API Key
- Cloudflare R2 (Account ID, Access Key, Secret Key, Endpoint)
- Google Drive OAuth JSON
- Expo EAS Token
- Telegram Bot Token (optional for future use)

### Step 2: SSH into Oracle Cloud Instance

```bash
ssh -i /path/to/oracle_key.key opc@129.154.42.154
```

### Step 3: Clone Repository

```bash
cd ~
git clone -b claude/new-session-dxi5li https://github.com/piyush333/nacpac-dev.git
cd nacpac-dev
```

### Step 4: Install Dependencies

```bash
# System dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip nodejs npm git

# Python dependencies
pip3 install -r jico-system/requirements.txt
# If no requirements.txt exists, install:
pip3 install discord.py python-dotenv boto3 google-auth-oauthlib google-api-python-client

# Node dependencies
npm install -g eas-cli
cd nacpac-workspace-main/mobile && npm install && cd ../../
cd nacpac-workspace-main/desktop && npm install && cd ../../
```

### Step 5: Create Environment Variables

Create `~/.env`:

```bash
nano ~/.env
```

Paste and fill in (see ENVIRONMENT_VARIABLES_SETUP.md for all variables):

```
DISCORD_TOKEN=<your-token>
DISCORD_GUILD_ID=<your-guild-id>
ANTHROPIC_API_KEY=<your-api-key>
R2_ACCOUNT_ID=<your-account-id>
R2_ACCESS_KEY=<your-access-key>
R2_SECRET_KEY=<your-secret-key>
R2_ENDPOINT=<your-endpoint>
NACPAC_R2_BUCKET=nacpac-workspace
NACPAC_R2_URL=<your-r2-url>
GOOGLE_CREDENTIALS_JSON=<your-google-json>
EAS_TOKEN=<your-eas-token>
NACPAC_DIR=/home/opc/nacpac-dev/nacpac-workspace-main
MOBILE_DIR=/home/opc/nacpac-dev/nacpac-workspace-main/mobile
DESKTOP_DIR=/home/opc/nacpac-dev/nacpac-workspace-main/desktop
LOG_LEVEL=INFO
```

### Step 6: Load Environment Variables

```bash
cat >> ~/.bashrc << 'EOF'
if [ -f ~/.env ]; then
  export $(cat ~/.env | grep -v '^#' | xargs)
fi
EOF

source ~/.bashrc

# Verify
echo $DISCORD_TOKEN  # Should not be empty
```

### Step 7: Test Discord Connection

```bash
cd ~/nacpac-dev/jico-system
python3 -c "
import os
import discord

token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Bot connected as {client.user}')
    await client.close()

try:
    client.run(token)
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

### Step 8: Set Up Systemd Service

Create `/etc/systemd/system/jico-manager.service`:

```bash
sudo tee /etc/systemd/system/jico-manager.service > /dev/null << 'EOF'
[Unit]
Description=JICO Discord Manager Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/nacpac-dev/jico-system
ExecStart=/usr/bin/python3 /home/opc/nacpac-dev/jico-system/discord_manager.py

# Load environment variables from ~/.env
EnvironmentFile=/home/opc/.env

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=jico-manager

# Auto-restart
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable jico-manager
sudo systemctl start jico-manager
```

### Step 9: Verify Service is Running

```bash
# Check status
sudo systemctl status jico-manager

# View logs (live)
sudo journalctl -u jico-manager -f

# Check for errors
sudo journalctl -u jico-manager -n 100
```

### Step 10: Test Discord Workflow

1. Go to your Discord server
2. In #general, type: `Hi piyush, what is the agenda today!`
3. Bot should respond with greeting
4. Try requesting a build: `dark mode feature for nacpac app`
5. Follow the button workflow:
   - Click [✅ Yes] to approve
   - Click [✅ Generate Preview] or [⏭️ Skip Preview]
   - Select [📱 APK] or [🖥️ EXE] or [📦 BOTH]
   - Check #nacpac-dev for download links after build completes

## Post-Deployment Operations

### Viewing Logs

```bash
# Real-time logs
sudo journalctl -u jico-manager -f

# Last 100 lines
sudo journalctl -u jico-manager -n 100

# Today's logs
sudo journalctl -u jico-manager --since today

# Search for errors
sudo journalctl -u jico-manager -p err
```

### Restarting Service

```bash
sudo systemctl restart jico-manager
sudo systemctl status jico-manager
```

### Updating Code

If you push updates to the git branch:

```bash
cd ~/nacpac-dev
git fetch origin claude/new-session-dxi5li
git reset --hard origin/claude/new-session-dxi5li

# Restart bot
sudo systemctl restart jico-manager
```

### Building Manually (for testing)

```bash
cd ~/nacpac-dev/jico-system
export $(cat ~/.env | grep -v '^#' | xargs)

# Build APK
eas build --platform android --profile preview --non-interactive

# Build EXE
cd ../nacpac-workspace-main/desktop
npm run build
```

### Checking Google Drive Backups

```bash
# List all backups
python3 -c "
import sys
sys.path.insert(0, '/home/opc/nacpac-dev/jico-system')
from google_drive_backup import GoogleDriveBackup
import os
os.environ['GOOGLE_CREDENTIALS_JSON'] = os.getenv('GOOGLE_CREDENTIALS_JSON')

backup = GoogleDriveBackup()
for file in backup.list_backups():
    print(f\"{file['name']} - {file['createdTime']}\")
"
```

### Rollback to Previous Build

```bash
# In Discord #general, type:
!rollback apk
# or
!rollback exe
# or
!rollback both
```

## Monitoring & Maintenance

### Daily Checks

```bash
# Bot is running
sudo systemctl status jico-manager

# No error logs
sudo journalctl -u jico-manager -p err --since today

# Google Drive has recent backups
python3 check_backups.py

# R2 has latest builds
aws s3 ls --endpoint-url $R2_ENDPOINT s3://nacpac-workspace/
```

### Weekly Maintenance

- Check Discord logs for any errors
- Verify Google Drive backups are happening
- Rotate API keys if needed
- Review cost tracking (should stay within $10/day and $50/month)

### Monthly Tasks

- Update dependencies: `pip3 install -U discord.py boto3 google-auth-oauthlib`
- Review and rotate Discord token
- Check GitHub secret scanning alerts
- Backup configuration files

## Troubleshooting

### Bot won't start

```bash
# Check for syntax errors
python3 -m py_compile jico-system/discord_manager.py

# Check environment variables
env | grep DISCORD

# Check logs
sudo journalctl -u jico-manager -n 50
```

### Builds not uploading to R2

```bash
# Test R2 connectivity
aws s3 ls --endpoint-url $R2_ENDPOINT

# Check credentials
echo $R2_ACCESS_KEY
echo $R2_SECRET_KEY
```

### Google Drive backup failing

```bash
# Verify credentials
echo $GOOGLE_CREDENTIALS_JSON | jq .

# Check folder exists
curl -H "Authorization: Bearer $GOOGLE_TOKEN" \
  https://www.googleapis.com/drive/v3/files/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO
```

### Discord bot not responding

```bash
# Check bot is in guild
curl -H "Authorization: Bot $DISCORD_TOKEN" \
  https://discord.com/api/v10/guilds/$DISCORD_GUILD_ID

# Check message intents are enabled
# Admin panel → Integrations → Bot → MESSAGE CONTENT INTENT
```

## Security Notes

1. **Never commit credentials to git** - Use environment variables only
2. **Rotate tokens regularly** - Especially Discord and API keys
3. **Monitor GitHub secret scanning** - Address any alerts immediately
4. **Restrict Oracle Cloud firewall** - Only allow SSH and outbound HTTPS
5. **Use SSH keys, not passwords** - 4096-bit RSA minimum
6. **Enable systemd security hardening** - See systemd docs
7. **Monitor API usage** - Stay within cost limits ($50/month, $10/day)

## Cost Optimization

The system is designed to minimize API calls:
- Discord API: **Free** (included in discord.py)
- Anthropic Claude Haiku: **~$0.00001 per 1K tokens** (optional preview generation only)
- Cloudflare R2: **~$0.015 per GB storage** (builds kept in 2-build history)
- Google Drive: **Free** (15GB free tier)
- EAS/npm: **Free** (local builds with your tokens)

Total estimated cost: **~$5-10/month** for build storage

## Support & Resources

- Discord.py docs: https://discordpy.readthedocs.io/
- Anthropic API: https://docs.anthropic.com/
- EAS CLI: https://docs.expo.dev/eas/
- Cloudflare R2: https://developers.cloudflare.com/r2/
- Google Drive API: https://developers.google.com/drive/api

## Next Steps

1. ✅ Gather all credentials (CREDENTIALS_REFERENCE.md)
2. ✅ Deploy to Oracle Cloud (this guide)
3. ✅ Test Discord workflow
4. ✅ Monitor logs for 24 hours
5. ✅ Set up alerts/monitoring if needed
6. ✅ Document any custom extensions

---

**Last Updated:** July 1, 2026
**Deployment Status:** Ready for Oracle Cloud
**Estimated Deployment Time:** 30-45 minutes
