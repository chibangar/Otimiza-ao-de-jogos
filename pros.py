"""Base de dados de pros CS2 + apply com 1 clique.
Fontes: ProSettings.net / setup.gg / csdb.gg (set 2026).
Fotos em assets/pros/<id>.png
"""
import os
import re

import game_tweaks

# id, nome, nome real, equipa, pais, role, foto
PROS = [
    {
        "id": "donk", "name": "donk", "real": "Danil Kryshkovets",
        "team": "Team Spirit", "country": "RU", "role": "Rifler",
        "photo": "assets/pros/donk.png",
        "dpi": 800, "sens": 1.25, "zoom": 1.0, "hz": 1000,
        "res": "1280x960", "aspect": "4:3 Stretched",
        "cross": {"length": 1, "thick": 1.5, "gap": -4, "dot": 0,
                  "color": 5, "r": 0, "g": 255, "b": 165, "alpha": 255},
        "vm": {"fov": 68, "x": 2.5, "y": 0, "z": -1.5, "preset": 2},
        "bob": {"lower": 5, "lat": 0.33, "vert": 0.14, "cycle": 0.98},
        "fps": 600, "radar": 0.7, "launch": "",
        "video": {"w": 1280, "h": 960, "aspect": 0, "msaa": "8", "aniso": "0"},
    },
    {
        "id": "monesy", "name": "m0NESY", "real": "Ilya Osipov",
        "team": "Falcons", "country": "RU", "role": "AWPer",
        "photo": "assets/pros/monesy.png",
        "dpi": 400, "sens": 2.3, "zoom": 1.0, "hz": 2000,
        "res": "1280x960", "aspect": "4:3 Stretched",
        "cross": {"length": 1, "thick": 1, "gap": -4, "dot": 0,
                  "color": 4, "r": 0, "g": 255, "b": 255, "alpha": 255},
        "vm": {"fov": 68, "x": 2.5, "y": 0, "z": -1.5, "preset": 3},
        "bob": {"lower": 5, "lat": 0.33, "vert": 0.14, "cycle": 0.98},
        "fps": 999, "radar": 0.91, "launch": "",
        "video": {"w": 1280, "h": 960, "aspect": 0, "msaa": "8", "aniso": "0"},
    },
    {
        "id": "zywoo", "name": "ZywOo", "real": "Mathieu Herbaut",
        "team": "Vitality", "country": "FR", "role": "AWPer",
        "photo": "assets/pros/zywoo.png",
        "dpi": 400, "sens": 1.9, "zoom": 1.0, "hz": 1000,
        "res": "1280x960", "aspect": "4:3 Stretched",
        "cross": {"length": 2, "thick": 0, "gap": -3, "dot": 0,
                  "color": 1, "r": 0, "g": 255, "b": 0, "alpha": 255},
        "vm": {"fov": 68, "x": 2.5, "y": 0, "z": -1.5, "preset": 1},
        "bob": {"lower": 5, "lat": 0.4, "vert": 0.25, "cycle": 0.98},
        "fps": 400, "radar": 0.4,
        "launch": "-novid -tickrate 128 -allow_third_party_software",
        "video": {"w": 1280, "h": 960, "aspect": 0, "msaa": "4", "aniso": "4"},
    },
    {
        "id": "s1mple", "name": "s1mple", "real": "Oleksandr Kostyliev",
        "team": "BC.Game", "country": "UA", "role": "AWPer",
        "photo": "assets/pros/s1mple.png",
        "dpi": 400, "sens": 3.09, "zoom": 1.0, "hz": 1000,
        "res": "1280x960", "aspect": "4:3 Stretched",
        "cross": {"length": 1, "thick": 1, "gap": -4, "dot": 0,
                  "color": 4, "r": 0, "g": 255, "b": 255, "alpha": 200},
        "vm": {"fov": 68, "x": 2.5, "y": 0, "z": -1.5, "preset": 2},
        "bob": {"lower": 21, "lat": 0.33, "vert": 0.14, "cycle": 0.98},
        "fps": 0, "radar": 0.45,
        "launch": "-freq 360 -novid -console +fps_max 999",
        "video": {"w": 1280, "h": 960, "aspect": 0, "msaa": "8", "aniso": "0"},
    },
    {
        "id": "niko", "name": "NiKo", "real": "Nikola Kovac",
        "team": "Falcons", "country": "BA", "role": "Rifler",
        "photo": "assets/pros/niko.png",
        "dpi": 800, "sens": 0.815, "zoom": 0.9, "hz": 2000,
        "res": "1280x960", "aspect": "4:3 Stretched",
        "cross": {"length": 0, "thick": 2, "gap": -4, "dot": 1,
                  "color": 5, "r": 0, "g": 255, "b": 145, "alpha": 255},
        "vm": {"fov": 68, "x": 2.5, "y": 0, "z": -1.5, "preset": 2},
        "bob": {"lower": 15, "lat": 0.33, "vert": 0.14, "cycle": 0.98},
        "fps": 400, "radar": 0.35, "launch": "",
        "video": {"w": 1280, "h": 960, "aspect": 0, "msaa": "8", "aniso": "1"},
    },
    {
        "id": "ropz", "name": "ropz", "real": "Robin Kool",
        "team": "Vitality", "country": "EE", "role": "Rifler",
        "photo": "assets/pros/ropz.png",
        "dpi": 400, "sens": 1.77, "zoom": 1.0, "hz": 2000,
        "res": "1920x1080", "aspect": "16:9 Nativa",
        "cross": {"length": 2, "thick": 0.5, "gap": -3, "dot": 0,
                  "color": 1, "r": 0, "g": 255, "b": 0, "alpha": 255},
        "vm": {"fov": 68, "x": 2.5, "y": 0, "z": -1.5, "preset": 2},
        "bob": {"lower": 5, "lat": 0.1, "vert": 0.1, "cycle": 0.98},
        "fps": 999, "radar": 0.65, "launch": "",
        "video": {"w": 1920, "h": 1080, "aspect": 1, "msaa": "2", "aniso": "0"},
    },
]

