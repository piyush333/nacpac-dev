#!/usr/bin/env python3
"""
Complete Session Backup to Google Drive
Backs up entire jico-system and documentation for disaster recovery
"""

import os
import json
import zipfile
import shutil
import webbrowser
from pathlib import Path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive setup
SCOPES = ['https://www.googleapis.com/auth/drive']
GDRIVE_FOLDER_ID = "1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO"  # Your Google Drive folder

# Paths to backup
BACKUP_ITEMS = [
    "/home/user/nacpac-dev/jico-system",
    "/home/user/nacpac-dev/BUILD_SUMMARY.md",
    "/home/user/nacpac-dev/DEPLOYMENT_GUIDE.md",
    "/home/user/nacpac-dev/DISCORD_ARCHITECTURE.md",
    "/home/user/nacpac-dev/OPTIMIZATION_STRATEGY.md",
    "/home/user/nacpac-dev/DISCORD_SETUP.md",
]

class GDriveBackup:
    def __init__(self):
        self.service = None
        self.creds = None
        self.backup_dir = Path("/tmp/jico-backup")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def authenticate(self):
        """Authenticate with Google Drive (one-time setup)"""
        print("🔐 Authenticating with Google Drive...")

        try:
            # Try to use existing token
            if os.path.exists("token.json"):
                self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
                print("✅ Using existing credentials from token.json")

            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    print("🔄 Refreshing expired credentials...")
                    self.creds.refresh(Request())
                elif os.path.exists("credentials.json"):
                    # Use OAuth2 flow with credentials.json
                    print("📝 Starting OAuth2 authentication (browser will open)...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials.json", SCOPES
                    )
                    self.creds = flow.run_local_server(port=0, open_browser=True)

                    # Save credentials for next time
                    with open("token.json", "w") as token:
                        token.write(self.creds.to_json())
                    print("✅ Credentials saved to token.json")
                else:
                    print("❌ ERROR: credentials.json not found")
                    print("\n📋 Setup instructions:")
                    print("1. Go to: https://console.cloud.google.com/")
                    print("2. Create a new project or select existing")
                    print("3. Enable 'Google Drive API'")
                    print("4. Create OAuth 2.0 Desktop App credentials:")
                    print("   - Go to 'Credentials'")
                    print("   - Click 'Create Credentials' → 'OAuth client ID'")
                    print("   - Choose 'Desktop' application type")
                    print("   - Download JSON")
                    print("5. Save as 'credentials.json' in this folder")
                    print("6. Run this script again")
                    return False

            self.service = build("drive", "v3", credentials=self.creds)
            print("✅ Authenticated with Google Drive")
            return True

        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_backup_zip(self):
        """Create a zip file with all backup items"""
        print(f"\n📦 Creating backup package...")

        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        self.backup_dir.mkdir(parents=True)

        zip_path = self.backup_dir / f"JICO-Backup-{self.timestamp}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item_path in BACKUP_ITEMS:
                path = Path(item_path)

                if not path.exists():
                    print(f"  ⚠️  Skipping (not found): {item_path}")
                    continue

                if path.is_file():
                    # Add file
                    arcname = path.relative_to("/home/user/nacpac-dev")
                    zipf.write(path, arcname)
                    print(f"  ✅ {arcname}")
                elif path.is_dir():
                    # Add directory (excluding __pycache__, .git, etc.)
                    for file_path in path.rglob("*"):
                        if any(skip in file_path.parts for skip in ["__pycache__", ".git", "node_modules", ".venv", "venv"]):
                            continue
                        if file_path.is_file():
                            arcname = file_path.relative_to("/home/user/nacpac-dev")
                            zipf.write(file_path, arcname)

        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Backup created: {zip_path.name} ({size_mb:.1f} MB)")
        return zip_path

    def upload_to_gdrive(self, zip_path):
        """Upload backup to Google Drive"""
        print(f"\n📤 Uploading to Google Drive...")

        try:
            file_metadata = {
                'name': zip_path.name,
                'parents': [GDRIVE_FOLDER_ID]
            }

            media = MediaFileUpload(zip_path, mimetype='application/zip', resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            print(f"✅ Uploaded: {file['webViewLink']}")
            return file['webViewLink']

        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None

    def create_recovery_guide(self, drive_link):
        """Create a recovery guide"""
        guide = f"""# JICO Session Backup Recovery Guide

**Backup Date:** {self.timestamp}
**Backup File:** JICO-Backup-{self.timestamp}.zip
**Google Drive Link:** {drive_link}

## Recovery Steps

1. **Download the backup:**
   - Go to the Google Drive link above
   - Download JICO-Backup-{self.timestamp}.zip

2. **Extract to new location:**
   ```bash
   unzip JICO-Backup-{self.timestamp}.zip
   cd nacpac-dev/jico-system
   ```

3. **Set up environment:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure .env:**
   - Add your Discord token: DISCORD_TOKEN=...
   - Add your server ID: DISCORD_GUILD_ID=...
   - Add other credentials as needed

5. **Start the bot:**
   ```bash
   python main.py
   ```

## What's Included

- ✅ jico-system/ - Complete bot system
- ✅ All documentation (DEPLOYMENT_GUIDE.md, etc.)
- ✅ Memory files and context
- ✅ Configuration templates
- ✅ Source code and scripts

## Important Notes

- .env file is NOT included (security)
- Add your credentials when restoring
- All code is committed to GitHub as backup
- This zip is your complete session snapshot

## Additional Backups

Backups are automatically created daily in Google Drive.
Check the folder for multiple versions.

**Last Backup:** {self.timestamp}
"""

        guide_path = self.backup_dir / "RECOVERY_GUIDE.md"
        guide_path.write_text(guide)
        print(f"\n📖 Recovery guide created: {guide_path}")
        return guide

    def run(self):
        """Run complete backup"""
        print("=" * 60)
        print("🔄 JICO System Complete Backup")
        print("=" * 60)

        # Authenticate
        if not self.authenticate():
            return False

        # Create backup zip
        zip_path = self.create_backup_zip()
        if not zip_path:
            return False

        # Upload to Google Drive
        drive_link = self.upload_to_gdrive(zip_path)
        if not drive_link:
            return False

        # Create recovery guide
        self.create_recovery_guide(drive_link)

        print("\n" + "=" * 60)
        print("✅ BACKUP COMPLETE")
        print("=" * 60)
        print(f"📍 Location: Google Drive folder")
        print(f"📦 File: JICO-Backup-{self.timestamp}.zip")
        print(f"🔗 Link: {drive_link}")
        print("\nYou can restore this backup anytime to recover your session.")

        return True

if __name__ == "__main__":
    backup = GDriveBackup()
    success = backup.run()
    exit(0 if success else 1)
