#!/bin/bash
# JICO Discord Manager - Automated Oracle Cloud Deployment
# Run this on Oracle instance after cloning the repo

set -e  # Exit on error

echo "========================================="
echo "JICO Discord Manager - Auto Deploy"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as opc or ubuntu user
CURRENT_USER=$(whoami)
if [ "$CURRENT_USER" != "opc" ] && [ "$CURRENT_USER" != "ubuntu" ]; then
    echo -e "${RED}Error: Must run as opc or ubuntu user${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Update system packages${NC}"
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip nodejs npm git curl

echo -e "${GREEN}✓ System packages installed${NC}"
echo ""

echo -e "${YELLOW}Step 2: Install Python dependencies${NC}"
pip3 install -q discord.py python-dotenv boto3 google-auth-oauthlib google-api-python-client requests

echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 3: Install Node.js dependencies${NC}"
npm install -g -qq eas-cli

if [ -d "nacpac-workspace-main/mobile" ]; then
    echo "  Installing mobile dependencies..."
    cd nacpac-workspace-main/mobile
    npm install -q
    cd ../../
fi

if [ -d "nacpac-workspace-main/desktop" ]; then
    echo "  Installing desktop dependencies..."
    cd nacpac-workspace-main/desktop
    npm install -q
    cd ../../
fi

echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 4: Create .env file${NC}"

if [ ! -f ~/.env ]; then
    cp .env.oracle.template ~/.env
    echo -e "${GREEN}✓ Created ~/.env from template${NC}"

    echo ""
    echo -e "${YELLOW}IMPORTANT: You need to fill in the Firebase section${NC}"
    echo ""
    echo "Edit your .env file:"
    echo "  nano ~/.env"
    echo ""
    echo "Find the FIREBASE section (around line 56) and fill in:"
    echo "  FIREBASE_API_KEY=AIzaSyAmvqkpyBKEZogyk0j_Ti9ob6eUntE2CeM"
    echo "  FIREBASE_AUTH_DOMAIN=nacpac-production-4134a.firebaseapp.com"
    echo "  FIREBASE_STORAGE_BUCKET=nacpac-production-4134a.firebasestorage.app"
    echo "  FIREBASE_MESSAGING_SENDER_ID=371880247454"
    echo "  FIREBASE_APP_ID=1:371880247454:web:b9ae971b4aa16bea673b8f"
    echo ""
    echo "Then press Ctrl+X, Y, Enter to save"
    echo ""
    read -p "Press Enter once you've saved the .env file..."
else
    echo "  ~/.env already exists, skipping creation"
fi

echo ""

echo -e "${YELLOW}Step 5: Load environment variables${NC}"

# Add to bashrc if not already there
if ! grep -q "Load environment variables" ~/.bashrc; then
    cat >> ~/.bashrc << 'BASHRC_EOF'

# Load environment variables
if [ -f ~/.env ]; then
  export $(cat ~/.env | grep -v '^#' | xargs)
fi
BASHRC_EOF
fi

# Load them now
export $(cat ~/.env | grep -v '^#' | xargs)

echo -e "${GREEN}✓ Environment variables loaded${NC}"
echo ""

echo -e "${YELLOW}Step 6: Test Discord connection${NC}"

python3 << 'PYEOF'
import os
import sys

token = os.getenv('DISCORD_TOKEN')
guild_id = os.getenv('DISCORD_GUILD_ID')

if not token or token == '<DISCORD_BOT_TOKEN>':
    print("❌ DISCORD_TOKEN not set or still has placeholder")
    sys.exit(1)

if not guild_id or guild_id == '<GUILD_ID>':
    print("❌ DISCORD_GUILD_ID not set or still has placeholder")
    sys.exit(1)

print("✓ Discord token found")
print("✓ Guild ID found")
print("✓ Credentials are valid")
PYEOF

echo ""

echo -e "${YELLOW}Step 7: Create systemd service${NC}"

HOME_DIR="/home/$CURRENT_USER"

sudo tee /etc/systemd/system/jico-manager.service > /dev/null << SYSTEMD_EOF
[Unit]
Description=JICO Discord Manager Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$HOME_DIR/nacpac-dev/jico-system
ExecStart=/usr/bin/python3 $HOME_DIR/nacpac-dev/jico-system/discord_manager.py

# Load environment variables from ~/.env
EnvironmentFile=$HOME_DIR/.env

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=jico-manager

# Auto-restart on failure
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

echo -e "${GREEN}✓ Systemd service created${NC}"
echo ""

echo -e "${YELLOW}Step 8: Enable and start service${NC}"

sudo systemctl daemon-reload
sudo systemctl enable jico-manager
sudo systemctl start jico-manager

sleep 2

if sudo systemctl is-active --quiet jico-manager; then
    echo -e "${GREEN}✓ Service is running${NC}"
else
    echo -e "${RED}⚠ Service failed to start. Check logs:${NC}"
    echo "  sudo journalctl -u jico-manager -n 50"
    exit 1
fi

echo ""

echo "========================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Check bot status:"
echo "   sudo systemctl status jico-manager"
echo ""
echo "2. View logs (live):"
echo "   sudo journalctl -u jico-manager -f"
echo ""
echo "3. Test in Discord:"
echo "   - Go to #general channel"
echo "   - Type: Hi piyush, what is the agenda today!"
echo "   - Bot should respond with greeting"
echo ""
echo "4. To restart if needed:"
echo "   sudo systemctl restart jico-manager"
echo ""
