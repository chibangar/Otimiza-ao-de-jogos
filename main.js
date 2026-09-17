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

ipcMain.handle('analyze-pc', async () => {
  // Diagnóstico do PC (paridade com app.py analyze_pc): lê estado real e recomenda.
  const recs = [];
  let score = 100;
  const push = (id, icon, title, reason, impact, action, penalty) => {
    recs.push({ id, icon, title, reason, impact, action });
    score -= penalty;
  };
  let reg = {};
  try {
    const r = await runPS("$j=@{}; try{$j.gamemode=(Get-ItemProperty 'HKCU:\\Software\\Microsoft\\GameBar' -Name AllowAutoGameMode -ErrorAction Stop).AllowAutoGameMode}catch{$j.gamemode=$null}; try{$j.capture=(Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR' -Name AppCaptureEnabled -ErrorAction Stop).AppCaptureEnabled}catch{$j.capture=$null}; try{$j.dvr=(Get-ItemProperty 'HKCU:\\System\\GameConfigStore' -Name GameDVR_Enabled -ErrorAction Stop).GameDVR_Enabled}catch{$j.dvr=$null}; try{$j.visual=(Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name VisualFXSetting -ErrorAction Stop).VisualFXSetting}catch{$j.visual=$null}; try{$j.net=(Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile' -Name NetworkThrottlingIndex -ErrorAction Stop).NetworkThrottlingIndex}catch{$j.net=$null}; try{$j.hags=(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers' -Name HwSchMode -ErrorAction Stop).HwSchMode}catch{$j.hags=$null}; $j | ConvertTo-Json -Compress");
    reg = JSON.parse(r.output || '{}');
  } catch {}
  const power = await runCMD('powercfg /getactivescheme');
  const pout = (power.output || '').toLowerCase();
  if (!pout.includes('e9a42b02') && !pout.includes('8c5e7fda'))
    push('power', '⚡', 'Energia máxima', 'O teu plano de energia está em modo económico/equilibrado — o CPU trava antes de dar o máximo nos jogos.', 'ALTO', 'power', 15);
  if (String(reg.gamemode) !== '1')
    push('gamemode', '🎮', 'Modo Jogo do Windows', 'O Modo Jogo está desligado — o Windows não prioriza o jogo quando estás em ranked.', 'ALTO', 'gamemode', 10);
  if (String(reg.capture) !== '0' || String(reg.dvr) !== '0')
    push('gamebar', '📼', 'Desligar DVR / Game Bar', 'A captura em 2º plano (DVR) está ativa e rouba FPS e disco enquanto jogas.', 'MÉDIO', 'gamebar', 8);
  if (String(reg.visual) !== '2')
    push('visual', '✨', 'Efeitos em modo desempenho', 'Animações e sombras do Windows estão a gastar GPU/CPU que devia ir para o jogo.', 'MÉDIO', 'visual', 8);
  if (String(reg.net) !== '4294967295')
    push('net', '🌐', 'Rede otimizada para jogos', 'O Windows limita a rede para poupar CPU — isto aumenta ping e dá spikes em jogos online.', 'ALTO', 'net', 10);
  if (String(reg.hags) !== '2')
    push('gpu', '🖥️', 'Prioridade GPU (HAGS)', 'O agendamento de GPU acelerado por hardware está desligado — perdes latência e FPS (pede reinício).', 'MÉDIO', 'gpu', 8);
  const total = parseFloat((await runPS('[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)')).output) || 16;
  const free = parseFloat((await runPS('[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024/1024,1)')).output) || 8;
  if (total <= 8)
    push('kill', '🧹', 'Limpar apps em 2º plano', `Só tens ${total} GB de RAM — browsers e launchers abertos comem a memória do jogo.`, 'ALTO', 'kill', 12);
  else if (free < total * 0.25)
    push('kill', '🧹', 'Limpar apps em 2º plano', `Só tens ${free} GB livres de ${total} GB — há apps pesadas abertas agora.`, 'MÉDIO', 'kill', 8);
  const diskFree = parseFloat((await runPS('[math]::Round((Get-PSDrive C).Free/1GB,1)')).output) || 50;
  if (diskFree < 15)
    push('temp', '💽', 'Limpeza de disco + TEMP', `O disco C: só tem ${diskFree} GB livres — jogos com pouco espaço têm stutter e updates falham.`, 'ALTO', 'temp', 12);
  score = Math.max(0, Math.min(100, score));
  const verdict = score >= 85 ? 'Máquina de guerra! Só afinações finas. ⚔' : score >= 65 ? 'Bom, mas há FPS fácil por ganhar. 🎯' : score >= 40 ? 'A perder desempenho todos os dias. 🔧' : 'Modo tartaruga! Precisas disto urgente. 🚨';
  const order = { ALTO: 0, 'MÉDIO': 1 };
  recs.sort((a, b) => (order[a.impact] ?? 2) - (order[b.impact] ?? 2));
  return { success: true, score, verdict, specs: `${total} GB RAM • C: ${diskFree} GB livres`, recs };
});

