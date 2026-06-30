# NACPAC Operator Machine Setup

## Overview
This guide sets up the operator machine for **automatic OTA (Over-The-Air) updates** without manual intervention.

## Requirements
- Windows 10+
- Node.js installed (for deploy server)
- Internet connection
- Google Drive folder shared with operator (for downloading `.exe` updates)

## Step 1: Copy to Operator Machine
1. Copy the entire `C:\Users\piyus\nacpac\desktop` folder to the operator machine
2. Or just these files:
   - `NACPAC Production 1.0.0.exe`
   - `deploy-server.js`
   - `start-operator.bat`

## Step 2: Start the Operator Environment
Double-click `start-operator.bat` on the operator machine.

This will:
1. Start the **Deploy Server** (listens for update commands)
2. Start the **NACPAC app** (the dashboard)

Both run in the background. Operator can use the app normally.

## Step 3: Configure Google Drive Sync
Updates are downloaded from Google Drive. Choose one:

### Option A: Google Drive Desktop Client (Simplest)
1. Install [Google Drive for Desktop](https://www.google.com/drive/download/)
2. Sign in and sync the shared folder to `%USERPROFILE%\NACPAC-Deploy`
3. Deploy server will auto-detect new `.exe` files

### Option B: Manual Upload
1. Admin uploads new `.exe` to Google Drive
2. Operator manually downloads to `%USERPROFILE%\NACPAC-Deploy`
3. Send update command from your phone

## Step 4: Remote Update Command
From your phone (via Claude remote control):

```
deploy latest
```

This will:
1. ✓ Download latest `.exe` from `NACPAC-Deploy` folder
2. ✓ Stop the running app
3. ✓ Replace the executable
4. ✓ Restart the app
5. ✓ Operator sees new version running instantly

No manual intervention needed.

## Monitoring

### Check current version:
```
current version
```

### Check deployment status:
```
status
```

### View logs:
Logs are in: `%USERPROFILE%\NACPAC-Deploy\deploy.log`

## Troubleshooting

### "Google Drive folder ID not configured"
- Set environment variable: `NACPAC_DRIVE_FOLDER_ID=<your-folder-id>`
- Or ensure `.exe` is in `%USERPROFILE%\NACPAC-Deploy` manually

### App doesn't restart after deploy
- Check `deploy.log` for errors
- Ensure `.exe` file is not corrupted
- Manually restart by running `start-operator.bat` again

### Deploy server crashes
- Check `deploy.log`
- Ensure Node.js is installed: `node --version`
- Restart: `start-operator.bat`

## Automation (Optional)

To auto-start on Windows boot:
1. Save `start-operator.bat` path to a `.lnk` shortcut
2. Place shortcut in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
3. Next boot, NACPAC will auto-run with deploy server

---

**Admin Note:** Each time you build a new `.exe` on your dev machine, upload it to the shared Google Drive folder. Then send "deploy latest" from your phone and the operator machine updates instantly.
