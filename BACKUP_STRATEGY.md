# Complete Backup & Disaster Recovery Strategy

**Goal:** Prevent loss of session/code even if local machine crashes. Multiple redundant backups across Git, Google Drive, and Oracle VM.

## Backup Layers

### Layer 1: Git Repository (Continuous)
- **What:** Code commits to GitHub
- **When:** Every code change (via git push)
- **Status:** ✅ Active
- **Recovery:** `git clone piyush333/nacpac-dev`

### Layer 2: Google Drive Backup (Automated Daily)
- **What:** Complete session zip file + recovery guide
- **When:** Daily at 2 AM (configurable)
- **What's included:**
  - `jico-system/` - Complete bot system
  - `memory.md` - Session context
  - `skills.md` - Custom skills
  - All documentation
  - Configuration templates
  - Source code
- **What's excluded:** `.env` (security - you add credentials when restoring)
- **Folder:** https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO
- **Status:** 🟡 Needs setup (see below)

### Layer 3: Oracle VM Deployment (Persistent)
- **What:** Running bot instance on cloud VM
- **When:** 24/7 uptime
- **Status:** 📋 Planned (next phase)
- **Benefits:** No local machine dependency

## Quick Start: Set Up Google Drive Backups

### Step 1: Get OAuth Credentials (5 minutes)

```bash
# Download credentials.json from Google Cloud Console
# (See GOOGLE_DRIVE_BACKUP_SETUP.md for detailed steps)
cp ~/Downloads/credentials.json /home/user/nacpac-dev/
```

### Step 2: Run Setup Script (2 minutes)

```bash
cd /home/user/nacpac-dev
bash setup_backup_cron.sh
```

This script will:
1. ✅ Check credentials.json exists
2. ✅ Test the backup works (first run opens browser for OAuth)
3. ✅ Create cron job for daily 2 AM backups
4. ✅ Set up logging

### Step 3: Verify Setup (1 minute)

```bash
# Check cron job is installed
crontab -l | grep backup

# Monitor backup logs
tail -f /tmp/gdrive-backup.log

# Check Google Drive folder for backups
# https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO
```

## File Locations

```
/home/user/nacpac-dev/
├── backup_to_gdrive.py              ← Main backup script
├── BACKUP_STRATEGY.md               ← This file
├── GOOGLE_DRIVE_BACKUP_SETUP.md     ← Detailed setup guide
├── setup_backup_cron.sh             ← Automated setup helper
├── credentials.json                 ← (create from Google Cloud) DO NOT COMMIT
└── token.json                       ← (auto-created) DO NOT COMMIT
```

Both `credentials.json` and `token.json` are in `.gitignore` to prevent accidental commits.

## How to Restore from Backup

When you need to recover (new machine, fresh session, etc.):

```bash
# 1. Download backup from Google Drive
# https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO
# Download the most recent JICO-Backup-*.zip

# 2. Extract backup
unzip JICO-Backup-20260630_140500.zip

# 3. Read recovery guide
cat RECOVERY_GUIDE.md

# 4. Copy files to new location
cp -r jico-system/ /home/user/nacpac-dev/

# 5. Install dependencies
cd /home/user/nacpac-dev/jico-system
pip install -r requirements.txt

# 6. Create .env with credentials
# (recovery guide has template)
cat > .env << 'EOF'
DISCORD_TOKEN=your_token_here
DISCORD_GUILD_ID=your_guild_id_here
... other credentials ...
EOF

# 7. Verify setup
python setup_discord_channels.py

# 8. Run bot
python main.py
```

## Backup Contents Breakdown

### Size & Frequency
- **Typical size:** 30-50 MB per backup (compressed)
- **Frequency:** Daily at 2 AM
- **Retention:** Google Drive stores all versions (check folder)
- **Cost:** Free (using personal Google Drive)

