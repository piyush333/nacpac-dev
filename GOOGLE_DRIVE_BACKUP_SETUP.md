# Google Drive Backup Setup Guide

Complete session backup to Google Drive for disaster recovery. This ensures you never lose your work even if your local machine crashes.

## What Gets Backed Up

- `jico-system/` - Complete bot system
- `memory.md` - Session context and learnings
- `skills.md` - Custom skills documentation
- All documentation: DEPLOYMENT_GUIDE.md, DISCORD_ARCHITECTURE.md, OPTIMIZATION_STRATEGY.md, BUILD_SUMMARY.md, etc.
- Source code and all project files
- **NOT included**: .env file (security - you add credentials when restoring)

## Step 1: Create Google Cloud Project & OAuth Credentials

### 1a. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on project selector at top-left
3. Click "NEW PROJECT"
4. Name it: `nacpac-backup`
5. Click "CREATE"
6. Wait for creation to complete

### 1b. Enable Google Drive API

1. In the left menu, go to "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click on it and click "ENABLE"

### 1c. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "CREATE CREDENTIALS" button
3. Select "OAuth client ID"
4. Choose application type: **Desktop**
5. Click "CREATE"
6. You'll get a popup with your credentials
7. Click "DOWNLOAD JSON" (the download icon)
8. This downloads `client_secret_*.json`

### 1d. Rename and Place Credentials

1. Rename the downloaded file to `credentials.json`
2. Move it to `/home/user/nacpac-dev/credentials.json`

```bash
mv ~/Downloads/client_secret_*.json /home/user/nacpac-dev/credentials.json
```

## Step 2: Test the Backup Script

Run the backup manually to test:

```bash
cd /home/user/nacpac-dev
python backup_to_gdrive.py
```

### First Run - Browser Authentication

The first time you run it:
1. A browser window will open asking you to log in to Google
2. Log in with your Google account (piyushjindal333@gmail.com)
3. Click "Allow" to give the backup app access to your Google Drive
4. Browser will say "The authentication flow has completed"
5. A `token.json` file is created automatically
6. Backup proceeds and uploads to your Google Drive folder

### After First Run

Subsequent runs use the saved `token.json` and don't need browser authentication.

## Step 3: Verify Backup in Google Drive

1. Open [Google Drive](https://drive.google.com)
2. Navigate to folder: https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO
3. You should see a new zip file: `JICO-Backup-YYYYMMDD_HHMMSS.zip`
4. You should also see: `RECOVERY_GUIDE.md` (with restoration instructions)

## Step 4: Set Up Automated Daily Backups

Create a cron job for automatic backups every day:

```bash
# Edit crontab
crontab -e

# Add this line (backs up daily at 2 AM)
0 2 * * * cd /home/user/nacpac-dev && python backup_to_gdrive.py >> /tmp/gdrive-backup.log 2>&1
```

Check if it's set:
```bash
crontab -l
```

Monitor the cron logs:
```bash
tail -f /tmp/gdrive-backup.log
```

## Files Created

After setup, you'll have:

```
/home/user/nacpac-dev/
├── credentials.json      ← (from Google Cloud Console) DO NOT COMMIT
├── token.json            ← (created after first run) DO NOT COMMIT
├── backup_to_gdrive.py   ← Backup script
└── GOOGLE_DRIVE_BACKUP_SETUP.md ← This file
```

**Important:** Don't commit `credentials.json` or `token.json` to git. They contain authentication tokens.

Add to `.gitignore`:
```bash
credentials.json
token.json
```

## Troubleshooting

### "credentials.json not found"
- You skipped Step 1c - Download the JSON from Google Cloud Console
- Make sure it's in `/home/user/nacpac-dev/credentials.json`

### Browser doesn't open
- OAuth server starts on `localhost:8080`
- Open in your browser manually: http://localhost:8080
- Or check if port 8080 is already in use

### "Invalid client ID"
- The credentials.json is malformed
- Download fresh credentials from Google Cloud Console
- Make sure you're using Desktop application type

### Upload fails
- Check internet connection
- Verify Google Drive folder ID is correct (should be: `1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO`)
- Check if folder exists in your Drive

### Cron job not running
```bash
# Check if cron is running
sudo service cron status

# Check cron logs
grep CRON /var/log/syslog | tail -20

# Test cron manually
cd /home/user/nacpac-dev && python backup_to_gdrive.py
```

## Recovery: How to Restore from Backup

When setting up a new session:

1. Download the `JICO-Backup-*.zip` from Google Drive
2. Extract: `unzip JICO-Backup-*.zip`
3. The `RECOVERY_GUIDE.md` inside has full restoration instructions
4. Copy all files to your new machine
5. Create `.env` with your credentials (API keys, tokens)
6. Continue development

## Testing Backup Integrity

Every few weeks, test that your backup works:

```bash
# Download a backup from Google Drive
# Extract it to a temp folder
unzip JICO-Backup-*.zip -d /tmp/backup-test

# Verify key files exist
ls /tmp/backup-test/jico-system/
ls /tmp/backup-test/memory.md
ls /tmp/backup-test/RECOVERY_GUIDE.md
```

## Monitoring

Check the backup log:
```bash
tail -f /tmp/gdrive-backup.log
```

Expected output:
```
============================================================
🔄 JICO System Complete Backup
============================================================

🔐 Authenticating with Google Drive...
✅ Using existing credentials from token.json

📦 Creating backup package...
  ✅ jico-system/...
  ✅ memory.md
  ✅ BUILD_SUMMARY.md
  ...
✅ Backup created: JICO-Backup-20260630_140500.zip (45.3 MB)

📤 Uploading to Google Drive...
✅ Uploaded: https://drive.google.com/file/d/...

📖 Recovery guide created: /tmp/jico-backup/RECOVERY_GUIDE.md

============================================================
✅ BACKUP COMPLETE
============================================================
📍 Location: Google Drive folder
📦 File: JICO-Backup-20260630_140500.zip
🔗 Link: https://drive.google.com/file/d/...

You can restore this backup anytime to recover your session.
```

## Summary

```bash
# One-time setup
1. Download credentials.json from Google Cloud Console
2. cp credentials.json /home/user/nacpac-dev/

# Test it works
3. python backup_to_gdrive.py

# Automate it
4. crontab -e
5. Add: 0 2 * * * cd /home/user/nacpac-dev && python backup_to_gdrive.py >> /tmp/gdrive-backup.log 2>&1

# Monitor
6. tail -f /tmp/gdrive-backup.log
```

**You're protected! Every backup is stored safely in Google Drive.**