ipcMain.handle('opt-debloat', async () => {
  const cmd = `$apps=@('Microsoft.BingNews','Microsoft.BingWeather','Microsoft.GetHelp','Microsoft.Getstarted','Microsoft.MicrosoftOfficeHub','Microsoft.MicrosoftSolitaireCollection','Microsoft.People','Microsoft.Todos','Microsoft.WindowsFeedbackHub','Microsoft.YourPhone','Microsoft.ZuneMusic','Microsoft.ZuneVideo','Clipchamp.Clipchamp','Microsoft.549981C3F5F10'); $n=0; foreach($a in $apps){ $p=Get-AppxPackage -Name $a -ErrorAction SilentlyContinue; if($p){ $p | Remove-AppxPackage -ErrorAction SilentlyContinue; $n++ } }; 'DEBLOAT OK — ' + $n + ' apps removidas (Xbox e Game Bar intactos)'`;
  return await runPS(cmd);
});

ipcMain.handle('opt-privacy-on', async () => {
  return await runPS(`New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Force | Out-Null; Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Name 'AllowTelemetry' -Value 0 -Force; New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Force | Out-Null; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Name 'Enabled' -Value 0 -Force; 'PRIVACIDADE OK'`);
});

ipcMain.handle('opt-privacy-off', async () => {
  return await runPS(`Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Name 'AllowTelemetry' -Value 1 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Name 'Enabled' -Value 1 -Force; 'Privacidade restaurada'`);
});

ipcMain.handle('opt-gaming-extra', async (e, enable) => {
  const v = enable ? 1 : 0;
  if (enable) {
    return await runPS(`Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseSpeed' -Value '0' -Force; Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseThreshold1' -Value '0' -Force; Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseThreshold2' -Value '0' -Force; New-Item -Path 'HKCU:\\System\\GameConfigStore' -Force | Out-Null; Set-ItemProperty -Path 'HKCU:\\System\\GameConfigStore' -Name 'GameDVR_FSEBehaviorMode' -Value 2 -Force; New-Item -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling' -Force | Out-Null; Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling' -Name 'PowerThrottlingOff' -Value 1 -Force; 'GAMING EXTRA OK'`);
  }
  return await runPS(`Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseSpeed' -Value '1' -Force; Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseThreshold1' -Value '6' -Force; Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseThreshold2' -Value '10' -Force; Set-ItemProperty -Path 'HKCU:\\System\\GameConfigStore' -Name 'GameDVR_FSEBehaviorMode' -Value 0 -Force; Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling' -Name 'PowerThrottlingOff' -Value 0 -Force; 'Gaming extra restaurado'`);
});

ipcMain.handle('opt-system-extra', async (e, enable) => {
  if (enable) {
    return await runPS(`New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize' -Force | Out-Null; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize' -Name 'StartupDelayInMSec' -Value 0 -Force; New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization' -Force | Out-Null; Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization' -Name 'NoLockScreen' -Value 1 -Force; 'SISTEMA OK'`);
  }
  return await runPS(`Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize' -Name 'StartupDelayInMSec' -Force -ErrorAction SilentlyContinue; Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization' -Name 'NoLockScreen' -Value 0 -Force; 'Sistema restaurado'`);
});

