const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Screen capture
  getScreenInfo: () => ipcRenderer.invoke('get-screen-info'),
  captureScreenRegion: (region) => ipcRenderer.invoke('capture-screen-region', region),
  setCaptureRegion: (region) => ipcRenderer.invoke('set-capture-region', region),
  
  // Window controls
  minimize: () => ipcRenderer.invoke('minimize-window'),
  maximize: () => ipcRenderer.invoke('maximize-window'),
  close: () => ipcRenderer.invoke('close-window'),
  
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // Event listeners
  onScreenCapture: (callback) => {
    ipcRenderer.removeAllListeners('screen-capture');
    ipcRenderer.on('screen-capture', callback);
  },
  
  onPatternDetected: (callback) => {
    ipcRenderer.removeAllListeners('pattern-detected');
    ipcRenderer.on('pattern-detected', callback);
  },
  
  // Cleanup
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});
