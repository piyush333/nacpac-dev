import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import pickle

logger = logging.getLogger(__name__)

class GoogleDriveBackup:
    """Backup and restore system using Google Drive"""

    BACKUP_FOLDER_ID = "1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO"
    CREDENTIALS_FILE = Path(__file__).parent / "google_credentials.json"
    TOKEN_FILE = Path(__file__).parent / ".google_token.pickle"

    def __init__(self, credentials_path: str = None):
        """Initialize Google Drive backup with credentials"""
        self.credentials_path = credentials_path or str(self.CREDENTIALS_FILE)
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive API"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.service_account import Credentials
            from google.oauth2.credentials import Credentials as UserCredentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            # Try service account first
            if self.credentials_path and Path(self.credentials_path).exists():
                try:
                    creds = Credentials.from_service_account_file(
                        self.credentials_path,
                        scopes=['https://www.googleapis.com/auth/drive']
                    )
                    self.service = build('drive', 'v3', credentials=creds)
                    logger.info("✅ Authenticated with Google Drive (Service Account)")
                    return
                except:
                    pass

                # Try OAuth flow for installed app
                try:
                    creds = None
                    if self.TOKEN_FILE.exists():
                        with open(self.TOKEN_FILE, 'rb') as token:
                            creds = pickle.load(token)

                    if not creds or not creds.valid:
                        if creds and creds.expired and creds.refresh_token:
                            creds.refresh(Request())
                        else:
                            flow = InstalledAppFlow.from_client_secrets_file(
                                self.credentials_path,
                                scopes=['https://www.googleapis.com/auth/drive']
                            )
                            creds = flow.run_local_server(port=0)

                        with open(self.TOKEN_FILE, 'wb') as token:
                            pickle.dump(creds, token)

                    self.service = build('drive', 'v3', credentials=creds)
                    logger.info("✅ Authenticated with Google Drive (OAuth)")
                except Exception as e:
                    logger.error(f"OAuth flow failed: {e}")

        except ImportError:
            logger.warning("Google Drive libraries not installed. Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")

    def backup_folder(self, local_path: str, folder_name: str = None) -> bool:
        """Backup a folder to Google Drive"""
        if not self.service:
            logger.warning("Google Drive not authenticated")
            return False

        try:
            from googleapiclient.http import MediaFileUpload
            import zipfile
            import io

            local_path = Path(local_path)
            if not local_path.exists():
                logger.error(f"Path not found: {local_path}")
                return False

            # Create zip file
            zip_name = folder_name or local_path.name
            zip_path = Path("/tmp") / f"{zip_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

            logger.info(f"Creating backup zip: {zip_path}")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in local_path.rglob('*'):
                    if file_path.is_file() and '.git' not in str(file_path):
                        arcname = file_path.relative_to(local_path.parent)
                        zf.write(file_path, arcname)

            # Upload to Google Drive
            file_metadata = {
                'name': zip_path.name,
                'parents': [self.BACKUP_FOLDER_ID]
            }
            media = MediaFileUpload(str(zip_path), mimetype='application/zip')
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, createdTime'
            ).execute()

            logger.info(f"✅ Backed up to Google Drive: {file['name']}")
            zip_path.unlink()
            return True

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

    def list_backups(self) -> list:
        """List all backups in Google Drive folder"""
        if not self.service:
            return []

        try:
            results = self.service.files().list(
                q=f"'{self.BACKUP_FOLDER_ID}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name, createdTime, size)',
                pageSize=20
            ).execute()

            files = results.get('files', [])
            logger.info(f"Found {len(files)} backups in Google Drive")
            return files

        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []

    def get_status(self) -> Dict[str, Any]:
        """Get backup status"""
        return {
            "authenticated": self.service is not None,
            "folder_id": self.BACKUP_FOLDER_ID,
            "backups": self.list_backups()
        }
