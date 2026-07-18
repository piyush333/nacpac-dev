"""Secure secrets management via Supabase.

Loads all sensitive credentials from Supabase secrets table at startup,
avoiding hardcoded values in code or environment variables.
"""

import os
import logging
from typing import Optional
from supabase import create_client

logger = logging.getLogger(__name__)


class SecretsManager:
    """Load and cache secrets from Supabase."""

    def __init__(self):
        """Initialize secrets manager."""
        self._secrets = {}
        self._loaded = False
        self.client = None

    def connect(self, supabase_url: str, supabase_key: str) -> bool:
        """Connect to Supabase.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key (service role)

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = create_client(supabase_url, supabase_key)
            logger.info("✓ Connected to Supabase secrets backend")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to Supabase: {e}")
            return False

    def load_all_secrets(self) -> bool:
        """Load all secrets from Supabase secrets table.

        Returns:
            True if all secrets loaded successfully, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized. Call connect() first.")
            return False

        try:
            response = self.client.table("secrets").select("key, value").execute()

            if response.data:
                for row in response.data:
                    self._secrets[row["key"]] = row["value"]

                logger.info(f"✓ Loaded {len(self._secrets)} secrets from Supabase")
                self._loaded = True
                return True
            else:
                logger.warning("⚠ No secrets found in Supabase table")
                return False

        except Exception as e:
            logger.error(f"✗ Failed to load secrets: {e}")
            return False

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret value.

        Tries Supabase cache first, then environment variables as fallback.

        Args:
            key: Secret key name
            default: Default value if not found

        Returns:
            Secret value, default, or None
        """
        # Try cached secrets first
        if key in self._secrets:
            return self._secrets[key]

        # Fallback to environment variable
        env_value = os.getenv(key)
        if env_value:
            return env_value

        return default

    def get_required_secret(self, key: str) -> str:
        """Get a required secret. Raises error if not found.

        Args:
            key: Secret key name

        Returns:
            Secret value

        Raises:
            ValueError: If secret not found
        """
        value = self.get_secret(key)
        if not value:
            raise ValueError(f"Required secret not found: {key}")
        return value


# Global secrets manager instance
_secrets_manager = SecretsManager()


def init_secrets(supabase_url: Optional[str] = None, supabase_key: Optional[str] = None) -> bool:
    """Initialize global secrets manager at app startup.

    Args:
        supabase_url: Supabase URL (defaults to env var SUPABASE_URL)
        supabase_key: Supabase key (defaults to env var SUPABASE_KEY)

    Returns:
        True if secrets loaded successfully, False otherwise
    """
    url = supabase_url or os.getenv("SUPABASE_URL")
    key = supabase_key or os.getenv("SUPABASE_KEY")

    if not url or not key:
        logger.error("SUPABASE_URL and SUPABASE_KEY environment variables required")
        return False

    if not _secrets_manager.connect(url, key):
        return False

    return _secrets_manager.load_all_secrets()


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a secret from the global manager.

    Args:
        key: Secret key name
        default: Default value if not found

    Returns:
        Secret value, default, or None
    """
    return _secrets_manager.get_secret(key, default)


def get_required_secret(key: str) -> str:
    """Get a required secret from the global manager.

    Args:
        key: Secret key name

    Returns:
        Secret value

    Raises:
        ValueError: If secret not found
    """
    return _secrets_manager.get_required_secret(key)