ipcMain.handle('opt-privacy-extra', async (e, enable) => {
  if (enable) return await runPS(`New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Force | Out-Null; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'ContentDeliveryAllowed' -Value 0 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'SilentInstalledAppsEnabled' -Value 0 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'Start_TrackProgs' -Value 0 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Search' -Name 'BingSearchEnabled' -Value 0 -Force; 'PRIVACIDADE+ OK'`);
  return await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'ContentDeliveryAllowed' -Value 1 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'Start_TrackProgs' -Value 1 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Search' -Name 'BingSearchEnabled' -Value 1 -Force; 'Privacidade+ restaurada'`);
});

ipcMain.handle('opt-services', async (e, enable) => {
  const v = enable ? 4 : 3;
  return await runPS(`$svcs=@('DiagTrack','MapsBroker','RetailDemo','PhoneSvc','SmsRouter','Fax','PcaSvc','NfcSvc','dmwappushservice','lfsvc'); foreach($s in $svcs){ Set-ItemProperty -Path ('HKLM:\\SYSTEM\\CurrentControlSet\\Services\\' + $s) -Name 'Start' -Value ${v} -Force -ErrorAction SilentlyContinue }; '${enable ? 'SERVIÇOS OK' : 'Serviços restaurados'}'`);
});

ipcMain.handle('opt-schedtasks', async (e, enable) => {
  const op = enable ? 'Disable' : 'Enable';
  return await runPS(`$ts=@('\\Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator','\\Microsoft\\Windows\\Feedback\\Siuf\\DmClient','\\Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser','\\Microsoft\\Windows\\Maps\\MapsUpdateTask'); foreach($t in $ts){ schtasks /Change /TN $t /${op} }; '${enable ? 'TAREFAS OK' : 'Tarefas restauradas'}'`);
});

ipcMain.handle('opt-updates', async (e, enable) => {
  if (enable) return await runPS(`New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Force | Out-Null; Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'NoAutoUpdate' -Value 1 -Force; Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'NoAutoRebootWithLoggedOnUsers' -Value 1 -Force; 'UPDATES OK'`);
  return await runPS(`Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'NoAutoUpdate' -Value 0 -Force; Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'NoAutoRebootWithLoggedOnUsers' -Value 0 -Force; 'Updates restaurados'`);
});

ipcMain.handle('opt-sound', async (e, enable) => {
  const v = enable ? 1 : 0;
  return await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Multimedia\\Audio' -Name 'UserDuckingPreference' -Value ${enable ? 3 : 1} -Force; '${enable ? 'SOM OK' : 'Som restaurado'}'`);
});

ipcMain.handle('opt-winnotify', async (e, enable) => {
  const v = enable ? 1 : 0;
  return await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications' -Name 'ToastEnabled' -Value ${v} -Force; '${enable ? 'Notificações restauradas' : 'NOTIFICAÇÕES OFF'}'`);
});

ipcMain.handle('opt-customize', async (e, enable) => {
  if (enable) return await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Search' -Name 'SearchboxTaskbarMode' -Value 0 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarMn' -Value 0 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarEndTask' -Value 1 -Force; 'VISUAL OK'`);
  return await runPS(`Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Search' -Name 'SearchboxTaskbarMode' -Value 1 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarMn' -Value 1 -Force; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarEndTask' -Value 0 -Force; 'Personalização restaurada'`);
});

ipcMain.handle('opt-power-extra', async (e, enable) => {
  const v = enable ? 0 : 1;
  return await runPS(`Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power' -Name 'HibernateEnabled' -Value ${v} -Force; '${enable ? 'ENERGIA+ OK' : 'Energia+ restaurada'}'`);
});

ipcMain.handle('opt-perf-extra', async (e, enable) => {
  if (enable) return await runPS(`Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseHoverTime' -Value '10' -Force; Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'MenuShowDelay' -Value '0' -Force; Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl' -Name 'Win32PrioritySeparation' -Value 38 -Force; 'PERFORMANCE+ OK'`);
  return await runPS(`Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseHoverTime' -Value '400' -Force; Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'MenuShowDelay' -Value '400' -Force; Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl' -Name 'Win32PrioritySeparation' -Value 2 -Force; 'Performance+ restaurada'`);
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
