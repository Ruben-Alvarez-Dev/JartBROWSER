import { app, BrowserWindow, ipcMain, dialog, Menu, Tray, nativeImage, shell } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Environment
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

// Window state
let mainWindow: BrowserWindow | null = null;
let wizardWindow: BrowserWindow | null = null;
let tray: Tray | null = null;

// App configuration
interface AppConfig {
  mode: 'simple' | 'advanced';
  deploymentType: 'local' | 'vps' | 'hybrid';
  providers: Record<string, { enabled: boolean; apiKey?: string }>;
  dockerRunning: boolean;
  backendPort: number;
  mcpPort: number;
}

let appConfig: AppConfig = {
  mode: 'simple',
  deploymentType: 'local',
  providers: {},
  dockerRunning: false,
  backendPort: 8000,
  mcpPort: 3001
};

// ============== Window Creation ==============

function createMainWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    title: 'JartBROWSER',
    backgroundColor: '#0f0f0f',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true
    },
    show: false
  });

  // Load content
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  // Show when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  // Handle close
  mainWindow.on('close', (event) => {
    if (tray && !app.isQuitting) {
      event.preventDefault();
      mainWindow?.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create menu
  createAppMenu();
}

function createWizardWindow(): void {
  wizardWindow = new BrowserWindow({
    width: 800,
    height: 600,
    resizable: false,
    title: 'JartBROWSER Setup Wizard',
    backgroundColor: '#0f0f0f',
    parent: mainWindow || undefined,
    modal: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  if (isDev) {
    wizardWindow.loadURL('http://localhost:5173/#/wizard');
  } else {
    wizardWindow.loadFile(path.join(__dirname, '../renderer/index.html'), {
      hash: '/wizard'
    });
  }

  wizardWindow.setMenu(null);
  wizardWindow.on('closed', () => {
    wizardWindow = null;
  });
}

// ============== Menu ==============

function createAppMenu(): void {
  const template: Electron.MenuItemConstructorOptions[] = [
    {
      label: 'JartBROWSER',
      submenu: [
        { label: 'About JartBROWSER', role: 'about' },
        { type: 'separator' },
        { label: 'Preferences', accelerator: 'CmdOrCtrl+,', click: () => mainWindow?.webContents.send('navigate', '/settings') },
        { type: 'separator' },
        { label: 'Quit', accelerator: 'CmdOrCtrl+Q', click: () => { app.isQuitting = true; app.quit(); } }
      ]
    },
    {
      label: 'File',
      submenu: [
        { label: 'New Tab', accelerator: 'CmdOrCtrl+T', click: () => mainWindow?.webContents.send('new-tab') },
        { label: 'New Window', accelerator: 'CmdOrCtrl+Shift+N', click: () => createMainWindow() },
        { type: 'separator' },
        { label: 'Import Configuration', click: handleImportConfig },
        { label: 'Export Configuration', click: handleExportConfig },
        { type: 'separator' },
        { label: 'Close Tab', accelerator: 'CmdOrCtrl+W', role: 'close' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { label: 'Undo', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
        { label: 'Redo', accelerator: 'CmdOrCtrl+Shift+Z', role: 'redo' },
        { type: 'separator' },
        { label: 'Cut', accelerator: 'CmdOrCtrl+X', role: 'cut' },
        { label: 'Copy', accelerator: 'CmdOrCtrl+C', role: 'copy' },
        { label: 'Paste', accelerator: 'CmdOrCtrl+V', role: 'paste' },
        { label: 'Select All', accelerator: 'CmdOrCtrl+A', role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { label: 'Reload', accelerator: 'CmdOrCtrl+R', role: 'reload' },
        { label: 'Force Reload', accelerator: 'CmdOrCtrl+Shift+R', role: 'forceReload' },
        { type: 'separator' },
        { label: 'Toggle DevTools', accelerator: 'F12', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: 'Zoom In', accelerator: 'CmdOrCtrl+Plus', role: 'zoomIn' },
        { label: 'Zoom Out', accelerator: 'CmdOrCtrl+-', role: 'zoomOut' },
        { label: 'Reset Zoom', accelerator: 'CmdOrCtrl+0', role: 'resetZoom' },
        { type: 'separator' },
        { label: 'Toggle Fullscreen', accelerator: 'F11', role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Docker',
      submenu: [
        { label: 'Start Services', click: () => mainWindow?.webContents.send('docker', 'start') },
        { label: 'Stop Services', click: () => mainWindow?.webContents.send('docker', 'stop') },
        { type: 'separator' },
        { label: 'Open Docker Dashboard', click: () => shell.openExternal('http://localhost:8080') },
        { type: 'separator' },
        { label: 'View Logs', click: () => mainWindow?.webContents.send('docker', 'logs') }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { label: 'Minimize', accelerator: 'CmdOrCtrl+M', role: 'minimize' },
        { label: 'Maximize', click: () => mainWindow?.isMaximized() ? mainWindow.unmaximize() : mainWindow?.maximize() },
        { type: 'separator' },
        { label: 'Always on Top', type: 'checkbox', checked: false, click: (menuItem) => mainWindow?.setAlwaysOnTop(menuItem.checked) }
      ]
    },
    {
      label: 'Help',
      submenu: [
        { label: 'Documentation', click: () => shell.openExternal('https://docs.jartbrowser.io') },
        { label: 'Report Issue', click: () => shell.openExternal('https://github.com/jartbrowser/JartBROWSER/issues') },
        { type: 'separator' },
        { label: 'View Logs', click: () => shell.openPath(path.join(app.getPath('userData'), 'logs')) }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// ============== System Tray ==============

function createTray(): void {
  // Create a simple icon
  const icon = nativeImage.createEmpty();
  
  tray = new Tray(icon);
  tray.setToolTip('JartBROWSER');
  
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show JartBROWSER', click: () => mainWindow?.show() },
    { type: 'separator' },
    { label: 'Start Docker', click: () => mainWindow?.webContents.send('docker', 'start') },
    { label: 'Stop Docker', click: () => mainWindow?.webContents.send('docker', 'stop') },
    { type: 'separator' },
    { label: 'Quit', click: () => { app.isQuitting = true; app.quit(); } }
  ]);
  
  tray.setContextMenu(contextMenu);
  tray.on('click', () => mainWindow?.show());
}

// ============== IPC Handlers ==============

function setupIpcHandlers(): void {
  // Config
  ipcMain.handle('get-config', () => appConfig);
  
  ipcMain.handle('set-config', (_, config: Partial<AppConfig>) => {
    appConfig = { ...appConfig, ...config };
    return appConfig;
  });

  // Dialog
  ipcMain.handle('show-open-dialog', async (_, options) => {
    return dialog.showOpenDialog(mainWindow!, options);
  });

  ipcMain.handle('show-save-dialog', async (_, options) => {
    return dialog.showSaveDialog(mainWindow!, options);
  });

  ipcMain.handle('show-message-box', async (_, options) => {
    return dialog.showMessageBox(mainWindow!, options);
  });

  // App info
  ipcMain.handle('get-app-version', () => app.getVersion());
  ipcMain.handle('get-app-path', (_, name) => app.getPath(name as any));

  // Window
  ipcMain.handle('minimize-window', () => mainWindow?.minimize());
  ipcMain.handle('maximize-window', () => {
    if (mainWindow?.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow?.maximize();
    }
  });
  ipcMain.handle('close-window', () => mainWindow?.close());
  ipcMain.handle('is-maximized', () => mainWindow?.isMaximized());

  // Shell
  ipcMain.handle('open-external', (_, url) => shell.openExternal(url));
  ipcMain.handle('open-path', (_, filePath) => shell.openPath(filePath));

  // Docker (placeholder - would communicate with backend)
  ipcMain.handle('docker-status', async () => {
    return { running: appConfig.dockerRunning, containers: [] };
  });

  ipcMain.handle('docker-start', async () => {
    appConfig.dockerRunning = true;
    return { success: true };
  });

  ipcMain.handle('docker-stop', async () => {
    appConfig.dockerRunning = false;
    return { success: true };
  });

  // API
  ipcMain.handle('api-request', async (_, { endpoint, method, body }) => {
    const port = appConfig.backendPort;
    const url = `http://localhost:${port}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined
      });
      return await response.json();
    } catch (error) {
      return { error: String(error) };
    }
  });
}

// ============== Config Import/Export ==============

async function handleImportConfig(): Promise<void> {
  const result = await dialog.showOpenDialog(mainWindow!, {
    title: 'Import Configuration',
    filters: [{ name: 'JSON', extensions: ['json'] }],
    properties: ['openFile']
  });

  if (!result.canceled && result.filePaths.length > 0) {
    // Would read and parse config file
    mainWindow?.webContents.send('config-imported', result.filePaths[0]);
  }
}

async function handleExportConfig(): Promise<void> {
  const result = await dialog.showSaveDialog(mainWindow!, {
    title: 'Export Configuration',
    defaultPath: 'jartbrowser-config.json',
    filters: [{ name: 'JSON', extensions: ['json'] }]
  });

  if (!result.canceled && result.filePath) {
    // Would save config to file
    mainWindow?.webContents.send('config-exported', result.filePath);
  }
}

// ============== App Lifecycle ==============

// Extend app type to include isQuitting
declare module 'electron' {
  interface App {
    isQuitting?: boolean;
  }
}

app.whenReady().then(() => {
  console.log('[JartBROWSER] Starting application...');
  
  // Setup IPC
  setupIpcHandlers();
  
  // Create main window
  createMainWindow();
  
  // Create system tray
  createTray();
  
  // Check if first run - show wizard
  const isFirstRun = !app.getPath('userData');
  if (isFirstRun) {
    createWizardWindow();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });

  console.log('[JartBROWSER] Application ready');
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('[JartBROWSER] Uncaught exception:', error);
  dialog.showErrorBox('Error', `An unexpected error occurred: ${error.message}`);
});

process.on('unhandledRejection', (reason) => {
  console.error('[JartBROWSER] Unhandled rejection:', reason);
});