### What's Included
```
JICO-Backup-20260630_140500.zip
├── jico-system/                         ← Complete bot
│   ├── main.py                          ← Main bot
│   ├── discord_manager.py               ← Discord routing
│   ├── compression_layer.py             ← Keyword classification
│   ├── nacpac_manager.py                ← Nacpac worker
│   ├── jico_manager.py                  ← Jico worker
│   ├── health_monitor.py                ← Health checks
│   ├── git_sync.py                      ← Git sync
│   ├── config.py                        ← Configuration
│   ├── requirements.txt                 ← Dependencies
│   └── ... other files ...
├── memory.md                            ← Session memory
├── skills.md                            ← Skills documentation
├── DEPLOYMENT_GUIDE.md                  ← How to deploy
├── DISCORD_ARCHITECTURE.md              ← System design
├── DISCORD_SETUP.md                     ← Discord setup
├── OPTIMIZATION_STRATEGY.md             ← Cost optimization
├── BUILD_SUMMARY.md                     ← Build status
├── RECOVERY_GUIDE.md                    ← How to restore
└── ... other documentation ...
```

### What's NOT Included (Security)
- `.env` file (contains API keys)
- `credentials.json` (Google Cloud auth)
- `token.json` (OAuth token)
- `.git` folder (use GitHub for git history)
- `node_modules/` (too large, reinstall via npm/pip)
- `__pycache__/` (compiled cache)

You must add these yourself when restoring.

## Testing Your Backup

Every week, verify your backup works:

```bash
# Download the most recent backup from Google Drive
# (Recommended: use Browser → Right-click → Download)

# Extract to temp folder
mkdir /tmp/backup-test
unzip JICO-Backup-*.zip -d /tmp/backup-test

# Verify structure
ls -la /tmp/backup-test/jico-system/
ls /tmp/backup-test/memory.md
ls /tmp/backup-test/RECOVERY_GUIDE.md

# Should see all expected files
# If yes, your backup is good
# Clean up
rm -rf /tmp/backup-test
```

## Monitoring Backups

### Check Recent Backups
```bash
# List today's backups
ls -lh /tmp/jico-backup/

# View last backup log
tail -50 /tmp/gdrive-backup.log
```

### Cron Job Status
```bash
# Verify cron job exists
crontab -l

# Check cron service is running
sudo service cron status

# View recent cron executions
grep CRON /var/log/syslog | tail -20
```

### Google Drive Folder
```
https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO
```
- Should contain multiple `JICO-Backup-*.zip` files (one per day)
- Each backup includes `RECOVERY_GUIDE.md`
- Size grows over time (keep 5-10 recent ones)

## Troubleshooting

### Backup hasn't run
```bash
# Check if cron is working
sudo service cron status

# Run backup manually
python3 /home/user/nacpac-dev/backup_to_gdrive.py

# Check for errors
tail /tmp/gdrive-backup.log
```

### Cron job disappeared
```bash
# Re-run setup script
cd /home/user/nacpac-dev
bash setup_backup_cron.sh
```

### Can't access Google Drive folder
1. Verify you're logged in to Google Drive (piyushjindal333@gmail.com)
2. Copy folder URL: https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO
3. Open in browser, check if folder is shared with you

### Backup file is corrupted
1. Delete the bad file from Google Drive
2. Run backup manually to create new one: `python3 backup_to_gdrive.py`
3. Test extraction: `unzip -t JICO-Backup-*.zip`

## Redundancy Summary

| Layer | Method | Frequency | Recovery Time |
|-------|--------|-----------|---|
| **Code** | Git push | Every commit | 1-5 min |
| **Session** | Google Drive | Daily 2 AM | 5-10 min |
| **Bot Instance** | Oracle VM | 24/7 | 1-2 min |

**You have 3 independent backup paths. Session is protected.** ✅

## Next: Oracle VM Deployment

After Google Drive backups are working:

1. Set up Oracle VM instance
2. Clone from GitHub
3. Run bot as systemd service
4. Bot continues running even if local machine is down

See `DEPLOYMENT_GUIDE.md` for Oracle VM instructions.

## Commands Reference

```bash
# Setup
bash /home/user/nacpac-dev/setup_backup_cron.sh

# Test backup manually
python3 /home/user/nacpac-dev/backup_to_gdrive.py

# View backup logs
tail -f /tmp/gdrive-backup.log

# Check cron status
crontab -l

# Edit cron schedule (2 AM daily)
crontab -e

# Disable backup cron (if needed)
crontab -r

# Restore from Google Drive backup
# 1. Download JICO-Backup-*.zip
# 2. unzip JICO-Backup-*.zip
# 3. Follow RECOVERY_GUIDE.md
```

---

**Status:** Google Drive backups are ready for setup. Follow "Quick Start" section above.

**Questions?** See GOOGLE_DRIVE_BACKUP_SETUP.md for detailed instructions.
