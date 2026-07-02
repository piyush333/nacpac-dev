# Jico Agentic System

Multi-agent orchestration platform for Jico organization. Autonomous code builds, deployments, and backups.

## Architecture

```
Discord (user interface)
    ↓
Orchestrator (intent parsing, routing)
    ↓
Dev Agents (NacPac, Jico Life)
    ├─ Git tools (clone, branch, commit, push)
    ├─ Build tools (EAS, npm, Python scripts)
    ├─ Deploy tools (staging, production, Netlify)
    └─ Backup tools (R2, Google Drive, GitHub)
    ↓
Supabase (task queue, cost tracking, memory)
```

## Quick Start

### 1. Install dependencies

```bash
cd /home/ubuntu/nacpac-dev/agentic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.template .env
# Edit .env with your actual values
nano .env
```

### 3. Run locally (testing)

```bash
python3 -m agentic.main
```

### 4. Deploy as systemd service (Oracle VM)

```bash
sudo cp systemd/jico-agentic.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jico-agentic
sudo systemctl start jico-agentic
sudo systemctl status jico-agentic
```

View logs:
```bash
sudo journalctl -u jico-agentic -f
```

## Discord Commands

### `/task`
Submit a task to the agentic system.

```
/task brand:nacpac request:Build APK for v2.1
/task brand:jico_life request:Deploy AR experience to staging
```

### `!status`
Show current system status (branches, commits, last deploys).

### `!help_agentic`
Show help and available commands.

## Supported Tasks

### NacPac
- **Build APK**: `eas build --platform android --profile preview`
- **Build EXE**: `npm run build` (desktop/)
- **Deploy to staging**: Auto-upload + restart
- **Deploy to production**: Requires approval

### Jico Life
- **Build GLB**: `python scripts/build_glb.py [render.png]`
- **Deploy to staging**: Push to staging branch → Netlify auto-deploys
- **Deploy to production**: Push to main → Netlify auto-deploys

## Automation

- ✅ Auto-build on code changes
- ✅ Auto-deploy to staging
- ✅ Auto-backup (R2 + Google Drive + GitHub)
- ✅ Auto-retry on failures
- ✅ Auto-heal from crashes
- 🟡 Manual approval: production deploys, cost overruns

## Cost Tracking

Every API call is logged to Supabase with token count and cost.

- **Haiku**: $0.80/M input tokens, $4.00/M output tokens (cheap)
- **Sonnet**: $3.00/M input tokens, $15.00/M output tokens (smart)
- **Daily cap**: $10/day (hard stop)
- **Monthly cap**: $50/month (warning at 80%)

## Failsafe Mechanisms

1. **Dead Letter Queue**: Failed tasks go to `failed_tasks` table
2. **Auto-retry**: Exponential backoff (2s, 4s, 8s, 16s) up to 3 attempts
3. **Health Monitor**: Ping every 5 min; auto-restart if down
4. **Discord Alerts**: Critical errors alert user
5. **Rollback**: `!rollback nacpac-apk` restores last successful build

## Files

- `main.py` — Entry point
- `config.py` — Environment variables
- `memory.py` — Supabase client
- `cost_tracker.py` — Token usage & budget enforcement
- `agents/` — Orchestrator, NacPac Dev, Jico Life Dev
- `tools/` — Git, Build, Deploy, Backup operations
- `discord_bot.py` — Discord interface
- `failsafe/` — Health monitoring, auto-retry, scheduling
- `systemd/jico-agentic.service` — Systemd service file
- `.env.template` — Configuration template

## Logs

- Local: `/tmp/jico-agentic.log`
- System: `journalctl -u jico-agentic`

## Next Steps

1. Set up Supabase project + schema
2. Create `.env` from `.env.template`
3. Deploy to Oracle VM
4. Test via Discord: `/task brand:nacpac request:Build APK`
5. Monitor logs: `journalctl -u jico-agentic -f`

---

**Status:** Phase 1 complete. Ready for Supabase setup + Oracle deployment.
