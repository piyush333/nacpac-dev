import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID')
    DISCORD_LOGS_CHANNEL = os.getenv('DISCORD_LOGS_CHANNEL', 'logs')
    DISCORD_REPORTS_CHANNEL = os.getenv('DISCORD_REPORTS_CHANNEL', 'reports')

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    ALLOWED_USER_ID = int(os.getenv('ALLOWED_USER_ID', '0'))

    # Anthropic
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # Cloudflare R2
    R2_ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID')
    R2_ACCESS_KEY = os.getenv('R2_ACCESS_KEY')
    R2_SECRET_KEY = os.getenv('R2_SECRET_KEY')
    R2_ENDPOINT = os.getenv('R2_ENDPOINT')

    # Nacpac
    NACPAC_R2_BUCKET = os.getenv('NACPAC_R2_BUCKET')
    NACPAC_R2_URL = os.getenv('NACPAC_R2_URL')

    # Jico
    JICO_R2_BUCKET = os.getenv('JICO_R2_BUCKET')
    JICO_R2_URL = os.getenv('JICO_R2_URL')

    # Oracle VM
    ORACLE_VM_IP = os.getenv('ORACLE_VM_IP')
    ORACLE_VM_USER = os.getenv('ORACLE_VM_USER')
    ORACLE_SSH_KEY_PATH = os.getenv('ORACLE_SSH_KEY_PATH')
    AGENT_ENDPOINT = os.getenv('AGENT_ENDPOINT')
    AGENT_TOKEN = os.getenv('AGENT_TOKEN')

    # System
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
