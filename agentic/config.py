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
DISCORD_GENERAL_CHANNEL_ID = int(os.getenv("DISCORD_GENERAL_CHANNEL_ID", "0"))
DISCORD_BUILDS_CHANNEL_ID = int(os.getenv("DISCORD_BUILDS_CHANNEL_ID", "0"))
DISCORD_DEPLOYS_CHANNEL_ID = int(os.getenv("DISCORD_DEPLOYS_CHANNEL_ID", "0"))
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

# Repos
NACPAC_REPO_PATH = os.getenv("NACPAC_REPO_PATH", "/home/user/nacpac-dev/nacpac-workspace-main")
JICO_REPO_PATH = os.getenv("JICO_REPO_PATH", "/home/user/nacpac-dev/nacpac-workspace-main")  # Same workspace

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

# Models
HAIKU_MODEL = "claude-3-5-haiku-20241022"
SONNET_MODEL = "claude-3-5-sonnet-20241022"

# System
SYSTEM_USER = os.getenv("SYSTEM_USER", "ubuntu")
ORACLE_VM_IP = os.getenv("ORACLE_VM_IP", "68.233.110.235")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")

# Validation
def validate_config():
    """Ensure all required env vars are set."""
    required = [
        "ANTHROPIC_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "DISCORD_TOKEN",
        "DISCORD_GUILD_ID",
        "ALLOWED_USER_ID",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise ValueError(f"Missing env vars: {', '.join(missing)}")

if __name__ == "__main__":
    validate_config()
    print("✅ Config validated")
