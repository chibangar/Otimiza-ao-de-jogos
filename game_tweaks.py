"""Otimizações dentro do próprio jogo — CS2 e WoW (Midnight)."""
import os
import re
import shutil
import glob

# ---------------- helpers ----------------
def backup_file(path):
    if not path or not os.path.isfile(path):
        return None
    bak = path + ".midnight_backup"
    if not os.path.exists(bak):
        try:
            shutil.copy2(path, bak)
        except Exception:
            return None
    return bak

def restore_file(path):
    bak = (path or "") + ".midnight_backup"
    if os.path.isfile(bak):
        try:
            shutil.copy2(bak, path)
            return {"success": True, "output": f"Restaurado: {os.path.basename(path)}"}
        except Exception as e:
            return {"success": False, "output": str(e)}
    return {"success": False, "output": "Sem backup encontrado."}

def set_wtf_value(text, key, value):
    """Define SET key \"value\" no Config.wtf (substitui ou adiciona)."""
    pattern = re.compile(rf'^SET\s+{re.escape(key)}\s+.*$', re.MULTILINE | re.IGNORECASE)
    line = f'SET {key} "{value}"'
    if pattern.search(text):
        return pattern.sub(line, text)
    return text.rstrip() + "\n" + line + "\n"

# ---------------- CS2 ----------------
def _hidden_kwargs():
    import subprocess
    kw = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)}
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kw["startupinfo"] = si
    except Exception:
        pass
    return kw


def _cfg_store():
    try:
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        p = os.path.join(base, "MidnightOptimizer")
        os.makedirs(p, exist_ok=True)
        return os.path.join(p, "paths.json")
    except Exception:
        return None


def get_custom_cs2():
    try:
        import json
        f = _cfg_store()
        if f and os.path.isfile(f):
            p = (json.load(open(f, encoding="utf-8")) or {}).get("cs2", "")
            if p and os.path.isdir(p):
                return p
    except Exception:
        pass
    return ""


def set_custom_cs2(path):
    try:
        import json
        f = _cfg_store()
        d = {}
        if f and os.path.isfile(f):
            d = json.load(open(f, encoding="utf-8")) or {}
        d["cs2"] = path
        if f:
            json.dump(d, open(f, "w", encoding="utf-8"))
        return True
    except Exception:
        return False


def steam_roots():
    """Raizes do Steam: registo oficial + caminhos comuns."""
    roots = []
    try:
        import winreg
        for hive, sub in [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam"),
        ]:
            try:
                with winreg.OpenKey(hive, sub) as k:
                    p, _ = winreg.QueryValueEx(k, "SteamPath")
                    if p and os.path.isdir(p):
                        roots.append(os.path.normpath(p))
            except Exception:
                pass
    except Exception:
        pass
    for env in ["ProgramFiles(x86)", "ProgramW6432", "ProgramFiles"]:
        base = os.environ.get(env)
        if base:
            c = os.path.join(base, "Steam")
            if os.path.isdir(c):
                roots.append(c)
    for c in [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam",
              r"D:\Steam", r"E:\Steam", r"F:\Steam"]:
        if os.path.isdir(c):
            roots.append(c)
    out = []
    seen = set()
    for r in roots:
        r = os.path.normpath(r)
        if r.lower() not in seen:
            seen.add(r.lower())
            out.append(r)
    return out


def steam_libraries():
    """Todas as bibliotecas: raiz + libraryfolders.vdf (novo e antigo)."""
    libs = []
    seen = set()

    def add(p):
        p = os.path.normpath(p)
        if os.path.isdir(p) and p.lower() not in seen:
            seen.add(p.lower())
            libs.append(p)

    for root in steam_roots():
        add(root)
        vdf = os.path.join(root, "steamapps", "libraryfolders.vdf")
        if not os.path.isfile(vdf):
            continue
        try:
            txt = open(vdf, encoding="utf-8", errors="ignore").read()
            for m in re.finditer(r'"path"\s+"([^"]+)"', txt):
                add(m.group(1).replace("\\\\", "\\"))
            for m in re.finditer(r'"\d+"\s+"([^"]+)"', txt):
                p = os.path.normpath(m.group(1).replace("\\\\", "\\"))
                if "steamapps" in p.lower():
                    add(os.path.dirname(p) if os.path.basename(p).lower() == "steamapps" else p)
        except Exception:
            pass
    return libs


