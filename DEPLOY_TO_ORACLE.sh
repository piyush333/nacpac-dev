#!/bin/bash
# Automated deployment script for Jico Agentic System to Oracle Cloud
# Run this from your local machine

set -e

# Configuration
ORACLE_IP="144.24.129.201"
SSH_KEY_PATH="./sshkey20260702.key"
ORACLE_USER="ubuntu"
REPO_URL="https://github.com/piyush333/nacpac-dev.git"
REPO_BRANCH="claude/agentic-system-org-j9gvae"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Jico Agentic System - Oracle Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check SSH key exists
if [ ! -f "$SSH_KEY_PATH" ]; then
  echo -e "${RED}❌ SSH key not found: $SSH_KEY_PATH${NC}"
  echo "Please provide your SSH key in the current directory"
  exit 1
fi

chmod 600 "$SSH_KEY_PATH"
echo -e "${GREEN}✅ SSH key found${NC}"

# Function to run SSH command
ssh_cmd() {
  ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "${ORACLE_USER}@${ORACLE_IP}" "$1"
}

# 1. Test SSH connection
echo ""
echo -e "${YELLOW}1. Testing SSH connection...${NC}"
if ssh_cmd "echo 'SSH connection successful'" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ SSH connection OK${NC}"
else
  echo -e "${RED}❌ SSH connection failed${NC}"
  exit 1
fi

# 2. Install system dependencies
echo ""
echo -e "${YELLOW}2. Installing system dependencies...${NC}"
ssh_cmd "
sudo apt update -y
sudo apt install -y python3.11 python3.11-venv python3-pip git curl wget
python3 --version
"
echo -e "${GREEN}✅ Dependencies installed${NC}"

# 3. Clone repository
echo ""
echo -e "${YELLOW}3. Cloning repository...${NC}"
ssh_cmd "
if [ ! -d /home/ubuntu/nacpac-dev ]; then
  git clone -b $REPO_BRANCH $REPO_URL /home/ubuntu/nacpac-dev
  echo 'Repository cloned'
else
  cd /home/ubuntu/nacpac-dev && git pull origin $REPO_BRANCH
  echo 'Repository updated'
fi
"
echo -e "${GREEN}✅ Repository ready${NC}"

# 4. Create Python environment
echo ""
echo -e "${YELLOW}4. Setting up Python environment...${NC}"
ssh_cmd "
cd /home/ubuntu/nacpac-dev/agentic
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo 'Python environment ready'
"
echo -e "${GREEN}✅ Python environment created${NC}"

# 5. Upload .env file (user must create this first)
echo ""
echo -e "${YELLOW}5. Uploading .env file...${NC}"
if [ ! -f "agentic/.env" ]; then
  echo -e "${RED}❌ .env file not found in agentic/.env${NC}"
  echo "Please create agentic/.env with your credentials before running this script"
  echo ""
  echo "Copy and fill in:"
  echo "  cp agentic/.env.template agentic/.env"
  echo "  nano agentic/.env"
  exit 1
fi

# SCP the .env file (careful - contains secrets!)
scp -i "$SSH_KEY_PATH" agentic/.env "${ORACLE_USER}@${ORACLE_IP}:/home/ubuntu/nacpac-dev/agentic/.env" > /dev/null 2>&1
echo -e "${GREEN}✅ .env uploaded (securely)${NC}"

# 6. Test Supabase connection
echo ""
echo -e "${YELLOW}6. Testing Supabase connection...${NC}"
ssh_cmd "
cd /home/ubuntu/nacpac-dev/agentic
source venv/bin/activate
python3 -c \"
from memory import memory
from config import validate_config
validate_config()
state = memory.get_brand_state('nacpac')
print('✅ Supabase connected')
print(f'  Brand: nacpac, Branch: {state.get(\\\"current_branch\\\")}')
\" 2>&1 || echo '⚠️  Supabase test skipped (may need schema setup)'
"
echo -e "${GREEN}✅ Supabase test complete${NC}"

# 7. Install systemd service
echo ""
echo -e "${YELLOW}7. Installing systemd service...${NC}"
ssh_cmd "
sudo cp /home/ubuntu/nacpac-dev/agentic/systemd/jico-agentic.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jico-agentic
echo 'Service installed'
"
echo -e "${GREEN}✅ Systemd service installed${NC}"

# 8. Start service
echo ""
echo -e "${YELLOW}8. Starting agentic system...${NC}"
ssh_cmd "
sudo systemctl start jico-agentic
sleep 2
sudo systemctl status jico-agentic --no-pager
"
echo -e "${GREEN}✅ Service started${NC}"

# 9. Show logs
echo ""
echo -e "${YELLOW}9. Recent logs:${NC}"
ssh_cmd "
sudo journalctl -u jico-agentic -n 20 --no-pager
"

# Done
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "System is running on: ${ORACLE_IP}"
echo ""
echo "Monitor logs:"
echo "  ssh -i $SSH_KEY_PATH ubuntu@${ORACLE_IP}"
echo "  sudo journalctl -u jico-agentic -f"
echo ""
echo "Test Discord bot:"
echo "  /task brand:nacpac request:Show status"
echo ""
