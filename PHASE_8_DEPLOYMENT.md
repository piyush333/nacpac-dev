# Phase 8: Go Live — DigitalOcean Deployment Guide

**Status**: Phase 8 in progress  
**Last Updated**: 2026-07-18  
**Owner**: Central Session

---

## Overview

Phase 8 deploys the agentic system to **DigitalOcean App Platform** for **24/7 production operation**. The bot runs always-on, accepts tasks via Discord, executes builds/deployments via dev agents, and backs up artifacts to **R2 (Cloudflare)** and **Google Drive**.

### Key Principles

✅ **Minimal environment variables**: Only `SUPABASE_URL` and `SUPABASE_KEY` set in DigitalOcean  
✅ **Secure secrets**: All credentials stored in Supabase `secrets` table, not in config/git  
✅ **24/7 availability**: Bot runs continuously, no scheduled downtime  
✅ **Multiple backup targets**: Every build artifact backed up to R2, Google Drive, GitHub Releases  
✅ **Health monitoring**: 5-min health checks, auto-restart on failure  
✅ **Cost control**: Daily ($10) and monthly ($50) spend caps enforced in Supabase  

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DigitalOcean App                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Discord Bot (agentic/discord_bot.py)                    │  │
│  │  - Listens to #general channel messages                  │  │
│  │  - Routes tasks to Orchestrator Agent                    │  │
│  │  - Posts approval buttons for user review                │  │
│  │                                                          │  │
│  │  [Secrets Initialization]                               │  │
│  │  - Loads 11 credentials from Supabase at startup         │  │
│  │  - Caches in memory for fast access                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │  Orchestrator Agent (agentic/agents/orchestrator.py)    │  │
│  │  - Parses natural language → intent (brand + task_type) │  │
│  │  - Routes to NacPac or Jico Life Dev Agent              │  │
│  │  - Logs all decisions to Supabase                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│     │                              │                            │
│     ▼                              ▼                            │
│  ┌─────────────────────┐  ┌──────────────────────────┐         │
│  │ NacPac Dev Agent    │  │ Jico Life Dev Agent      │         │
│  ├─────────────────────┤  ├──────────────────────────┤         │
│  │ - build_apk()       │  │ - build_glb_model()      │         │
│  │ - build_exe()       │  │ - deploy_to_staging()    │         │
│  │ - deploy_staging()  │  │ - deploy_to_production() │         │
│  │ - deploy_prod()     │  │                          │         │
│  └─────────────────────┘  └──────────────────────────┘         │
│     │                              │                            │
│     └──────────────────┬───────────┘                            │
│                        ▼                                        │
│     ┌──────────────────────────────────────────────────┐       │
│     │  Backup & Artifact Management                   │       │
│     │  - R2 (Cloudflare) - Fast CDN access            │       │
│     │  - Google Drive - Familiar backup               │       │
│     │  - GitHub Releases - Versioned storage          │       │
│     └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────┐
│   Supabase           │
│  ┌────────────────┐  │
│  │ secrets        │  │ ← All credentials stored securely
│  │ tasks          │  │ ← Task history & logging
│  │ runs           │  │ ← Agent execution logs
│  │ costs          │  │ ← Daily/monthly spend tracking
│  │ brand_state    │  │ ← Current branch/deploy status
│  └────────────────┘  │
└──────────────────────┘
```

---

## Infrastructure Setup

### 1. DigitalOcean App Platform

**Deployment Method**: GitHub Auto-Deploy

```yaml
# When you push to claude/agentic-system-org-j9gvae:
# DigitalOcean automatically:
# 1. Clones the repo
# 2. Builds Docker image
# 3. Deploys to app platform
# 4. Runs health checks
# 5. Auto-restarts on failure
```

**Health Check Endpoint**:
- URL: `http://app:8080/health`
- Interval: 5 minutes
- Expected response: `{"status": "ok", "bot_user": "bot_name"}`

**Auto-Restart Policy**:
- Watches `/health` endpoint every 5 min
- If no response or status ≠ "ok": restarts container
- Maximum 5 restarts per hour (prevents restart loops)

### 2. Cloudflare R2

**Purpose**: Fast, durable backup for APK/EXE builds

