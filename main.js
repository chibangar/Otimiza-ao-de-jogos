const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const { exec } = require('child_process');
const os = require('os');
const fs = require('fs');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 640,
    backgroundColor: '#060714',
    autoHideMenuBar: true,
    title: 'Midnight Optimizer',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// ---------- helpers ----------
function runPS(command) {
  return new Promise((resolve) => {
    exec(`powershell -NoProfile -ExecutionPolicy Bypass -Command "${command.replace(/"/g, "'")}"`, { timeout: 60000 }, (error, stdout, stderr) => {
      resolve({ success: !error, output: (stdout || stderr || '').trim(), error: error ? error.message : null });
    });
  });
}

function runCMD(command) {
  return new Promise((resolve) => {
    exec(command, { timeout: 60000 }, (error, stdout, stderr) => {
      resolve({ success: !error, output: (stdout || stderr || '').trim(), error: error ? error.message : null });
    });
  });
}

// ---------- SYSTEM INFO ----------
ipcMain.handle('get-system-info', async () => {
  const cpu = await runPS("(Get-CimInstance Win32_Processor).Name");
  const gpu = await runPS("(Get-CimInstance Win32_VideoController).Name -join ' | '");
  const ramTotal = await runPS("[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)");
  const ramFree = await runPS("[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024/1024,1)");
  const disk = await runPS("Get-PSDrive C | Select-Object -ExpandProperty Free");
  const diskFreeGB = await runPS("[math]::Round((Get-PSDrive C).Free/1GB,1)");
  const win = await runPS("(Get-CimInstance Win32_OperatingSystem).Caption");
  const power = await runCMD("powercfg /getactivescheme");

  const totalMem = parseFloat(ramTotal.output) || 16;
  const freeMem = parseFloat(ramFree.output) || 8;
  const usedPct = Math.round(((totalMem - freeMem) / totalMem) * 100);

  return {
    cpu: cpu.output || os.cpus()[0].model,
    gpu: gpu.output || 'GPU não detetada',
    ramTotal: ramTotal.output || '?',
    ramFree: ramFree.output || '?',
    ramUsedPct: usedPct,
    diskFree: diskFreeGB.output || '?',
    os: win.output || `${os.type()} ${os.release()}`,
    power: power.output || '',
    hostname: os.hostname()
  };
});

// ---------- Otimizações individuais ----------
ipcMain.handle('opt-power-high', async () => {
  // Ativa plano Alto Desempenho / Ultimate
  await runCMD('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 2>nul');
  const r = await runCMD('powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61');
  if (!r.success) await runCMD('powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c');
  return r;
});

ipcMain.handle('opt-power-balanced', async () => {
  return await runCMD('powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e');
});

ipcMain.handle('opt-game-mode', async (e, enable) => {
  const v = enable ? 1 : 0;
  const cmd = `Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AllowAutoGameMode' -Value ${v} -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AutoGameModeEnabled' -Value ${v} -Force`;
  return await runPS(cmd);
});

ipcMain.handle('opt-game-bar', async (e, disable) => {
  // disable=true -> desativa Game Bar/DVR
  const cap = disable ? 0 : 1;
  const dvr = disable ? 0 : 1;
  const cmd = `Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR' -Name 'AppCaptureEnabled' -Value ${cap} -Force; Set-ItemProperty -Path 'HKCU:\\System\\GameConfigStore' -Name 'GameDVR_Enabled' -Value ${dvr} -Force`;
  return await runPS(cmd);
});

ipcMain.handle('opt-clean-temp', async () => {
  const cmd = `Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path 'C:\\Windows\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue; ipconfig /flushdns | Out-Null; 'LIMPEZA OK'`;
  return await runPS(cmd);
});

