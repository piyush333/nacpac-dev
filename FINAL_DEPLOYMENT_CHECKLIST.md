# 🚀 Final Deployment Checklist

**Oracle IP:** `144.24.129.201`  
**Status:** Ready to deploy

---

## Step 1: Gather Credentials (5 minutes)

You have SSH keys. Now I need:

### A. Supabase (CRITICAL)
- [ ] Create free project: https://supabase.com/sign-up
- [ ] Project name: `jico-agentic`
- [ ] Copy from **Settings → API**:
  - `SUPABASE_URL` (looks like `https://xxx.supabase.co`)
  - `SUPABASE_KEY` (anon key, starts with `eyJh...`)

### B. Discord (CRITICAL)
From your Discord server setup:
- [ ] `DISCORD_TOKEN` (your bot's token)
- [ ] `DISCORD_GUILD_ID` (right-click server → Copy Server ID)
- [ ] `DISCORD_GENERAL_CHANNEL_ID` (right-click #general → Copy Channel ID)
- [ ] `DISCORD_BUILDS_CHANNEL_ID` (create channel #builds, copy ID)
- [ ] `DISCORD_DEPLOYS_CHANNEL_ID` (create channel #deploys, copy ID)
- [ ] `ALLOWED_USER_ID` (right-click yourself → Copy User ID)

### C. Backups (Optional, add later if you have them)
- [ ] Cloudflare R2 credentials (4 values)
- [ ] Google Drive credentials JSON
- [ ] GitHub token

---

## Step 2: Create .env File (5 minutes)

On your local machine:

```bash
# In nacpac-dev/agentic/
cp .env.template .env

# Edit with your actual values
nano .env  # or your favorite editor
```

**Fill in:**
```
ANTHROPIC_API_KEY=your_anthropic_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
DISCORD_TOKEN=your_bot_token
DISCORD_GUILD_ID=123456789
DISCORD_GENERAL_CHANNEL_ID=123456789
DISCORD_BUILDS_CHANNEL_ID=123456789
DISCORD_DEPLOYS_CHANNEL_ID=123456789
ALLOWED_USER_ID=your_user_id
```

Leave other values as default for now.

---

## Step 3: Prepare for Deployment (2 minutes)

On your local machine, in the repo root:

```bash
# Copy your SSH key to current directory
cp /path/to/sshkey20260702.key ./

# Make deployment script executable
chmod +x DEPLOY_TO_ORACLE.sh
```

---

## Step 4: Run Deployment Script (10 minutes)

```bash
# From repo root
./DEPLOY_TO_ORACLE.sh
```

This script will:
1. ✅ Test SSH connection
2. ✅ Install Python + git
3. ✅ Clone agentic code
4. ✅ Create Python environment
5. ✅ Upload `.env` (secure)
6. ✅ Install systemd service
7. ✅ Start the bot
8. ✅ Show logs

---

## Step 5: Set Up Supabase Schema (5 minutes)

While deployment is running, set up Supabase:

1. Go to your Supabase project dashboard
2. Click **SQL Editor**
3. Create new query
4. Copy entire contents of `agentic/schema.sql`
5. Paste and run

This creates all tables and seeds initial data.

---

## Step 6: Verify Deployment (5 minutes)

After script completes, test:

```bash
# SSH to your instance
ssh -i sshkey20260702.key ubuntu@144.24.129.201

# Check service status
sudo systemctl status jico-agentic

# Watch logs (live)
sudo journalctl -u jico-agentic -f

# Exit with Ctrl+C
```

Expected logs:
```
✅ Bot logged in as YourBotName#1234
Synced X command(s)
```

---

## Step 7: Test Discord Bot (2 minutes)

In your Discord server:

```
/task brand:nacpac request:Show status
```

Expected:
1. Bot shows approval buttons: [✅ Approve] [❌ Reject]
2. Click Approve
3. Bot replies: "✅ Task Completed..."

---

## Step 8: Create Supabase Schema (DO THIS NOW)

Before testing Discord, you MUST run the schema:

### Option A: Via Supabase UI
1. Go to https://supabase.com/dashboard
2. Select your `jico-agentic` project
3. Click **SQL Editor** (left sidebar)
4. Click **New Query**
5. Open file: `agentic/schema.sql`
6. Copy entire contents
7. Paste into SQL editor
8. Click **Run**
9. Wait for "Success" message

### Option B: Via psql (if you have Postgres installed)
```bash
psql "postgresql://[user]:[password]@[host]:5432/postgres" \
  -f agentic/schema.sql
```

Get connection string from Supabase: **Settings → Database → Connection String**

---

## Troubleshooting

### "SSH connection failed"
- Verify SSH key path is correct
- Check Oracle instance is running
- Check IP address: 144.24.129.201

### "Supabase connection error"
- Verify `SUPABASE_URL` format (should have `https://` prefix)
- Verify `SUPABASE_KEY` starts with `eyJh`
- Check schema is created (run `agentic/schema.sql`)

### "Discord bot not responding"
- Verify bot is in your server
- Verify bot has **Send Messages** permission
- Verify bot has **Use Slash Commands** permission
- Check logs: `sudo journalctl -u jico-agentic | grep -i discord`

### "Systemd service won't start"
- Check logs: `sudo journalctl -u jico-agentic -n 50`
- Verify `.env` file exists and has correct values
- Try starting manually: `cd /home/ubuntu/nacpac-dev/agentic && source venv/bin/activate && python3 main.py`

---

## Success Criteria ✅

Once complete, you should have:

- ✅ Oracle instance running with Python + git
- ✅ Agentic system deployed as systemd service (24/7)
- ✅ Supabase project with schema + tables
- ✅ Discord bot responding to `/task` commands
- ✅ Tasks logged to Supabase
- ✅ System auto-restarts on crash

---

## Next Steps

1. Monitor logs for 24 hours: `sudo journalctl -u jico-agentic -f`
2. Test all commands:
   - `/task brand:nacpac request:Build APK`
   - `/task brand:jico_life request:Show status`
3. Set up backups (R2, Google Drive, GitHub)
4. Set up monitoring + alerts

---

## Timeline

| Step | Time | Status |
|------|------|--------|
| 1. Gather credentials | 5m | ⏳ TODO |
| 2. Create .env | 5m | ⏳ TODO |
| 3. Prepare for deployment | 2m | ⏳ TODO |
| 4. Run deployment script | 10m | ⏳ TODO |
| 5. Set up Supabase schema | 5m | ⏳ TODO |
| 6. Verify deployment | 5m | ⏳ TODO |
| 7. Test Discord bot | 2m | ⏳ TODO |
| **Total** | **~34 minutes** | ⏳ IN PROGRESS |

---

**Ready? Start with Step 1!** 🚀

When you've gathered the credentials and created `.env`, reply with the values and I'll confirm everything is correct before you run the deployment script.
