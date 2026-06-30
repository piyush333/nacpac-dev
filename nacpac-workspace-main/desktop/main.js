// ─────────────────────────────────────────────────────────────────
//  NACPAC Desktop — Electron Main Process
// ─────────────────────────────────────────────────────────────────
const { app, BrowserWindow, ipcMain, shell, Notification, dialog } = require('electron');
const path = require('path');
const { autoUpdater } = require('electron-updater');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width:  1280,
    height: 800,
    minWidth:  900,
    minHeight: 600,
    backgroundColor: '#0f0d1a',
    titleBarStyle: 'default',
    webPreferences: {
      preload:         path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration:  false,
    },
    icon: path.join(__dirname, 'assets', 'icon.ico'),
    title: 'NACPAC Production',
  });

  mainWindow.loadFile('index.html');

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
}

// ── Auto-updater ──────────────────────────────────────────────────
function setupAutoUpdater() {
  autoUpdater.autoDownload = true;
  autoUpdater.autoInstallOnAppQuit = true;

  autoUpdater.on('error', (err) => {
    // Log silently — don't bother the operator for update check failures
    console.error('[updater] error:', err.message);
  });

  autoUpdater.on('update-available', info => {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: `NACPAC Production v${info.version} is being downloaded…`,
      buttons: ['OK'],
    });
  });

  autoUpdater.on('update-downloaded', () => {
    dialog.showMessageBox(mainWindow, {
      type: 'question',
      title: 'Update Ready',
      message: 'Update downloaded. Restart now to apply?',
      buttons: ['Restart', 'Later'],
    }).then(({ response }) => {
      if (response === 0) autoUpdater.quitAndInstall();
    });
  });

  // Check for updates every 30 minutes
  autoUpdater.checkForUpdatesAndNotify();
  setInterval(() => autoUpdater.checkForUpdatesAndNotify(), 30 * 60 * 1000);
}

app.whenReady().then(() => {
  createWindow();
  if (app.isPackaged) setupAutoUpdater();

  // Pin to taskbar on Windows
  if (process.platform === 'win32' && mainWindow) {
    mainWindow.setAppDetails({
      appId: 'com.nacpac.desktop',
      appIconPath: path.join(__dirname, 'assets', 'icon.ico'),
      appIconIndex: 0,
      recentDisplayName: 'NACPAC Production',
    });
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// ── IPC: App version ──────────────────────────────────────────────
ipcMain.handle('get-app-version', () => app.getVersion());

// ── IPC: Manual update check ──────────────────────────────────────
ipcMain.handle('check-for-updates', () => {
  if (app.isPackaged) autoUpdater.checkForUpdatesAndNotify();
});

// ── IPC: Open URL in system browser (for file downloads) ──────────
ipcMain.on('open-url', (event, url) => {
  shell.openExternal(url);
});

// ── IPC: Show OS notification ─────────────────────────────────────
ipcMain.on('notify', (event, { title, body }) => {
  if (Notification.isSupported()) {
    new Notification({ title, body, silent: false }).show();
  }
});

// ── IPC: Set window badge (new job count) ─────────────────────────
ipcMain.on('set-badge', (event, count) => {
  if (process.platform === 'darwin') {
    app.dock.setBadge(count > 0 ? String(count) : '');
  }
});
