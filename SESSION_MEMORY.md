# Session Memory & Guidelines

**Date:** July 1, 2026  
**Status:** Discord Bot Deployment to Oracle Cloud (In Progress)

---

## Critical Rules for Future Sessions

### Before Any Action
- ✅ **Always ask before building** - Get explicit permission before running builds
- ✅ **Always push automation scripts to git** - Never leave scripts in local memory only
- ✅ **Always respond summarized** - Keep responses short, user asks for details if needed

### Contingency & Backup Planning
- ✅ **Stop progress loss** - If session disconnects, have rollback/recovery plan ready
- ✅ **Backup is priority #1** - Before deployments, ensure backups exist
- ✅ **Save everything** - Code, architecture, config, builds, credentials reference

### What to Back Up
1. **Source Code** - All repos and branches
2. **Architecture Docs** - DEPLOYMENT_GUIDE.md, CREDENTIALS_REFERENCE.md, etc.
3. **Memory/Context** - SESSION_MEMORY.md (this file), chat transcripts
4. **Build Files** - APK, EXE, archives from R2 and Google Drive
5. **.env & Config** - Template files (never commit actual secrets, only templates)
6. **Repo State** - Current branch, uncommitted changes, merge status
7. **Storage Buckets** - R2 bucket contents, Google Drive backups
8. **Chat Sessions** - Export important conversations for recovery

---

## Current Deployment Status

### ✅ Completed
- Discord bot framework with greeting detection
- Task screening (keyword-based, no API calls)
- Approval buttons [✅ Yes] [❌ No]
- Optional preview generation (Anthropic Haiku)
- Build type selection [📱 APK] [🖥️ EXE] [📦 BOTH]
- Build backup system (last 2 builds per type)
- Google Drive auto-backup for source code
- .env.oracle.template with 39/44 credentials pre-filled
- All 44 credentials collected from user
- Automated deployment script (auto-deploy.sh)
- Fixed for Ubuntu user (not just opc)
- Fixed Node.js version (18.x for EAS CLI)

### 🔄 In Progress
- Running auto-deploy.sh on Ubuntu instance (68.233.110.235)
- Script will install dependencies, create systemd service, start bot

### ⏳ Next Steps (Pending)
1. Complete auto-deploy.sh execution on Ubuntu instance
2. User fills in Firebase values when prompted
3. systemd service starts jico-manager bot
4. Test Discord workflow in #general channel
5. Verify APK/EXE builds work end-to-end
6. Monitor logs for 24 hours
7. Backup all credentials and deployment artifacts

---

## Key Technical Details

### Instance Info
- **Public IP:** 68.233.110.235
- **User:** ubuntu (NOT opc)
- **SSH Key:** C:/Users/piyus/Downloads/oracle_key.key
- **Repo Branch:** claude/new-session-dxi5li
- **Home Dir:** /home/ubuntu

### Credentials Status
- ✅ Discord Token & Guild ID
- ✅ Anthropic API Key
- ✅ Cloudflare R2 (all 8 values)
- ✅ Google Drive OAuth JSON
- ✅ EAS Token
- ✅ Firebase (all 5 values: API Key, Auth Domain, Storage Bucket, Messaging Sender ID, App ID)
- ✅ All file paths configured
- ✅ Oracle Cloud & Agent credentials

### Firebase Values (Provided by User)
```
FIREBASE_API_KEY=AIzaSyAmvqkpyBKEZogyk0j_Ti9ob6eUuntE2CeM
FIREBASE_AUTH_DOMAIN=nacpac-production-4134a.firebaseapp.com
FIREBASE_STORAGE_BUCKET=nacpac-production-4134a.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=371880247454
FIREBASE_APP_ID=1:371880247454:web:b9ae971b4aa16bea673b8f
```

