# Production Setup - Oracle VM

## Phase 1: Clone Real Repos

On Oracle VM:
```bash
cd /home/ubuntu

# NacPac repo
git clone https://github.com/piyush333/nacpac-workspace-main.git
cd nacpac-workspace-main
npm install
cd ..

# Jico repo  
git clone https://github.com/piyush333/jico-workspace.git
cd jico-workspace
npm install
cd ..
```

Verify paths in `/home/ubuntu/nacpac-dev/agentic/.env`:
```
NACPAC_REPO_PATH=/home/ubuntu/nacpac-workspace-main
JICO_REPO_PATH=/home/ubuntu/jico-workspace
```

---

## Phase 2: Configure EAS

```bash
cd /home/ubuntu/nacpac-dev
eas login
# Enter EAS account credentials
# Choose default project
```

Verify in `.env`:
```
EAS_BUILD_PROFILE=preview  # or change to production
```

---

## Phase 3: Enable Approval Flow

The Discord bot already has approval buttons! They appear when you:

**In Discord #general:**
```
build nacpac apk
```

Bot shows:
```
📋 Task Approval
Message: build nacpac apk
Agent: nacpac_dev
Brand: nacpac
Task Type: build

[✓ Approve] [✗ Reject]
```

Click **✓ Approve** → Build starts → Results posted

---

## Phase 4: Test Real Build

**In Discord #general:**
```
build nacpac apk
```

Expected flow:
1. Bot shows approval buttons
2. You click ✓
3. EAS build starts (takes 5-10 min first time)
4. APK download link posted to Discord

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `eas: command not found` | `npm install -g eas-cli` |
| `repo not found` | Verify paths: `ls -la /home/ubuntu/nacpac-workspace-main` |
| Build fails | Check EAS logs: `eas build --status` |
| Bot not responding | Check: `ps aux \| grep discord_bot` |

---

## Commands Reference

**Restart bot:**
```bash
killall python3
nohup python3 -m agentic.discord_bot > discord_bot.log 2>&1 &
```

**Monitor:**
```bash
tail -f discord_bot.log
```

**Check system:**
```bash
python3 agentic/cli.py list-agents
python3 agentic/cli.py status
```

