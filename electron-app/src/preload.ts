import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // Config
  getConfig: () => ipcRenderer.invoke('get-config'),
  setConfig: (config: any) => ipcRenderer.invoke('set-config', config),

  // Dialog
  showOpenDialog: (options: any) => ipcRenderer.invoke('show-open-dialog', options),
  showSaveDialog: (options: any) => ipcRenderer.invoke('show-save-dialog', options),
  showMessageBox: (options: any) => ipcRenderer.invoke('show-message-box', options),

  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getAppPath: (name: string) => ipcRenderer.invoke('get-app-path', name),

  // Window controls
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
  closeWindow: () => ipcRenderer.invoke('close-window'),
  isMaximized: () => ipcRenderer.invoke('is-maximized'),

  // Shell
  openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
  openPath: (path: string) => ipcRenderer.invoke('open-path', path),

  // Docker
  dockerStatus: () => ipcRenderer.invoke('docker-status'),
  dockerStart: () => ipcRenderer.invoke('docker-start'),
  dockerStop: () => ipcRenderer.invoke('docker-stop'),

  // API
  apiRequest: (options: { endpoint: string; method: string; body?: any }) => 
    ipcRenderer.invoke('api-request', options),

  // Event listeners
  onNavigate: (callback: (route: string) => void) => {
    ipcRenderer.on('navigate', (_, route) => callback(route));
  },
  onDocker: (callback: (action: string) => void) => {
    ipcRenderer.on('docker', (_, action) => callback(action));
  },
  onNewTab: (callback: () => void) => {
    ipcRenderer.on('new-tab', () => callback());
  },
  onConfigImported: (callback: (path: string) => void) => {
    ipcRenderer.on('config-imported', (_, path) => callback(path));
  },
  onConfigExported: (callback: (path: string) => void) => {
    ipcRenderer.on('config-exported', (_, path) => callback(path));
  },

  // Remove listeners
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// Type declarations
declare global {
  interface Window {
    electronAPI: {
      getConfig: () => Promise<any>;
      setConfig: (config: any) => Promise<any>;
      showOpenDialog: (options: any) => Promise<any>;
      showSaveDialog: (options: any) => Promise<any>;
      showMessageBox: (options: any) => Promise<any>;
      getAppVersion: () => Promise<string>;
      getAppPath: (name: string) => Promise<string>;
      minimizeWindow: () => Promise<void>;
      maximizeWindow: () => Promise<void>;
      closeWindow: () => Promise<void>;
      isMaximized: () => Promise<boolean>;
      openExternal: (url: string) => Promise<void>;
      openPath: (path: string) => Promise<string>;
      dockerStatus: () => Promise<any>;
      dockerStart: () => Promise<any>;
      dockerStop: () => Promise<any>;
      apiRequest: (options: { endpoint: string; method: string; body?: any }) => Promise<any>;
      onNavigate: (callback: (route: string) => void) => void;
      onDocker: (callback: (action: string) => void) => void;
      onNewTab: (callback: () => void) => void;
      onConfigImported: (callback: (path: string) => void) => void;
      onConfigExported: (callback: (path: string) => void) => void;
      removeAllListeners: (channel: string) => void;
    };
  }
}
