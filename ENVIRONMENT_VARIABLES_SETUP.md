# Environment Variables Setup Guide

This guide explains how to set up all necessary environment variables for the Nacpac Discord Bot system across different deployment contexts.

## All Required Environment Variables

### Discord Configuration
```
DISCORD_TOKEN=<your-discord-bot-token>
DISCORD_GUILD_ID=<your-guild-id>
DISCORD_LOGS_CHANNEL=logs
DISCORD_REPORTS_CHANNEL=reports
```

### Telegram Bot Configuration
```
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
ALLOWED_USER_ID=<your-user-id>
```

### Anthropic (Claude API - Haiku for previews)
```
ANTHROPIC_API_KEY=<your-anthropic-api-key>
```

### Cloudflare R2 Storage (for APK/EXE uploads)
```
R2_ACCOUNT_ID=<your-r2-account-id>
R2_ACCESS_KEY=<your-r2-access-key>
R2_SECRET_KEY=<your-r2-secret-key>
R2_ENDPOINT=<your-r2-endpoint-url>
NACPAC_R2_BUCKET=nacpac-workspace
NACPAC_R2_URL=<your-r2-public-url>
JICO_R2_BUCKET=jico-workspace
JICO_R2_URL=<your-jico-r2-public-url>
```

### Google Drive Backup (NEW - credentials from environment)
```
GOOGLE_CREDENTIALS_JSON=<paste-your-google-oauth-credentials-json-here>
```

See `GOOGLE_DRIVE_SETUP.md` for how to obtain these credentials.

### EAS CLI Token (for APK builds)
```
EAS_TOKEN=<your-expo-eas-token>
```

### Local File Paths (on deployment machine)
```
NACPAC_DIR=/home/opc/nacpac-workspace-main
MOBILE_DIR=/home/opc/nacpac-workspace-main/mobile
DESKTOP_DIR=/home/opc/nacpac-workspace-main/desktop
JICO_DIR=/home/opc/jico-workspace-main
```

### Oracle Cloud VM Configuration (for remote deployment)
```
ORACLE_VM_IP=129.154.42.154
ORACLE_VM_USER=opc
ORACLE_SSH_KEY_PATH=/home/opc/jico-system/ssh/oracle_key.key
AGENT_ENDPOINT=http://129.154.42.154:8000
AGENT_TOKEN=<your-agent-token>
```

### Logging
```
LOG_LEVEL=INFO
```

---

## Setup Methods by Context

### Method 1: Bash Profile (.bashrc or .bash_profile)

Add to `~/.bashrc` or `~/.bash_profile`:

```bash
# Discord Configuration
export DISCORD_TOKEN="<your-discord-bot-token>"
export DISCORD_GUILD_ID="<your-guild-id>"
export DISCORD_LOGS_CHANNEL="logs"
export DISCORD_REPORTS_CHANNEL="reports"

# Telegram Bot Configuration
export TELEGRAM_BOT_TOKEN="<your-telegram-bot-token>"
export ALLOWED_USER_ID="<your-user-id>"

# Anthropic (Claude API)
export ANTHROPIC_API_KEY="<your-anthropic-api-key>"

# Cloudflare R2
export R2_ACCOUNT_ID="<your-r2-account-id>"
export R2_ACCESS_KEY="<your-r2-access-key>"
export R2_SECRET_KEY="<your-r2-secret-key>"
export R2_ENDPOINT="<your-r2-endpoint-url>"
export NACPAC_R2_BUCKET="nacpac-workspace"
export NACPAC_R2_URL="<your-r2-public-url>"
export JICO_R2_BUCKET="jico-workspace"
export JICO_R2_URL="<your-jico-r2-public-url>"

# Google Drive Backup
export GOOGLE_CREDENTIALS_JSON='<your-google-oauth-credentials-json>'

# EAS Token
export EAS_TOKEN="<your-eas-token>"

# File Paths
export NACPAC_DIR="/home/opc/nacpac-workspace-main"
export MOBILE_DIR="/home/opc/nacpac-workspace-main/mobile"
export DESKTOP_DIR="/home/opc/nacpac-workspace-main/desktop"
export JICO_DIR="/home/opc/jico-workspace-main"

# Oracle Cloud
export ORACLE_VM_IP="129.154.42.154"
export ORACLE_VM_USER="opc"
export ORACLE_SSH_KEY_PATH="/home/opc/jico-system/ssh/oracle_key.key"
export AGENT_ENDPOINT="http://129.154.42.154:8000"
export AGENT_TOKEN="<your-agent-token>"

# Logging
export LOG_LEVEL="INFO"
```