ipcMain.handle('opt-network', async () => {
  const steps = [];
  steps.push(await runCMD('ipconfig /flushdns'));
  // Desativa network throttling para jogos
  steps.push(await runPS(`Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile' -Name 'NetworkThrottlingIndex' -Value 4294967295 -Force`));
  steps.push(await runPS(`Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile' -Name 'SystemResponsiveness' -Value 0 -Force`));
  const ok = steps.every(s => s.success);
  return { success: ok, output: steps.map(s => s.output).join('\n') };
});

ipcMain.handle('opt-visual-effects', async (e, performance) => {
  // performance=true -> modo desempenho (sem animações)
  if (performance) {
    return await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name 'VisualFXSetting' -Value 2 -Force; Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop\\WindowMetrics' -Name 'MinAnimate' -Value '0' -Force`);
  } else {
    return await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name 'VisualFXSetting' -Value 0 -Force; Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop\\WindowMetrics' -Name 'MinAnimate' -Value '1' -Force`);
  }
});

ipcMain.handle('opt-kill-background', async () => {
  const list = ['OneDrive.exe','Teams.exe','msedge.exe','chrome.exe','firefox.exe','Spotify.exe','Discord.exe','Skype.exe','Cortana.exe','XboxApp.exe','YourPhone.exe'];
  const results = [];
  for (const p of list) {
    const r = await runCMD(`taskkill /F /IM ${p} 2>nul`);
    results.push(r);
  }
  return { success: true, output: 'Processos em 2º plano terminados.' };
});

ipcMain.handle('opt-gpu-priority', async () => {
  // HAGS + prioridade GPU para jogos
  const cmd = `Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers' -Name 'HwSchMode' -Value 2 -Force; Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games' -Name 'GPU Priority' -Value 8 -Force; Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games' -Name 'Priority' -Value 6 -Force; 'GPU OK (reinicia para HAGS total)'`;
  return await runPS(cmd);
});

// ---------- MODO COMPETITIVO ----------
ipcMain.handle('competitive-on', async () => {
  const log = [];
  const push = (name, r) => log.push(`${r.success ? '✔' : '✘'} ${name}`);

  let r = await runCMD('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 2>nul');
  r = await runCMD('powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61');
  push('Plano Ultimate Performance ativo', r);

  r = await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AllowAutoGameMode' -Value 1 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AutoGameModeEnabled' -Value 1 -Force; 'OK'`);
  push('Modo Jogo ativado', r);

  r = await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR' -Name 'AppCaptureEnabled' -Value 0 -Force; Set-ItemProperty -Path 'HKCU:\\System\\GameConfigStore' -Name 'GameDVR_Enabled' -Value 0 -Force; 'OK'`);
  push('Game DVR / Game Bar desativados', r);

  r = await runPS(`Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; 'OK'`);
  push('Ficheiros temporários limpos', r);

  r = await runCMD('ipconfig /flushdns');
  push('DNS limpo (ping mais estável)', r);

  r = await runPS(`Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile' -Name 'NetworkThrottlingIndex' -Value 4294967295 -Force; Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile' -Name 'SystemResponsiveness' -Value 0 -Force; 'OK'`);
  push('Rede otimizada para jogos', r);

  r = await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name 'VisualFXSetting' -Value 2 -Force; 'OK'`);
  push('Efeitos visuais em modo desempenho', r);

  // Mata browsers e apps pesadas (não mata Discord por defeito no modo competitivo? mata sim para FPS máximo)
  const killList = ['OneDrive.exe','Teams.exe','msedge.exe','chrome.exe','firefox.exe','Spotify.exe','Skype.exe'];
  for (const p of killList) { await runCMD(`taskkill /F /IM ${p} 2>nul`); }
  push('Apps em 2º plano encerradas', { success: true });

  return { success: true, output: log.join('\n') };
});

ipcMain.handle('competitive-off', async () => {
  const log = [];
  let r = await runCMD('powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e');
  log.push(`${r.success ? '✔' : '✘'} Plano Equilibrado restaurado`);
  r = await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name 'VisualFXSetting' -Value 0 -Force; 'OK'`);
  log.push(`${r.success ? '✔' : '✘'} Efeitos visuais restaurados`);
  return { success: true, output: log.join('\n') };
});

