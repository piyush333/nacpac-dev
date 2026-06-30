// ─────────────────────────────────────────────────────────────────
//  NACPAC Desktop — Preload / Context Bridge
//  Exposes safe APIs from main process to renderer
// ─────────────────────────────────────────────────────────────────
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('nacpac', {
  /** Open a URL in the system default browser */
  openUrl: (url) => ipcRenderer.send('open-url', url),

  /** Show a native OS notification */
  notify: (title, body) => ipcRenderer.send('notify', { title, body }),

  /** Update the taskbar badge count */
  setBadge: (count) => ipcRenderer.send('set-badge', count),

  /** Get the current app version (e.g. "1.0.1") */
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  /** Manually trigger an update check (no-op outside packaged builds) */
  checkForUpdates: () => ipcRenderer.invoke('check-for-updates'),
});
