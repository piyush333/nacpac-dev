# Jico Agentic System - Deployment Guide

## Prerequisites

### On Your Local Machine
- SSH key: `ssh-key-2026-07-02.key` (in the current directory)
- Access to Oracle Cloud VM: `144.24.129.201`

### On the Oracle VM
- Ubuntu 20.04+ with Python 3.11+
- Git access to the repository

## Quick Deploy

From the root of this repository, run:

```bash
./DEPLOY_TO_ORACLE.sh
```

This script will:
1. Connect to the Oracle VM via SSH
2. Install system dependencies
3. Clone/update the repository
4. Create a Python virtual environment
5. Install all Python dependencies
6. Upload the `.env` file with credentials
7. Test the Supabase connection
8. Install and start the systemd service
9. Show recent logs

## Manual Deployment

### 1. SSH into the Oracle VM

```bash
ssh -i ssh-key-2026-07-02.key ubuntu@144.24.129.201
```

### 2. Clone the Repository

```bash
git clone -b claude/agentic-system-org-j9gvae https://github.com/piyush333/nacpac-dev.git ~/nacpac-dev
cd ~/nacpac-dev/agentic
```

### 3. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Configure Credentials

Copy your `.env` file to the server (from your local machine):

```bash
scp -i ssh-key-2026-07-02.key agentic/.env ubuntu@144.24.129.201:/home/ubuntu/nacpac-dev/agentic/.env
```

### 5. Test the Setup

```bash
source venv/bin/activate
python3 -c "
from config import validate_config
from memory import memory
validate_config()
print('✅ Config validated')
print('✅ Memory client ready')
"
```

### 6. Install as a Systemd Service

```bash
sudo cp systemd/jico-agentic.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jico-agentic
sudo systemctl start jico-agentic
```

### 7. Verify the Service is Running

```bash
sudo systemctl status jico-agentic
sudo journalctl -u jico-agentic -f
```

## Troubleshooting

### Issue: Service fails to start
**Check logs:**
```bash
sudo journalctl -u jico-agentic -n 50 --no-pager
```

**Common causes:**
- `.env` file missing or has wrong permissions
- Python venv not properly set up
- Supabase credentials invalid

### Issue: Supabase connection fails
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
2. Ensure the Supabase project schema has been initialized:
   ```bash
   # Run schema.sql in Supabase SQL editor
   ```
3. Check Supabase project hasn't disabled the Anon API key

### Issue: Discord bot doesn't respond to commands
1. Verify `DISCORD_TOKEN` is valid
2. Verify `DISCORD_GUILD_ID` is correct
3. Check the bot has permissions in Discord
4. Ensure Discord slash commands have synced:
   ```bash
   # The bot syncs automatically on startup, check logs
   sudo journalctl -u jico-agentic -f | grep -i "synced"
   ```

## Testing the Bot

### From Discord

1. Go to your Discord server
2. Type `/task brand:nacpac request:Show status`
3. The bot should respond with an approval view

### From the Command Line

To test the config and memory system:

```bash
ssh -i ssh-key-2026-07-02.key ubuntu@144.24.129.201 << 'EOF'
cd ~/nacpac-dev/agentic
source venv/bin/activate
python3 << 'PYEOF'
from memory import memory
state = memory.get_brand_state('nacpac')
if state:
    print(f"✅ Connected to Supabase")
    print(f"   NacPac branch: {state.get('current_branch')}")
else:
    print("⚠️  Could not fetch brand state")
PYEOF
EOF
```

## Service Management

### View logs (live)
```bash
sudo journalctl -u jico-agentic -f
```

### View recent logs
```bash
sudo journalctl -u jico-agentic -n 100 --no-pager
```

### Restart the service
```bash
sudo systemctl restart jico-agentic
```

### Stop the service
```bash
sudo systemctl stop jico-agentic
```

### Check service status
```bash
sudo systemctl status jico-agentic
```

## Environment Variables

The `.env` file should contain:

```
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Supabase
SUPABASE_URL=https://xsjxyauozqpkdkwbzsda.supabase.co
SUPABASE_KEY=eyJhbGc...

# Discord
DISCORD_TOKEN=MTUyMT...
DISCORD_GUILD_ID=1521215133576073429
ALLOWED_USER_ID=1521214461963407430
DISCORD_GENERAL_CHANNEL_ID=1522297561073975456
DISCORD_NACPAC_DEV_CHANNEL_ID=1522297624466690239
DISCORD_JICO_DEV_CHANNEL_ID=1522297657853350080
DISCORD_LOGS_CHANNEL_ID=1522297768452952094
DISCORD_REPORTS_CHANNEL_ID=1522297790686957690

# Repos
NACPAC_REPO_PATH=/home/ubuntu/nacpac-workspace-main
JICO_REPO_PATH=/home/ubuntu/nacpac-workspace-main

# Build config
EAS_BUILD_PROFILE=preview
FIREBASE_PROJECT=nacpac-production-4134a

# Cost limits
DAILY_CAP_USD=10.0
MONTHLY_CAP_USD=50.0

# System
SYSTEM_USER=ubuntu
ORACLE_VM_IP=144.24.129.201
```

## Next Steps

- Configure additional agents (NacPac Dev, Jico Life Dev)
- Set up GitHub integration for automated builds
- Configure R2, Google Drive, and other cloud storage
- Create task workflows for different brands

## Support

For issues or questions, check:
- Bot logs: `sudo journalctl -u jico-agentic -f`
- Supabase status: https://supabase.com/
- Discord bot permissions: Check the server settings