// ---------- JOGOS ----------
ipcMain.handle('launch-game-boosted', async (e, gamePath) => {
  if (!gamePath || !fs.existsSync(gamePath)) return { success: false, output: 'Ficheiro não encontrado.' };
  // Mata porcaria leve e lança jogo em prioridade Alta
  await runCMD('taskkill /F /IM msedge.exe 2>nul');
  await runCMD('taskkill /F /IM chrome.exe 2>nul');
  const { spawn } = require('child_process');
  try {
    const ext = path.extname(gamePath).toLowerCase();
    if (ext === '.lnk' || ext === '.exe') {
      // Lança com prioridade alta via cmd /c start
      exec(`cmd /c start "" /HIGH "${gamePath}"`);
      return { success: true, output: 'Jogo lançado com prioridade ALTA.' };
    }
    shell.openPath(gamePath);
    return { success: true, output: 'Jogo lançado.' };
  } catch (err) {
    return { success: false, output: String(err) };
  }
});

ipcMain.handle('open-external', async (e, url) => {
  shell.openExternal(url);
});

// ---------- CHAT DE BUGS (Electron: ficheiro local) ----------
function bugsFile() {
  try { return path.join(app.getPath('userData'), 'bugs.json'); }
  catch { return path.join(os.tmpdir(), 'midnight_bugs.json'); }
}
function bugsLoad() {
  try {
    const p = bugsFile();
    if (fs.existsSync(p)) { const d = JSON.parse(fs.readFileSync(p, 'utf8')); return Array.isArray(d) ? d : []; }
  } catch {}
  return [];
}
function bugsSave(items) {
  try { fs.writeFileSync(bugsFile(), JSON.stringify(items.slice(-500), null, 1), 'utf8'); } catch {}
}
ipcMain.handle('bugs-list', async () => ({ success: true, bugs: bugsLoad() }));
ipcMain.handle('bugs-add', async (e, text) => {
  text = (text || '').trim();
  if (!text) return { success: false, output: 'Escreve o bug primeiro.' };
  const items = bugsLoad();
  items.push({ user: 'eu', text: text.slice(0, 2000), when: new Date().toLocaleString('pt-PT') });
  bugsSave(items);
  return { success: true, output: 'Bug registado. Obrigado!' };
});

// ---------- ARRANQUE COM O WINDOWS (Electron) ----------
const AUTOSTART_NAME = 'Midnight Optimizer';
ipcMain.handle('autostart-get', async () => {
  try {
    if (process.platform !== 'win32') {
      const s = app.getLoginItemSettings();
      return { success: true, enabled: !!s.openAtLogin };
    }
    const r = await runCMD(`reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "${AUTOSTART_NAME}"`);
    return { success: true, enabled: !!r.success, path: r.success ? r.output : '' };
  } catch (err) { return { success: false, enabled: false, output: String(err) }; }
});
ipcMain.handle('autostart-set', async (e, enable) => {
  try {
    app.setLoginItemSettings({ openAtLogin: !!enable, name: AUTOSTART_NAME });
    if (process.platform === 'win32') {
      if (enable) {
        const exe = process.execPath;
        const r = await runCMD(`reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "${AUTOSTART_NAME}" /t REG_SZ /d "\\"${exe}\\"" /f`);
        return { success: r.success, enabled: !!r.success, output: r.success ? 'Arranque com o Windows ATIVADO. ✔' : ('Falha: ' + r.output) };
      }
      await runCMD(`reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "${AUTOSTART_NAME}" /f`);
      return { success: true, enabled: false, output: 'Arranque com o Windows DESATIVADO.' };
    }
    return { success: true, enabled: !!enable, output: !!enable ? 'Arranque ATIVADO. ✔' : 'Arranque DESATIVADO.' };
  } catch (err) { return { success: false, output: String(err) }; }
});
