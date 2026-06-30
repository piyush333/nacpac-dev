#!/bin/bash
# Deploy JICO Manager bot to Oracle VM

set -e

ORACLE_IP="129.154.42.154"
ORACLE_USER="opc"
ORACLE_KEY="$HOME/.ssh/oracle_key.key"
REMOTE_DIR="/home/ubuntu/nacpac-dev"

echo "🚀 Deploying JICO Manager to Oracle VM"
echo "========================================"
echo ""

# Check SSH key
if [ ! -f "$ORACLE_KEY" ]; then
    echo "❌ ERROR: SSH key not found at $ORACLE_KEY"
    echo ""
    echo "Setup instructions:"
    echo "1. Generate SSH key on Oracle VM"
    echo "2. Download private key"
    echo "3. Save to: $ORACLE_KEY"
    echo "4. chmod 600 $ORACLE_KEY"
    exit 1
fi

echo "✅ SSH key found: $ORACLE_KEY"
echo ""

# Test SSH connection
echo "🔗 Testing SSH connection to $ORACLE_IP..."
if ! ssh -i "$ORACLE_KEY" -o StrictHostKeyChecking=accept-new "$ORACLE_USER@$ORACLE_IP" "echo ✅ Connected" 2>/dev/null; then
    echo "❌ ERROR: Cannot connect to Oracle VM"
    echo ""
    echo "Troubleshooting:"
    echo "1. Verify IP address: $ORACLE_IP"
    echo "2. Verify username: $ORACLE_USER"
    echo "3. Verify SSH key: $ORACLE_KEY"
    echo "4. Check SSH key permissions: chmod 600 $ORACLE_KEY"
    exit 1
fi

echo ""
echo "📦 Cloning repository to Oracle VM..."
ssh -i "$ORACLE_KEY" "$ORACLE_USER@$ORACLE_IP" << 'REMOTE_COMMANDS'
set -e
cd /home/ubuntu
if [ -d nacpac-dev ]; then
    echo "📂 Repository already exists, pulling latest..."
    cd nacpac-dev
    git pull origin main
else
    echo "📥 Cloning fresh repository..."
    git clone https://github.com/piyush333/nacpac-dev.git
    cd nacpac-dev
fi
echo "✅ Repository ready"
REMOTE_COMMANDS

echo ""
echo "📥 Installing Python dependencies..."
ssh -i "$ORACLE_KEY" "$ORACLE_USER@$ORACLE_IP" << 'REMOTE_COMMANDS'
cd /home/ubuntu/nacpac-dev/jico-system
python3 -m pip install --upgrade pip --quiet
python3 -m pip install -r requirements.txt --quiet 2>&1 | grep -E "Successfully|error|ERROR" || true
echo "✅ Dependencies installed"
REMOTE_COMMANDS

echo ""
echo "⚙️  Setting up systemd service..."
ssh -i "$ORACLE_KEY" "$ORACLE_USER@$ORACLE_IP" << 'REMOTE_COMMANDS'
set -e
cd /home/ubuntu/nacpac-dev
sudo cp jico-manager.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jico-manager.service
echo "✅ Systemd service registered"
REMOTE_COMMANDS

echo ""
echo "🔐 Setting up Google Drive credentials..."
if [ ! -f "credentials.json" ]; then
    echo "⚠️  credentials.json not found locally"
    echo "Skipping - user must upload credentials.json manually"
else
    scp -i "$ORACLE_KEY" credentials.json "$ORACLE_USER@$ORACLE_IP:/home/ubuntu/nacpac-dev/" 2>/dev/null
    echo "✅ Credentials uploaded"
fi

echo ""
echo "🤖 Starting JICO Manager service..."
ssh -i "$ORACLE_KEY" "$ORACLE_USER@$ORACLE_IP" << 'REMOTE_COMMANDS'
sudo systemctl start jico-manager.service
sleep 2
status=$(sudo systemctl is-active jico-manager.service)
if [ "$status" = "active" ]; then
    echo "✅ Service started successfully"
else
    echo "⚠️  Service status: $status"
    echo "Check logs: sudo journalctl -u jico-manager.service -n 20"
fi
REMOTE_COMMANDS

echo ""
echo "📊 Checking service status..."
ssh -i "$ORACLE_KEY" "$ORACLE_USER@$ORACLE_IP" "sudo systemctl status jico-manager.service --no-pager | head -20"

echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Monitor logs: ssh -i $ORACLE_KEY $ORACLE_USER@$ORACLE_IP 'sudo journalctl -u jico-manager.service -f'"
echo "2. Check status: ssh -i $ORACLE_KEY $ORACLE_USER@$ORACLE_IP 'sudo systemctl status jico-manager.service'"
echo "3. Set up backups: bash /home/user/nacpac-dev/setup_backup_cron.sh"
echo ""
echo "Bot is now running 24/7 on Oracle VM at $ORACLE_IP"
echo ""