### Bot Workflow
```
User: "Hi piyush, what is the agenda today!"
  ↓
Discord Bot: Greeting detected ✓
  ↓
User: [Task description]
  ↓
Bot: Screening keywords (no API calls)
  ↓
Bot: [✅ Yes] [❌ No] approval buttons
  ↓
If approved → [✅ Generate Preview] [⏭️ Skip]
  ↓
User: [📱 APK] [🖥️ EXE] [📦 BOTH]
  ↓
Build execution:
  - APK: eas build --platform android --profile preview --non-interactive
  - EXE: npm run build (in desktop/)
  ↓
Upload to R2 → Save to build backup → Auto-backup to Google Drive
  ↓
Post download links to #nacpac-dev
```

### Rollback Command
```
!rollback apk    # Restore last successful APK
!rollback exe    # Restore last successful EXE
!rollback both   # Restore both
```

---

## Files Created This Session

| File | Purpose |
|------|---------|
| `discord_manager.py` | Main Discord bot with workflow |
| `nacpac_manager.py` | Build orchestration |
| `google_drive_backup.py` | Google Drive auto-backup |
| `build_backup.py` | Build metadata tracking |
| `auto-deploy.sh` | Automated deployment script |
| `.env.oracle.template` | Environment variables template |
| `DEPLOYMENT_GUIDE.md` | Step-by-step deployment instructions |
| `CREDENTIALS_REFERENCE.md` | Where to get each credential |
| `ENVIRONMENT_VARIABLES_SETUP.md` | 4 methods to set variables |
| `GOOGLE_DRIVE_SETUP.md` | Google Drive backup config |
| `FIREBASE_CREDENTIALS_GUIDE.md` | How to find Firebase values |
| `FIREBASE_VALUES_REFERENCE.md` | Quick copy-paste Firebase values |
| `CREDENTIALS_STATUS.md` | Deployment readiness checklist |
| `SESSION_MEMORY.md` | This file |

---

## If Session Disconnects

**Recovery Checklist:**
1. ✅ All code is in git branch `claude/new-session-dxi5li` - Pull it
2. ✅ All credentials documented in CREDENTIALS_STATUS.md
3. ✅ Firebase values in FIREBASE_VALUES_REFERENCE.md
4. ✅ Deployment guide in DEPLOYMENT_GUIDE.md
5. ✅ If bot is running, check: `sudo journalctl -u jico-manager -f`
6. ✅ If deployment incomplete, re-run: `bash auto-deploy.sh`

**What's NOT in git (keep separate):**
- `.env` file (has actual secrets) - only on Oracle instance
- Build artifacts (APK/EXE) - in R2 and Google Drive
- Chat transcripts - export from Claude session

---

## Cost Tracking

**Budget:** $50/month, $10/day

**Estimated Usage:**
- Discord API: Free
- Anthropic Claude Haiku: ~$0.00001 per 1K tokens (preview only, optional)
- Cloudflare R2: ~$0.015 per GB (last 2 builds = ~500MB = $0.01/month)
- Google Drive: Free (15GB free tier)
- EAS/npm: Free (user's tokens)

**Total:** ~$5-10/month

---

## Important Notes

### Security
- ❌ NEVER commit `.env` files with actual secrets
- ❌ NEVER share SSH keys
- ❌ NEVER commit Firebase/Discord/Anthropic tokens
- ✅ Only commit templates with placeholders
- ✅ Use `.gitignore` to exclude credential files
- ✅ Store actual secrets on Oracle instance only

### Best Practices
- Always test Discord workflow before shipping
- Monitor logs after deployment: `sudo journalctl -u jico-manager -f`
- Keep last 2 builds as contingency via BuildBackup
- Auto-backup to Google Drive after each successful build
- Rotate credentials every 30 days

---

## For Next Session

When resuming:
1. Read this file first (SESSION_MEMORY.md)
2. Pull latest branch: `git pull origin claude/new-session-dxi5li`
3. Check deployment status:
   - SSH to instance: `ssh -i C:/Users/piyus/Downloads/oracle_key.key ubuntu@68.233.110.235`
   - Check bot: `sudo systemctl status jico-manager`
   - View logs: `sudo journalctl -u jico-manager -n 50`
4. Ask user before making any changes
5. Keep this file updated after major milestones

---

**Last Updated:** 2026-07-01 17:45 UTC  
**Status:** Deployment script running on Ubuntu instance  
**Next Check:** When user reports deployment complete or error
