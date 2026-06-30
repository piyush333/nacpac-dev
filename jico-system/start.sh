#!/bin/bash

# JICO System Startup Script

set -e

echo "🚀 Starting JICO System..."
echo ""

# Check Python
python3 --version

# Check .env
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and configure"
    exit 1
fi

# Run system test
echo ""
echo "🧪 Running system connectivity test..."
python3 test_system.py || true

# Start main system
echo ""
echo "▶️  Starting JICO System..."
python3 main.py
