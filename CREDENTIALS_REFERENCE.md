# Credentials Reference Guide

This guide shows where each credential comes from and where to put it.

## Credential Sources & Setup

### 1. Discord Bot Token
**Where to get it:** Discord Developer Portal
- https://discord.com/developers/applications
- Create application → Bot → Copy Token
- Give bot permissions: MESSAGE_CONTENT, SEND_MESSAGES, MANAGE_CHANNELS

**Where to put it:**
```bash
export DISCORD_TOKEN="your-token-here"
```

### 2. Discord Guild ID
**Where to get it:** Your Discord Server
- Enable Developer Mode (User Settings → Advanced → Developer Mode)
- Right-click server → Copy Server ID

**Where to put it:**
```bash
export DISCORD_GUILD_ID="your-guild-id"
```

### 3. Anthropic API Key
**Where to get it:** Anthropic Console
- https://console.anthropic.com/
- Create API key in account settings
- Keep it secret! Used for Claude Haiku preview generation

**Where to put it:**
```bash
export ANTHROPIC_API_KEY="sk-ant-api..."
```

### 4. Cloudflare R2 Credentials
**Where to get it:** Cloudflare Dashboard
- R2 Settings → API Tokens → Create Token
- Get: Account ID, Access Key, Secret Key, Endpoint
- Used for uploading APK/EXE builds

**Where to put it:**
```bash
export R2_ACCOUNT_ID="your-account-id"
export R2_ACCESS_KEY="your-access-key"
export R2_SECRET_KEY="your-secret-key"
export R2_ENDPOINT="https://your-account-id.r2.cloudflarestorage.com"
```

### 5. Google Drive OAuth Credentials
**Where to get it:** Google Cloud Console
- https://console.cloud.google.com/
- Create project "nacpac-backup"
- APIs & Services → OAuth consent screen
- APIs & Services → Credentials → Create OAuth 2.0 credential (Desktop app)
- Download JSON file

**The JSON looks like:**
```json
{
  "installed": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "client_secret": "your-client-secret",
    "project_id": "nacpac-backup",
    ...
  }
}
```

**Where to put it:**
```bash
# Convert to single line (copy from google_credentials.json)
export GOOGLE_CREDENTIALS_JSON='{"installed":{...}}'
```

**Backup Folder ID:** `1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO`
- All backups go to this Google Drive folder
- Share with your Google account to view backups

### 6. Expo EAS Token
**Where to get it:** Expo Dashboard
- https://expo.dev/
- Create account / login
- Profile → Access Tokens → Create
- Used for building APK with EAS

**Where to put it:**
```bash
export EAS_TOKEN="your-eas-token"
```

### 7. Telegram Bot Token
**Where to get it:** Telegram BotFather
- Message @BotFather on Telegram
- /newbot → Follow prompts
- Copy the token provided

**Where to put it:**
```bash
export TELEGRAM_BOT_TOKEN="your-telegram-token"
```

### 8. Oracle Cloud Credentials
**Location:** Oracle Cloud Instance
- **IP:** 129.154.42.154
- **User:** opc
- **SSH Key:** `/home/opc/jico-system/ssh/oracle_key.key`

**Where to put it:**
```bash
export ORACLE_VM_IP="129.154.42.154"
export ORACLE_VM_USER="opc"
export ORACLE_SSH_KEY_PATH="/path/to/oracle_key.key"
export AGENT_TOKEN="your-agent-token"
```

---

## Step-by-Step Setup for Oracle Cloud Deployment

### Step 1: SSH into Oracle Instance
```bash
ssh -i /path/to/oracle_key.key opc@129.154.42.154
```

### Step 2: Create .env file on Oracle Server
```bash
nano ~/.env
# or
vim ~/.env
```

Paste all your credentials (use placeholders from ENVIRONMENT_VARIABLES_SETUP.md)

### Step 3: Load in ~/.bashrc
```bash
cat >> ~/.bashrc << 'EOF'
# Load environment variables
if [ -f ~/.env ]; then
  export $(cat ~/.env | grep -v '^#' | xargs)
fi
EOF

source ~/.bashrc
```

### Step 4: Verify Credentials Are Loaded
```bash
# Check each one
echo $DISCORD_TOKEN      # Should print your token
echo $ANTHROPIC_API_KEY  # Should print your key
echo $EAS_TOKEN         # Should print your token
```

### Step 5: Set Up Systemd Service
See "Systemd Service Setup" section in ENVIRONMENT_VARIABLES_SETUP.md

```bash
sudo nano /etc/systemd/system/jico-manager.service
# Paste the systemd config with your environment variables
```

### Step 6: Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable jico-manager
sudo systemctl start jico-manager
sudo systemctl status jico-manager
```

### Step 7: Monitor Logs
```bash
sudo journalctl -u jico-manager -f
```

---

## Security Checklist

- [ ] NEVER commit `.env` files to git
- [ ] NEVER share credentials in chat, email, or screenshots
- [ ] NEVER hardcode credentials in source files
- [ ] Rotate tokens periodically (especially Discord, Telegram, Anthropic)
- [ ] Use environment variables on production servers
- [ ] Use `.gitignore` to exclude credential files
- [ ] Review GitHub secret scanning alerts regularly
- [ ] Use strong SSH keys (4096-bit RSA minimum)
- [ ] Lock down Oracle Cloud firewall rules

---

## Troubleshooting

### Bot won't connect to Discord
```bash
# Check token is valid
curl -H "Authorization: Bot $DISCORD_TOKEN" https://discord.com/api/v10/users/@me

# Check guild ID
echo $DISCORD_GUILD_ID
```

### Builds won't upload to R2
```bash
# Test R2 connectivity
aws s3 ls --endpoint-url $R2_ENDPOINT

# Check R2 credentials
echo $R2_ACCOUNT_ID
echo $R2_ACCESS_KEY
```

### Google Drive backup not working
```bash
# Check credentials are loaded
echo $GOOGLE_CREDENTIALS_JSON | jq .

# Verify folder access
# Open in browser: https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO
```

### EAS build failing
```bash
# Check EAS token
echo $EAS_TOKEN

# Test EAS CLI
eas --version
eas account --whoami
```

---

## File Locations After Setup

```
Oracle Cloud (/home/opc/)
├── jico-system/
│   ├── discord_manager.py
│   ├── nacpac_manager.py
│   ├── google_drive_backup.py
│   ├── build_backup.py
│   ├── logs/
│   └── .google_token.pickle (auto-generated)
├── nacpac-workspace-main/
│   ├── mobile/ (Expo React Native)
│   ├── desktop/ (Electron)
│   └── build artifacts
└── jico-workspace-main/

Environment Variables
├── ~/.env (local development)
├── ~/.bashrc (bash shell)
└── systemd service (production)
```
