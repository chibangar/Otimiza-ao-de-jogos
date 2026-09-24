"""
Midnight Optimizer — App nativa Windows
Estilo WoW Midnight | Modo Competitivo
Backend Python + WebView2 (Edge) — gera .exe único
"""
import os
import sys
import json
import re
import subprocess
import platform
import shutil
import tempfile
import threading
import urllib.request
import webview
import game_tweaks
import pros
import overlay
import voicefx
import accounts
import oauth_login
import servers
import online

if len(sys.argv) > 1 and sys.argv[1] == "--overlay":
    overlay.handle_cli(sys.argv[2:])
    sys.exit(0)

try:
    import sounddevice as sd
    _SD_OK = True
except Exception:
    sd = None
    _SD_OK = False

try:
    import miniaudio
    _MA_OK = True
except Exception:
    miniaudio = None
    _MA_OK = False

try:
    import keyboard as _kb
    _KB_OK = True
except Exception:
    _kb = None
    _KB_OK = False

_LAST_IN, _LAST_OUT, _LAST_GAIN = None, None, 1.5
_HK = []
_SB_CACHE = {}
_SESSION = {"user": None}

_VS = {"stream": None, "state": None, "effect": "", "gain": 1.5,
       "rec": None, "recording": False, "last_wav": "",
       "mon": None, "mon_state": None}

APP_VERSION = "3.2.0"
REPO = "chibangar/Otimiza-ao-de-jogos"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Novidades mostradas no popup ao ligar a app (uma linha por novidade).
APP_NEWS = [
    "🎯 Miras & Viewmodels CS2: Miras dos pros com códigos de partilha, comandos de consola (~) e imagens de posicionamento de arma sem alterar binds ou sensibilidade.",
    "⚡ Resolução de Registo de Tiros (Sub-Tick Hitreg): Otimização com 1 clique para tiros que não registam, limpeza de cache de shaders DirectX e buffer de rede em 0 ticks.",
    "🔔 In-Game Notification Overlay: Overlay flutuante animado com popout sobre os jogos, 100% VAC-Safe e sem perda de foco.",
    "🛡️ Otimizações Profissionais Seguras: Configuração não destrutiva que mantém 100% intactos os teus controlos, sensibilidades e vídeo.",
    "✨ Nova Interface Obsidian Profissional: Design system ergonómico, moderno e sem distrações.",
    "📊 Novo Centro de Controlo no Dashboard: Telemetria em tempo real para CPU, GPU, RAM e Disco.",
    "📦 Compilação e Releases Contínuas no GitHub Actions para Windows.",
]

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

def _hidden():
    """Flags para NUNCA mostrar janela de consola ao correr comandos."""
    kw = {"creationflags": _NO_WINDOW}
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        kw["startupinfo"] = si
    except Exception:
        pass
    return kw

def run_ps(command: str, timeout=60):
    """Corre PowerShell e devolve dict (sem janela)."""
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True, text=True, timeout=timeout, **_hidden()
        )
        out = (r.stdout or r.stderr or "").strip()
        return {"success": r.returncode == 0, "output": out}
    except Exception as e:
        return {"success": False, "output": str(e)}

def run_cmd(command: str, timeout=60):
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True,
                           timeout=timeout, **_hidden())
        out = (r.stdout or r.stderr or "").strip()
        return {"success": r.returncode == 0, "output": out}
    except Exception as e:
        return {"success": False, "output": str(e)}


def _ver_tuple(v):
    try:
        return tuple(int(x) for x in str(v).lstrip("vV").split("."))
    except Exception:
        return (0,)

_UPDATE = {"status": "idle", "pct": 0, "error": "", "path": "", "version": "", "notes": ""}
_WINDOW = None
_ISSUES_CACHE = {"at": 0, "items": []}

def log_error(msg):
    try:
        p = os.path.join(tempfile.gettempdir(), "midnight_debug.log")
        with open(p, "a", encoding="utf-8") as f:
            import datetime
            f.write(f"[{datetime.datetime.now():%H:%M:%S}] {msg}\n")
    except Exception:
        pass
    return {"success": True}


