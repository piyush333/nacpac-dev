FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    git curl build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18+ using NodeSource repository (more reliable than apt default)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Verify Node and npm are available
RUN node --version && npm --version

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install EAS CLI globally
RUN npm install -g @expo/eas-cli && which eas

# Cache bust: force fresh rebuild - 2026-07-06T14:55Z (NodeSource Node.js + eas-cli)
RUN echo "Build timestamp: $(date +%s)"
COPY agentic/ ./agentic/
RUN ls -la ./agentic/agents/ && echo "Files copied successfully"
RUN mkdir -p /tmp

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import os; exit(0 if os.getenv('DISCORD_TOKEN') else 1)"

CMD ["python", "-m", "agentic.main"]
