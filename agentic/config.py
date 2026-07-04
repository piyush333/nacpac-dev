"""Configuration module for Jico agentic system."""

import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

# Discord channels
DISCORD_GENERAL_CHANNEL_ID = int(os.getenv("DISCORD_GENERAL_CHANNEL_ID", "0"))
DISCORD_NACPAC_DEV_CHANNEL_ID = int(os.getenv("DISCORD_NACPAC_DEV_CHANNEL_ID", "0"))
DISCORD_JICO_DEV_CHANNEL_ID = int(os.getenv("DISCORD_JICO_DEV_CHANNEL_ID", "0"))
DISCORD_LOGS_CHANNEL_ID = int(os.getenv("DISCORD_LOGS_CHANNEL_ID", "0"))
DISCORD_REPORTS_CHANNEL_ID = int(os.getenv("DISCORD_REPORTS_CHANNEL_ID", "0"))

# Repos (use local paths for testing, Oracle VM paths for production)
NACPAC_REPO_PATH = os.getenv("NACPAC_REPO_PATH", "/home/user/nacpac-dev/nacpac-workspace-main")
JICO_REPO_PATH = os.getenv("JICO_REPO_PATH", "/home/user/nacpac-dev/jico-system")  # Use jico-system for now

# Build paths
EAS_BUILD_PROFILE = os.getenv("EAS_BUILD_PROFILE", "preview")
FIREBASE_PROJECT = os.getenv("FIREBASE_PROJECT", "nacpac-production-4134a")

# R2 (Cloudflare)
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NACPAC = os.getenv("R2_BUCKET_NACPAC", "nacpac-builds")
R2_BUCKET_JICO = os.getenv("R2_BUCKET_JICO", "jico-builds")

# Google Drive
GOOGLE_DRIVE_CREDENTIALS_JSON = os.getenv("GOOGLE_DRIVE_CREDENTIALS_JSON")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "piyush333/nacpac-dev")

# Cost caps
DAILY_CAP_USD = float(os.getenv("DAILY_CAP_USD", "10.0"))
MONTHLY_CAP_USD = float(os.getenv("MONTHLY_CAP_USD", "50.0"))

# Models (complexity-based selection)
HAIKU_MODEL = "claude-haiku-4-5-20251001"  # Orchestration, routing, fast decisions
SONNET_MODEL = "claude-sonnet-5"  # Dev tasks: code reasoning, complex builds
OPUS_MODEL = "claude-opus-4-8"  # Heavy lifting: multi-step orchestration

# System
SYSTEM_USER = os.getenv("SYSTEM_USER", "ubuntu")
ORACLE_VM_IP = os.getenv("ORACLE_VM_IP", "68.233.110.235")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")

# Validation
def validate_config():
    """Ensure all required env vars are set."""
    # Core requirements (Discord bot + API)
    required = [
        "ANTHROPIC_API_KEY",
        "DISCORD_TOKEN",
        "DISCORD_GUILD_ID",
        "ALLOWED_USER_ID",
        "DISCORD_GENERAL_CHANNEL_ID",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise ValueError(f"Missing env vars: {', '.join(missing)}")

    # Optional but warn if missing (memory + logging)
    optional = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_optional = [k for k in optional if not os.getenv(k)]
    if missing_optional:
        print(f"⚠️  Warning: Optional env vars missing: {', '.join(missing_optional)}")
        print("   Memory features will be disabled")

if __name__ == "__main__":
    validate_config()
    print("✅ Config validated")
