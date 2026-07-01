# Google Drive Backup Setup Guide

The Google Drive backup system has been refactored to load credentials from environment variables instead of committing them to git (which is a security risk).

## How to Configure

You have three options for providing Google credentials:

### Option 1: Environment Variable with JSON String (Recommended for Servers)

Set the `GOOGLE_CREDENTIALS_JSON` environment variable with the entire OAuth credentials as a JSON string:

```bash
export GOOGLE_CREDENTIALS_JSON='{"installed":{"client_id":"YOUR_CLIENT_ID","project_id":"nacpac-backup","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"YOUR_CLIENT_SECRET","redirect_uris":["http://localhost"]}}'
```

### Option 2: Environment Variable with File Path

Set the `GOOGLE_CREDENTIALS_PATH` environment variable pointing to a credentials file:

```bash
export GOOGLE_CREDENTIALS_PATH="/path/to/secure/google_credentials.json"
```

### Option 3: Local File (Development Only)

Place `google_credentials.json` in the `jico-system/` directory. This file is in `.gitignore` and won't be committed to git.

## For Oracle Cloud Deployment

Add the environment variable to your systemd service file or to the `.env` file used by the bot:

### In `.env` file:
```
GOOGLE_CREDENTIALS_JSON={"installed":{...}}
```

### In Systemd Service (`/etc/systemd/system/jico-manager.service`):
```ini
[Service]
Environment="GOOGLE_CREDENTIALS_JSON={"installed":{...}}"
```

## Token File

The system will create a `.google_token.pickle` file in the `jico-system/` directory after the first successful authentication. This file is also in `.gitignore` and contains the refresh token for future authentications.

## Backup Folder ID

All backups are stored in Google Drive folder ID: `1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO`

You can verify this folder exists at: https://drive.google.com/drive/folders/1CewTnTKvFpRrpSopFdXWNZG-mgoRZVrO

## Automatic Backup Flow

When a build succeeds (APK or EXE), the system automatically:
1. Zips the entire Nacpac codebase (excluding .git)
2. Uploads to Google Drive with timestamp: `nacpac-dev_YYYYMMDD_HHMMSS.zip`
3. Creates a token pickle for future authentications
4. Logs backup status to the Discord bot

## Troubleshooting

- If you see "Google Drive not authenticated", the credentials are missing or invalid
- If oauth flow hangs, you may need to run the bot locally once to authorize, then use the generated token
- Check logs with: `grep -i "google" logs.txt`