Then reload your shell:
```bash
source ~/.bashrc
# or
source ~/.bash_profile
```

### Method 2: .env File in Project Directory (Local Development)

Create or update `.env` in the project root:

```
# Discord Configuration
DISCORD_TOKEN=<your-discord-bot-token>
DISCORD_GUILD_ID=<your-guild-id>
DISCORD_LOGS_CHANNEL=logs
DISCORD_REPORTS_CHANNEL=reports

# Telegram Bot
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
ALLOWED_USER_ID=<your-user-id>

# Anthropic
ANTHROPIC_API_KEY=<your-anthropic-api-key>

# Cloudflare R2
R2_ACCOUNT_ID=<your-r2-account-id>
R2_ACCESS_KEY=<your-r2-access-key>
R2_SECRET_KEY=<your-r2-secret-key>
R2_ENDPOINT=<your-r2-endpoint-url>
NACPAC_R2_BUCKET=nacpac-workspace
NACPAC_R2_URL=<your-r2-public-url>
JICO_R2_BUCKET=jico-workspace
JICO_R2_URL=<your-jico-r2-public-url>

# Google Drive
GOOGLE_CREDENTIALS_JSON=<your-google-oauth-credentials-json>

# EAS
EAS_TOKEN=<your-eas-token>

# Paths
NACPAC_DIR=/home/opc/nacpac-workspace-main
MOBILE_DIR=/home/opc/nacpac-workspace-main/mobile
DESKTOP_DIR=/home/opc/nacpac-workspace-main/desktop
JICO_DIR=/home/opc/jico-workspace-main

# Oracle Cloud
ORACLE_VM_IP=129.154.42.154
ORACLE_VM_USER=opc
ORACLE_SSH_KEY_PATH=/home/opc/jico-system/ssh/oracle_key.key
AGENT_ENDPOINT=http://129.154.42.154:8000
AGENT_TOKEN=<your-agent-token>

# Logging
LOG_LEVEL=INFO
```

Load in Python with:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

### Method 3: Systemd Service (Production on Oracle Cloud)

Create `/etc/systemd/system/jico-manager.service`:

```ini
[Unit]
Description=JICO Discord Manager Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/jico-system
ExecStart=/usr/bin/python3 /home/opc/jico-system/discord_manager.py

# Environment Variables (one per line)
Environment="DISCORD_TOKEN=<your-discord-bot-token>"
Environment="DISCORD_GUILD_ID=<your-guild-id>"
Environment="DISCORD_LOGS_CHANNEL=logs"
Environment="DISCORD_REPORTS_CHANNEL=reports"
Environment="TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>"
Environment="ALLOWED_USER_ID=<your-user-id>"
Environment="ANTHROPIC_API_KEY=<your-anthropic-api-key>"
Environment="R2_ACCOUNT_ID=<your-r2-account-id>"
Environment="R2_ACCESS_KEY=<your-r2-access-key>"
Environment="R2_SECRET_KEY=<your-r2-secret-key>"
Environment="R2_ENDPOINT=<your-r2-endpoint-url>"
Environment="NACPAC_R2_BUCKET=nacpac-workspace"
Environment="NACPAC_R2_URL=<your-r2-public-url>"
Environment="JICO_R2_BUCKET=jico-workspace"
Environment="JICO_R2_URL=<your-jico-r2-public-url>"
Environment="GOOGLE_CREDENTIALS_JSON=<your-google-oauth-credentials-json>"
Environment="EAS_TOKEN=<your-eas-token>"
Environment="NACPAC_DIR=/home/opc/nacpac-workspace-main"
Environment="MOBILE_DIR=/home/opc/nacpac-workspace-main/mobile"
Environment="DESKTOP_DIR=/home/opc/nacpac-workspace-main/desktop"
Environment="JICO_DIR=/home/opc/jico-workspace-main"
Environment="ORACLE_VM_IP=129.154.42.154"
Environment="ORACLE_VM_USER=opc"
Environment="AGENT_ENDPOINT=http://129.154.42.154:8000"
Environment="AGENT_TOKEN=<your-agent-token>"
Environment="LOG_LEVEL=INFO"

Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=jico-manager

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable jico-manager
sudo systemctl start jico-manager

# Check status
sudo systemctl status jico-manager

# View logs
sudo journalctl -u jico-manager -f
```

