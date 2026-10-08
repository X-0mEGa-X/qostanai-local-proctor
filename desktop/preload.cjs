const {contextBridge, ipcRenderer} = require('electron');
contextBridge.exposeInMainWorld('desktop', {
  setProtected: (enabled) => ipcRenderer.invoke('set-protected', Boolean(enabled)),
  emergencyStop: () => ipcRenderer.invoke('emergency-stop'),
  onSecurityEvent: (callback) => ipcRenderer.on('security-event', (_event, code) => callback(code)),
  onEmergency: (callback) => ipcRenderer.on('emergency-exit', () => callback()),
});
