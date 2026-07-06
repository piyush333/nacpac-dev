FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git curl build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cache bust: force fresh rebuild - 2026-07-06T10:25
RUN echo "Build timestamp: $(date)"
COPY agentic/ ./agentic/
RUN ls -la ./agentic/agents/ && echo "Files copied successfully"
RUN mkdir -p /tmp

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import os; exit(0 if os.getenv('DISCORD_TOKEN') else 1)"

CMD ["python", "-m", "agentic.main"]
