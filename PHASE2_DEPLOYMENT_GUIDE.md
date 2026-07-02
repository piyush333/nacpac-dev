# Phase 2 Deployment Guide: Supabase + Oracle VM

This guide walks through deploying the agentic system to a remote Oracle VM with Supabase as the persistent memory layer.

---

## Part 1: Supabase Setup (5 minutes)

### 1.1 Create Supabase Project

1. Go to https://supabase.com
2. Sign in or create account
3. Click "New Project"
4. Fill in:
   - **Project name:** `jico-agentic` (or your choice)
   - **Database password:** Strong password (save it)
   - **Region:** Closest to your location
5. Wait for project to be created (~2 minutes)

### 1.2 Create Tables

1. In Supabase dashboard, go to **SQL Editor**
2. Create a new query
3. Copy entire contents of `agentic/schema.sql`
4. Paste into SQL editor
5. Click **Run**
6. Verify tables are created (check **Tables** in sidebar)

Tables created:
- `brands` (NacPac, Jico Life)
- `tasks` (queue)
- `runs` (execution history)
- `brand_state` (current branch/commit)
- `builds` (build artifacts)
- `deployments` (deployment history)
- `decisions` (decision log)
- `knowledge` (org facts)
- `costs` (token usage)
- `sessions` (session tracking)
- `failed_tasks` (dead letter queue)

### 1.3 Get Credentials

1. In Supabase dashboard, go to **Settings → API**
2. Copy:
   - **Project URL** → `SUPABASE_URL` in `.env`
   - **Anon Key** (public) → `SUPABASE_KEY` in `.env`
3. Save these temporarily

---

## Part 2: Environment Configuration (5 minutes)

### 2.1 Fill in .env

```bash
cd /home/user/nacpac-dev/agentic
cp .env.template .env
nano .env  # Edit with your values
```

**Required values:**

```
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Supabase (from Part 1.3)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbG...

# Discord (from your bot setup)
DISCORD_TOKEN=MzA...
DISCORD_GUILD_ID=123456789
DISCORD_GENERAL_CHANNEL_ID=123456789
DISCORD_BUILDS_CHANNEL_ID=123456789
DISCORD_DEPLOYS_CHANNEL_ID=123456789
ALLOWED_USER_ID=your_discord_user_id

# Repos (should stay default, both in same workspace)
NACPAC_REPO_PATH=/home/ubuntu/nacpac-dev/nacpac-workspace-main
JICO_REPO_PATH=/home/ubuntu/nacpac-dev/nacpac-workspace-main

# Build
EAS_BUILD_PROFILE=preview
FIREBASE_PROJECT=nacpac-production-4134a

# R2 (Cloudflare)
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NACPAC=nacpac-builds
R2_BUCKET_JICO=jico-builds

# Google Drive
GOOGLE_DRIVE_CREDENTIALS_JSON=/home/ubuntu/google-creds.json
GOOGLE_DRIVE_FOLDER_ID=your_folder_id

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_REPO=piyush333/nacpac-dev

# Cost Caps
DAILY_CAP_USD=10.0
MONTHLY_CAP_USD=50.0

# System
SYSTEM_USER=ubuntu
ORACLE_VM_IP=68.233.110.235
SSH_KEY_PATH=/home/ubuntu/.ssh/oracle_key.key
```

### 2.2 Verify .env

```bash
# Check that all required vars are set
grep -E "ANTHROPIC_API_KEY|SUPABASE_URL|DISCORD_TOKEN" .env
```

---

## Part 3: Local Testing (5 minutes)

### 3.1 Install Dependencies

```bash
cd /home/user/nacpac-dev/agentic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Test Memory Client

```bash
python3 -c "
from memory import memory
from config import validate_config

validate_config()
print('✅ Config validated')

# Test Supabase connection
try:
    nacpac_state = memory.get_brand_state('nacpac')
    print(f'✅ Supabase connected: {nacpac_state}')
except Exception as e:
    print(f'❌ Supabase error: {e}')
"
```

Expected output:
```
✅ Config validated
✅ Supabase connected: {'id': '...', 'brand': 'nacpac', ...}
```

### 3.3 Test Cost Tracker

```bash
python3 -c "
from cost_tracker import cost_tracker

# Test cost calculation
cost = cost_tracker.calculate_cost('claude-3-5-haiku-20241022', 1000, 500)
print(f'Haiku cost (1000 in + 500 out): \${cost:.6f}')

cost = cost_tracker.calculate_cost('claude-3-5-sonnet-20241022', 1000, 500)
print(f'Sonnet cost (1000 in + 500 out): \${cost:.6f}')

# Test cost gating
can_afford, msg = cost_tracker.can_afford_call(5000)
print(f'Can afford call: {can_afford}')
"
```

---

## Part 4: Deploy to Oracle VM (15 minutes)

### 4.1 SSH to Oracle VM

```bash
ssh -i /path/to/oracle_key.key ubuntu@68.233.110.235
```

### 4.2 Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Verify
python3 --version  # Should be 3.11+
```

