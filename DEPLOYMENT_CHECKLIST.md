# Oracle VM Deployment Checklist

## Tomorrow - Deploy to Oracle VM (144.24.129.201)

### 1. SSH to Oracle VM
```bash
ssh -i /home/ubuntu/.ssh/oracle_key.key ubuntu@144.24.129.201
```

### 2. Run deployment script
```bash
cd nacpac-dev
bash DEPLOY_TO_ORACLE.sh
```

### 3. Configure EAS (Expo build service)
```bash
cd /home/ubuntu/nacpac-dev
eas login
# Enter your EAS credentials
```

### 4. Verify repos exist
```bash
ls -la /home/ubuntu/nacpac-workspace-main
ls -la /home/ubuntu/jico-workspace  # May not exist yet
```

### 5. Start Discord bot (runs forever)
```bash
python agentic/discord_bot.py
# Should say: ✅ Bot logged in as JicoAgent#1234
```

### 6. Test in Discord
In your Discord server #general channel, type:
```
build nacpac apk
```

Bot should respond with:
- Parsed intent
- Approval buttons
- ✓ Approve / ✗ Reject

Click Approve → Build starts → Results posted

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `DISCORD_TOKEN not set` | Update `agentic/.env` with real token |
| `eas command not found` | Run `npm install -g eas-cli` |
| `git: command not found` | Ubuntu has git, should work |
| `npx: not found` | Need Node.js 18+ installed |

---

## What to expect

- **First build**: Will download EAS, cache, compile → 5-10 min
- **Subsequent builds**: Faster (2-3 min)
- **Failures**: Check logs in Discord reply
- **Cost tracking**: Logs to Supabase (may show 403 if creds wrong, OK to ignore)

---

## If you need help during deployment
- Check system logs: `python agentic/cli.py status`
- Check Discord bot: Look for errors in terminal
- Check repos exist: `ls -la /home/ubuntu/nacpac-workspace-main`