**Credentials** (in Supabase secrets):
```
R2_ACCOUNT_ID: 80e3d8a13ee6ba6163951832a60af7d4
R2_ACCESS_KEY_ID: a5153ff264447a9a8482875f25215cb3
R2_SECRET_ACCESS_KEY: 072dbc9b4789169732cbe0c8d25bd2d8a417253e6a6a2fbf76af157318ebdffd
R2_BUCKET_NAME: nacpac-workspace
```

**Bucket Structure**:
```
nacpac-workspace/
├── builds/
│   ├── 2026-07-18/
│   │   ├── nacpac-apk-release-v1.0.0.apk
│   │   └── nacpac-exe-release-v1.0.0.exe
│   └── 2026-07-19/
│       └── ...
└── logs/
    └── build-log-2026-07-18-143022.txt
```

**Access URL** (public read):
```
https://nacpac-workspace.r2.cloudflarestorage.com/builds/2026-07-18/nacpac-apk-release-v1.0.0.apk
```

### 3. Google Drive Backup

**Purpose**: Redundant backup, familiar interface for manual access

**Folder** (in Supabase secrets):
```
GOOGLE_DRIVE_BACKUP_FOLDER_ID: 12NVqDTdpcuM9ZHKua9KT_UazGrYkoSa1
Folder URL: https://drive.google.com/drive/folders/12NVqDTdpcuM9ZHKua9KT_UazGrYkoSa1
```

**Backup Process**:
- After every successful build, upload artifact to this folder
- Organize by date: `NacPac-2026-07-18/` → `APK-release-v1.0.0.apk`
- Retains last 30 days automatically (you can set Google Drive expiration)

---

## Deployment Process

### Step 1: Verify All Credentials in Supabase

```bash
# Check secrets table has all 11 keys
SELECT key FROM secrets ORDER BY key;
```

Expected output:
```
BUILD_TEST_MODE
DISCORD_BOT_TOKEN
EAS_TOKEN
GITHUB_TOKEN
GOOGLE_DRIVE_BACKUP_FOLDER_ID
R2_ACCESS_KEY_ID
R2_ACCOUNT_ID
R2_BUCKET_NAME
R2_SECRET_ACCESS_KEY
SUPABASE_KEY
SUPABASE_URL
```

### Step 2: Configure DigitalOcean App

**Environment Variables** (ONLY these two in DigitalOcean):
```
SUPABASE_URL=https://xsjxyauozqpkdkwbzsda.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

All other credentials are loaded from Supabase at runtime via `secrets_manager.py`.

**Resource Allocation**:
- CPU: 1 shared CPU (sufficient for Discord bot)
- Memory: 512 MB (Discord bot + agent initialization)
- Disk: 2 GB (logs, temporary builds)

**Auto-Deploy**:
- Connected to GitHub: `jico-org/nacpac-workspace`
- Branch: `claude/agentic-system-org-j9gvae`
- Deploy on every push: Enabled

### Step 3: Deploy

```bash
# Push to DigitalOcean-connected branch
git push -u origin claude/agentic-system-org-j9gvae

# DigitalOcean automatically:
# 1. Triggers webhook on GitHub push
# 2. Clones latest code
# 3. Builds Docker image
# 4. Deploys to app platform
# 5. Runs health checks
# 6. Logs to DigitalOcean dashboard
```

**Monitor Deployment**:
1. Go to DigitalOcean App Platform dashboard
2. Select "nacpac-workspace" app
3. Watch "Deployment" tab for progress
4. Check "Logs" tab for errors

### Step 4: Verify Health

```bash
# Once deployed, test health endpoint:
curl https://your-app-url.ondigitalocean.app/health

# Expected response:
{
  "status": "ok",
  "bot_user": "JicoBot#1234",
  "uptime_seconds": 42
}
```

### Step 5: Test in Discord

```
1. Go to #general channel
2. Type: "Build the NacPac APK"
3. Bot should respond with approval buttons
4. Click ✅ Approve
5. Watch build progress in #logs
6. Download artifact from R2 link
```

---

## Secrets Management

### How Secrets Are Loaded

```python
# At bot startup:
from agentic.secrets_manager import init_secrets

