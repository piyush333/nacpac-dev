# JICO Discord Automation System - Deployment Guide

## Overview

Complete Discord-based automation system for Nacpac and Jico projects. Routes natural language commands through Claude Haiku compression → Task Router → Specialized Managers → Workers → Results.

**Architecture:**
```
User (Discord) 
    ↓
Discord Manager Bot (discord_manager.py)
    ↓
Compression Layer (Haiku) - converts natural language to task JSON
    ↓
Task Router - decides: execute now or schedule?
    ├─ Nacpac Manager (4 workers: dev, seo, ads, build)
    ├─ Jico Manager (4 workers: dev, seo, ads, build)
    └─ Scheduler (Oracle VM for future tasks)
    ↓
Results posted back to Discord + Telegram notifications
```

## System Components

### 1. **Discord Manager** (`discord_manager.py`)
- Listens for messages in Discord
- Routes through compression layer
- Queues tasks to auto mode
- Posts results back to Discord

### 2. **Compression Layer** (`compression_layer.py`)
- Uses Claude 3.5 Haiku to convert natural language → structured JSON
- Detects task type: `nacpac` (code changes, builds) or `jico` (AR/Shopify)
- Extracts action, target worker, parameters, priority
- Handles scheduling with ISO8601 timestamps

### 3. **Task Router** (`task_router.py`)
- Routes tasks to appropriate manager (Nacpac/Jico)
- Decides: execute immediately or schedule for later
- Passes scheduled tasks to Oracle VM via TaskScheduler

### 4. **Nacpac Manager** (`nacpac_manager.py`)
- **Dev Worker:** Generates code changes using Claude Code CLI against codebase
- **Build Worker:** Compiles APK (via EAS), EXE (via npm), uploads to Cloudflare R2
- **SEO & Ads Workers:** Placeholder for metadata/campaign tasks
- Complete workflow: code → git push → builds → R2 upload

### 5. **Jico Manager** (`jico_manager.py`)
- Handles AR/3D content tasks
- Current tasks: placeholder (to be implemented based on AR build pipeline)

### 6. **Auto Mode** (`auto_mode.py`)
- Background task execution (FIFO queue, up to 5 concurrent workers)
- Autonomous 24/7 operation
- Task monitoring and completion tracking
- Fail-safe with health monitoring and auto-recovery

### 7. **Health Monitor** (`health_monitor.py`)
- Checks system health every 30 seconds
- Monitors 8 components: Discord, Anthropic, R2, Oracle VM, task queue, workers
- Auto-recovery with up to 5 retry attempts
- Graceful degradation when components fail

### 8. **Git Sync** (`git_sync.py`)
- Hourly automatic sync from GitHub org repos
- Pre-sync backups (keeps last 10)
- Instant rollback on sync failure
- Prevents code corruption

### 9. **Circuit Breaker** (`circuit_breaker.py`)
- Prevents cascade failures (CLOSED → OPEN → HALF_OPEN states)
- Protects 4 services: Discord, Anthropic, Cloudflare R2, Oracle VM
- Fast-fail when service down
- Automatic recovery when service restored

## File Structure