def cs2_running():
    """CS2 a correr? Devolve (bool, caminho_do_exe)."""
    try:
        import subprocess
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process cs2 -ErrorAction SilentlyContinue | Select-Object -First 1).Path"],
            capture_output=True, text=True, timeout=20, **_hidden_kwargs())
        path = (r.stdout or "").strip()
        if path and os.path.isfile(path):
            return True, path
    except Exception:
        pass
    try:
        import subprocess
        r = subprocess.run('tasklist /FI "IMAGENAME eq cs2.exe" /FO CSV /NH',
                           shell=True, capture_output=True, text=True,
                           timeout=20, **_hidden_kwargs())
        if '"cs2.exe"' in (r.stdout or "").lower():
            return True, ""
    except Exception:
        pass
    return False, ""


def kill_cs2():
    """Mata o processo cs2.exe preso (quando ja fechaste o jogo mas ele ficou pendurado)."""
    try:
        import subprocess
        import time
        subprocess.run('taskkill /F /IM cs2.exe', shell=True, capture_output=True,
                       timeout=30, **_hidden_kwargs())
        time.sleep(2)
        running, _ = cs2_running()
        if running:
            return {"success": False,
                    "output": "cs2.exe continua vivo. Reinicia o Steam/PC."}
        return {"success": True, "output": "✔ CS2 fechado a forca. Ja podes aplicar."}
    except Exception as e:
        return {"success": False, "output": str(e)}


def _info_from_base(base):
    cfg_dir = os.path.join(base, "game", "csgo", "cfg")
    if not os.path.isdir(cfg_dir):
        return {}
    vids = []
    for lib in steam_libraries():
        for ud in glob.glob(os.path.join(lib, "userdata", "*", "730", "local", "cfg", "cs2_video.txt")):
            if ud not in vids:
                vids.append(ud)
    return {"base": base, "cfg_dir": cfg_dir,
            "autoexec": os.path.join(cfg_dir, "autoexec.cfg"),
            "video_candidates": vids}


def find_steam():
    return steam_roots()

def find_cs2():
    """Deteccao robusta: pasta manual > manifest 730 > comuns > processo."""
    custom = get_custom_cs2()
    if custom:
        info = _info_from_base(custom)
        if info:
            info["source"] = "manual"
            return info
    # 1. appmanifest_730.acf = prova de instalacao
    for lib in steam_libraries():
        man = os.path.join(lib, "steamapps", "appmanifest_730.acf")
        base = os.path.join(lib, "steamapps", "common", "Counter-Strike Global Offensive")
        if os.path.isfile(man) or os.path.isdir(os.path.join(base, "game", "csgo", "cfg")):
            info = _info_from_base(base)
            if info:
                info["source"] = "steam"
                return info
    # 2. processo a correr revela a pasta
    running, path = cs2_running()
    if running and path:
        low = path.lower()
        i = low.find("counter-strike global offensive")
        if i > 0:
            base = path[:i + len("Counter-Strike Global Offensive")]
            info = _info_from_base(base)
            if info:
                info["source"] = "processo"
                return info
    # 3. caminhos diretos
    for p in [r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive",
              r"C:\Program Files\Steam\steamapps\common\Counter-Strike Global Offensive",
              r"D:\Steam\steamapps\common\Counter-Strike Global Offensive",
              r"E:\Steam\steamapps\common\Counter-Strike Global Offensive",
              r"F:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive"]:
        info = _info_from_base(p)
        if info:
            info["source"] = "comum"
            return info
    running, path = cs2_running()
    return {"running": running, "process_path": path}