### 4.3 Clone Repository

```bash
cd /home/ubuntu
git clone https://github.com/piyush333/nacpac-dev.git
cd nacpac-dev/agentic
```

### 4.4 Create Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.5 Copy .env

**On your local machine:**
```bash
scp -i /path/to/oracle_key.key \
  /home/user/nacpac-dev/agentic/.env \
  ubuntu@68.233.110.235:/home/ubuntu/nacpac-dev/agentic/.env
```

**Or manually on VM:**
```bash
# On Oracle VM
nano /home/ubuntu/nacpac-dev/agentic/.env
# Paste contents from local .env
```

### 4.6 Test on VM

```bash
cd /home/ubuntu/nacpac-dev/agentic
source venv/bin/activate
python3 -c "
from memory import memory
from config import validate_config
validate_config()
print('✅ Config OK')
state = memory.get_brand_state('nacpac')
print(f'✅ Supabase connected: {state}')
"
```

### 4.7 Install Systemd Service

```bash
# Copy service file
sudo cp /home/ubuntu/nacpac-dev/agentic/systemd/jico-agentic.service /etc/systemd/system/

# Enable service (auto-start on boot)
sudo systemctl daemon-reload
sudo systemctl enable jico-agentic

# Start service
sudo systemctl start jico-agentic

# Verify
sudo systemctl status jico-agentic
```

Expected output:
```
● jico-agentic.service - Jico Agentic System
     Loaded: loaded (/etc/systemd/system/jico-agentic.service; enabled; vendor preset: enabled)
     Active: active (running) since ...
     ...
```

### 4.8 Monitor Logs

```bash
# Real-time logs
sudo journalctl -u jico-agentic -f

# Or check logfile
sudo tail -f /var/log/jico-agentic.log
```

---

## Part 5: Test Discord Bot (5 minutes)

### 5.1 Verify Bot is Running

```bash
# From VM
sudo systemctl status jico-agentic

# Should show: Active: active (running)
```

### 5.2 Test Discord Command

In your Discord guild, send:
```
/task brand:nacpac request:Show status
```

Expected flow:
1. Bot receives command
2. Orchestrator parses intent
3. Shows approval buttons: [✅ Approve] [❌ Reject]
4. Click ✅ Approve
5. Agent executes
6. Bot posts result: "✅ Task Completed..."

### 5.3 Check Memory

In Supabase dashboard:
1. Go to **Tables → tasks**
2. Should see your Discord command as a row
3. Status should be "completed"

---

## Part 6: Monitoring Setup (Optional)

### 6.1 Health Check Script

Create `/home/ubuntu/check-agentic.sh`:

```bash
#!/bin/bash
STATUS=$(sudo systemctl is-active jico-agentic)

if [ "$STATUS" != "active" ]; then
  echo "⚠️ Agentic system is $STATUS"
  # Optional: send Discord alert
else
  echo "✅ Agentic system is running"
fi
```

### 6.2 Cron Job for Health Check

```bash
crontab -e
# Add:
*/5 * * * * /home/ubuntu/check-agentic.sh
```

---

## Troubleshooting

### Bot not responding to Discord commands?
```bash
# Check Discord bot is logged in
sudo journalctl -u jico-agentic | grep "logged in"

# Check bot has permission in Discord guild
# Go to Discord → Server Settings → App Integrations → Your App
# Ensure bot has "Send Messages" + "Use Slash Commands" permissions
```

### Supabase connection error?
```bash
# Verify .env is set correctly
grep SUPABASE /home/ubuntu/nacpac-dev/agentic/.env

# Test connection manually
python3 -c "from supabase import create_client; create_client('$SUPABASE_URL', '$SUPABASE_KEY')"
```

### Cost tracker showing errors?
```bash
# Check daily/monthly caps in Supabase
SELECT * FROM costs WHERE date >= CURRENT_DATE - INTERVAL '1 month';

# Reset cost table if needed (BE CAREFUL)
# DELETE FROM costs WHERE date < CURRENT_DATE;
```

### Service not starting?
```bash
# Check service file syntax
sudo systemctl status jico-agentic
sudo journalctl -xe  # Extended error messages

# Manually run to see errors
cd /home/ubuntu/nacpac-dev/agentic
source venv/bin/activate
python3 -m agentic.main
```

---

## Next Steps

Once deployment is complete:

1. ✅ Monitor logs for 24 hours: `journalctl -u jico-agentic -f`
2. ✅ Test all Discord commands (build APK, build EXE, deploy, etc.)
3. ✅ Verify Supabase is logging tasks correctly
4. ✅ Check R2 backups are working
5. ✅ Set up Google Drive backup
6. ✅ Set up GitHub release backup
7. ✅ Document any custom configurations

---

**Status:** Phase 2 deployment guide complete. Ready to execute!
