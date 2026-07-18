# Phase 8 Deployment Checklist

**Timeline**: ~2 hours from start to verified production operation

---

## Pre-Deployment (1 hour)

### Code Preparation
- [x] All Phase 1-7 work committed and pushed to `claude/agentic-system-org-j9gvae`
- [x] `agentic/secrets_manager.py` created and tested locally
- [x] `discord_bot.py` updated to call `init_secrets()` on startup
- [x] All tests passing: `python -m pytest agentic/tests/`
- [x] No hardcoded credentials in code or config files

### Supabase Verification
- [x] `secrets` table exists and contains all 11 credentials
  - [x] SUPABASE_URL, SUPABASE_KEY (service role)
  - [x] DISCORD_BOT_TOKEN, GITHUB_TOKEN, EAS_TOKEN
  - [x] R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ACCOUNT_ID, R2_BUCKET_NAME
  - [x] GOOGLE_DRIVE_BACKUP_FOLDER_ID, BUILD_TEST_MODE=false

### R2 Setup
- [x] Cloudflare R2 bucket: `nacpac-workspace`
- [x] R2 credentials in Supabase
- [x] Bucket publicly readable

### Google Drive Setup
- [x] Backup folder created
- [x] Folder ID in Supabase
- [x] Sharing configured

### Discord & GitHub
- [x] Bot token fresh and working
- [x] GitHub token in Supabase
- [x] All required channels exist

---

## DigitalOcean Setup (30 min)

### Create App
- [ ] GitHub connected to DigitalOcean
- [ ] Repository: `jico-org/nacpac-workspace`
- [ ] Branch: `claude/agentic-system-org-j9gvae`
- [ ] Auto-deploy enabled

### Environment Variables (ONLY these two)
- [ ] SUPABASE_URL
- [ ] SUPABASE_KEY
- [ ] All other credentials come from Supabase

### Resource Allocation
- [ ] CPU: 1 shared
- [ ] Memory: 512 MB
- [ ] Disk: 2 GB

### Health Check
- [ ] Endpoint: `/health`
- [ ] Port: 8080
- [ ] Interval: 5 min

---

## Post-Deployment Testing (30 min)

### Bot Verification
- [ ] Bot online in Discord
- [ ] Responds to messages
- [ ] Secrets loaded (check logs)

### Full Workflow Test
- [ ] Feature request → Proposal → Approval
- [ ] Build task → Approval → Completes
- [ ] Deploy task → Approval → Completes

### Backup Verification
- [ ] Artifacts in R2
- [ ] Download links work
- [ ] Artifacts also in Google Drive

### Supabase Checks
- [ ] Tasks logged correctly
- [ ] Costs tracked accurately
- [ ] No errors in logs

---

## Monitoring Setup (15 min)

- [ ] DigitalOcean alerts configured
  - [ ] Deployment failures
  - [ ] Resource usage (CPU > 80%, Memory > 90%)
  - [ ] Health check failures
- [ ] Discord notifications working
- [ ] Email alerts to piyushjindal333@gmail.com

---

## Cost Verification

```sql
SELECT SUM(cost_usd) as today FROM costs WHERE DATE(created_at) = CURRENT_DATE;
SELECT SUM(cost_usd) as month FROM costs WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE);
```

- [ ] Daily spend < $10
- [ ] Monthly spend < $50

---

## Final Security Audit

- [ ] No credentials in DigitalOcean logs
- [ ] No credentials in git history
- [ ] TLS on all connections
- [ ] R2 bucket secure
- [ ] Google Drive folder secure

---

## Post-Deployment Monitoring (1 week)

### Daily Checks
- [ ] Bot online and responsive
- [ ] At least 1 successful task
- [ ] No unhandled errors
- [ ] Budget within limits

### Weekly Review
- [ ] 99%+ uptime
- [ ] 5+ successful tasks
- [ ] 0 critical errors
- [ ] Costs accurate within 5%
- [ ] All artifacts backed up

---

**Phase 8 Complete**: System LIVE 🚀
**Next**: Add Jico Life Dev Agent (Phase 1-8 repeated)