BY_ID = {p["id"]: p for p in PROS}


def list_pros():
    out = []
    for p in PROS:
        out.append({
            "id": p["id"], "name": p["name"], "real": p["real"],
            "team": p["team"], "country": p["country"], "role": p["role"],
            "photo": p["photo"], "dpi": p["dpi"], "sens": p["sens"],
            "edpi": round(p["dpi"] * p["sens"]),
            "res": p["res"], "aspect": p["aspect"],
        })
    return out


def build_pro_cfg(p):
    c = p["cross"]
    v = p["vm"]
    b = p["bob"]
    lines = [
        f"// Midnight Optimizer — config de {p['name']} ({p['team']})",
        "// Sensibilidade: ajusta ao teu DPI para igualar o eDPI do pro",
        f"sensitivity \"{p['sens']}\"",
        f"zoom_sensitivity_ratio \"{p['zoom']}\"",
        "m_rawinput 1",
        "",
        "// Mira",
        "cl_crosshairstyle 4",
        f"cl_crosshairsize {c['length']}",
        f"cl_crosshairthickness {c['thick']}",
        f"cl_crosshairgap {c['gap']}",
        f"cl_crosshairdot {c['dot']}",
        "cl_crosshair_drawoutline 0",
        f"cl_crosshaircolor {c['color']}",
        f"cl_crosshaircolor_r {c['r']}",
        f"cl_crosshaircolor_g {c['g']}",
        f"cl_crosshaircolor_b {c['b']}",
        "cl_crosshairusealpha 1",
        f"cl_crosshairalpha {c['alpha']}",
        "cl_crosshair_t 0",
        "",
        "// Viewmodel",
        f"viewmodel_fov {v['fov']}",
        f"viewmodel_offset_x {v['x']}",
        f"viewmodel_offset_y {v['y']}",
        f"viewmodel_offset_z {v['z']}",
        f"viewmodel_presetpos {v['preset']}",
        "cl_usenewbob 0",
        f"cl_bob_lower_amt {b['lower']}",
        f"cl_bobamt_lat {b['lat']}",
        f"cl_bobamt_vert {b['vert']}",
        f"cl_bobcycle {b['cycle']}",
        "",
        "// Rede + FPS",
        "rate 786432",
        "cl_cmdrate 128",
        "cl_updaterate 128",
        "cl_interp 0",
        "cl_interp_ratio 1",
        f"fps_max {p['fps']}",
        "cl_showfps 1",
        f"cl_hud_radar_scale {p['radar']}",
        "",
        "host_writeconfig",
        f"echo \"MIDNIGHT: config de {p['name']} aplicada\"",
    ]
    return "\n".join(lines) + "\n"


