# 🛡️ FAIL-SAFE SYSTEM - Enterprise-Grade Reliability

Your JICO system now includes **comprehensive fail-safe mechanisms** to prevent crashes and ensure 24/7 operation.

---

## 🏥 Health Monitoring System

Continuously monitors all components and automatically recovers from failures.

### What Gets Monitored

```
✅ Discord Bot         - Connection status
✅ Anthropic API       - Response time & availability  
✅ Cloudflare R2       - Bucket connectivity
✅ Task Queue          - Queue responsiveness
✅ Auto Mode           - Process running status
✅ Disk Space          - Storage availability
✅ Memory              - RAM utilization
```

### Health Check Schedule

- **Every 30 seconds** - Full system health check
- **Failure threshold** - 3 consecutive failures before action
- **Auto recovery** - Automatic restart of failed components
- **Max recovery attempts** - 5 before critical alert

### How It Works

```
Health Monitor Loop (every 30 seconds):
├─ Check all components
├─ Count consecutive failures
├─ If failures ≥ 3:
│  ├─ Trigger recovery procedure
│  └─ Track recovery attempts
├─ If failures ≥ 5:
│  ├─ Mark as critical
│  └─ Notify administrators
└─ Report status
```

---

## 🔄 Automatic Git Sync

Keeps your code up-to-date from GitHub repos automatically.

### How It Works

```
Git Sync Scheduler (hourly):
├─ Create backup of current code
├─ Pull latest from GitHub (jico-workspace & nacpac-workspace)
├─ If pull succeeds:
│  └─ Update code in place
├─ If pull fails:
│  └─ Restore from backup automatically
└─ Log results
```

### Features

- ✅ **Automatic hourly updates** - Stay current with latest code
- ✅ **Pre-sync backups** - Never lose code on update failure
- ✅ **Instant rollback** - Revert to previous version if needed
- ✅ **Backup history** - Keep last 10 backups per repo
- ✅ **GitHub authentication** - Uses your PAT for private repos

### Backup Management

```
Backups Location: /home/user/jico-system/backups/

Structure:
jico-workspace_20260630_134500/
nacpac-workspace_20260630_134500/
jico-workspace_20260630_123000/
nacpac-workspace_20260630_123000/
... (keeps last 10)
```

### Manual Git Operations

**Check sync status:**
```
git_sync = GitSync(token="YOUR_GITHUB_TOKEN")
status = await git_sync.get_sync_status()
```

**Manually sync repos:**
```
await git_sync.manual_sync()              # Sync all
await git_sync.manual_sync("jico-workspace")  # Sync specific
```

**Restore from backup:**
```
await git_sync.restore_backup("jico-workspace")
```

**View backup history:**
```
backups = await git_sync.get_backup_history("jico-workspace")
```

---

## 🚨 Circuit Breaker Pattern

Prevents cascade failures by stopping requests to failing services.

### How It Works

```
Service Request Flow:

1. CLOSED (Normal)
   ├─ Requests go through normally
   └─ Count failures

2. OPEN (Failing)
   ├─ Reject all requests immediately
   ├─ Stop overloading failing service
   └─ Wait for recovery timeout

3. HALF_OPEN (Testing)
   ├─ Allow limited test requests
   ├─ If test succeeds → Return to CLOSED
   └─ If test fails → Return to OPEN
```

### Protected Services

| Service | Failure Threshold | Recovery Timeout |
|---------|------------------|------------------|
| Discord Bot | 3 failures | 30 seconds |
| Anthropic API | 5 failures | 60 seconds |
| Cloudflare R2 | 5 failures | 60 seconds |
| Oracle VM | 3 failures | 120 seconds |

### Circuit Breaker Behavior

**CLOSED → OPEN (Service failing):**
```
5 consecutive failures detected
↓
Circuit breaker OPENS
↓
New requests immediately rejected (fast-fail)
↓
Service gets time to recover (without being hammered)
```

**OPEN → HALF_OPEN (Recovery time elapsed):**
```
30 seconds recovery timeout passed
↓
Circuit breaker enters HALF_OPEN
↓
Test requests allowed
↓
If test succeeds → Back to CLOSED
If test fails → Back to OPEN (retry after delay)
```

---

## 🔁 Recovery Procedures

Automatic recovery procedures for each component:

### Discord Bot Recovery
- Attempt reconnection
- Reset connection state
- Reinitialize event listeners
- Resume from last known state

### Anthropic API Recovery
- Test API connectivity
- Clear cache if corrupted
- Reinitialize API client
- Retry requests

### Cloudflare R2 Recovery
- Test bucket connectivity
- Verify credentials
- Retry with exponential backoff
- Fall back to cache if available

### Auto Mode Recovery
- Restart task executor
- Requeue pending tasks
- Resume from last checkpoint
- Resume normal operation

---

## 📊 Monitoring Dashboard

Real-time system status view.

### Discord Commands

**Get system health:**
```
!health_status
```

Response:
```
🏥 System Health Status
Discord Bot: ✅ Healthy
Anthropic API: ✅ Healthy
Cloudflare R2: ✅ Healthy
Task Queue: ✅ Healthy
Auto Mode: ✅ Healthy
Disk Space: ✅ 45% used
Memory: ✅ 62% used

Last Check: 2026-06-30 13:45:00
```

**Get circuit breaker status:**
```
!circuit_breaker_status
```

Response:
```
🔌 Circuit Breaker Status
Discord Bot: 🟢 CLOSED (0/3 failures)
Anthropic API: 🟢 CLOSED (1/5 failures)
Cloudflare R2: 🟢 CLOSED (0/5 failures)
Oracle VM: 🟢 CLOSED (0/3 failures)
```

**Get git sync status:**
```
!git_sync_status
```