### Method 4: Docker Deployment

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  jico-manager:
    build: .
    container_name: jico-manager
    environment:
      - DISCORD_TOKEN=<your-discord-bot-token>
      - DISCORD_GUILD_ID=<your-guild-id>
      - DISCORD_LOGS_CHANNEL=logs
      - DISCORD_REPORTS_CHANNEL=reports
      - TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
      - ALLOWED_USER_ID=<your-user-id>
      - ANTHROPIC_API_KEY=<your-anthropic-api-key>
      - R2_ACCOUNT_ID=<your-r2-account-id>
      - R2_ACCESS_KEY=<your-r2-access-key>
      - R2_SECRET_KEY=<your-r2-secret-key>
      - R2_ENDPOINT=<your-r2-endpoint-url>
      - NACPAC_R2_BUCKET=nacpac-workspace
      - NACPAC_R2_URL=<your-r2-public-url>
      - JICO_R2_BUCKET=jico-workspace
      - JICO_R2_URL=<your-jico-r2-public-url>
      - GOOGLE_CREDENTIALS_JSON=<your-google-oauth-credentials-json>
      - EAS_TOKEN=<your-eas-token>
      - NACPAC_DIR=/home/opc/nacpac-workspace-main
      - MOBILE_DIR=/home/opc/nacpac-workspace-main/mobile
      - DESKTOP_DIR=/home/opc/nacpac-workspace-main/desktop
      - LOG_LEVEL=INFO
    volumes:
      - /home/opc/nacpac-workspace-main:/home/opc/nacpac-workspace-main
      - /home/opc/jico-workspace-main:/home/opc/jico-workspace-main
    restart: always
```

---

## File Locations Summary

| Purpose | Location | Notes |
|---------|----------|-------|
| Discord Bot Code | `/home/opc/jico-system/discord_manager.py` | Main bot entry point |
| Nacpac Manager | `/home/opc/jico-system/nacpac_manager.py` | Build orchestration |
| Build Backup System | `/home/opc/jico-system/build_backup.py` | Tracks last 2 builds |
| Google Drive Backup | `/home/opc/jico-system/google_drive_backup.py` | Auto-backup to Drive |
| Bot Logs | `/home/opc/jico-system/logs/` | Bot activity logs |
| Google Token Cache | `/home/opc/jico-system/.google_token.pickle` | OAuth token (auto-generated) |
| EAS Token | Environment variable `EAS_TOKEN` | Never commit to git |
| SSH Key (Oracle) | `/home/user/jico-system/ssh/oracle_key.key` | For remote access |
| Nacpac App | `/home/opc/nacpac-workspace-main/` | Clone of production app |
| Mobile App | `/home/opc/nacpac-workspace-main/mobile/` | Expo React Native |
| Desktop App | `/home/opc/nacpac-workspace-main/desktop/` | Electron app |

---

## Security Best Practices

✅ **DO:**
- Load credentials from environment variables
- Use systemd service for auto-restart
- Rotate tokens periodically
- Use `.gitignore` for local credential files
- Use `sudo systemctl show -p Environment jico-manager` to verify secrets are loaded

❌ **DON'T:**
- Commit secrets to git (even in history)
- Hardcode credentials in source code
- Share `.env` files in chat or email
- Use weak SSH keys
- Leave console access unprotected

---

## Verification Commands

```bash
# Check environment variables are loaded
printenv | grep DISCORD_TOKEN

# For systemd service
sudo systemctl show -p Environment jico-manager | grep DISCORD

# Check bot is running
sudo systemctl status jico-manager

# View recent logs
sudo journalctl -u jico-manager -n 50

# Test Discord bot connection
python3 -c "import os; print('Discord Token:', 'SET' if os.getenv('DISCORD_TOKEN') else 'NOT SET')"
```

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'dotenv'"**
```bash
pip install python-dotenv
```

**"Discord bot not responding"**
1. Check token is set: `echo $DISCORD_TOKEN`
2. Check bot is running: `sudo systemctl status jico-manager`
3. Check for errors: `sudo journalctl -u jico-manager -e`

**"Google Drive backup not working"**
1. Verify `GOOGLE_CREDENTIALS_JSON` is set
2. Check for permission to folder ID: `1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO`
3. Install dependencies: `pip install google-auth-oauthlib google-api-python-client`

**"R2 upload failing"**
1. Verify all R2_* variables are set correctly
2. Check bucket name matches: `nacpac-workspace`
3. Test connectivity: `aws s3 ls --endpoint-url $R2_ENDPOINT`
