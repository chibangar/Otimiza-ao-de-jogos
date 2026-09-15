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
import tempfile
import threading
import urllib.request
import webview
import game_tweaks
import pros
import voicefx

try:
    import sounddevice as sd
    _SD_OK = True
except Exception:
    sd = None
    _SD_OK = False

_VS = {"stream": None, "state": None, "effect": "", "gain": 1.5,
       "rec": None, "recording": False, "last_wav": ""}

APP_VERSION = "1.3.0"
REPO = "chibangar/Otimiza-ao-de-jogos"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
            # lança com prioridade Alta (sem janela de consola)
            subprocess.Popen(f'cmd /c start "" /HIGH "{game_path}"', shell=True, **_hidden())
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

    # ---------- PROS CS2 ----------
    def list_pros(self):
        return pros.list_pros()

    def apply_pro(self, pro_id):
        return pros.apply_pro(pro_id)

    # ---------- ESTUDIO DE VOZ ----------
    def voice_effects(self):
        out = []
        for e in voicefx.EFFECTS:
            out.append({**e, "photo": f"assets/voice/{e['id']}.png"})
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
            return {"success": True, "inputs": ins, "outputs": outs,
                    "default_in": sd.default.device[0], "default_out": sd.default.device[1]}
        except Exception as e:
            return {"success": False, "output": str(e)}

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
        if not _SD_OK:
            return {"success": False, "output": "Falta: pip install sounddevice numpy"}
        self.voice_stop()
        import numpy as np
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
        try:
            if _VS.get("stream") is not None:
                _VS["stream"].stop()
                _VS["stream"].close()
        except Exception:
            pass
        _VS["stream"] = None
        try:
            if sd is not None:
                sd.stop()
        except Exception:
            pass
        return {"success": True, "output": "Voz parada."}

    def voice_record_start(self, in_idx=-1):
        if not _SD_OK:
            return {"success": False, "output": "Falta: pip install sounddevice numpy"}
        import numpy as np
        self.voice_stop()
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

    # ---------- AUTO-UPDATE ----------
    def app_version(self):
        return {"version": APP_VERSION}

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
            for a in rel.get("assets", []):
                if a.get("name", "").lower().endswith(".exe"):
                    dl = a.get("browser_download_url", "")
                    break
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
        cur = sys.executable
        bat = os.path.join(tempfile.gettempdir(), "midnight_update.bat")
        with open(bat, "w") as f:
            f.write("@echo off\n")
            f.write("timeout /t 2 /nobreak >nul\n")
            f.write(":loop\n")
            f.write(f'move /Y "{new_exe}" "{cur}" >nul 2>&1\n')
            f.write('if errorlevel 1 (timeout /t 1 /nobreak >nul & goto loop)\n')
            f.write(f'start "" "{cur}"\n')
            f.write('del "%~f0"\n')
        subprocess.Popen(["cmd", "/c", bat], shell=False, **_hidden(),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            if _WINDOW is not None:
                _WINDOW.destroy()
        finally:
            os._exit(0)


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
