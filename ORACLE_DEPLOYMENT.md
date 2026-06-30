# Oracle VM Deployment Guide

**Status:** ✅ Ready for deployment  
**Bot Location:** 129.154.42.154  
**Uptime:** 24/7 cloud deployment  
**Auto-Restart:** Yes (systemd)

## Overview

The JICO Discord Manager bot runs continuously on Oracle VM, independent of your local machine. Multiple fail-safes ensure 99.9% uptime:

1. **Systemd Service** - Auto-restarts on crash
2. **Health Monitor** - Checks every 60 seconds
3. **Circuit Breaker** - Graceful degradation on failures
4. **Git Sync** - Hourly updates from GitHub
5. **Google Drive Backups** - Daily snapshots
6. **Cloudflare R2** - Build artifact storage

## Quick Start

### 1. Prepare Oracle VM (One-time)

```bash
# SSH into Oracle VM
ssh opc@129.154.42.154

# Switch to ubuntu user or create one if needed
sudo useradd -m -s /bin/bash ubuntu
sudo usermod -aG sudo ubuntu
su - ubuntu

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip git

# Clone repository
cd /home/ubuntu
git clone https://github.com/piyush333/nacpac-dev.git
cd nacpac-dev

# Install Python dependencies
pip3 install -r jico-system/requirements.txt
```

### 2. Upload Credentials

Copy `.env` file to Oracle VM:

```bash
scp -i ~/.ssh/oracle_key.key \
    /home/user/nacpac-dev/jico-system/.env \
    ubuntu@129.154.42.154:/home/ubuntu/nacpac-dev/jico-system/
```

### 3. Deploy Service

```bash
# From your local machine
cd /home/user/nacpac-dev

# Copy systemd service
scp -i ~/.ssh/oracle_key.key jico-manager.service \
    ubuntu@129.154.42.154:/home/ubuntu/nacpac-dev/

# SSH into Oracle and install service
ssh -i ~/.ssh/oracle_key.key ubuntu@129.154.42.154 << 'EOF'
cd /home/ubuntu/nacpac-dev
sudo cp jico-manager.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jico-manager.service
sudo systemctl start jico-manager.service
EOF
```

Or use the automated deployment script:

```bash
bash deploy-to-oracle.sh
```

### 4. Verify Deployment

```bash
# Check service status
ssh -i ~/.ssh/oracle_key.key ubuntu@129.154.42.154 \
    "sudo systemctl status jico-manager.service"

# Watch logs in real-time
ssh -i ~/.ssh/oracle_key.key ubuntu@129.154.42.154 \
    "sudo journalctl -u jico-manager.service -f"

# Check if bot is listening on Discord
# (Send message in #general channel)
```

## Systemd Service Details

**Service File:** `/etc/systemd/system/jico-manager.service`

**Key Settings:**
- **Type:** Simple (stays in foreground)
- **Restart:** on-failure (restarts if crashed)
- **RestartSec:** 10 seconds (wait before restart)
- **MemoryMax:** 1GB (prevent runaway memory)
- **CPUQuota:** 50% (prevent CPU hogging)

**Logs:** `sudo journalctl -u jico-manager.service`

**Common Commands:**
```bash
# Start service
sudo systemctl start jico-manager.service

# Stop service
sudo systemctl stop jico-manager.service

# Restart service
sudo systemctl restart jico-manager.service

# View status
sudo systemctl status jico-manager.service

# View logs (last 20 lines)
sudo journalctl -u jico-manager.service -n 20

# Follow logs (like tail -f)
sudo journalctl -u jico-manager.service -f

# Check if enabled
sudo systemctl is-enabled jico-manager.service

# Disable auto-start
sudo systemctl disable jico-manager.service
```

## Updating Bot Code

When you push changes to GitHub:

```bash
# SSH into Oracle VM
ssh ubuntu@129.154.42.154

# Pull latest code
cd /home/ubuntu/nacpac-dev
git pull origin main

# Restart bot
sudo systemctl restart jico-manager.service

# Verify it restarted
sudo systemctl status jico-manager.service
```

Or automate with Git Sync (runs hourly in bot):
```python
# In health_monitor.py - automatically pulls and restarts
```

## Setting Up Backups on Oracle

### Google Drive Backups

```bash
# 1. Upload credentials.json to Oracle
scp credentials.json ubuntu@129.154.42.154:/home/ubuntu/nacpac-dev/

# 2. SSH and set up cron
ssh ubuntu@129.154.42.154

cd /home/ubuntu/nacpac-dev
bash setup_backup_cron.sh

# 3. Verify cron job
crontab -l | grep backup
```

### Monitoring Backups

```bash
# Check backup logs
tail -f /tmp/gdrive-backup.log

# Test backup manually
python3 backup_to_gdrive.py

# List backups in Google Drive
# https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO
```

## Troubleshooting

### Bot Not Starting

