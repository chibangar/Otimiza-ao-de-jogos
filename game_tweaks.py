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
def find_steam():
    cands = []
    for env in ["ProgramFiles(x86)", "ProgramW6432", "ProgramFiles"]:
        base = os.environ.get(env)
        if base:
            cands.append(os.path.join(base, "Steam"))
    cands += [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam", r"D:\Steam"]
    # libraryfolders.vdf pode apontar outras libs
    libs = set()
    for s in cands:
        if os.path.isdir(s):
            libs.add(s)
            vdf = os.path.join(s, "steamapps", "libraryfolders.vdf")
            if os.path.isfile(vdf):
                try:
                    txt = open(vdf, encoding="utf-8", errors="ignore").read()
                    for m in re.finditer(r'"path"\s+"([^"]+)"', txt):
                        p = m.group(1).replace("\\\\", "\\")
                        if os.path.isdir(p):
                            libs.add(p)
                except Exception:
                    pass
    return sorted(libs)

def find_cs2():
    """Devolve {base, cfg_dir, video_path, autoexec} ou {}."""
    for lib in find_steam():
        base = os.path.join(lib, "steamapps", "common", "Counter-Strike Global Offensive")
        cfg_dir = os.path.join(base, "game", "csgo", "cfg")
        if os.path.isdir(cfg_dir):
            # video: userdata/<id>/730/local/cfg/cs2_video.txt
            videos = glob.glob(os.path.join(lib, "..", "..", "*"))  # fallbacknoop
            vids = []
            for ud in glob.glob(os.path.join(lib, "..", "userdata", "*", "730", "local", "cfg", "cs2_video.txt")):
                vids.append(ud)
            for ud in glob.glob(r"C:\Program Files (x86)\Steam\userdata\*\730\local\cfg\cs2_video.txt"):
                if ud not in vids:
                    vids.append(ud)
            return {
                "base": base, "cfg_dir": cfg_dir,
                "autoexec": os.path.join(cfg_dir, "autoexec.cfg"),
                "video_candidates": vids,
            }
    # tenta caminho direto
    for p in [r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg",
              r"D:\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg"]:
        if os.path.isdir(p):
            return {"base": os.path.dirname(os.path.dirname(p)), "cfg_dir": p,
                    "autoexec": os.path.join(p, "autoexec.cfg"), "video_candidates": []}
    return {}

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

def apply_cs2_competitive():
    info = find_cs2()
    if not info:
        return {"success": False, "output": "CS2 não detetado. Abre o jogo uma vez no Steam ou escolhe a pasta manualmente."}
    logs = []
    autoexec = info["autoexec"]
    backup_file(autoexec)
    try:
        with open(autoexec, "w", encoding="utf-8") as f:
            f.write(CS2_AUTOEXEC)
        logs.append(f"✔ autoexec.cfg competitivo escrito ({autoexec})")
    except Exception as e:
        return {"success": False, "output": f"Falha a escrever autoexec: {e}"}
    # video low em todos os cs2_video.txt encontrados
    for v in info.get("video_candidates", []):
        try:
            backup_file(v)
            txt = open(v, encoding="utf-8", errors="ignore").read()
            # baixa tudo: cpu/gpu/mem level 0, msaa 0
            txt = re.sub(r'"setting\.cpu_level"\s+"[^"]*"', '"setting.cpu_level"  "0"', txt)
            txt = re.sub(r'"setting\.gpu_level"\s+"[^"]*"', '"setting.gpu_level"  "0"', txt)
            txt = re.sub(r'"setting\.mem_level"\s+"[^"]*"', '"setting.mem_level"  "0"', txt)
            txt = re.sub(r'"setting\.mat_antialias"\s+"[^"]*"', '"setting.mat_antialias"  "0"', txt)
            open(v, "w", encoding="utf-8").write(txt)
            logs.append(f"✔ vídeo low aplicado ({v})")
        except Exception as e:
            logs.append(f"✘ vídeo {v}: {e}")
    logs.append(f"ⓘ Launch Options (colar no Steam → CS2 → Propriedades): {CS2_LAUNCH_COMPETITIVE}")
    return {"success": True, "output": "\n".join(logs), "launch": CS2_LAUNCH_COMPETITIVE, "info": info}

def restore_cs2():
    info = find_cs2()
    if not info:
        return {"success": False, "output": "CS2 não detetado."}
    out = [restore_file(info["autoexec"])["output"]]
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