def apply_pro(pro_id):
    p = BY_ID.get(pro_id)
    if not p:
        return {"success": False, "output": "Pro desconhecido."}
    info = game_tweaks.find_cs2()
    if not info:
        return {"success": False,
                "output": "CS2 nao detetado. Abre o jogo uma vez no Steam e volta aqui."}
    logs = []
    cfg_dir = info["cfg_dir"]

    # 1. midnight_pro.cfg com tudo do pro
    pro_cfg = os.path.join(cfg_dir, "midnight_pro.cfg")
    game_tweaks.backup_file(pro_cfg)
    try:
        with open(pro_cfg, "w", encoding="utf-8") as f:
            f.write(build_pro_cfg(p))
        logs.append(f"✔ midnight_pro.cfg ({p['name']})")
    except Exception as e:
        return {"success": False, "output": f"Falha a escrever cfg: {e}"}

    # 2. autoexec executa o ficheiro do pro
    autoexec = info["autoexec"]
    game_tweaks.backup_file(autoexec)
    try:
        cur = ""
        if os.path.isfile(autoexec):
            cur = open(autoexec, encoding="utf-8", errors="ignore").read()
        if "midnight_pro" not in cur:
            with open(autoexec, "a", encoding="utf-8") as f:
                if cur and not cur.endswith("\n"):
                    f.write("\n")
                f.write("exec midnight_pro\n")
        logs.append("✔ autoexec ligado ao pro")
    except Exception as e:
        logs.append(f"✘ autoexec: {e}")

    # 3. video: resolucao + MSAA + aniso do pro
    v = p["video"]
    for vid in info.get("video_candidates", []):
        try:
            game_tweaks.backup_file(vid)
            txt = open(vid, encoding="utf-8", errors="ignore").read()
            txt = re.sub(r'"setting\.defaultres"\s+"[^"]*"',
                         f"\"setting.defaultres\"\t\t\"{v['w']}\"", txt)
            txt = re.sub(r'"setting\.defaultresheight"\s+"[^"]*"',
                         f"\"setting.defaultresheight\"\t\t\"{v['h']}\"", txt)
            txt = re.sub(r'"setting\.aspectratiomode"\s+"[^"]*"',
                         f"\"setting.aspectratiomode\"\t\t\"{v['aspect']}\"", txt)
            txt = re.sub(r'"setting\.mat_antialias"\s+"[^"]*"',
                         f"\"setting.mat_antialias\"\t\t\"{v['msaa']}\"", txt)
            txt = re.sub(r'"setting\.mat_forceaniso"\s+"[^"]*"',
                         f"\"setting.mat_forceaniso\"\t\t\"{v['aniso']}\"", txt)
            open(vid, "w", encoding="utf-8").write(txt)
            logs.append(f"✔ video {v['w']}x{v['h']} aplicado")
        except Exception as e:
            logs.append(f"✘ video: {e}")

    if p["launch"]:
        logs.append(f"ⓘ Launch Options (colar no Steam): {p['launch']}")
    else:
        logs.append("ⓘ Este pro nao usa Launch Options.")
    logs.append(f"ⓘ DPI do pro: {p['dpi']} — ajusta o teu rato p/ eDPI {round(p['dpi']*p['sens'])}.")
    return {"success": True, "output": "\n".join(logs),
            "launch": p["launch"], "name": p["name"]}
