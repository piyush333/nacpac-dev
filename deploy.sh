#!/bin/bash
# One-command deployment to Oracle VM
# Usage: bash deploy.sh

set -e

echo "🚀 Jico Agentic System - Deployment Starting"
echo "=============================================="
echo ""

# Clone/update repo
if [ ! -d "nacpac-dev" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/piyush333/nacpac-dev.git
else
    echo "📥 Repository exists, pulling latest..."
fi

cd nacpac-dev

echo "📥 Pulling latest code..."
git pull origin claude/agentic-system-org-j9gvae

echo ""
echo "📦 Installing Python dependencies..."
pip install -r agentic/requirements.txt

echo ""
echo "🔧 Installing Node.js build tools..."
npm install -g eas-cli webpack webpack-cli yarn 2>/dev/null || true

echo ""
echo "✅ Deployment complete!"
echo ""
echo "=============================================="
echo "Next: Start the Discord bot"
echo "=============================================="
echo ""
echo "Run this command (keep it running):"
echo "  python agentic/discord_bot.py"
echo ""
echo "Then in Discord #general channel:"
echo "  'build nacpac apk'"
echo ""
