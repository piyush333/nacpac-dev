#!/bin/bash
# Deploy Jico Agentic System to Oracle VM
# Run this on Oracle VM (144.24.129.201)

set -e

echo "🚀 Deploying Jico Agentic System..."

# Setup directories
mkdir -p /home/ubuntu
cd /home/ubuntu

# Clone repo
if [ ! -d "nacpac-dev" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/piyush333/nacpac-dev.git
else
    echo "📥 Pulling latest..."
    cd nacpac-dev
    git pull origin claude/agentic-system-org-j9gvae
    cd ..
fi

cd nacpac-dev

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r agentic/requirements.txt

# Install Node/build tools
echo "🔧 Installing build tools..."
npm install -g eas-cli webpack webpack-cli
npm install -g yarn

# Update .env for Oracle paths
echo "⚙️  Updating .env for Oracle VM paths..."
sed -i 's|NACPAC_REPO_PATH=.*|NACPAC_REPO_PATH=/home/ubuntu/nacpac-workspace-main|' agentic/.env
sed -i 's|JICO_REPO_PATH=.*|JICO_REPO_PATH=/home/ubuntu/jico-workspace|' agentic/.env

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Configure EAS: eas login"
echo "2. Start Discord bot: python agentic/discord_bot.py"
echo "3. In Discord #general: 'build nacpac apk'"
echo ""
