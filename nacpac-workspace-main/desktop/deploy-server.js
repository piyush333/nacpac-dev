#!/usr/bin/env node
/**
 * NACPAC OTA Deploy Server
 * Runs on operator machine to handle automatic .exe updates from Google Drive
 *
 * Usage: node deploy-server.js
 *
 * Commands (via remote control or direct):
 * - "deploy latest" → downloads newest .exe from Google Drive, replaces, restarts
 * - "check updates" → checks if new version available
 * - "current version" → shows running version
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { spawn, exec } = require('child_process');
const os = require('os');

// ── Config ───────────────────────────────────────────────────────
const CONFIG = {
  appName: 'NACPAC Production',
  appExeName: 'NACPAC Production 1.0.0.exe',
  appDir: path.dirname(__filename),
  deployDir: path.join(os.homedir(), 'NACPAC-Deploy'),

  // Google Drive folder ID where .exe is stored
  // Replace with your actual folder ID
  googleDriveFolderId: process.env.NACPAC_DRIVE_FOLDER_ID || '',

  // Local version file to track current version
  versionFile: path.join(os.homedir(), 'NACPAC-Deploy', 'version.json'),

  logFile: path.join(os.homedir(), 'NACPAC-Deploy', 'deploy.log'),
};

// ── Logging ──────────────────────────────────────────────────────
function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const logMsg = `[${timestamp}] [${level}] ${message}`;
  console.log(logMsg);

  try {
    fs.appendFileSync(CONFIG.logFile, logMsg + '\n');
  } catch (e) {
    // Silently fail if can't write to log
  }
}

// ── Initialize ───────────────────────────────────────────────────
function initialize() {
  try {
    if (!fs.existsSync(CONFIG.deployDir)) {
      fs.mkdirSync(CONFIG.deployDir, { recursive: true });
    }

    if (!fs.existsSync(CONFIG.versionFile)) {
      fs.writeFileSync(CONFIG.versionFile, JSON.stringify({
        version: '1.0.0',
        lastUpdated: new Date().toISOString(),
        lastChecked: new Date().toISOString(),
      }, null, 2));
    }

    log('Deploy server initialized', 'INFO');
  } catch (e) {
    log(`Initialization failed: ${e.message}`, 'ERROR');
  }
}

// ── Read version ─────────────────────────────────────────────────
function readVersion() {
  try {
    const data = fs.readFileSync(CONFIG.versionFile, 'utf8');
    return JSON.parse(data);
  } catch (e) {
    log(`Error reading version: ${e.message}`, 'WARN');
    return { version: '1.0.0', lastUpdated: new Date().toISOString() };
  }
}

// ── Write version ────────────────────────────────────────────────
function writeVersion(versionObj) {
  try {
    fs.writeFileSync(CONFIG.versionFile, JSON.stringify(versionObj, null, 2));
  } catch (e) {
    log(`Error writing version: ${e.message}`, 'ERROR');
  }
}

// ── Check for updates ────────────────────────────────────────────
async function checkUpdates() {
  return new Promise((resolve) => {
    log('Checking for updates from Google Drive...', 'INFO');

    if (!CONFIG.googleDriveFolderId) {
      log('Google Drive folder ID not configured. Set NACPAC_DRIVE_FOLDER_ID env var', 'WARN');
      resolve({ available: false, reason: 'Not configured' });
      return;
    }

    // This is a placeholder — in production, you'd query Google Drive API
    // For now, we assume updates are available and user will trigger deployment
    const current = readVersion();
    resolve({
      available: true,
      currentVersion: current.version,
      message: 'Run "deploy latest" to update'
    });
  });
}

// ── Download from Google Drive ───────────────────────────────────
async function downloadFromDrive() {
  return new Promise((resolve, reject) => {
    if (!CONFIG.googleDriveFolderId) {
      reject(new Error('Google Drive folder ID not configured'));
      return;
    }

    log(`Fetching latest .exe from Google Drive folder: ${CONFIG.googleDriveFolderId}`, 'INFO');

    // Placeholder: In production, use google-auth-library and google-drive-api
    // For MVP, operator manually uploads to shared folder and we sync via rclone or similar

    const downloadPath = path.join(CONFIG.deployDir, CONFIG.appExeName);

    // Check if file exists locally in deploy folder (manual sync assumed)
    if (fs.existsSync(downloadPath)) {
      log(`Found ${CONFIG.appExeName} in deploy folder`, 'INFO');
      resolve({ success: true, path: downloadPath });
    } else {
      reject(new Error(`${CONFIG.appExeName} not found in ${CONFIG.deployDir}. Ensure file is synced from Google Drive.`));
    }
  });
}

// ── Kill app process ─────────────────────────────────────────────
async function killApp() {
  return new Promise((resolve) => {
    log('Stopping NACPAC app...', 'INFO');

    exec(`taskkill /IM "${CONFIG.appExeName}" /F`, (error) => {
      if (error && !error.message.includes('not found')) {
        log(`Warning stopping app: ${error.message}`, 'WARN');
      } else {
        log('App stopped', 'INFO');
      }
      // Wait a moment for clean shutdown
      setTimeout(() => resolve(), 500);
    });
  });
}

// ── Replace executable ───────────────────────────────────────────
async function replaceExecutable(newPath) {
  return new Promise((resolve, reject) => {
    const currentPath = path.join(CONFIG.appDir, CONFIG.appExeName);
    const backupPath = path.join(CONFIG.deployDir, `${CONFIG.appExeName}.backup`);

    try {
      // Backup current
      if (fs.existsSync(currentPath)) {
        fs.copyFileSync(currentPath, backupPath);
        log(`Backed up current version to ${backupPath}`, 'INFO');
      }

      // Replace with new
      fs.copyFileSync(newPath, currentPath);
      log(`Replaced ${currentPath} with new version`, 'INFO');
      resolve();
    } catch (e) {
      reject(new Error(`Failed to replace executable: ${e.message}`));
    }
  });
}

// ── Start app ────────────────────────────────────────────────────
async function startApp() {
  return new Promise((resolve, reject) => {
    const appPath = path.join(CONFIG.appDir, CONFIG.appExeName);

    log(`Starting NACPAC from ${appPath}`, 'INFO');

    try {
      // Spawn detached so it survives after this process exits
      const proc = spawn(appPath, [], {
        detached: true,
        stdio: 'ignore'
      });

      proc.unref();

      setTimeout(() => {
        log('App started successfully', 'INFO');
        resolve();
      }, 1000);
    } catch (e) {
      reject(new Error(`Failed to start app: ${e.message}`));
    }
  });
}

// ── Deploy flow ──────────────────────────────────────────────────
async function deployLatest() {
  try {
    log('═══ STARTING OTA DEPLOYMENT ═══', 'INFO');

    // 1. Download
    const { path: downloadPath } = await downloadFromDrive();
    log(`Downloaded: ${downloadPath}`, 'INFO');

    // 2. Kill running app
    await killApp();
    log('Killed running app', 'INFO');

    // 3. Replace executable
    await replaceExecutable(downloadPath);
    log('Replaced executable', 'INFO');

    // 4. Update version file
    const newVersion = readVersion();
    newVersion.lastUpdated = new Date().toISOString();
    writeVersion(newVersion);

    // 5. Start app
    await startApp();
    log('Started new version', 'INFO');

    log('═══ DEPLOYMENT COMPLETE ═══', 'INFO');
    return { success: true, message: 'App updated and restarted' };
  } catch (e) {
    log(`DEPLOYMENT FAILED: ${e.message}`, 'ERROR');
    return { success: false, error: e.message };
  }
}

// ── Command handler ──────────────────────────────────────────────
async function handleCommand(command) {
  const cmd = command.toLowerCase().trim();

  if (cmd === 'deploy latest') {
    return await deployLatest();
  }

  if (cmd === 'check updates') {
    return await checkUpdates();
  }

  if (cmd === 'current version') {
    const ver = readVersion();
    return { version: ver.version, lastUpdated: ver.lastUpdated };
  }

  if (cmd === 'status') {
    const ver = readVersion();
    return {
      app: CONFIG.appName,
      version: ver.version,
      lastUpdated: ver.lastUpdated,
      deployDir: CONFIG.deployDir,
      logFile: CONFIG.logFile
    };
  }

  return { error: `Unknown command: ${command}. Try: "deploy latest", "check updates", "current version", "status"` };
}

// ── Main ─────────────────────────────────────────────────────────
async function main() {
  initialize();

  log(`NACPAC Deploy Server started`, 'INFO');
  log(`App directory: ${CONFIG.appDir}`, 'INFO');
  log(`Deploy directory: ${CONFIG.deployDir}`, 'INFO');
  log(`Log file: ${CONFIG.logFile}`, 'INFO');

  // Listen for stdin commands (for testing)
  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
  });

  rl.on('line', async (line) => {
    const result = await handleCommand(line);
    console.log(JSON.stringify(result, null, 2));
  });

  rl.on('close', () => {
    log('Deploy server exiting', 'INFO');
    process.exit(0);
  });
}

main().catch(e => {
  log(`Fatal error: ${e.message}`, 'ERROR');
  process.exit(1);
});

// Export for programmatic use
module.exports = { handleCommand, deployLatest, checkUpdates };