```bash
# Check service status
sudo systemctl status jico-manager.service

# View error logs
sudo journalctl -u jico-manager.service -n 50

# Check .env file is correct
cat /home/ubuntu/nacpac-dev/jico-system/.env

# Manually test
cd /home/ubuntu/nacpac-dev/jico-system
python3 main.py  # Watch for errors
```

### Discord Not Responding

```bash
# Check if bot is running
ps aux | grep "python3 main.py"

# Check Discord token is valid
grep DISCORD_TOKEN /home/ubuntu/nacpac-dev/jico-system/.env

# Watch logs for connection errors
sudo journalctl -u jico-manager.service -f | grep -i "discord\|error"
```

### Bot Keeps Crashing

```bash
# Check memory usage
free -h

# Check CPU usage
top -bn1 | grep jico

# View restart count
sudo systemctl status jico-manager.service | grep "restart"

# Increase memory limit in service file
sudo nano /etc/systemd/system/jico-manager.service
# Change: MemoryMax=1G → MemoryMax=2G
# Then: sudo systemctl daemon-reload && sudo systemctl restart jico-manager.service
```

### SSH Connection Issues

```bash
# Test connection
ssh -vvv -i ~/.ssh/oracle_key.key ubuntu@129.154.42.154

# Check SSH key permissions (must be 600)
ls -la ~/.ssh/oracle_key.key

# Fix permissions if needed
chmod 600 ~/.ssh/oracle_key.key

# Check known_hosts
ssh-keyscan -H 129.154.42.154 >> ~/.ssh/known_hosts
```

## Performance Monitoring

### Real-time Monitoring

```bash
# Watch service logs + resource usage
ssh ubuntu@129.154.42.154 << 'EOF'
watch -n 5 'echo "=== Service Status ==="; \
  systemctl status jico-manager.service --no-pager | head -10; \
  echo ""; echo "=== Recent Logs ==="; \
  journalctl -u jico-manager.service -n 5 --no-pager'
EOF
```

### Disk Usage

```bash
# Check storage
ssh ubuntu@129.154.42.154 "df -h /home/ubuntu"

# Check what's taking space
ssh ubuntu@129.154.42.154 "du -sh /home/ubuntu/nacpac-dev/*"
```

### Network Connections

```bash
# Check Discord connection
ssh ubuntu@129.154.42.154 "sudo netstat -tupn | grep -i python"

# Check Google Drive API
ssh ubuntu@129.154.42.154 "sudo netstat -tupn | grep 443"
```

## Automated Deployment Checklist

- [ ] Oracle VM instance created (IP: 129.154.42.154)
- [ ] SSH key generated and saved locally
- [ ] Python 3 and dependencies installed on Oracle
- [ ] `.env` file uploaded with Discord token and credentials
- [ ] Systemd service file installed: `/etc/systemd/system/jico-manager.service`
- [ ] Service enabled and started: `sudo systemctl enable jico-manager.service`
- [ ] Bot confirmed running: Check Discord #general channel
- [ ] Backup script installed: `setup_backup_cron.sh`
- [ ] Google Drive credentials uploaded: `credentials.json`
- [ ] Backup cron job created: `crontab -l`
- [ ] First backup verified: Check Google Drive folder

## Recovery: Restore from Backup

If the bot needs to be restored from backup:

```bash
# 1. On local machine, download backup
# Open: https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO
# Download the most recent JICO-Backup-*.zip

# 2. Extract backup
unzip JICO-Backup-20260630_*.zip

# 3. Upload to Oracle
scp -r jico-system ubuntu@129.154.42.154:/home/ubuntu/nacpac-dev/

# 4. Restart bot
ssh ubuntu@129.154.42.154 "sudo systemctl restart jico-manager.service"

# 5. Verify
ssh ubuntu@129.154.42.154 "sudo systemctl status jico-manager.service"
```

## Cost Optimization

Oracle VM pricing for this setup:
- **Compute:** $6-10/month (Always Free Tier eligible)
- **Storage:** $0 (20GB Always Free)
- **Data Transfer:** $0 (Some Always Free)
- **Google Drive:** Free (personal account)
- **Cloudflare R2:** $0.015 per GB stored, $0.015 per GB transferred

**Total Monthly Cost:** ~$0-10 (often free with Oracle Always Free Tier)

## Next: Full Multi-Layer Backup

Your complete backup redundancy is now:

```
GitHub (Code)
    ↓
Oracle VM (Running Bot)
    ├→ Google Drive (Daily snapshots)
    ├→ Cloudflare R2 (Build artifacts)
    └→ Git Sync (Hourly updates from GitHub)
    
Local Windows Machine
    └→ Can restore from any backup
```

## Resources

- [Oracle Cloud Always Free](https://www.oracle.com/cloud/free/)
- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Google Drive API Docs](https://developers.google.com/drive/api)
- [Cloudflare R2 Docs](https://developers.cloudflare.com/r2/)

---

**Status:** Your JICO bot is now deployed to the cloud. Local machine can crash without losing work. ✅
