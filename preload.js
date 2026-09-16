const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('midnightAPI', {
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  powerHigh: () => ipcRenderer.invoke('opt-power-high'),
  powerBalanced: () => ipcRenderer.invoke('opt-power-balanced'),
  gameMode: (enable) => ipcRenderer.invoke('opt-game-mode', enable),
  gameBar: (disable) => ipcRenderer.invoke('opt-game-bar', disable),
  cleanTemp: () => ipcRenderer.invoke('opt-clean-temp'),
  network: () => ipcRenderer.invoke('opt-network'),
  visualEffects: (perf) => ipcRenderer.invoke('opt-visual-effects', perf),
  killBackground: () => ipcRenderer.invoke('opt-kill-background'),
  gpuPriority: () => ipcRenderer.invoke('opt-gpu-priority'),
  competitiveOn: () => ipcRenderer.invoke('competitive-on'),
  competitiveOff: () => ipcRenderer.invoke('competitive-off'),
  launchGame: (p) => ipcRenderer.invoke('launch-game-boosted', p),
  bugsList: () => ipcRenderer.invoke('bugs-list'),
  bugsAdd: (t) => ipcRenderer.invoke('bugs-add', t),
  autostartGet: () => ipcRenderer.invoke('autostart-get'),
  autostartSet: (e) => ipcRenderer.invoke('autostart-set', e),
});