# In on_ready() event:
if init_secrets():  # Loads all 11 credentials from Supabase
    logger.info("✅ Secrets initialized")
    # Now discord_bot.py can use get_secret("DISCORD_BOT_TOKEN")
    # Instead of hardcoding or env var
```

### Why This Approach?

| Method | Security | Ease | Audit |
|--------|----------|------|-------|
| Environment vars in DigitalOcean | ⚠️ Medium | ✅ Easy | ⚠️ Limited |
| Hardcoded in config.py | ❌ Bad | ✅ Easy | ❌ None |
| **Supabase table (Phase 8)** | ✅ Excellent | ✅ Easy | ✅ Full |

Benefits:
- Credentials not visible in DigitalOcean logs
- Credentials not in git history
- Can rotate credentials without redeploying
- Full audit trail in Supabase
- Easy to add new agents (jico_life_dev, marketing_bot, etc.)

---

## Monitoring & Health Checks

### Health Check Endpoint

```python
# In discord_bot.py:
@app.route('/health')
async def health_check():
    return {
        "status": "ok",
        "bot_user": bot.user.name if bot.user else "not_connected",
        "uptime_seconds": int(time.time() - bot_start_time),
        "agents_loaded": bool(orchestrator)
    }
```

DigitalOcean polls this every **5 minutes**:
- If healthy (200 response): Continue running
- If unhealthy (timeout or 500): Auto-restart container

### Logs & Monitoring

**DigitalOcean Dashboard**:
- Real-time logs: `Logs` tab in app dashboard
- Deployment history: `Deployments` tab
- Resource usage: `Overview` tab
- Alerts: Configurable email alerts for restart events

**Supabase Logs** (persistent):
- Task history: `tasks` table
- Agent execution: `runs` table
- Cost tracking: `costs` table

**Discord Notifications**:
- #logs channel: Detailed build/deploy logs
- #reports channel: Summary reports
- Direct reply: User-facing confirmation

---

## Cost Tracking & Budgets

### Daily & Monthly Caps

**DigitalOcean App Platform**:
- Compute (1 CPU, 512 MB): ~$5-7/month
- Bandwidth: ~$1-2/month  
- Storage: Negligible

**Supabase (PostgreSQL)**:
- Included in free tier up to 500 MB
- Estimated: $10-15/month if needed

**R2 (Cloudflare)**:
- Storage: $0.015 per GB/month
- Requests: $0.20 per 1M requests
- Estimated: $3-5/month

**Google Drive**:
- Free tier: 15 GB storage
- Estimated: Free (if within quota)

**EAS Build (Expo)**:
- Per-build credits: ~100-200 credits per APK
- Estimated: ~$20-30/month (if building daily)

**Total Estimated**: $40-60/month (within your $50/month cap)

### Cost Enforcement

```sql
-- Before every model call, check costs:
SELECT SUM(cost_usd) as today_total
FROM costs
WHERE DATE(created_at) = CURRENT_DATE;

-- If today_total > $10: Reject build with error message
-- If month_total > $50: Reject with warning
```

---

## Production Runbook

### Emergency Restart

**Via DigitalOcean Dashboard**:
1. Go to App → Components → App Service
2. Click "Restart" button
3. Wait 1-2 min for bot to reconnect

**Via CLI** (if SSH access):
```bash
systemctl restart discord-bot  # On DigitalOcean VM
```

### Rotating Credentials

If a token is compromised:

```sql
-- Update in Supabase (no redeployment needed):
UPDATE secrets SET value = 'new_token_here', updated_at = NOW()
WHERE key = 'GITHUB_TOKEN';