Response:
```
🔄 Git Sync Status
jico-workspace: ✅ In Sync
  Last sync: 2026-06-30 13:00:00
  Latest: a1b2c3d Fix: update compression layer

nacpac-workspace: ✅ In Sync
  Last sync: 2026-06-30 13:00:00
  Latest: e4f5g6h Feature: add new worker
```

**View backup history:**
```
!backup_history jico-workspace
```

Response:
```
📦 Backup History for jico-workspace

1. jico-workspace_20260630_134500 (2.3 MB)
2. jico-workspace_20260630_123000 (2.3 MB)
3. jico-workspace_20260630_113000 (2.3 MB)
4. ... (last 10 backups)
```

---

## ⚠️ Critical Failure Handling

What happens when a component exceeds recovery limits.

### Critical Failure Procedure

```
Component fails 5 times:
├─ Component disabled
├─ System enters degraded mode
├─ Critical alert sent
│  ├─ Discord notification
│  ├─ Telegram alert
│  └─ Log file entry
├─ Administrator notified
└─ Fallback behavior activated
```

### Degraded Mode Operation

- ❌ Failed component disabled
- ⚠️ System continues with reduced functionality
- ✅ Other components operate normally
- 📋 Tasks queued but may not execute (if critical component)
- 📊 Health monitor continues checking
- 🔄 Retries recovery periodically

### Example: Anthropic API Failure

```
Critical Anthropic API Failure:
├─ Message compression disabled
├─ Direct task execution fallback
├─ System handles raw Discord messages
├─ Tasks routed without NLP compression
└─ Administrator needed to restore

Status: ⚠️ Degraded Mode
Warning: Natural language compression unavailable
```

---

## 🚀 Starting the Fail-Safe System

### Launch with all protections:

```bash
python main.py
```

Auto-starts:
- ✅ Health Monitor
- ✅ Git Sync Scheduler (hourly)
- ✅ Circuit Breaker Manager
- ✅ Auto Mode Executor
- ✅ Discord Bot

### Configuration

Edit `jico-system/.env` for thresholds:

```bash
# Health check (seconds)
HEALTH_CHECK_INTERVAL=30
HEALTH_FAILURE_THRESHOLD=3
HEALTH_MAX_RECOVERY=5

# Git sync (minutes)
GIT_SYNC_INTERVAL=60
GIT_SYNC_BACKUP_KEEP=10

# Circuit breaker (seconds)
CIRCUIT_FAILURE_THRESHOLD=3
CIRCUIT_RECOVERY_TIMEOUT=60
```

---

## 📈 Monitoring & Logging

### Log Levels

```
DEBUG   - Detailed component info
INFO    - Normal operations ✅
WARNING - Degraded performance ⚠️
ERROR   - Component failure ❌
CRITICAL - System failure 🚨
```

### Log Locations

- **Main log**: `/tmp/jico-system.log`
- **Health log**: `/tmp/jico-health.log`
- **Sync log**: `/tmp/jico-sync.log`
- **Backups**: `/home/user/jico-system/backups/`

### Watch Logs in Real-Time

```bash
# All logs
tail -f /tmp/jico-system.log

# Health only
tail -f /tmp/jico-system.log | grep "Health"

# Errors only
tail -f /tmp/jico-system.log | grep "ERROR"

# Circuit breaker
tail -f /tmp/jico-system.log | grep "circuit"
```

---

## 🔐 Backup & Restore Strategy

### Automatic Backups

- ✅ Before every git sync
- ✅ Timestamped for easy identification
- ✅ Limited to last 10 backups (space efficient)
- ✅ Full repo snapshots (can restore any version)

### Manual Backup

```python
await git_sync.create_backup("jico-workspace", repo_path)
```

### Manual Restore

```python
# Restore latest backup
await git_sync.restore_backup("jico-workspace")

# List available backups
backups = await git_sync.get_backup_history("jico-workspace")
```

---

## 🛠️ Troubleshooting

### System is in Degraded Mode

1. Check which component failed: `!circuit_breaker_status`
2. View logs: `tail -f /tmp/jico-system.log`
3. Attempt recovery: `!health_status`
4. If persists, manual restart needed

### Git Sync Failed

1. Check status: `!git_sync_status`
2. View backup: `!backup_history <repo>`
3. Manual restore: `await git_sync.restore_backup()`
4. Check GitHub token validity

### Out of Disk Space

1. Check usage: `df -h`
2. Clean old backups: `rm /home/user/jico-system/backups/old_*`
3. Monitor: `!health_status`

---

## 📋 Checklist for Production

Before deploying to Oracle VM:

- ✅ Health Monitor enabled
- ✅ Git Sync configured with valid token
- ✅ Circuit Breakers tested
- ✅ Backup location accessible
- ✅ Logging configured
- ✅ Discord notifications enabled
- ✅ Telegram alerts enabled
- ✅ Auto Mode running
- ✅ Initial backup created
- ✅ Administrator contacts documented

---

## 🎯 Summary

Your JICO system now has **enterprise-grade reliability**:

| Feature | Status |
|---------|--------|
| Health Monitoring | ✅ 24/7 active |
| Auto Recovery | ✅ 5 attempts per component |
| Git Sync | ✅ Hourly with backup |
| Circuit Breakers | ✅ 4 protected services |
| Backup/Restore | ✅ Last 10 versions |
| Graceful Degradation | ✅ Continues with reduced features |
| Logging | ✅ Real-time monitoring |
| Administrator Alerts | ✅ Discord + Telegram |

**Result:** System stays operational even during failures. Auto-recovery prevents crashes. Hourly updates keep code current. Backups prevent data loss.

🚀 **Your system is production-ready with fail-safe protection!**