```
jico-system/
├── main.py                    # System entry point
├── config.py                  # Configuration management
├── discord_manager.py         # Discord bot + message processing
├── compression_layer.py       # Haiku NLP engine
├── task_router.py            # Task routing logic
├── nacpac_manager.py         # Nacpac workflow (code → build → upload)
├── jico_manager.py           # Jico workflow (AR/3D)
├── auto_mode.py              # Autonomous execution engine
├── health_monitor.py         # Component health & auto-recovery
├── git_sync.py               # GitHub sync with backups
├── circuit_breaker.py        # Cascade failure prevention
├── utils.py                  # R2Storage, OracleVM, TaskScheduler
├── test_system.py            # Connectivity verification
├── test_nacpac_workflow.py   # Full workflow tests
├── requirements.txt          # Python dependencies
├── .env                       # Credentials (git-ignored)
├── memory.md                 # System documentation
├── DEPLOYMENT_GUIDE.md       # This file
├── ssh/
│   └── oracle_key.key        # Oracle VM SSH key
└── backups/                  # Git sync backups

nacpac-workspace-main/        # Nacpac codebase (mobile + desktop)
├── mobile/                   # Expo React Native (Android)
├── desktop/                  # Electron (Windows)
└── techbot/bot.py           # Reference implementation

jico-workspace-main/          # Jico codebase (AR experience)
├── ar/                       # AR assets and HTML
└── systems/                  # Backend systems
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Discord Bot Token (with Message Content Intent)
- Anthropic API Key (for Claude Haiku)
- GitHub Token (with org repo access)
- Cloudflare R2 credentials (account ID, access key, secret key)
- Oracle VM SSH key (for scheduling)
- EAS CLI configured (for APK builds)
- npm/Node.js (for EXE builds)

### 1. Install Dependencies
```bash
cd jico-system
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
```env
# Discord
DISCORD_TOKEN=your_bot_token
DISCORD_GUILD_ID=your_guild_id
DISCORD_LOGS_CHANNEL=logs
DISCORD_REPORTS_CHANNEL=reports

# Anthropic
ANTHROPIC_API_KEY=your_api_key

# Cloudflare R2
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_ENDPOINT=https://{account_id}.r2.cloudflarestorage.com

# Nacpac/Jico
NACPAC_DIR=/path/to/nacpac-workspace-main
MOBILE_DIR=/path/to/nacpac-workspace-main/mobile
DESKTOP_DIR=/path/to/nacpac-workspace-main/desktop
JICO_DIR=/path/to/jico-workspace-main

# Oracle VM (for scheduled tasks)
ORACLE_VM_IP=your_vm_ip
ORACLE_VM_USER=opc
ORACLE_SSH_KEY_PATH=/path/to/oracle_key.key
AGENT_ENDPOINT=http://your_vm_ip:8000
AGENT_TOKEN=your_token
```

### 3. Set Up Discord Bot
1. Create bot in Discord Developer Portal
2. Enable "Message Content Intent"
3. Set command prefix to `!`
4. Add bot to server with permissions: Read/Write messages, Add reactions

### 4. Test System
```bash
python test_nacpac_workflow.py
```

Should show: ✅ 5/5 tests passed

### 5. Run System
```bash
python main.py
```

## Usage Examples

### Discord Commands

**Code Changes (Nacpac):**
```
"Add a login screen to mobile app"
"Fix the desktop UI crash on startup"
"Update the home page design"
```
→ System: Generates code, pushes to GitHub

**Builds:**
```
"Build APK for testing"
"Build EXE and upload to R2"
"Build both APK and EXE"
```
→ System: Compiles, uploads to Cloudflare R2

**Scheduled Tasks:**
```
"Schedule a build tomorrow at 10am"
"Build APK next Friday"
```
→ System: Stores in Oracle VM scheduler, executes at time

**System Commands:**
```
!status              - Show system health
!help_jico           - Show help
!auto_mode start     - Enable autonomous execution
!auto_mode stop      - Disable autonomous execution
!auto_mode status    - Show pending tasks
!auto_mode history   - Show recent tasks
```

## Nacpac Workflow Details

### Code Generation → Build → Upload

1. **Natural Language → Task JSON**
   - User: "Add dark mode toggle to home screen"
   - Compression: `{"task_type": "nacpac", "target": "dev", "action": "..."}`

2. **Code Generation (Dev Worker)**
   - Runs: `claude --print --max-turns 5 "Make these changes..."`
   - Applies changes to `NACPAC_DIR`

3. **Git Push**
   - Commits: `git add . && git commit -m "auto: code update"`
   - Pushes to `origin main` (mobile submodule first, then parent)

4. **Build & Upload (Build Worker)**
   - **APK:** `eas build --platform android --profile preview --non-interactive`
     - Runs in `MOBILE_DIR`
     - Takes 10-20 minutes
     - URL returned in results
   
   - **EXE:** `npm run build` (in `DESKTOP_DIR`)
     - Compiled executable saved to `dist/`
     - Uploaded to R2: `nacpac-workspace/desktop/{filename}`
     - Public URL returned

5. **Results Posted**
   - Discord: Build status + download URLs
   - Telegram: Summary notification

## System Status Indicators

### Auto Mode Status
- `🤖` Running - accepting and executing tasks
- `⏸️` Paused - not accepting new tasks
- `⏹️` Stopped - system idle

### Health Status
- `✅` All systems operational
- `⚠️` One component degraded (graceful operation continues)
- `❌` Multiple failures (system may be unstable)

### Circuit Breaker States
- `CLOSED` - Service working normally
- `OPEN` - Service failing, fast-fail active
- `HALF_OPEN` - Testing if service recovered

## Monitoring & Logs