def pick_cs2_folder():
    """O utilizador aponta a pasta do CS2. Fica guardada para sempre."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(
            title="Escolhe 'Counter-Strike Global Offensive' (steamapps/common)")
        root.destroy()
        if not folder:
            return {"success": False, "output": "Cancelado."}
        folder = os.path.normpath(folder)
        info = _info_from_base(folder)
        if not info and os.path.basename(folder).lower() == "cfg" and \
                os.path.isfile(os.path.join(folder, "config.cfg")):
            base = os.path.dirname(os.path.dirname(os.path.dirname(folder)))
            info = _info_from_base(base)
        if not info:
            return {"success": False,
                    "output": "Pasta invalida: escolhe 'Counter-Strike Global Offensive'."}
        set_custom_cs2(info["base"])
        return {"success": True, "output": f"✔ CS2 fixado em {info['base']}", "info": info}
    except Exception as e:
        return {"success": False, "output": str(e)}


def _ensure_exec(cfg_dir, target):
    """Garante 'exec <target>' no autoexec SEM apagar o do utilizador."""
    autoexec = os.path.join(cfg_dir, "autoexec.cfg")
    line = f"exec {target}"
    cur = ""
    if os.path.isfile(autoexec):
        backup_file(autoexec)
        cur = open(autoexec, encoding="utf-8", errors="ignore").read()
        if re.search(rf"^\s*{re.escape(line)}\s*$", cur, re.MULTILINE):
            return False, "autoexec ja chama " + target
    with open(autoexec, "a", encoding="utf-8") as f:
        if cur and not cur.endswith("\n"):
            f.write("\n")
        f.write(f"\n// Midnight Optimizer\n{line}\n")
    check = open(autoexec, encoding="utf-8", errors="ignore").read()
    if line not in check:
        raise IOError("autoexec nao aceitou a linha exec")
    return True, f"autoexec ligado a {target}"

CS2_LAUNCH_COMPETITIVE = "-novid -tickrate 128 -high -threads 8 +fps_max 0 +cl_showfps 1 -nojoy -nosteamcontroller -noht"

CS2_AUTOEXEC = """// Midnight Optimizer — CS2 Competitivo (FPS máximo + visibilidade)
// Gerado automaticamente. Backup em autoexec.cfg.midnight_backup
fps_max 0
fps_max_ui 144
cl_showfps 1
rate 786432
cl_cmdrate 128
cl_updaterate 128
cl_interp 0
cl_interp_ratio 1
cl_lagcompensation 1
cl_predict 1
engine_low_latency_sleep_after_client_tick true
fps_report_missing 0
r_dynamic 0
r_drawtracers_firstperson 0
muzzle_flash_scale 0
cl_ragdoll_physics_enable 0
cl_phys_enable 0
violence_hblood 0
host_writeconfig
echo "MIDNIGHT CS2 COMPETITIVO ATIVO"
"""

CS2_COMPETITIVE_CFG = """// Midnight Optimizer — CS2 Competitivo (ficheiro proprio, nao mexe no teu autoexec)
fps_max 0
fps_max_ui 144
cl_showfps 1
rate 786432
cl_cmdrate 128
cl_updaterate 128
cl_interp 0
cl_interp_ratio 1
cl_lagcompensation 1
cl_predict 1
engine_low_latency_sleep_after_client_tick true
fps_report_missing 0
r_dynamic 0
r_drawtracers_firstperson 0
muzzle_flash_scale 0
cl_ragdoll_physics_enable 0
cl_phys_enable 0
violence_hblood 0
host_writeconfig
echo "MIDNIGHT CS2 COMPETITIVO ATIVO"
"""

def apply_cs2_competitive():
    running, _ = cs2_running()
    if running:
        return {"success": False,
                "output": "⛔ Fecha o CS2 primeiro! O jogo apaga mudancas feitas com ele aberto."}
    info = find_cs2()
    if not info or not info.get("cfg_dir"):
        return {"success": False,
                "output": "CS2 nao detetado. Prime 'Escolher pasta do CS2' e aponta para o jogo."}
    logs = []
    cfg_dir = info["cfg_dir"]
    # 1. ficheiro proprio (nunca apaga o teu autoexec)
    target = os.path.join(cfg_dir, "midnight_competitive.cfg")
    backup_file(target)
    try:
        with open(target, "w", encoding="utf-8") as f:
            f.write(CS2_COMPETITIVE_CFG)
        back = open(target, encoding="utf-8").read()
        if "MIDNIGHT CS2 COMPETITIVO" not in back:
            raise IOError("verificacao de escrita falhou")
        logs.append(f"✔ midnight_competitive.cfg escrito e verificado")
    except Exception as e:
        return {"success": False, "output": f"Falha a escrever cfg: {e}"}
    # 2. liga no autoexec sem apagar nada
    try:
        _, detail = _ensure_exec(cfg_dir, "midnight_competitive")
        logs.append(f"✔ {detail}")
    except Exception as e:
        return {"success": False, "output": f"Falha no autoexec (o teu ficou intacto): {e}"}
    # 3. video low em todos os cs2_video.txt encontrados
    for v in info.get("video_candidates", []):
        try:
            backup_file(v)
            txt = open(v, encoding="utf-8", errors="ignore").read()
            txt = re.sub(r'"setting\.cpu_level"\s+"[^"]*"', '"setting.cpu_level"  "0"', txt)
            txt = re.sub(r'"setting\.gpu_level"\s+"[^"]*"', '"setting.gpu_level"  "0"', txt)
            txt = re.sub(r'"setting\.mem_level"\s+"[^"]*"', '"setting.mem_level"  "0"', txt)
            txt = re.sub(r'"setting\.mat_antialias"\s+"[^"]*"', '"setting.mat_antialias"  "0"', txt)
            open(v, "w", encoding="utf-8").write(txt)
            logs.append(f"✔ video low aplicado ({os.path.basename(os.path.dirname(os.path.dirname(v)))})")
        except Exception as e:
            logs.append(f"✘ video: {e}")
    if not info.get("video_candidates"):
        logs.append("ⓘ cs2_video.txt nao encontrado (abre o jogo uma vez p/ o gerar)")
    logs.append(f"ⓘ Pasta usada: {info['base']}")
    logs.append(f"ⓘ Launch Options (colar no Steam → CS2 → Propriedades): {CS2_LAUNCH_COMPETITIVE}")
    return {"success": True, "output": "\n".join(logs), "launch": CS2_LAUNCH_COMPETITIVE, "info": info}

def restore_cs2():
    info = find_cs2()
    if not info or not info.get("cfg_dir"):
        return {"success": False, "output": "CS2 nao detetado."}
    out = []
    # remove os nossos ficheiros, restaura os backups
    for fn in ["midnight_competitive.cfg", "midnight_pro.cfg"]:
        p = os.path.join(info["cfg_dir"], fn)
        try:
            if os.path.isfile(p):
                os.remove(p)
                out.append(f"Removido: {fn}")
        except Exception as e:
            out.append(f"✘ {fn}: {e}")
    out.append(restore_file(info["autoexec"])["output"])
    for v in info.get("video_candidates", []):
        out.append(restore_file(v)["output"])
    return {"success": True, "output": "\n".join(out)}

# ---------------- WOW ----------------
def find_wow():
    cands = [
        r"C:\Program Files (x86)\World of Warcraft",
        r"C:\Program Files\World of Warcraft",
        r"D:\World of Warcraft",
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Battle.net"),
    ]
    # Battle.net config pode ter o caminho
    try:
        bnet = os.path.join(os.environ.get("APPDATA", ""), "Battle.net", "Battle.net.config")
        if os.path.isfile(bnet):
            txt = open(bnet, encoding="utf-8", errors="ignore").read()
            for m in re.finditer(r"[A-Z]:\\\\[^\"\\\\]*(?:\\\\[^\"\\\\]*)*Warcraft[^\"\\\\]*", txt):
                p = m.group(0).replace("\\\\", "\\")
                if os.path.isdir(p):
                    cands.append(p)
    except Exception:
        pass
    for p in list(cands):
        if p and os.path.isdir(p):
            # _retail_ é o Midnight/The War Within
            for sub in ["_retail_", "_classic_", ""]:
                cfg = os.path.join(p, sub, "WTF", "Config.wtf") if sub else os.path.join(p, "WTF", "Config.wtf")
                if os.path.isfile(cfg):
                    return {"base": p, "flavor": sub or "root", "config": cfg}
            # devolve base mesmo sem config (primeira run)
            if "_retail_" in os.listdir(p):
                return {"base": p, "flavor": "_retail_", "config": os.path.join(p, "_retail_", "WTF", "Config.wtf")}
    # procura discos
    for d in ["C:", "D:", "E:"]:
        for q in [f"{d}\\World of Warcraft\\_retail_\\WTF\\Config.wtf",
                  f"{d}\\Program Files (x86)\\World of Warcraft\\_retail_\\WTF\\Config.wtf"]:
            if os.path.isfile(q):
                return {"base": os.path.dirname(os.path.dirname(os.path.dirname(q))), "flavor": "_retail_", "config": q}
    return {}

WOW_COMPETITIVE = {
    # Raid/M+ FPS máximo, ainda bonito o suficiente
    "graphicsQuality": "1",
    "raidGraphicsQuality": "1",
    "shadowMode": "0",
    "shadowTextureSize": "512",
    "liquidDetail": "0",
    "sunShafts": "0",
    "SSAO": "0",
    "depthEffects": "0",
    "particleDensity": "10",
    "spellDensity": "10",
    "projectedTextures": "0",
    "MSAA": "0",
    "textureFilteringMode": "0",
    "terrainLodDist": "300",
    "wmoLodDist": "300",
    "entityLodDist": "5",
    "maxFPS": "200",
    "maxFPSBk": "60",
    "GxApi": "D3D12",
}

WOW_BALANCED = {
    "graphicsQuality": "4",
    "raidGraphicsQuality": "3",
    "shadowMode": "1",
    "liquidDetail": "1",
    "sunShafts": "1",
    "SSAO": "1",
    "particleDensity": "50",
    "maxFPS": "144",
    "maxFPSBk": "60",
}

def apply_wow(mode="competitive"):
    info = find_wow()
    if not info or not info.get("config"):
        base = (info or {}).get("base")
        if base:
            return {"success": False, "output": f"WoW encontrado em {base} mas Config.wtf ainda não existe. Abre o jogo uma vez e volta aqui."}
        return {"success": False, "output": "WoW não detetado. Abre o jogo uma vez ou escolhe a pasta manualmente."}
    cfg = info["config"]
    if not os.path.isfile(cfg):
        return {"success": False, "output": f"Abre o WoW uma vez para gerar o Config.wtf ({cfg})."}
    backup_file(cfg)
    try:
        txt = open(cfg, encoding="utf-8", errors="ignore").read()
        vals = WOW_COMPETITIVE if mode == "competitive" else WOW_BALANCED
        for k, v in vals.items():
            txt = set_wtf_value(txt, k, v)
        open(cfg, "w", encoding="utf-8").write(txt)
        n = len(vals)
        return {"success": True, "output": f"✔ WoW {mode} aplicado ({n} cvars em {cfg}). Backup guardado.", "info": info}
    except Exception as e:
        return {"success": False, "output": str(e)}

def restore_wow():
    info = find_wow()
    if not info or not info.get("config"):
        return {"success": False, "output": "WoW não detetado."}
    return restore_file(info["config"])