-- Bot loads fresh secrets on next startup
-- Optionally restart via DigitalOcean dashboard
```

### Viewing Logs

**Real-time**:
- DigitalOcean Dashboard → App → Logs tab

**Historical** (last 24 hrs):
- DigitalOcean stores in app logs
- Supabase stores in `runs` table (indefinitely)

**Search for errors**:
```sql
SELECT timestamp, level, message
FROM app_logs
WHERE level IN ('ERROR', 'CRITICAL')
ORDER BY timestamp DESC
LIMIT 20;
```

### Scaling

**If bot becomes slow**:
1. Increase CPU: DigitalOcean App → Scale → 2 shared CPU
2. Increase memory: Scale → 1 GB RAM
3. No code changes needed

**If storage fills up**:
1. Clean old logs: `DELETE FROM runs WHERE created_at < NOW() - INTERVAL '30 days'`
2. Archive to Google Drive
3. Increase disk allocation

---

## Success Metrics (After 1 Week)

✅ **Reliability**: 99%+ uptime  
✅ **Response time**: <5 seconds for approval requests  
✅ **Cost accuracy**: Actual spend within 5% of forecast  
✅ **Build success**: 95%+ of tasks complete successfully  
✅ **Error recovery**: Auto-restart within 5 min of failure  

### Acceptance Criteria

- [ ] Bot runs continuously for 7 days without manual intervention
- [ ] At least 5 successful builds (APK or EXE)
- [ ] Artifacts backed up to R2 and Google Drive
- [ ] Cost tracking accurate within $1
- [ ] All Discord channels receiving updates
- [ ] Zero hardcoded credentials in logs or error messages

---

## Rollback Plan

If production issues occur:

**Immediate** (within 1 hour):
1. Pause bot in DigitalOcean (set replica count to 0)
2. Investigate error in logs
3. Push fix to git branch
4. Verify in test environment

**Short-term** (within 4 hours):
1. Restart bot with previous working commit: `git revert HEAD`
2. Deploy to DigitalOcean (auto-redeploy)
3. Verify health checks pass
4. Resume testing of fix

**If unrecoverable**:
1. Keep Phase 7 test infrastructure running
2. Manually execute builds via discord_bot.py (local)
3. No data loss (all task history in Supabase)

---

## Next Steps (Post-Deployment)

1. **Monitor first week**: Watch for any failures, adjust resource allocation
2. **Onboard Jico Life Dev Agent**: Repeat Phase 1-8 for jico_life_dev agent
3. **Add MCPO Agents** (Phase 9+):
   - Marketing Bot (ad campaigns, analytics)
   - Customer Success Bot (support tickets, feedback)
   - Product Bot (roadmap, prioritization)
   - Operations Bot (infra, monitoring)
4. **Optimize costs**: Fine-tune resource allocation based on actual usage

---

## Troubleshooting

### Bot doesn't connect to Discord

**Check**:
- `DISCORD_BOT_TOKEN` in Supabase secrets table
- Token hasn't been regenerated in Discord Developer Portal
- Bot has permissions: Send Messages, Embed Links, Add Reactions

**Fix**:
```bash
# Retrieve current token from Google Drive folder
# Update in Supabase:
UPDATE secrets SET value = 'new_token' WHERE key = 'DISCORD_BOT_TOKEN';

# Restart bot via DigitalOcean dashboard
```

### Build fails with "Credentials not found"

**Check**:
- All 11 secrets in Supabase table
- `init_secrets()` called successfully (check logs)
- Supabase connection working

**Fix**:
```bash
# Verify secrets loaded:
curl https://your-app-url.ondigitalocean.app/health

# If agent is None, secrets failed to load
# Check Supabase URL and KEY in DigitalOcean env vars
```

### R2 upload fails

**Check**:
- `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` correct
- Bucket name matches: `nacpac-workspace`
- Bucket exists in Cloudflare dashboard

**Fix**:
```bash
# Test R2 connection manually:
aws s3 ls s3://nacpac-workspace/ \
  --endpoint-url https://80e3d8a13ee6ba6163951832a60af7d4.r2.cloudflarestorage.com \
  --region auto

# If fails, verify credentials in Supabase
```

### App running out of disk space

**Check**:
```bash
df -h  # On DigitalOcean VM
# If /app partition > 90% full:
```

**Fix**:
1. Clean old builds: `find /app -name "*.apk" -mtime +30 -delete`
2. Clean logs: `truncate -s 0 /app/logs/*.log`
3. Increase disk allocation in DigitalOcean
4. Archive old logs to Google Drive

---

**Owner**: Central Session  
**Last Updated**: 2026-07-18  
**Next Review**: After first week of production operation