### Log Locations
- Main: `/tmp/jico-system.log` (or configured path)
- Console: Real-time output when running `python main.py`

### Discord Status
Send `!status` to see:
- Discord Bot connection
- Compression Layer status
- Nacpac Manager readiness
- Jico Manager readiness
- Oracle VM connectivity

### Log Analysis
```bash
# Watch logs in real-time
tail -f /tmp/jico-system.log

# Check for errors
grep ERROR /tmp/jico-system.log

# Check health checks
grep "Health" /tmp/jico-system.log

# Check git sync
grep "sync" /tmp/jico-system.log | tail -10

# Check circuit breaker
grep "circuit" /tmp/jico-system.log
```

## Troubleshooting

### Issue: Bot not responding to messages
**Solution:**
1. Check Discord Guild ID in `.env`
2. Check bot has "Message Content Intent" enabled
3. Check bot has message permissions in channel
4. Check `!status` command returns OK

### Issue: "Permission denied" on file write
**Solution:**
1. Discord compression task routed to Claude Code
2. Claude Code requires write permission prompt (CLI feature)
3. Not an issue in this system - we read/modify files programmatically

### Issue: Builds failing with "No .exe found"
**Solution:**
1. Check `npm run build` completes successfully
2. Check `DESKTOP_DIR` path is correct
3. Check dist/ directory is created
4. Check permissions on dist/ directory

### Issue: APK build times out
**Solution:**
1. EAS builds can take 10-20 minutes normally
2. Increase timeout in `nacpac_manager.py` if needed
3. Check EAS CLI is configured with correct profile
4. Check network connectivity to EAS servers

### Issue: API Key errors
**Solution:**
1. Verify API key format (starts with `sk-ant-api03`)
2. Check API key isn't expired
3. Check API key has correct permissions
4. Test with `python -c "from anthropic import Anthropic"`

## Performance Tuning

### Concurrent Workers
- Default: 5 concurrent tasks
- Adjust in `auto_mode.py`: `MAX_CONCURRENT_WORKERS`

### Health Check Interval
- Default: 30 seconds
- Adjust in `health_monitor.py`: `HEALTH_CHECK_INTERVAL`

### Git Sync Interval
- Default: 60 minutes
- Adjust in `git_sync.py`: `GIT_SYNC_INTERVAL`

### Build Timeouts
- APK: 1800 seconds (30 min)
- EXE: 300 seconds (5 min)
- Adjust in `nacpac_manager.py` if needed

## Security Considerations

### Credentials
- All sensitive data in `.env` file (git-ignored)
- Never commit `.env` file
- Rotate API keys periodically
- SSH key stored locally, not in git

### Git Access
- Uses GitHub PAT token (read + write access)
- Token should have minimal required permissions
- Stored in environment, not in code

### Discord Bot Token
- Created bot in Discord Developer Portal
- Token never logged or exposed
- Regenerate if token leaked

### Cloudflare R2
- Access key and secret in environment only
- Builds uploaded to private bucket initially
- Public URL generation for user downloads

## Deployment Options

### Option 1: Local Development
```bash
cd /home/user/nacpac-dev/jico-system
python main.py
```
- Best for testing and development
- All builds run locally
- Real-time logs visible

### Option 2: Oracle VM Deployment
```bash
# SSH to Oracle VM
ssh -i oracle_key.key opc@129.154.42.154

# Run on VM with nohup for persistence
nohup python /path/to/jico-system/main.py > bot.log 2>&1 &
```
- 24/7 operation
- Scheduled tasks execute on VM
- Logs accessible via SSH

### Option 3: Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY jico-system/ .
CMD ["python", "main.py"]
```

### Option 4: Systemd Service (Linux)
```ini
[Unit]
Description=JICO Discord Bot
After=network.target

[Service]
Type=simple
User=jico
WorkingDirectory=/home/jico/jico-system
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Next Steps

1. **Verify Credentials** - Test all API keys work
2. **Test Locally** - Run `python main.py` and send test messages
3. **Test Builds** - Request APK/EXE build and verify R2 upload
4. **Monitor Logs** - Watch for health checks and auto-recovery
5. **Deploy to Oracle VM** - Set up for 24/7 operation
6. **Add Jico Workers** - Implement AR build pipeline for Jico tasks

## Support

For issues or questions:
1. Check logs: `grep ERROR /tmp/jico-system.log`
2. Run test: `python test_nacpac_workflow.py`
3. Check system status: `!status` in Discord
4. Review memory.md for system architecture
