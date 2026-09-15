"""
Midnight Optimizer — App nativa Windows
Estilo WoW Midnight | Modo Competitivo
Backend Python + WebView2 (Edge) — gera .exe único
"""
import os
import sys
import json
import subprocess
import platform
import shutil
import webview
import game_tweaks

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_ps(command: str, timeout=60):
    """Corre PowerShell e devolve dict."""
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True, text=True, timeout=timeout
        )
        out = (r.stdout or r.stderr or "").strip()
        return {"success": r.returncode == 0, "output": out}
    except Exception as e:
        return {"success": False, "output": str(e)}

def run_cmd(command: str, timeout=60):
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        out = (r.stdout or r.stderr or "").strip()
        return {"success": r.returncode == 0, "output": out}
    except Exception as e:
        return {"success": False, "output": str(e)}


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
        }

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
            # lança com prioridade Alta
            subprocess.Popen(f'cmd /c start "" /HIGH "{game_path}"', shell=True)
            return {"success": True, "output": "Jogo lançado com prioridade ALTA."}
        except Exception as e:
            return {"success": False, "output": str(e)}

    # ---------- IN-GAME: CS2 & WOW ----------
    def detect_games(self):
        cs = game_tweaks.find_cs2()
        wow = game_tweaks.find_wow()
        return {
            "cs2": {"found": bool(cs), "base": cs.get("base", ""), "cfg": cs.get("cfg_dir", ""),
                    "autoexec": cs.get("autoexec", ""), "videos": cs.get("video_candidates", [])},
            "wow": {"found": bool(wow and wow.get("config") and os.path.isfile(wow.get("config"))),
                    "base": (wow or {}).get("base", ""), "config": (wow or {}).get("config", ""),
                    "flavor": (wow or {}).get("flavor", "")},
        }

    def cs2_competitive(self):
        return game_tweaks.apply_cs2_competitive()

    def cs2_restore(self):
        return game_tweaks.restore_cs2()

    def cs2_launch_options(self):
        return {"success": True, "output": game_tweaks.CS2_LAUNCH_COMPETITIVE}

    def wow_competitive(self):
        return game_tweaks.apply_wow("competitive")

    def wow_balanced(self):
        return game_tweaks.apply_wow("balanced")

    def wow_restore(self):
        return game_tweaks.restore_wow()


def main():
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
    webview.start(debug=False)

if __name__ == "__main__":
    main()
