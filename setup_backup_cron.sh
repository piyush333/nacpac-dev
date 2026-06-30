#!/bin/bash
# Set up automated daily Google Drive backups

set -e

BACKUP_SCRIPT="/home/user/nacpac-dev/backup_to_gdrive.py"
LOG_FILE="/tmp/gdrive-backup.log"
CRON_JOB="0 2 * * * cd /home/user/nacpac-dev && python3 /home/user/nacpac-dev/backup_to_gdrive.py >> /tmp/gdrive-backup.log 2>&1"

echo "🔧 Setting up automated Google Drive backups"
echo "============================================================"
echo ""

# Check if credentials.json exists
if [ ! -f "/home/user/nacpac-dev/credentials.json" ]; then
    echo "❌ ERROR: credentials.json not found"
    echo ""
    echo "Setup instructions:"
    echo "1. Go to: https://console.cloud.google.com/"
    echo "2. Create new project: 'nacpac-backup'"
    echo "3. Enable 'Google Drive API'"
    echo "4. Create OAuth 2.0 Desktop credentials"
    echo "5. Download JSON as credentials.json"
    echo "6. Save to: /home/user/nacpac-dev/credentials.json"
    echo "7. Run this script again"
    exit 1
fi

echo "✅ Found credentials.json"
echo ""

# Check if backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ ERROR: backup_to_gdrive.py not found at $BACKUP_SCRIPT"
    exit 1
fi

echo "✅ Found backup script"
echo ""

# Test backup script works
echo "🧪 Testing backup script (first run - browser may open)..."
echo ""

cd /home/user/nacpac-dev
python3 backup_to_gdrive.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Backup test failed. Fix errors above and run again."
    exit 1
fi

echo ""
echo "✅ Backup test successful!"
echo ""

# Set up cron job
echo "📝 Setting up cron job for daily backups at 2 AM..."
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "backup_to_gdrive.py"; then
    echo "⚠️  Cron job already exists:"
    crontab -l | grep "backup_to_gdrive.py"
    echo ""
    read -p "Replace with new cron job? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "⏭️  Skipping cron setup"
        exit 0
    fi
fi

# Add cron job (with fallback for systems without crontab)
(crontab -l 2>/dev/null | grep -v "backup_to_gdrive.py"; echo "$CRON_JOB") | crontab -

echo "✅ Cron job installed:"
echo ""
crontab -l | grep "backup_to_gdrive.py"
echo ""

# Create log file
touch "$LOG_FILE"
echo "✅ Log file created: $LOG_FILE"
echo ""

echo "============================================================"
echo "✨ Setup complete!"
echo "============================================================"
echo ""
echo "📅 Automated backups will run daily at 2 AM"
echo "📊 Monitor progress: tail -f $LOG_FILE"
echo ""
echo "To disable backups:"
echo "  crontab -e"
echo "  (Remove the backup_to_gdrive.py line)"
echo ""
echo "To run backup manually:"
echo "  python3 /home/user/nacpac-dev/backup_to_gdrive.py"
echo ""
echo "Check your Google Drive folder for backups:"
echo "  https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO"
echo ""