class Api:
    # ---------- SISTEMA ----------
    def get_system_info(self):
        cpu = run_ps("(Get-CimInstance Win32_Processor).Name")
        gpu = run_ps("(Get-CimInstance Win32_VideoController).Name -join ' | '")
        ram_total = run_ps("[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)")
        ram_free = run_ps("[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024/1024,1)")
        disk_free = run_ps("[math]::Round((Get-PSDrive C).Free/1GB,1)")
        win = run_ps("(Get-CimInstance Win32_OperatingSystem).Caption")
        power = run_cmd("powercfg /getactivescheme")
        board = run_ps("(Get-CimInstance Win32_BaseBoard).Product")

        try:
            total = float((ram_total["output"] or "16").split()[0].replace(",", "."))
        except Exception:
            total = 16
        try:
            free = float((ram_free["output"] or "8").split()[0].replace(",", "."))
        except Exception:
            free = 8
        used_pct = round(((total - free) / total) * 100) if total else 0

        import socket
        return {
            "cpu": cpu["output"] or platform.processor() or "CPU",
            "gpu": gpu["output"] or "GPU não detetada",
            "ramTotal": (ram_total["output"] or "?").split()[0],
            "ramFree": (ram_free["output"] or "?").split()[0],
            "ramUsedPct": used_pct,
            "diskFree": (disk_free["output"] or "?").split()[0],
            "os": win["output"] or f"{platform.system()} {platform.release()}",
            "power": power["output"] or "",
            "hostname": socket.gethostname(),
            "motherboard": (board["output"] or "").split("\n")[0].strip() or "—",
        }

    def get_perf(self):
        """Métricas reais rápidas: CPU/RAM/DISCO (psutil) + GPU (nvidia-smi)."""
        out = {"cpuPct": None, "cpuGHz": None, "gpuPct": None,
               "gpuMemUsed": None, "gpuMemTotal": None,
               "ramPct": None, "ramUsed": None, "ramTotal": None,
               "diskPct": None, "diskUsed": None, "diskTotal": None}
        try:
            import psutil
            out["cpuPct"] = round(psutil.cpu_percent(interval=0.3))
            try:
                f = psutil.cpu_freq()
                if f and f.current:
                    out["cpuGHz"] = round(f.current / 1000, 1)
            except Exception:
                pass
            m = psutil.virtual_memory()
            out["ramPct"] = round(m.percent)
            out["ramUsed"] = round(m.used / (1024 ** 3), 1)
            out["ramTotal"] = round(m.total / (1024 ** 3), 1)
            try:
                d = psutil.disk_usage("C:\\")
                out["diskPct"] = round(d.percent)
                out["diskUsed"] = round(d.used / (1024 ** 3))
                out["diskTotal"] = round(d.total / (1024 ** 3))
            except Exception:
                pass
        except Exception as e:
            log_error("get_perf psutil: " + str(e))
        try:
            r = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=15, **_hidden())
            parts = (r.stdout or "").strip().split(",")
            if len(parts) >= 3:
                out["gpuPct"] = int(parts[0].strip())
                out["gpuMemUsed"] = int(parts[1].strip())
                out["gpuMemTotal"] = int(parts[2].strip())
        except Exception:
            pass
        return out

    # ---------- JANELA ----------
    def window_minimize(self):
        try:
            if _WINDOW is not None:
                _WINDOW.minimize()
            return {"success": True}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def window_toggle_maximize(self):
        try:
            if _WINDOW is not None:
                if getattr(_WINDOW, "_mid_max", False):
                    _WINDOW.restore()
                    _WINDOW._mid_max = False
                else:
                    _WINDOW.maximize()
                    _WINDOW._mid_max = True
            return {"success": True}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def window_close(self):
        try:
            if _WINDOW is not None:
                _WINDOW.destroy()
            return {"success": True}
        except Exception as e:
            return {"success": False, "output": str(e)}

    # ---------- Otimizações ----------
    def power_high(self):
        run_cmd("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61")
        r = run_cmd("powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61")
        if not r["success"]:
            r = run_cmd("powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")
        return r

    def power_balanced(self):
        return run_cmd("powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e")

    def game_mode(self, enable=True):
        v = 1 if enable else 0
        return run_ps(
            f"New-Item -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Force | Out-Null; "
            f"Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AllowAutoGameMode' -Value {v} -Force; "
            f"Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AutoGameModeEnabled' -Value {v} -Force; 'OK'"
        )

    def game_bar(self, disable=True):
        cap = 0 if disable else 1
        dvr = 0 if disable else 1
        return run_ps(
            f"New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR' -Force | Out-Null; "
            f"Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR' -Name 'AppCaptureEnabled' -Value {cap} -Force; "
            f"Set-ItemProperty -Path 'HKCU:\\System\\GameConfigStore' -Name 'GameDVR_Enabled' -Value {dvr} -Force; 'OK'"
        )

    def clean_temp(self):
        return run_ps(
            "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; "
            "Remove-Item -Path 'C:\\Windows\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue; "
            "ipconfig /flushdns | Out-Null; 'LIMPEZA OK — TEMP + DNS'"
        )

    def network(self):
        logs = []
        logs.append(run_cmd("ipconfig /flushdns"))
        logs.append(run_ps("Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile' -Name 'NetworkThrottlingIndex' -Value 4294967295 -Force; 'OK'"))
        logs.append(run_ps("Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile' -Name 'SystemResponsiveness' -Value 0 -Force; 'OK'"))
        ok = all(x["success"] for x in logs)
        return {"success": ok, "output": "\n".join(x["output"] for x in logs)}

    def visual_effects(self, performance=True):
        if performance:
            return run_ps("Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name 'VisualFXSetting' -Value 2 -Force; 'Efeitos em desempenho'")
        return run_ps("Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name 'VisualFXSetting' -Value 0 -Force; 'Efeitos restaurados'")

    def kill_background(self):
        kill_list = ["OneDrive.exe", "Teams.exe", "msedge.exe", "chrome.exe",
                     "firefox.exe", "Spotify.exe", "Skype.exe"]
        for p in kill_list:
            run_cmd(f"taskkill /F /IM {p} 2>nul")
        return {"success": True, "output": "Processos em 2º plano terminados."}

    def gpu_priority(self):
        return run_ps(
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers' -Name 'HwSchMode' -Value 2 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games' -Name 'GPU Priority' -Value 8 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games' -Name 'Priority' -Value 6 -Force; "
            "'GPU OK (reinicia para HAGS total)'"
        )

    # ---------- PRIVACIDADE (tweaks públicos, sem telemetria) ----------
    def privacy_on(self):
        return run_ps(
            "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Name 'AllowTelemetry' -Value 0 -Force; "
            "New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Name 'Enabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Privacy' -Name 'TailoredExperiencesWithDiagnosticDataEnabled' -Value 0 -Force; "
            "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Name 'EnableActivityFeed' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Name 'PublishUserActivities' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Name 'UploadUserActivities' -Value 0 -Force; "
            "New-Item -Path 'HKCU:\\Software\\Microsoft\\Siuf\\Rules' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Siuf\\Rules' -Name 'NumberOfSIUFInPeriod' -Value 0 -Force; "
            "New-Item -Path 'HKCU:\\Software\\Policies\\Microsoft\\Windows\\WindowsCopilot' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Policies\\Microsoft\\Windows\\WindowsCopilot' -Name 'TurnOffWindowsCopilot' -Value 1 -Force; "
            "'PRIVACIDADE OK — telemetria, ads, histórico e Copilot desligados'"
        )

    def privacy_off(self):
        return run_ps(
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Name 'AllowTelemetry' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Name 'Enabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Privacy' -Name 'TailoredExperiencesWithDiagnosticDataEnabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Name 'EnableActivityFeed' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Name 'PublishUserActivities' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Name 'UploadUserActivities' -Value 1 -Force; "
            "Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Siuf\\Rules' -Name 'NumberOfSIUFInPeriod' -Force -ErrorAction SilentlyContinue; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Policies\\Microsoft\\Windows\\WindowsCopilot' -Name 'TurnOffWindowsCopilot' -Value 0 -Force; "
            "'Privacidade restaurada'"
        )

    # ---------- PRIVACIDADE PROFUNDA (sugestões, tracking, IA) ----------
    def privacy_extra_on(self):
        return run_ps(
            "New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'ContentDeliveryAllowed' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'SubscribedContentEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'SilentInstalledAppsEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'PreInstalledAppsEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'OemPreInstalledAppsEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'RotatingLockScreenEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'RotatingLockScreenOverlayEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'Start_TrackProgs' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\International\\User Profile' -Name 'HttpAcceptLanguageOptOut' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Speech_OneCore\\Settings\\OnlineSpeechPrivacy' -Name 'HasAccepted' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Search' -Name 'BingSearchEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\SearchSettings' -Name 'IsDeviceSearchHistoryEnabled' -Value 0 -Force; "
            "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search' -Name 'AllowCortana' -Value 0 -Force; "
            "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsAI' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsAI' -Name 'AllowRecallEnablement' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsAI' -Name 'TurnOffSavingSnapshots' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsAI' -Name 'DisableAIDataAnalysis' -Value 1 -Force; "
            "'PRIVACIDADE+ OK — sem sugestões, sem tracking, sem Recall/IA'"
        )

    def privacy_extra_off(self):
        return run_ps(
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'ContentDeliveryAllowed' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'SubscribedContentEnabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'SilentInstalledAppsEnabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'PreInstalledAppsEnabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'RotatingLockScreenEnabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'Start_TrackProgs' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Search' -Name 'BingSearchEnabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search' -Name 'AllowCortana' -Value 1 -Force; "
            "Remove-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsAI' -Recurse -Force -ErrorAction SilentlyContinue; "
            "'Privacidade+ restaurada'"
        )

    # ---------- SERVIÇOS (desliga telemetria e tralha em 2º plano) ----------
    _SVC_OFF = {"DiagTrack": 2, "MapsBroker": 3, "RetailDemo": 3, "PhoneSvc": 3,
                "SmsRouter": 3, "Fax": 3, "PcaSvc": 3, "NfcSvc": 3, "TrkWks": 2,
                "dmwappushservice": 3, "lfsvc": 3, "SensorService": 3,
                "SensorDataService": 3}

    def services_gaming_on(self):
        parts = []
        for svc in self._SVC_OFF:
            parts.append(
                f"Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\{svc}' "
                f"-Name 'Start' -Value 4 -Force -ErrorAction SilentlyContinue")
        return run_ps("; ".join(parts) + "; 'SERVIÇOS OK — telemetria e tralha desligadas'")

    def services_gaming_off(self):
        parts = []
        for svc, default in self._SVC_OFF.items():
            parts.append(
                f"Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\{svc}' "
                f"-Name 'Start' -Value {default} -Force -ErrorAction SilentlyContinue")
        return run_ps("; ".join(parts) + "; 'Serviços restaurados'")

    # ---------- TAREFAS AGENDADAS (corta telemetria do Task Scheduler) ----------
    _TASKS_OFF = [
        r"\Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
        r"\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
        r"\Microsoft\Windows\Feedback\Siuf\DmClient",
        r"\Microsoft\Windows\Feedback\Siuf\DmClientOnScenarioDownload",
        r"\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
        r"\Microsoft\Windows\Application Experience\ProgramDataUpdater",
        r"\Microsoft\Windows\Autochk\Proxy",
        r"\Microsoft\Windows\Maps\MapsUpdateTask",
        r"\Microsoft\Windows\Power Efficiency Diagnostics\AnalyzeSystem",
        r"\Microsoft\Windows\Customer Experience Improvement Program\KernelCeipTask",
    ]

    def sched_tasks_off(self):
        parts = [f'schtasks /Change /TN "{t}" /Disable 2>$null' for t in self._TASKS_OFF]
        return run_ps("; ".join(parts) + "; 'TAREFAS OK — telemetria agendada desligada'")

    def sched_tasks_on(self):
        return run_ps(
            "; ".join([f'schtasks /Change /TN "{t}" /Enable 2>$null' for t in self._TASKS_OFF])
            + "; 'Tarefas restauradas'")

    # ---------- ATUALIZAÇÕES MANUAIS (sem reboot forçado, sem P2P) ----------
    def updates_manual_on(self):
        return run_ps(
            "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'NoAutoUpdate' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'AUOptions' -Value 2 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'NoAutoRebootWithLoggedOnUsers' -Value 1 -Force; "
            "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization' -Name 'DODownloadMode' -Value 99 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings' -Name 'IsContinuousInnovationOptedIn' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings' -Name 'ExcludeWUDriversInQualityUpdate' -Value 1 -Force; "
            "'UPDATES OK — tu decides quando atualizar, sem reboot a meio do jogo'"
        )

    def updates_manual_off(self):
        return run_ps(
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'NoAutoUpdate' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'AUOptions' -Value 4 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'NoAutoRebootWithLoggedOnUsers' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization' -Name 'DODownloadMode' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings' -Name 'IsContinuousInnovationOptedIn' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings' -Name 'ExcludeWUDriversInQualityUpdate' -Value 0 -Force; "
            "'Updates automáticos restaurados'"
        )

    # ---------- SOM (boot silencioso, sem ducking) ----------
    def sound_tweaks_on(self):
        return run_ps(
            "New-Item -Path 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI\\BootAnimation' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI\\BootAnimation' -Name 'DisableStartupSound' -Value 1 -Force; "
            "New-Item -Path 'HKCU:\\Software\\Microsoft\\Multimedia\\Audio' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Multimedia\\Audio' -Name 'UserDuckingPreference' -Value 3 -Force; "
            "'SOM OK — boot silencioso, chamadas não baixam o jogo'"
        )

    def sound_tweaks_off(self):
        return run_ps(
            "Set-ItemProperty -Path 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI\\BootAnimation' -Name 'DisableStartupSound' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Multimedia\\Audio' -Name 'UserDuckingPreference' -Value 1 -Force; "
            "'Som restaurado'"
        )

    # ---------- NOTIFICAÇÕES DO WINDOWS (toasts e sino) ----------
    def win_notify_off(self):
        return run_ps(
            "New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications' -Name 'ToastEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications' -Name 'LockScreenToastEnabled' -Value 0 -Force; "
            "New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings' -Name 'NOC_GLOBAL_SETTING_ALLOW_NOTIFICATION_SOUND' -Value 0 -Force; "
            "'NOTIFICAÇÕES OFF — Windows calado enquanto jogas'"
        )

    def win_notify_on(self):
        return run_ps(
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications' -Name 'ToastEnabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications' -Name 'LockScreenToastEnabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings' -Name 'NOC_GLOBAL_SETTING_ALLOW_NOTIFICATION_SOUND' -Value 1 -Force; "
            "'Notificações restauradas'"
        )

    # ---------- PERSONALIZAÇÃO (barra, Iniciar, Explorer) ----------
    def customize_on(self):
        return run_ps(
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Search' -Name 'SearchboxTaskbarMode' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarMn' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'ShowCopilotButton' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarEndTask' -Value 1 -Force; "
            "New-Item -Path 'HKLM:\\Software\\Policies\\Microsoft\\Dsh' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\Software\\Policies\\Microsoft\\Dsh' -Name 'AllowNewsAndInterests' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'Start_TrackDocs' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'Start_IrisRecommendations' -Value 0 -Force; "
            "New-Item -Path 'HKCU:\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32' -Name '(default)' -Value '' -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem' -Name 'LongPathsEnabled' -Value 1 -Force; "
            "'VISUAL OK — barra limpa, Iniciar sem tralha, menu clássico'"
        )

    def customize_off(self):
        return run_ps(
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Search' -Name 'SearchboxTaskbarMode' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarMn' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'ShowCopilotButton' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarEndTask' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\Software\\Policies\\Microsoft\\Dsh' -Name 'AllowNewsAndInterests' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'Start_TrackDocs' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'Start_IrisRecommendations' -Value 1 -Force; "
            "Remove-Item -Path 'HKCU:\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}' -Recurse -Force -ErrorAction SilentlyContinue; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem' -Name 'LongPathsEnabled' -Value 0 -Force; "
            "'Personalização restaurada'"
        )

    # ---------- ENERGIA EXTRA (hibernação, fast startup, USB) ----------
    _PWR_USB = "2a737441-1930-4402-8d77-b2bebba308a3c"
    _USB_SUSPEND = "48e6b7a6-50f6-478a-a5d4-53bb8fcc84df"

    def power_extra_on(self):
        r1 = run_ps(
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power' -Name 'HibernateEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\ControlSet001\\Control\\Session Manager\\Power' -Name 'HiberbootEnabled' -Value 0 -Force; "
            "'OK'")
        r2 = run_cmd(f"powercfg /setacvalueindex SCHEME_CURRENT {self._PWR_USB} {self._USB_SUSPEND} 0")
        ok = r1.get("success") and r2.get("success")
        return {"success": ok, "output": "ENERGIA+ OK — sem hibernação/fast startup, USB sempre ligado"}

    def power_extra_off(self):
        run_ps(
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power' -Name 'HibernateEnabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\ControlSet001\\Control\\Session Manager\\Power' -Name 'HiberbootEnabled' -Value 1 -Force; "
            "'OK'")
        run_cmd(f"powercfg /setacvalueindex SCHEME_CURRENT {self._PWR_USB} {self._USB_SUSPEND} 1")
        return {"success": True, "output": "Energia+ restaurada"}

    # ---------- PERFORMANCE EXTRA (resposta, CPU, latência) ----------
    def perf_extra_on(self):
        logs = []
        logs.append(run_ps(
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseHoverTime' -Value '10' -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'MenuShowDelay' -Value '0' -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'MultiTaskingAltTabFilter' -Value 3 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl' -Name 'Win32PrioritySeparation' -Value 38 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'UseNexusForGameBarEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'ShowStartupPanel' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control' -Name 'ServicesPipeTimeout' -Value 30000 -Force; "
            "'OK base'"))
        # Nagle off em todas as NICs (menos latência TCP).
        logs.append(run_ps(
            "Get-ChildItem 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces' | ForEach-Object { "
            "Set-ItemProperty -Path $_.PSPath -Name 'TcpAckFrequency' -Value 1 -Force -ErrorAction SilentlyContinue; "
            "Set-ItemProperty -Path $_.PSPath -Name 'TCPNoDelay' -Value 1 -Force -ErrorAction SilentlyContinue }; "
            "'OK nagle'"))
        # SysMain + Prefetch off SÓ em SSD.
        logs.append(run_ps(
            "$ssd = (Get-PhysicalDisk -ErrorAction SilentlyContinue | Where-Object {$_.MediaType -eq 'SSD'} | Measure-Object).Count -gt 0; "
            "if($ssd){ Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\SysMain' -Name 'Start' -Value 4 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters' -Name 'EnablePrefetcher' -Value 0 -Force; 'OK ssd' } "
            "else { 'HDD — SysMain mantido' }"))
        ok = all(x.get("success") for x in logs)
        return {"success": ok, "output": "PERFORMANCE+ OK — menus instantâneos, CPU no jogo, latência mínima"}

    def perf_extra_off(self):
        run_ps(
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseHoverTime' -Value '400' -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'MenuShowDelay' -Value '400' -Force; "
            "Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'MultiTaskingAltTabFilter' -Force -ErrorAction SilentlyContinue; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl' -Name 'Win32PrioritySeparation' -Value 2 -Force; "
            "Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'UseNexusForGameBarEnabled' -Force -ErrorAction SilentlyContinue; "
            "Remove-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control' -Name 'ServicesPipeTimeout' -Force -ErrorAction SilentlyContinue; "
            "Get-ChildItem 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces' | ForEach-Object { "
            "Remove-ItemProperty -Path $_.PSPath -Name 'TcpAckFrequency' -Force -ErrorAction SilentlyContinue; "
            "Remove-ItemProperty -Path $_.PSPath -Name 'TCPNoDelay' -Force -ErrorAction SilentlyContinue }; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\SysMain' -Name 'Start' -Value 2 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters' -Name 'EnablePrefetcher' -Value 3 -Force; "
            "'Performance+ restaurada'")
        return {"success": True, "output": "Performance+ restaurada"}

    # ---------- DEBLOAT (remove apps pré-instaladas inúteis, sem Xbox/Game Bar) ----------
    def debloat(self):
        return run_ps(
            "$apps=@('Microsoft.BingNews','Microsoft.BingWeather','Microsoft.GetHelp','Microsoft.Getstarted',"
            "'Microsoft.MicrosoftOfficeHub','Microsoft.MicrosoftSolitaireCollection','Microsoft.People','Microsoft.Todos',"
            "'Microsoft.WindowsFeedbackHub','Microsoft.YourPhone','Microsoft.ZuneMusic','Microsoft.ZuneVideo',"
            "'Clipchamp.Clipchamp','Microsoft.549981C3F5F10',"
            "'Microsoft.Microsoft3DViewer','Microsoft.MixedReality.Portal','Microsoft.SkypeApp',"
            "'MSTeams','Microsoft.WindowsMaps','Microsoft.MSPaint','Microsoft.PowerAutomateDesktop',"
            "'Microsoft.Copilot','microsoft.windowscommunicationsapps'); "
            "$n=0; foreach($a in $apps){ $p=Get-AppxPackage -Name $a -ErrorAction SilentlyContinue; "
            "if($p){ $p | Remove-AppxPackage -ErrorAction SilentlyContinue; $n++ } }; "
            "\"DEBLOAT OK — $n apps removidas (Xbox e Game Bar intactos)\""
        )

    # ---------- GAMING EXTRA (ratos + fullscreen + throttling) ----------
    def gaming_extra_on(self):
        return run_ps(
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseSpeed' -Value '0' -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseThreshold1' -Value '0' -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseThreshold2' -Value '0' -Force; "
            "New-Item -Path 'HKCU:\\System\\GameConfigStore' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\System\\GameConfigStore' -Name 'GameDVR_FSEBehaviorMode' -Value 2 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\System\\GameConfigStore' -Name 'GameDVR_DXGIHonorFSEWindowsCompatible' -Value 1 -Force; "
            "New-Item -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling' -Name 'PowerThrottlingOff' -Value 1 -Force; "
            "'GAMING EXTRA OK — sem aceleração do rato, FSE exclusivo, sem power throttling'"
        )

    def gaming_extra_off(self):
        return run_ps(
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseSpeed' -Value '1' -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseThreshold1' -Value '6' -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'MouseThreshold2' -Value '10' -Force; "
            "Set-ItemProperty -Path 'HKCU:\\System\\GameConfigStore' -Name 'GameDVR_FSEBehaviorMode' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\System\\GameConfigStore' -Name 'GameDVR_DXGIHonorFSEWindowsCompatible' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling' -Name 'PowerThrottlingOff' -Value 0 -Force; "
            "'Gaming extra restaurado'"
        )

    # ---------- SISTEMA (arranque + login + pesquisa) ----------
    def system_extra_on(self):
        return run_ps(
            "New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize' -Name 'StartupDelayInMSec' -Value 0 -Force; "
            "New-Item -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System' -Name 'VerboseStatus' -Value 1 -Force; "
            "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization' -Force | Out-Null; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization' -Name 'NoLockScreen' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\SearchSettings' -Name 'IsDynamicSearchBoxEnabled' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'HideFileExt' -Value 0 -Force; "
            "'SISTEMA OK — arranque sem atraso, sem lock screen, sem destaques na pesquisa'"
        )

    def system_extra_off(self):
        return run_ps(
            "Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize' -Name 'StartupDelayInMSec' -Force -ErrorAction SilentlyContinue; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System' -Name 'VerboseStatus' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization' -Name 'NoLockScreen' -Value 0 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\SearchSettings' -Name 'IsDynamicSearchBoxEnabled' -Value 1 -Force; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'HideFileExt' -Value 1 -Force; "
            "'Sistema restaurado'"
        )

    # ---------- DIAGNÓSTICO: qual a melhor otimização para ESTE pc ----------
    def analyze_pc(self):
        """Lê o estado real do PC e devolve score + recomendações ordenadas."""
        recs = []
        score = 100

        def push(rid, icon, title, reason, impact, action, penalty):
            recs.append({"id": rid, "icon": icon, "title": title,
                         "reason": reason, "impact": impact, "action": action})
            return penalty

        # 1) Estado do registo (1 só chamada PowerShell -> JSON).
        reg = {}
        try:
            r = run_ps(
                "$j=@{}; "
                "try{$j.gamemode=(Get-ItemProperty 'HKCU:\\Software\\Microsoft\\GameBar' -Name AllowAutoGameMode -ErrorAction Stop).AllowAutoGameMode}catch{$j.gamemode=$null}; "
                "try{$j.capture=(Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR' -Name AppCaptureEnabled -ErrorAction Stop).AppCaptureEnabled}catch{$j.capture=$null}; "
                "try{$j.dvr=(Get-ItemProperty 'HKCU:\\System\\GameConfigStore' -Name GameDVR_Enabled -ErrorAction Stop).GameDVR_Enabled}catch{$j.dvr=$null}; "
                "try{$j.visual=(Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name VisualFXSetting -ErrorAction Stop).VisualFXSetting}catch{$j.visual=$null}; "
                "try{$j.net=(Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile' -Name NetworkThrottlingIndex -ErrorAction Stop).NetworkThrottlingIndex}catch{$j.net=$null}; "
                "try{$j.hags=(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers' -Name HwSchMode -ErrorAction Stop).HwSchMode}catch{$j.hags=$null}; "
                "$j | ConvertTo-Json -Compress",
                timeout=30)
            reg = json.loads(r.get("output") or "{}")
        except Exception as e:
            log_error("analyze_pc reg: " + str(e))

        # 2) Plano de energia ativo.
        power = run_cmd("powercfg /getactivescheme")
        pout = (power.get("output") or "").lower()
        if "e9a42b02" not in pout and "8c5e7fda" not in pout:
            score -= push("power", "⚡", "Energia máxima",
                          "O teu plano de energia está em modo económico/equilibrado — o CPU trava antes de dar o máximo nos jogos.",
                          "ALTO", "power", 15)

        # 3) Modo Jogo.
        if str(reg.get("gamemode")) != "1":
            score -= push("gamemode", "🎮", "Modo Jogo do Windows",
                          "O Modo Jogo está desligado — o Windows não prioriza o jogo quando estás em ranked.",
                          "ALTO", "gamemode", 10)

        # 4) DVR / Game Bar a roubar FPS.
        if str(reg.get("capture")) not in ("0",) or str(reg.get("dvr")) not in ("0",):
            score -= push("gamebar", "📼", "Desligar DVR / Game Bar",
                          "A captura em 2º plano (DVR) está ativa e rouba FPS e disco enquanto jogas.",
                          "MÉDIO", "gamebar", 8)

        # 5) Efeitos visuais.
        if str(reg.get("visual")) != "2":
            score -= push("visual", "✨", "Efeitos em modo desempenho",
                          "Animações e sombras do Windows estão a gastar GPU/CPU que devia ir para o jogo.",
                          "MÉDIO", "visual", 8)

        # 6) Rede (throttling).
        try:
            if int(str(reg.get("net"))) != 4294967295:
                raise ValueError
        except Exception:
            score -= push("net", "🌐", "Rede otimizada para jogos",
                          "O Windows limita a rede para poupar CPU — isto aumenta ping e dá spikes em jogos online.",
                          "ALTO", "net", 10)

        # 7) GPU / HAGS.
        if str(reg.get("hags")) != "2":
            score -= push("gpu", "🖥️", "Prioridade GPU (HAGS)",
                          "O agendamento de GPU acelerado por hardware está desligado — perdes latência e FPS (pede reinício).",
                          "MÉDIO", "gpu", 8)

        # 8) RAM total / livre.
        try:
            total = float((run_ps("[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)")["output"] or "16").split()[0].replace(",", "."))
        except Exception:
            total = 16
        try:
            free = float((run_ps("[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024/1024,1)")["output"] or "8").split()[0].replace(",", "."))
        except Exception:
            free = 8
        if total <= 8:
            score -= push("kill", "🧹", "Limpar apps em 2º plano",
                          f"Só tens {total:g} GB de RAM — browsers e launchers abertos comem a memória do jogo.",
                          "ALTO", "kill", 12)
        elif free < total * 0.25:
            score -= push("kill", "🧹", "Limpar apps em 2º plano",
                          f"Só tens {free:g} GB livres de {total:g} GB — há apps pesadas abertas agora.",
                          "MÉDIO", "kill", 8)
        else:
            # mesmo com RAM livre, avisa se há comedores de RAM abertos
            try:
                tl = (run_cmd("tasklist", timeout=30).get("output") or "").lower()
                heavy = [p for p in ["chrome.exe", "msedge.exe", "firefox.exe", "spotify.exe", "teams.exe", "onedrive.exe"] if p in tl]
                if len(heavy) >= 2:
                    score -= push("kill", "🧹", "Limpar apps em 2º plano",
                                  f"Detetei {len(heavy)} apps pesadas abertas ({', '.join(heavy[:3])}) — fechá-las liberta FPS.",
                                  "MÉDIO", "kill", 6)
            except Exception:
                pass

        # 9) Disco C: cheio + TEMP.
        try:
            disk_free = float((run_ps("[math]::Round((Get-PSDrive C).Free/1GB,1)")["output"] or "50").split()[0].replace(",", "."))
        except Exception:
            disk_free = 50
        if disk_free < 15:
            score -= push("temp", "💽", "Limpeza de disco + TEMP",
                          f"O disco C: só tem {disk_free:g} GB livres — jogos com pouco espaço têm stutter e updates falham.",
                          "ALTO", "temp", 12)
        else:
            try:
                tmp = run_ps("$s=(Get-ChildItem $env:TEMP -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum; [math]::Round($s/1MB,1)", timeout=60)
                tmp_mb = float((tmp.get("output") or "0").split()[0].replace(",", "."))
                if tmp_mb > 500:
                    score -= push("temp", "🧺", "Limpeza da pasta TEMP",
                                  f"A tua TEMP tem {tmp_mb:,.0f} MB de lixo — limpa e liberta espaço + DNS fresco.",
                                  "MÉDIO", "temp", 6)
            except Exception:
                pass

        score = max(0, min(100, score))
        if score >= 85:
            verdict = "Máquina de guerra! Só afinações finas. ⚔"
        elif score >= 65:
            verdict = "Bom, mas há FPS fácil por ganhar. 🎯"
        elif score >= 40:
            verdict = "A perder desempenho todos os dias. 🔧"
        else:
            verdict = "Modo tartaruga! Precisas disto urgente. 🚨"

        specs = f"{total:g} GB RAM • C: {disk_free:g} GB livres"
        order = {"ALTO": 0, "MÉDIO": 1}
        recs.sort(key=lambda x: order.get(x["impact"], 2))
        return {"success": True, "score": score, "verdict": verdict,
                "specs": specs, "recs": recs}

    # ---------- COMPETITIVO ----------
    def competitive_on(self):
        log = []

        def push(name, r):
            log.append(f"{'✔' if r.get('success') else '✘'} {name}")

        run_cmd("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61")
        push("Plano Ultimate Performance ativo",
             run_cmd("powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61"))
        push("Modo Jogo ativado", self.game_mode(True))
        push("Game DVR / Game Bar desativados", self.game_bar(True))
        push("Ficheiros temporários limpos",
             run_ps("Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; 'OK'"))
        push("DNS limpo (ping mais estável)", run_cmd("ipconfig /flushdns"))
        push("Rede otimizada para jogos",
             run_ps("Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile' -Name 'NetworkThrottlingIndex' -Value 4294967295 -Force; 'OK'"))
        push("Efeitos visuais em modo desempenho", self.visual_effects(True))
        self.kill_background()
        push("Apps em 2º plano encerradas", {"success": True})
        return {"success": True, "output": "\n".join(log)}

    def competitive_off(self):
        log = []
        r = self.power_balanced()
        log.append(f"{'✔' if r['success'] else '✘'} Plano Equilibrado restaurado")
        r = self.visual_effects(False)
        log.append(f"{'✔' if r['success'] else '✘'} Efeitos visuais restaurados")
        return {"success": True, "output": "\n".join(log)}

    def pick_game_file(self):
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            path = filedialog.askopenfilename(
                title="Escolhe o jogo (.exe)",
                filetypes=[("Jogos", "*.exe *.lnk"), ("Todos", "*.*")]
            )
            root.destroy()
            if path:
                name = os.path.splitext(os.path.basename(path))[0]
                return {"success": True, "name": name, "path": path}
            return {"success": False, "output": "Cancelado."}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def launch_game(self, game_path):
        if not game_path or not os.path.exists(game_path):
            return {"success": False, "output": "Ficheiro não encontrado."}
        run_cmd("taskkill /F /IM msedge.exe 2>nul")
        run_cmd("taskkill /F /IM chrome.exe 2>nul")
        try:
            # lança com prioridade Alta (sem janela de consola)
            subprocess.Popen(f'cmd /c start "" /HIGH "{game_path}"', shell=True, **_hidden())
            return {"success": True, "output": "Jogo lançado com prioridade ALTA."}
        except Exception as e:
            return {"success": False, "output": str(e)}

    # ---------- IN-GAME: CS2 & WOW ----------
    def detect_games(self):
        cs = game_tweaks.find_cs2() or {}
        running, proc = game_tweaks.cs2_running()
        wow = game_tweaks.find_wow()
        return {
            "cs2": {"found": bool(cs.get("cfg_dir")), "base": cs.get("base", ""),
                    "cfg": cs.get("cfg_dir", ""), "source": cs.get("source", ""),
                    "running": running, "process_path": proc or cs.get("process_path", ""),
                    "autoexec": cs.get("autoexec", ""),
                    "videos": cs.get("video_candidates", [])},
            "wow": {"found": bool(wow and wow.get("config") and os.path.isfile(wow.get("config"))),
                    "base": (wow or {}).get("base", ""), "config": (wow or {}).get("config", ""),
                    "flavor": (wow or {}).get("flavor", "")},
        }

    def pick_cs2_folder(self):
        return game_tweaks.pick_cs2_folder()

    def kill_cs2(self):
        return game_tweaks.kill_cs2()

    def cs2_competitive(self):
        return game_tweaks.apply_cs2_competitive()

    def cs2_restore(self):
        return game_tweaks.restore_cs2()

    def cs2_launch_options(self):
        return {"success": True, "output": game_tweaks.CS2_LAUNCH_COMPETITIVE}

    def cs2_hitreg_fix(self):
        return game_tweaks.fix_cs2_hitreg()

    def test_in_game_overlay(self):
        overlay.notify_process(
            title="Overlay In-Game Ativo",
            message="Notificação demonstrativa com animação de popout!",
            badge="MIDNIGHT",
            theme="emerald",
            duration_sec=3.8
        )
        return {"success": True, "output": "Notificação overlay disparada no ecrã."}

    def wow_competitive(self):
        return game_tweaks.apply_wow("competitive")

    def wow_balanced(self):
        return game_tweaks.apply_wow("balanced")

    def wow_restore(self):
        return game_tweaks.restore_wow()

    # ---------- CONTAS ----------
    def _avatar_url(self, path):
        # data: URL (base64) em vez de file:// — o pywebview serve a pagina
        # em http://localhost e o Chromium bloqueia imagens file:// dali.
        try:
            if not path or not os.path.isfile(path):
                return ""
            if os.path.getsize(path) > 512 * 1024:
                return ""
            with open(path, "rb") as f:
                raw = f.read()
            if raw[:4] == b"\x89PNG":
                mime = "image/png"
            elif raw[:2] == b"\xff\xd8":
                mime = "image/jpeg"
            elif raw[:6] in (b"GIF87a", b"GIF89a"):
                mime = "image/gif"
            elif raw[:4] == b"RIFF" and b"WEBP" in raw[:16]:
                mime = "image/webp"
            else:
                return ""
            import base64
            return "data:" + mime + ";base64," + base64.b64encode(raw).decode()
        except Exception:
            return ""

    def users_list(self):
        try:
            users = accounts._load_users()
            return {"success": True, "users": [
                {"name": n, "avatar": self._avatar_url(u.get("avatar", ""))}
                for n, u in sorted(users.items())]}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def account_register(self, name, pw):
        return accounts.register(name, pw)

    def account_login(self, name, pw):
        r = accounts.check((name or "").strip(), pw or "")
        if r.get("success"):
            _SESSION["user"] = (name or "").strip() or accounts.GUEST
            accounts.save_session(_SESSION["user"])
        return r

    def account_logout(self):
        _SESSION["user"] = None
        accounts.clear_session()
        try:
            self.voice_stop()
        except Exception:
            pass
        return {"success": True, "output": "Sessao terminada."}

    def session_resume(self):
        u = accounts.load_session()
        if not u:
            return {"success": False, "output": "Sem sessao."}
        _SESSION["user"] = u
        return {"success": True, "user": u}

    def session_forget(self):
        accounts.clear_session()
        return {"success": True}

    def open_url(self, url):
        try:
            import webbrowser
            webbrowser.open(url)
            return {"success": True}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def open_releases_page(self):
        return self.open_url(f"https://github.com/{REPO}/releases/latest")

    # ---------- ADMIN OPCIONAL ----------
    def is_admin(self):
        try:
            import ctypes
            return {"admin": bool(ctypes.windll.shell32.IsUserAnAdmin())}
        except Exception:
            return {"admin": False}

    def restart_as_admin(self):
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                return {"success": False, "output": "Ja estas como administrador."}
            if getattr(sys, "frozen", False):
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, None, None, 1)
            else:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, f'"{os.path.abspath(__file__)}"', None, 1)
            threading.Timer(1.0, lambda: os._exit(0)).start()
            return {"success": True, "output": "A reiniciar como administrador…"}
        except Exception as e:
            return {"success": False, "output": str(e)}

    # ---------- ARRANQUE COM O WINDOWS ----------
    _AUTOSTART_NAME = "Midnight Optimizer"
    _AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def _autostart_target(self):
        """Caminho do .exe a registar no arranque (entre aspas)."""
        try:
            if getattr(sys, "frozen", False):
                return f'"{sys.executable}"'
            return f'"{sys.executable}" "{os.path.abspath(__file__)}"'
        except Exception:
            return ""

    def autostart_get(self):
        """Diz se a app arranca com o Windows (chave Run do HKCU)."""
        try:
            import winreg
            h = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._AUTOSTART_KEY,
                               0, winreg.KEY_READ)
            try:
                val, _ = winreg.QueryValueEx(h, self._AUTOSTART_NAME)
            finally:
                h.Close()
            return {"success": True, "enabled": bool(val), "path": val or ""}
        except FileNotFoundError:
            return {"success": True, "enabled": False, "path": ""}
        except Exception as e:
            return {"success": False, "enabled": False, "output": str(e)}

    def autostart_set(self, enable=True):
        """Liga/desliga o arranque com o Windows (sem precisar de admin)."""
        try:
            import winreg
            on = bool(enable)
            if on:
                target = self._autostart_target()
                if not target:
                    return {"success": False, "output": "Nao consegui resolver o caminho do .exe."}
                h = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._AUTOSTART_KEY,
                                   0, winreg.KEY_SET_VALUE)
                try:
                    winreg.SetValueEx(h, self._AUTOSTART_NAME, 0,
                                      winreg.REG_SZ, target)
                finally:
                    h.Close()
                return {"success": True, "enabled": True,
                        "output": "Arranque com o Windows ATIVADO. ✔"}
            h = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._AUTOSTART_KEY,
                               0, winreg.KEY_SET_VALUE)
            try:
                try:
                    winreg.DeleteValue(h, self._AUTOSTART_NAME)
                except FileNotFoundError:
                    pass
            finally:
                h.Close()
            return {"success": True, "enabled": False,
                    "output": "Arranque com o Windows DESATIVADO."}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def whoami(self):
        u = _SESSION.get("user")
        av = ""
        try:
            av = self._avatar_url(accounts._load_users().get(u, {}).get("avatar", ""))
        except Exception:
            pass
        return {"user": u, "avatar": av}

    def oauth_status(self):
        try:
            return {"success": True, **oauth_login.status()}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def oauth_google(self):
        r = oauth_login.login_google()
        if r.get("success"):
            _SESSION["user"] = r["user"]
            accounts.save_session(r["user"])
        return r

    def oauth_discord(self):
        r = oauth_login.login_discord()
        if r.get("success"):
            _SESSION["user"] = r["user"]
            accounts.save_session(r["user"])
        return r

    def oauth_save_discord(self, client_id, client_secret):
        return oauth_login.save_discord_config(client_id, client_secret)

    def _me(self):
        return _SESSION.get("user") or accounts.GUEST

    # ---------- SERVIDORES ----------
    def servers_list(self):
        try:
            return {"success": True, "servers": servers.load(), "modes": servers.MODES}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def servers_refresh(self):
        try:
            return {"success": True, "servers": servers.refresh()}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def servers_history(self):
        try:
            return {"success": True, "history": servers.history(self._me())}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def server_connect(self, ip, port):
        try:
            port = int(port)
        except Exception:
            return {"success": False, "output": "Porta invalida."}
        name, mode = "", ""
        for s in servers.load():
            if s.get("ip") == ip and int(s.get("port", 0)) == port:
                name, mode = s.get("sample_name", ""), s.get("mode", "")
                break
        servers.add_history(self._me(), {"ip": ip, "port": port, "name": name, "mode": mode})
        return servers.connect(ip, port)

    # ---------- ONLINE (pessoas + chat) ----------
    def online_start(self):
        try:
            return online.start(self._me())
        except Exception as e:
            return {"success": False, "output": str(e)}

    def online_stop(self):
        try:
            return online.stop()
        except Exception as e:
            return {"success": False, "output": str(e)}

    def online_state(self):
        try:
            return online.state()
        except Exception as e:
            return {"success": False, "output": str(e)}

    def chat_lobby_send(self, text):
        try:
            return online.lobby_send(text)
        except Exception as e:
            return {"success": False, "output": str(e)}

    def chat_lobby_fetch(self, after=0):
        try:
            return online.lobby_fetch(after)
        except Exception as e:
            return {"success": False, "output": str(e)}

    def chat_dm_send(self, peer, text):
        try:
            return online.dm_send(peer, text)
        except Exception as e:
            return {"success": False, "output": str(e)}

    def chat_dm_fetch(self, peer, after=0):
        try:
            return online.dm_fetch(peer, after)
        except Exception as e:
            return {"success": False, "output": str(e)}

    def chat_dm_threads(self):
        try:
            return online.dm_threads()
        except Exception as e:
            return {"success": False, "output": str(e)}

    # ---------- PROS CS2: MIRAS & VIEWMODELS ----------
    def list_pros(self):
        try:
            return pros.list_pros()
        except Exception as e:
            log_error("list_pros: " + str(e))
            return []

    def list_crosshairs(self):
        try:
            return pros.list_crosshairs()
        except Exception as e:
            log_error("list_crosshairs: " + str(e))
            return []

    def list_viewmodels(self):
        try:
            return pros.list_viewmodels()
        except Exception as e:
            log_error("list_viewmodels: " + str(e))
            return []

    def apply_crosshair(self, pro_id):
        return pros.apply_crosshair_safe(pro_id)

    def apply_viewmodel(self, preset_id):
        return pros.apply_viewmodel_safe(preset_id)

    def apply_pro(self, pro_id):
        return pros.apply_crosshair_safe(pro_id)

    # ---------- ESTUDIO DE VOZ ----------
    def voice_effects(self):
        out = []
        for e in voicefx.EFFECTS:
            out.append({**e, "photo": f"assets/voice/{e['id']}.png",
                        "live": voicefx.is_live(e)})
        return out

    def voice_devices(self):
        if not _SD_OK:
            return {"success": False, "output": "Falta: pip install sounddevice numpy"}
        try:
            devs = sd.query_devices()
            ins, outs = [], []
            for i, d in enumerate(devs):
                if d["max_input_channels"] > 0:
                    ins.append({"index": i, "name": d["name"]})
                if d["max_output_channels"] > 0:
                    outs.append({"index": i, "name": d["name"]})
            names = [(o["name"] or "").lower() for o in outs] + \
                    [(o["name"] or "").lower() for o in ins]
            virtual = any("midnight" in n or "cable" in n for n in names)
            return {"success": True, "inputs": ins, "outputs": outs,
                    "default_in": sd.default.device[0], "default_out": sd.default.device[1],
                    "virtual": virtual,
                    "cable": virtual}
        except Exception as e:
            return {"success": False, "output": str(e)}

    # ---------- MICRO VIRTUAL "MIDNIGHT" (por cima do VB-CABLE) ----------
    # Um driver de audio virtual do zero exigiria driver assinado; em vez
    # disso rebatizamos os endpoints do VB-CABLE (que o Setup ja instala)
    # para o nome da app. Discord/CS2 passam a mostrar "Midnight".
    _MIDNIGHT_NAMES = {"Render": "Midnight Speakers", "Capture": "Midnight Mic"}
    _MIDNIGHT_PKEY = "{a45c254e-df1c-4efd-8020-67d146a850e0},14"
    _MIDNIGHT_DESC = "{a45c254e-df1c-4efd-8020-67d146a850e0},2"

    def audio_virtual_endpoints(self):
        """Lista endpoints do micro virtual (VB-CABLE, com ou sem rebrand)."""
        found = []
        try:
            import winreg
        except Exception as e:
            return found
        for direction in ("Render", "Capture"):
            base = (r"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices"
                    rf"\Audio\{direction}")
            try:
                h = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base)
            except Exception:
                continue
            try:
                i = 0
                while True:
                    try:
                        guid = winreg.EnumKey(h, i)
                    except OSError:
                        break
                    i += 1
                    try:
                        hp = winreg.OpenKey(h, guid + "\\Properties")
                        try:
                            desc, _ = winreg.QueryValueEx(hp, self._MIDNIGHT_DESC)
                        except Exception:
                            desc = ""
                        try:
                            fr, _ = winreg.QueryValueEx(hp, self._MIDNIGHT_PKEY)
                        except Exception:
                            fr = ""
                        hp.Close()
                    except Exception:
                        continue
                    # Só o par principal (evita duplicar nomes na variante 16ch).
                    fr_u = (fr or "").upper()
                    if ((direction == "Render" and (desc or "") == "CABLE Input") or
                            (direction == "Capture" and (desc or "") == "CABLE Output") or
                            ("MIDNIGHT" in fr_u and ("CABLE" in (desc or "").upper()
                                                     or "VB-AUDIO" in (desc or "").upper()))):
                        want = self._MIDNIGHT_NAMES[direction]
                        found.append({"direction": direction, "guid": guid,
                                      "desc": desc, "friendly": fr or "",
                                      "branded": (fr or "") == want})
            finally:
                try:
                    h.Close()
                except Exception:
                    pass
        return found

    def audio_brand_virtual(self):
        """Rebatiza CABLE Input/Output -> Midnight Speakers/Mic (precisa admin)."""
        eps = self.audio_virtual_endpoints()
        if not eps:
            return {"success": False,
                    "output": "Micro virtual não encontrado. Corre o Setup para instalar."}
        if all(e.get("branded") for e in eps):
            return {"success": True, "output": "Já está como Midnight. ✔"}
        try:
            import winreg
        except Exception as e:
            return {"success": False, "output": str(e)}
        done = []
        for e in eps:
            if e.get("branded"):
                continue
            want = self._MIDNIGHT_NAMES[e["direction"]]
            key = (r"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices"
                   rf"\Audio\{e['direction']}\{e['guid']}\Properties")
            try:
                h = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key,
                                   0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(h, self._MIDNIGHT_PKEY, 0,
                                  winreg.REG_SZ, want)
                h.Close()
                done.append(f"{e['desc']} -> {want}")
            except PermissionError:
                return {"success": False,
                        "output": "Corre a app como Administrador para rebatizar."}
            except Exception as ex:
                return {"success": False, "output": f"Falha em {e['desc']}: {ex}"}
        return {"success": True,
                "output": "Micro virtual agora é Midnight:\n" + "\n".join(done) +
                          "\n\nSe os nomes antigos persistirem, reinicia o PC."}

    def audio_restart_service(self):
        """Reinicia o serviço de áudio (refresca os nomes; o som corta uns segundos)."""
        r = run_cmd("net stop Audiosrv /y")
        r2 = run_cmd("net start Audiosrv")
        ok = r2["success"]
        out = (r.get("output", "") + "\n" + r2.get("output", "")).strip()
        if not ok:
            return {"success": False,
                    "output": "Falha (corre como Administrador). " + out}
        return {"success": True, "output": "Serviço de áudio reiniciado. ✔"}

    def _dev(self, idx, which):
        try:
            i = int(idx)
            if i < 0:
                raise ValueError
            return i
        except Exception:
            try:
                return int(sd.default.device[which])
            except Exception:
                return None

    def _open_stream(self, in_idx, out_idx, callback):
        import numpy as np
        last_err = None
        for ch in (1, 2):
            try:
                s = sd.Stream(samplerate=voicefx.SR, blocksize=1024, dtype="float32",
                              device=(in_idx, out_idx), channels=ch, callback=callback)
                s.start()
                return s, ch, None
            except Exception as e:
                last_err = e
        return None, 0, str(last_err)

    def voice_start(self, effect_id="robot", in_idx=-1, out_idx=-1, gain=1.5):
        global _LAST_IN, _LAST_OUT, _LAST_GAIN
        if not _SD_OK:
            return {"success": False, "output": "Falta: pip install sounddevice numpy"}
        self.voice_stop()
        import numpy as np
        _LAST_IN, _LAST_OUT, _LAST_GAIN = in_idx, self._dev(out_idx, 1), float(gain)
        st = voicefx.new_state(effect_id)
        holder = {}

        def cb(indata, outdata, frames, time_info, status):
            x = np.asarray(indata, dtype=np.float32)
            if x.shape[1] > 1:
                x = x.mean(axis=1, dtype=np.float32)
            else:
                x = x[:, 0]
            y = voicefx.process_block(x, effect_id, st, voicefx.SR, float(gain))
            outdata[:, 0] = y[:frames]
            if outdata.shape[1] > 1:
                outdata[:, 1] = y[:frames]

        s, ch, err = self._open_stream(self._dev(in_idx, 0), self._dev(out_idx, 1), cb)
        if s is None:
            return {"success": False, "output": f"Audio falhou: {err}"}
        _VS.update({"stream": s, "state": st, "effect": effect_id, "gain": float(gain)})
        holder["ch"] = ch
        return {"success": True, "output": f"AO VIVO: {effect_id} (canais {ch})"}

    def voice_stop(self):
        """Para a cadeia de ENVIO (efeito ativo). Nao mexe no monitor nem nos sons."""
        try:
            if _VS.get("stream") is not None:
                _VS["stream"].stop()
                _VS["stream"].close()
        except Exception:
            pass
        _VS["stream"] = None
        return {"success": True, "output": "Efeito desativado."}

    def monitor_stop(self):
        """Para a monitorizacao (ouvir-me)."""
        try:
            if _VS.get("mon") is not None:
                _VS["mon"].stop()
                _VS["mon"].close()
        except Exception:
            pass
        _VS["mon"] = None
        return {"success": True, "output": "Monitor desligado."}

    def monitor_start(self, effect_id="radio", in_idx=-1, mon_idx=-1, gain=1.5):
        """Ouve-te a ti proprio COM o efeito (auscultadores). Independente do envio."""
        if not _SD_OK:
            return {"success": False, "output": "Falta: pip install sounddevice numpy"}
        self.monitor_stop()
        import numpy as np
        st = voicefx.new_state(effect_id)

        def cb(indata, outdata, frames, time_info, status):
            x = np.asarray(indata, dtype=np.float32)
            x = x.mean(axis=1, dtype=np.float32) if x.shape[1] > 1 else x[:, 0]
            y = voicefx.process_block(x, effect_id, st, voicefx.SR, float(gain))
            outdata[:, 0] = y[:frames]
            if outdata.shape[1] > 1:
                outdata[:, 1] = y[:frames]

        s, ch, err = self._open_stream(self._dev(in_idx, 0), self._dev(mon_idx, 1), cb)
        if s is None:
            return {"success": False,
                    "output": f"Monitor falhou (micro ocupado?): {err}"}
        _VS.update({"mon": s, "mon_state": st})
        return {"success": True, "output": f"🎙️ A ouvires-te com {effect_id}."}

    def _stop_all_audio(self):
        self.voice_stop()
        self.monitor_stop()
        try:
            if sd is not None:
                sd.stop()
        except Exception:
            pass

    def voice_record_start(self, in_idx=-1):
        if not _SD_OK:
            return {"success": False, "output": "Falta: pip install sounddevice numpy"}
        import numpy as np
        self._stop_all_audio()
        buf = []

        def cb(indata, frames, time_info, status):
            x = np.asarray(indata, dtype=np.float32)
            buf.append(x.mean(axis=1, dtype=np.float32) if x.shape[1] > 1 else x[:, 0].copy())

        try:
            s = sd.InputStream(samplerate=voicefx.SR, dtype="float32",
                               device=self._dev(in_idx, 0),
                               channels=1, callback=cb)
            s.start()
        except Exception:
            try:
                s = sd.InputStream(samplerate=voicefx.SR, dtype="float32",
                                   device=self._dev(in_idx, 0),
                                   channels=2, callback=cb)
                s.start()
            except Exception as e2:
                return {"success": False, "output": f"Mic falhou: {e2}"}
        _VS.update({"rec": s, "recording": True, "_buf": buf})
        return {"success": True, "output": "A gravar... fala agora (max 15s)."}

    def voice_record_stop(self, effect_id="demon", out_idx=-1, gain=1.5):
        import numpy as np
        import wave
        s = _VS.get("rec")
        buf = _VS.get("_buf", [])
        _VS["recording"] = False
        try:
            if s is not None:
                s.stop()
                s.close()
        except Exception:
            pass
        _VS["rec"] = None
        if not buf:
            return {"success": False, "output": "Nada gravado."}
        x = np.concatenate(buf)
        maxn = voicefx.SR * 15
        x = x[:maxn]
        y = voicefx.transform(x, effect_id, voicefx.SR, float(gain))
        wav = os.path.join(tempfile.gettempdir(), f"midnight_voz_{effect_id}.wav")
        try:
            with wave.open(wav, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(voicefx.SR)
                w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
            _VS["last_wav"] = wav
        except Exception as e:
            return {"success": False, "output": f"Falha WAV: {e}"}
        try:
            sd.play(y, voicefx.SR, device=self._dev(out_idx, 1))
        except Exception as e:
            return {"success": False, "output": f"Transformado mas falha a tocar: {e}"}
        return {"success": True, "output": f"✔ {effect_id}: {len(x)/voicefx.SR:.1f}s -> a tocar.",
                "secs": round(len(x) / voicefx.SR, 1), "wav": wav}

    def voice_replay(self, out_idx=-1):
        w = _VS.get("last_wav", "")
        if not w or not os.path.isfile(w):
            return {"success": False, "output": "Grava primeiro."}
        try:
            import wave
            import numpy as np
            with wave.open(w, "rb") as f:
                raw = f.readframes(f.getnframes())
                y = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767.0
            sd.play(y, voicefx.SR, device=self._dev(out_idx, 1))
            return {"success": True, "output": "A repetir ultima transformacao."}
        except Exception as e:
            return {"success": False, "output": str(e)}

    # ---------- SOUNDBOARD (myinstants + pessoais) ----------
    def soundboard_list(self):
        try:
            with open(os.path.join(BASE_DIR, "assets", "sounds", "manifest.json"),
                      encoding="utf-8") as f:
                builtin = json.load(f)
        except Exception as e:
            builtin = []
        try:
            customs = accounts.custom_sounds(self._me())
            for c in customs:
                c["photo"] = self._avatar_url(c.get("photo", ""))
            return builtin + customs
        except Exception:
            return builtin

    def soundboard_add(self):
        """Adiciona um som pessoal (mp3/wav/ogg) a conta atual."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            path = filedialog.askopenfilename(
                title="Escolhe um som (mp3/wav/ogg)",
                filetypes=[("Audio", "*.mp3 *.wav *.ogg"), ("Todos", "*.*")]
            )
            root.destroy()
            if not path:
                return {"success": False, "output": "Cancelado."}
            base = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(path))[0].lower()).strip("-")[:40] or "som"
            sdir = os.path.join(accounts.user_dir(self._me()), "sounds")
            dest = os.path.join(sdir, base + os.path.splitext(path)[1].lower())
            i = 1
            while os.path.exists(dest):
                dest = os.path.join(sdir, f"{base}-{i}{os.path.splitext(path)[1].lower()}")
                i += 1
            shutil.copy2(path, dest)
            # valida decode
            try:
                if miniaudio is None:
                    raise RuntimeError("sem decoder")
                miniaudio.decode_file(dest)
            except Exception:
                try:
                    os.remove(dest)
                except Exception:
                    pass
                return {"success": False, "output": "Ficheiro nao e audio valido."}
            # icon
            try:
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new("RGB", (256, 256), "#060714")
                d = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("arial.ttf", 110)
                except Exception:
                    font = ImageFont.load_default()
                letter = (base.strip() or "?")[0].upper()
                bb = d.textbbox((0, 0), letter, font=font)
                w, h = bb[2] - bb[0], bb[3] - bb[1]
                d.ellipse([28, 28, 228, 228], outline=(212, 175, 55), width=5)
                d.text(((256 - w) / 2 - bb[0], (256 - h) / 2 - bb[1] - 8), letter,
                       font=font, fill=(212, 175, 55))
                img.save(os.path.join(sdir, os.path.splitext(os.path.basename(dest))[0] + ".png"))
            except Exception:
                pass
            _SB_CACHE.pop("u_" + os.path.splitext(os.path.basename(dest))[0], None)
            return {"success": True, "output": f"Som '{base}' adicionado aos teus sons!"}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def soundboard_remove(self, sound_id):
        if not (sound_id or "").startswith("u_"):
            return {"success": False, "output": "So sons pessoais."}
        try:
            sdir = os.path.join(accounts.user_dir(self._me()), "sounds")
            stem = sound_id[2:]
            for fn in os.listdir(sdir):
                if os.path.splitext(fn)[0] == stem:
                    os.remove(os.path.join(sdir, fn))
            _SB_CACHE.pop(sound_id, None)
            return {"success": True, "output": "Som removido."}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def _sb_samples(self, sound_id):
        import numpy as np
        if sound_id in _SB_CACHE:
            return _SB_CACHE[sound_id]
        path = os.path.join(BASE_DIR, "assets", "sounds", sound_id + ".mp3")
        if not os.path.isfile(path):
            for s in self.soundboard_list():
                if s.get("id") == sound_id and s.get("file"):
                    cand = s["file"]
                    if not os.path.isabs(cand):
                        cand = os.path.join(BASE_DIR, cand)
                    if os.path.isfile(cand):
                        path = cand
                    break
        if not os.path.isfile(path):
            return None
        d = miniaudio.decode_file(path)
        y = np.array(d.samples, dtype=np.float32)
        if d.nchannels > 1:
            y = y.reshape(-1, d.nchannels).mean(axis=1)
        y = y / max(1e-6, np.max(np.abs(y))) * 0.9
        if d.sample_rate != voicefx.SR:
            y = np.interp(np.linspace(0, len(y) - 1, int(len(y) * voicefx.SR / d.sample_rate)),
                          np.arange(len(y)), y).astype(np.float32)
        _SB_CACHE[sound_id] = y
        return y

    def soundboard_play(self, sound_id, out_idx=-1):
        global _LAST_OUT
        if not (_SD_OK and _MA_OK):
            return {"success": False, "output": "Falta: pip install sounddevice miniaudio"}
        _LAST_OUT = self._dev(out_idx, 1)
        try:
            y = self._sb_samples(sound_id)
            if y is None:
                return {"success": False, "output": "Som nao encontrado."}
            sd.play(y, voicefx.SR, device=_LAST_OUT)
            return {"success": True, "output": f"▶ {sound_id}"}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def soundboard_stop(self):
        try:
            if sd is not None:
                sd.stop()
        except Exception:
            pass
        return {"success": True, "output": "Soundboard parada."}

    # ---------- HOTKEYS GLOBAIS ----------
    def hotkey_set(self, bindings):
        if not _KB_OK:
            return {"success": False, "output": "Falta: pip install keyboard"}
        self.hotkey_clear()
        ok, fail = 0, []
        for combo, b in (bindings or {}).items():
            try:
                _kb.add_hotkey(combo, self._hotkey_fire,
                               args=(str(b.get("kind", "")), str(b.get("id", ""))),
                               suppress=False)
                _HK.append(combo)
                ok += 1
            except Exception:
                fail.append(combo)
        return {"success": True, "output": f"Atalhos ativos: {ok}" + (f" (falhas: {fail})" if fail else "")}

    def hotkey_clear(self):
        try:
            if _kb is not None:
                _kb.clear_all_hotkeys()
        except Exception:
            pass
        _HK.clear()
        return {"success": True, "output": "Atalhos limpos."}

    def _hotkey_fire(self, kind, item_id):
        try:
            if kind == "voice":
                self.voice_stop()
                self.voice_start(item_id, _LAST_IN, _LAST_OUT, _LAST_GAIN)
                try:
                    if _WINDOW is not None:
                        _WINDOW.evaluate_js(f"vmSelectFromHotkey('{item_id}')")
                except Exception:
                    pass
            elif kind == "sound":
                self.soundboard_play(item_id, _LAST_OUT)
        except Exception:
            pass

    # ---------- AUTO-UPDATE ----------
    def app_version(self):
        return {"version": APP_VERSION}

    def get_news(self):
        """Novidades da versão atual (popup ao ligar a app)."""
        return {"version": APP_VERSION, "news": list(APP_NEWS)}

    def log_error(self, msg):
        return log_error(str(msg))

    def check_update(self):
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{REPO}/releases/latest",
                headers={"User-Agent": "MidnightOptimizer", "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                rel = json.loads(r.read().decode())
            latest = rel.get("tag_name", "")
            notes = rel.get("body", "") or ""
            dl = ""
            fallback = ""
            for a in rel.get("assets", []):
                nm = a.get("name", "")
                if nm == "MidnightOptimizer.exe":
                    dl = a.get("browser_download_url", "")
                    break
                if not fallback and nm.lower().endswith(".exe") and "setup" not in nm.lower():
                    fallback = a.get("browser_download_url", "")
            if not dl:
                dl = fallback
            available = bool(latest) and _ver_tuple(latest) > _ver_tuple(APP_VERSION)
            if available:
                _UPDATE.update({"version": latest, "notes": notes})
                _UPDATE["dl"] = dl
            return {"success": True, "current": APP_VERSION, "latest": latest,
                    "available": available, "notes": notes, "url": dl}
        except Exception as e:
            msg = str(e)
            if "404" in msg:
                msg = "Repo privado ou nao encontrado: torna o repo Publico no GitHub para ativar updates."
            return {"success": False, "current": APP_VERSION, "output": f"Sem updates: {msg}"}

    def start_update(self):
        if _UPDATE.get("status") == "downloading":
            return {"success": True, "output": "Ja a descarregar."}
        url = _UPDATE.get("dl", "")
        if not url:
            c = self.check_update()
            if not c.get("available"):
                return {"success": False, "output": "Sem atualizacao disponivel."}
            url = c.get("url", "")
        if not url:
            return {"success": False, "output": "Link do .exe nao encontrado."}
        _UPDATE.update({"status": "downloading", "pct": 0, "error": ""})

        def _dl():
            try:
                dest = os.path.join(tempfile.gettempdir(), "MidnightOptimizer_novo.exe")
                try:
                    if os.path.isfile(dest):
                        os.remove(dest)
                except Exception:
                    pass
                req = urllib.request.Request(url, headers={"User-Agent": "MidnightOptimizer"})
                with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
                    total = int(r.headers.get("Content-Length") or 0)
                    got = 0
                    while True:
                        chunk = r.read(1024 * 256)
                        if not chunk:
                            break
                        f.write(chunk)
                        got += len(chunk)
                        if total:
                            _UPDATE["pct"] = min(99, int(got * 100 / total))
                final = os.path.getsize(dest) if os.path.isfile(dest) else 0
                if total and final != total:
                    raise IOError(f"download incompleto ({final}/{total} bytes)")
                if final < 5 * 1024 * 1024:
                    raise IOError(f"ficheiro suspeito ({final} bytes)")
                _UPDATE.update({"status": "ready", "pct": 100, "path": dest})
            except Exception as e:
                _UPDATE.update({"status": "error", "error": str(e)})
        threading.Thread(target=_dl, daemon=True).start()
        return {"success": True, "output": "A descarregar..."}

    def update_progress(self):
        return {"status": _UPDATE.get("status", "idle"), "pct": _UPDATE.get("pct", 0),
                "error": _UPDATE.get("error", ""), "version": _UPDATE.get("version", "")}

    def apply_update_and_restart(self):
        if not getattr(sys, "frozen", False):
            return {"success": False, "output": "So no .exe final. Usa o .exe do GitHub."}
        new_exe = _UPDATE.get("path", "")
        if not new_exe or not os.path.isfile(new_exe):
            return {"success": False, "output": "Atualizacao ainda nao descarregada."}
        if os.path.getsize(new_exe) < 5 * 1024 * 1024:
            return {"success": False, "output": "Ficheiro descarregado invalido. Descarrega de novo."}
        cur = sys.executable
        logf = os.path.join(tempfile.gettempdir(), "midnight_update.log")
        try:
            if os.path.isfile(logf):
                os.remove(logf)
        except Exception:
            pass
        bat = os.path.join(tempfile.gettempdir(), "midnight_update.bat")
        try:
            with open(bat, "w") as f:
                f.write("@echo off\n")
                f.write(f'echo inicio > "{logf}"\n')
                f.write("timeout /t 2 /nobreak >nul\n")
                f.write("set N=0\n:loop\n")
                f.write(f'move /Y "{new_exe}" "{cur}" >nul 2>&1\n')
                f.write("if not errorlevel 1 goto done\n")
                f.write("set /a N+=1\n")
                f.write(f'echo tentativa %N% falhou >> "{logf}"\n')
                f.write("if %N% GEQ 20 goto fail\n")
                f.write("timeout /t 1 /nobreak >nul\n")
                f.write("goto loop\n:fail\n")
                f.write(f'echo FALHOU sem permissao >> "{logf}"\n')
                f.write("exit /b 1\n:done\n")
                f.write(f'echo OK >> "{logf}"\n')
                f.write(f'start "" "{cur}"\n')
                f.write('del "%~f0"\n')
        except Exception as e:
            return {"success": False, "output": f"Nao consegui preparar o restart: {e}"}
        try:
            admin = False
            try:
                admin = bool(self.is_admin().get("admin"))
            except Exception:
                pass
            if admin or self._dir_writable(cur):
                subprocess.Popen(["cmd", "/c", bat], shell=False, **_hidden(),
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                import ctypes
                ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe",
                                                    f'/c "{bat}"', None, 0)
        except Exception as e:
            log_error("apply_update: " + str(e))
            return {"success": False, "output": f"Falha a aplicar (usa o botao Manual): {e}"}
        # Sai de imediato SEM tocar na janela: destroy() a partir da thread
        # do JS pode bloquear e o restart nunca acontece. O .bat espera 2s,
        # troca o .exe e volta a abrir a app sozinho.
        try:
            import time
            time.sleep(0.3)
        except Exception:
            pass
        os._exit(0)

    def _dir_writable(self, path):
        try:
            t = os.path.join(os.path.dirname(path) or ".", ".midnight_wtest")
            with open(t, "w") as f:
                f.write("x")
            os.remove(t)
            return True
        except Exception:
            return False

    def update_last_result(self):
        try:
            p = os.path.join(tempfile.gettempdir(), "midnight_update.log")
            if os.path.isfile(p):
                txt = open(p, encoding="utf-8", errors="ignore").read()
                if "FALHOU" in txt:
                    try:
                        os.remove(p)
                    except Exception:
                        pass
                    return {"success": False,
                            "output": "O ultimo update falhou (sem permissao). Corre como administrador ou usa o botao Manual."}
        except Exception:
            pass
        return {"success": True}

    # ---------- CHAT DE BUGS ----------
    def _bugs_file(self):
        try:
            return os.path.join(accounts.data_root(), "bugs.json")
        except Exception:
            return os.path.join(BASE_DIR, "bugs.json")

    def _bugs_load(self):
        try:
            p = self._bugs_file()
            if os.path.isfile(p):
                with open(p, encoding="utf-8") as f:
                    d = json.load(f)
                    return d if isinstance(d, list) else []
        except Exception:
            pass
        return []

    def _bugs_save(self, items):
        with open(self._bugs_file(), "w", encoding="utf-8") as f:
            json.dump(items[-500:], f, ensure_ascii=False, indent=1)

    def bugs_list(self):
        try:
            local = self._bugs_load()
            linked = {e.get("issue") for e in local if e.get("issue")}
            merged = list(local)
            for it in self._github_issues():
                if it.get("number") in linked:
                    continue
                merged.append({
                    "user": it.get("user", "GitHub"),
                    "text": it.get("text", ""),
                    "when": it.get("when", ""),
                    "issue": it.get("number"),
                })
            return {"success": True, "bugs": merged[-500:]}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def bugs_add(self, text):
        text = (text or "").strip()
        if not text:
            return {"success": False, "output": "Escreve o bug primeiro."}
        if len(text) > 2000:
            return {"success": False, "output": "Mensagem demasiado longa (max 2000)."}
        try:
            import datetime
            me = self._me()
            items = self._bugs_load()
            entry = {
                "user": me,
                "text": text[:2000],
                "when": datetime.datetime.now().strftime("%d/%m %H:%M"),
            }
            items.append(entry)
            self._bugs_save(items)
            idx = len(items) - 1
            # Envia para o GitHub em 2º plano (não bloqueia nem rebenta).
            threading.Thread(target=self._report_issue,
                             args=(me, text[:2000], idx),
                             daemon=True).start()
            return {"success": True, "output": "Bug registado. Obrigado!"}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def _github_token(self):
        """Token para criar issues. Vem de ficheiro LOCAL (nunca do repo)."""
        try:
            t = (os.environ.get("GITHUB_TOKEN") or "").strip()
            if t:
                return t
            cands = [os.path.join(BASE_DIR, "bugs_config.json")]
            try:
                cands.append(os.path.join(accounts.data_root(), "bugs_config.json"))
            except Exception:
                pass
            for p in cands:
                if os.path.isfile(p):
                    with open(p, encoding="utf-8") as f:
                        d = json.load(f)
                    if isinstance(d, dict):
                        t = (d.get("github_token") or d.get("token") or "").strip()
                        if t:
                            return t
        except Exception:
            pass
        return ""

    def _github_issues(self):
        """Issues com label 'bug' (cache 60s). Leitura publica, sem token."""
        import time
        try:
            if time.time() - _ISSUES_CACHE.get("at", 0) < 60:
                return _ISSUES_CACHE.get("items", [])
        except Exception:
            pass
        items = []
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{REPO}/issues?state=open&labels=bug&per_page=50",
                headers={"User-Agent": "MidnightOptimizer",
                         "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode())
            for it in data or []:
                if "pull_request" in (it or {}):
                    continue
                body = (it.get("body") or "").strip()
                title = (it.get("title") or "").strip()
                if title.startswith("[Bug]"):
                    title = title[5:].strip()
                items.append({
                    "number": it.get("number"),
                    "user": "GitHub #" + str(it.get("number", "?")),
                    "text": (title + ("\n" + body if body else "")).strip()[:2000],
                    "when": (it.get("created_at") or "")[:10],
                })
        except Exception as e:
            log_error("github issues GET: " + str(e))
        try:
            _ISSUES_CACHE.update({"at": time.time(), "items": items})
        except Exception:
            pass
        return items

    def _report_issue(self, user, text, idx):
        """Cria a issue no GitHub e liga-a a entrada local. Nunca rebenta."""
        try:
            token = self._github_token()
            if not token:
                return
            import datetime
            first = (text.strip().split("\n") or ["Bug"])[0][:80] or "Bug"
            body = (f"**Utilizador:** {user}\n**Versão:** {APP_VERSION}\n"
                    f"**Data:** {datetime.datetime.now():%d/%m %H:%M}\n\n{text}")
            payload = json.dumps({"title": f"[Bug] {first}",
                                  "body": body, "labels": ["bug"]}).encode()
            req = urllib.request.Request(
                f"https://api.github.com/repos/{REPO}/issues", data=payload,
                headers={"User-Agent": "MidnightOptimizer",
                         "Accept": "application/vnd.github+json",
                         "Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(req, timeout=20) as r:
                issue = json.loads(r.read().decode())
            num = issue.get("number")
            if num:
                items = self._bugs_load()
                if 0 <= idx < len(items):
                    items[idx]["issue"] = num
                    self._bugs_save(items)
        except Exception as e:
            log_error("github issue POST: " + str(e))

    def bugs_clear(self):
        try:
            self._bugs_save([])
            return {"success": True, "output": "Chat de bugs limpo."}
        except Exception as e:
            return {"success": False, "output": str(e)}


def main():
    global _WINDOW
    api = Api()
    index = os.path.join(BASE_DIR, "index.html")
    window = webview.create_window(
        "Midnight Optimizer — Forja Competitiva",
        url=index,
        js_api=api,
        width=1280, height=800,
        min_size=(1024, 640),
        background_color="#060714",
    )
    _WINDOW = window
    webview.start(debug=False)

if __name__ == "__main__":
    main()
