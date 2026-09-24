"""
Midnight Optimizer — Miras (Crosshairs) e Viewmodels dos Pros para CS2.
Substitui configs invasivas por códigos de partilha e comandos de consola (~)
prontos a copiar e colar sem estragar NENHUMA bind, sensibilidade ou vídeo do utilizador.
100% Não destrutivo e VAC-Safe.
"""
import os
import re
import game_tweaks
import overlay

# ---------- MIRAS DOS PROS (CROSSHAIRS) ----------
# Códigos de partilha oficiais do CS2 (Settings -> Crosshair -> Share/Import)
# Comandos diretos de consola (~) para colar com 1 clique
PRO_CROSSHAIRS = [
    {
        "id": "monesy",
        "name": "m0NESY",
        "real": "Ilya Osipov",
        "team": "Falcons",
        "country": "RU",
        "role": "AWPer",
        "photo": "assets/pros/monesy.png",
        "share_code": "CSGO-3u26R-VODmS-Pmn2a-Y26sR-a8W7B",
        "console_cmd": "cl_crosshairstyle 4; cl_crosshairsize 1; cl_crosshairthickness 1; cl_crosshairgap -4; cl_crosshairdot 0; cl_crosshair_drawoutline 0; cl_crosshaircolor 4; cl_crosshaircolor_r 0; cl_crosshaircolor_g 255; cl_crosshaircolor_b 255; cl_crosshairusealpha 1; cl_crosshairalpha 255",
        "color_hex": "#00ffff",
        "desc": "Mira cyan compacta e precisa de m0NESY, referência mundial de rapidez e precisão com AWP e Deagle.",
        "params": {"size": 1, "thick": 1, "gap": -4, "dot": 0, "outline": 0, "color": "Cyan (#00ffff)"}
    },
    {
        "id": "donk",
        "name": "donk",
        "real": "Danil Kryshkovets",
        "team": "Team Spirit",
        "country": "RU",
        "role": "Rifler",
        "photo": "assets/pros/donk.png",
        "share_code": "CSGO-HRxqT-U3L2S-x9sP7-U22pU-F2aJD",
        "console_cmd": "cl_crosshairstyle 4; cl_crosshairsize 1; cl_crosshairthickness 1.5; cl_crosshairgap -4; cl_crosshairdot 0; cl_crosshair_drawoutline 0; cl_crosshaircolor 5; cl_crosshaircolor_r 0; cl_crosshaircolor_g 255; cl_crosshaircolor_b 165; cl_crosshairusealpha 1; cl_crosshairalpha 255",
        "color_hex": "#00ffa5",
        "desc": "Mira verde-menta ultracompacta com espessura 1.5, desenhada para spray transfer e agressividade pura de rifle.",
        "params": {"size": 1, "thick": 1.5, "gap": -4, "dot": 0, "outline": 0, "color": "Mint Green (#00ffa5)"}
    },
    {
        "id": "niko",
        "name": "NiKo",
        "real": "Nikola Kovač",
        "team": "Falcons",
        "country": "BA",
        "role": "Rifler",
        "photo": "assets/pros/niko.png",
        "share_code": "CSGO-XbaqV-3wASz-ip4tB-u4Gmu-nqcjC",
        "console_cmd": "cl_crosshairstyle 4; cl_crosshairsize 1; cl_crosshairthickness 1; cl_crosshairgap -4; cl_crosshairdot 0; cl_crosshair_drawoutline 0; cl_crosshaircolor 5; cl_crosshaircolor_r 0; cl_crosshaircolor_g 255; cl_crosshaircolor_b 145; cl_crosshairusealpha 1; cl_crosshairalpha 255",
        "color_hex": "#00ff91",
        "desc": "A retícula estática do maior rifler da história do CS, calibrada para headshots de um único tiro de AK-47.",
        "params": {"size": 1, "thick": 1, "gap": -4, "dot": 0, "outline": 0, "color": "Verde Esmeralda"}
    },
    {
        "id": "zywoo",
        "name": "ZywOo",
        "real": "Mathieu Herbaut",
        "team": "Vitality",
        "country": "FR",
        "role": "AWPer",
        "photo": "assets/pros/zywoo.png",
        "share_code": "CSGO-UmDxN-AZUpO-u4WCH-HQmu3-RERuF",
        "console_cmd": "cl_crosshairstyle 4; cl_crosshairsize 2; cl_crosshairthickness 0; cl_crosshairgap -3; cl_crosshairdot 0; cl_crosshair_drawoutline 0; cl_crosshaircolor 1; cl_crosshaircolor_r 0; cl_crosshaircolor_g 255; cl_crosshaircolor_b 0; cl_crosshairusealpha 1; cl_crosshairalpha 255",
        "color_hex": "#00ff00",
        "desc": "Mira verde clássica fina e limpa de ZywOo, ideal para alinhamento rápido em duelos de longa distância.",
        "params": {"size": 2, "thick": 0, "gap": -3, "dot": 0, "outline": 0, "color": "Verde Puro (#00ff00)"}
    },
    {
        "id": "s1mple",
        "name": "s1mple",
        "real": "Oleksandr Kostyliev",
        "team": "BC.Game",
        "country": "UA",
        "role": "AWPer",
        "photo": "assets/pros/s1mple.png",
        "share_code": "CSGO-UwHA2-rLBD3-qDws7-svzyC-yeoKG",
        "console_cmd": "cl_crosshairstyle 4; cl_crosshairsize 1; cl_crosshairthickness 1; cl_crosshairgap -4; cl_crosshairdot 0; cl_crosshair_drawoutline 0; cl_crosshaircolor 4; cl_crosshaircolor_r 0; cl_crosshaircolor_g 255; cl_crosshaircolor_b 255; cl_crosshairusealpha 1; cl_crosshairalpha 200",
        "color_hex": "#00e5ff",
        "desc": "Retícula estática do s1mple com ligeira transparência (alpha 200) para máxima perceção periférica do alvo.",
        "params": {"size": 1, "thick": 1, "gap": -4, "dot": 0, "outline": 0, "color": "Cyan Translúcido"}
    },
    {
        "id": "ropz",
        "name": "ropz",
        "real": "Robin Kool",
        "team": "Vitality",
        "country": "EE",
        "role": "Rifler",
        "photo": "assets/pros/ropz.png",
        "share_code": "CSGO-HnhrC-TaH2q-vV2mt-xkJvY-XwP5F",
        "console_cmd": "cl_crosshairstyle 4; cl_crosshairsize 2; cl_crosshairthickness 0.5; cl_crosshairgap -3; cl_crosshairdot 0; cl_crosshair_drawoutline 0; cl_crosshaircolor 1; cl_crosshaircolor_r 0; cl_crosshaircolor_g 255; cl_crosshaircolor_b 0; cl_crosshairusealpha 1; cl_crosshairalpha 255",
        "color_hex": "#00ff00",
        "desc": "Ajustada com espessura 0.5 para ecrãs 1080p, oferecendo traços finos para lurkers e duelos cirúrgicos.",
        "params": {"size": 2, "thick": 0.5, "gap": -3, "dot": 0, "outline": 0, "color": "Verde Suave"}
    },
    {
        "id": "fallen",
        "name": "FalleN",
        "real": "Gabriel Toledo",
        "team": "FURIA",
        "country": "BR",
        "role": "AWPer",
        "photo": "assets/pros/fallen.png",
        "share_code": "CSGO-A6zRA-7Uf47-kU6Yq-6YQ5z-9H9mE",
        "console_cmd": "cl_crosshairstyle 4; cl_crosshairsize 2; cl_crosshairthickness 1; cl_crosshairgap -6; cl_crosshairdot 0; cl_crosshair_drawoutline 0; cl_crosshaircolor 2; cl_crosshaircolor_r 255; cl_crosshaircolor_g 255; cl_crosshaircolor_b 0; cl_crosshairusealpha 1; cl_crosshairalpha 255",
        "color_hex": "#ffff00",
        "desc": "Mira amarela de alto contraste do Professor FalleN, visível em todas as zonas escuras ou claras dos mapas.",
        "params": {"size": 2, "thick": 1, "gap": -6, "dot": 0, "outline": 0, "color": "Amarelo (#ffff00)"}
    },
]

BY_CROSSHAIR_ID = {c["id"]: c for c in PRO_CROSSHAIRS}


# ---------- VIEWMODELS DOS PROS (POSICIONAMENTO DA ARMA) ----------
# Imagens SVG demonstrativas em assets/viewmodels/<id>.svg
# Comandos de consola diretos (~) para posicionar a arma no CS2
VIEWMODEL_PRESETS = [
    {
        "id": "classic_pro",
        "name": "Clássico Competitivo Pro",
        "tag": "Mais Usado (m0NESY & NiKo)",
        "desc": "Arma rebaixada à direita com FOV 68. O padrão dos profissionais: liberta o centro do ecrã para uma linha de mira perfeitamente limpa sem perder a referência do cano.",
        "image": "assets/viewmodels/classic_pro.svg",
        "fov": 68, "x": 2.5, "y": 0, "z": -1.5, "preset": 2,
        "console_cmd": "viewmodel_fov 68; viewmodel_offset_x 2.5; viewmodel_offset_y 0; viewmodel_offset_z -1.5; viewmodel_presetpos 2",
    },
    {
        "id": "compact_recessed",
        "name": "Compacto & Recuado",
        "tag": "Máxima Visão (FalleN / s1mple)",
        "desc": "Arma recuada e encostada ao canto inferior direito (z=-2). Reduz o volume aparente da arma no ecrã para não esconder nenhum inimigo que entre pelos flancos.",
        "image": "assets/viewmodels/compact_recessed.svg",
        "fov": 68, "x": 2.5, "y": 2, "z": -2, "preset": 0,
        "console_cmd": "viewmodel_fov 68; viewmodel_offset_x 2.5; viewmodel_offset_y 2; viewmodel_offset_z -2; viewmodel_presetpos 0",
    },
    {
        "id": "max_fov",
        "name": "FOV Máximo / AWP Estendido",
        "tag": "Estilo Snipers (ZywOo & donk)",
        "desc": "Arma projetada para a frente exibindo as mãos e o cano completo. Proporciona excelente sensação de recoil e alinhamento tático com rifles e AWP.",
        "image": "assets/viewmodels/max_fov.svg",
        "fov": 68, "x": 2.5, "y": 2, "z": -1, "preset": 3,
        "console_cmd": "viewmodel_fov 68; viewmodel_offset_x 2.5; viewmodel_offset_y 2; viewmodel_offset_z -1; viewmodel_presetpos 3",
    },
    {
        "id": "centered_doom",
        "name": "Centrado / Doom Simétrico",
        "tag": "Estilo Retro / Quake",
        "desc": "Arma posicionada na base central do ecrã. Ideal para jogadores que preferem simetria absoluta e foco direto no eixo vertical de mira.",
        "image": "assets/viewmodels/centered_doom.svg",
        "fov": 68, "x": -2, "y": 2, "z": -2, "preset": 0,
        "console_cmd": "viewmodel_fov 68; viewmodel_offset_x -2; viewmodel_offset_y 2; viewmodel_offset_z -2; viewmodel_presetpos 0",
    },
    {
        "id": "valve_default",
        "name": "Padrão Oficial CS2 (Desktop)",
        "tag": "Fábrica Valve",
        "desc": "Posicionamento padrão de fábrica da Valve (FOV 60, offset 1, 1, -1). Recomendado para quem prefere a estética original do jogo.",
        "image": "assets/viewmodels/valve_default.svg",
        "fov": 60, "x": 1, "y": 1, "z": -1, "preset": 1,
        "console_cmd": "viewmodel_fov 60; viewmodel_offset_x 1; viewmodel_offset_y 1; viewmodel_offset_z -1; viewmodel_presetpos 1",
    },
    {
        "id": "minimalist_low",
        "name": "Minimalista Ultra Baixo",
        "tag": "Anti-Distração",
        "desc": "A arma quase desaparece da visão durante o movimento, proporcionando a menor área obstruída possível em combates caóticos.",
        "image": "assets/viewmodels/minimalist_low.svg",
        "fov": 68, "x": 2.5, "y": -2, "z": -2, "preset": 0,
        "console_cmd": "viewmodel_fov 68; viewmodel_offset_x 2.5; viewmodel_offset_y -2; viewmodel_offset_z -2; viewmodel_presetpos 0",
    }
]

BY_VIEWMODEL_ID = {v["id"]: v for v in VIEWMODEL_PRESETS}


# ---------- MÉTODOS PÚBLICOS SEGUROS ----------

def list_crosshairs():
    """Lista todas as miras dos pros com código de partilha e comando de consola."""
    return PRO_CROSSHAIRS


def list_viewmodels():
    """Lista todos os posicionamentos de arma (viewmodels) com imagem e comandos."""
    return VIEWMODEL_PRESETS


def list_pros():
    """
    Mantido para compatibilidade da API existente, mas agora devolve dados
    focados exclusivamente em Miras e Viewmodels não destrutivos.
    """
    out = []
    for c in PRO_CROSSHAIRS:
        out.append({
            "id": c["id"],
            "name": c["name"],
            "real": c["real"],
            "team": c["team"],
            "country": c["country"],
            "role": c["role"],
            "photo": c["photo"],
            "share_code": c["share_code"],
            "console_cmd": c["console_cmd"],
            "color_hex": c["color_hex"],
            "desc": c["desc"],
            "params": c["params"],
        })
    return out


def apply_crosshair_safe(pro_id):
    """
    Aplica a mira do pro de forma 100% segura num ficheiro isolado (midnight_crosshair.cfg).
    NUNCA mexe em sensibilidade, binds, resolução ou definições de vídeo.
    """
    c = BY_CROSSHAIR_ID.get(pro_id)
    if not c:
        return {"success": False, "output": "Mira não encontrada."}

    info = game_tweaks.find_cs2()
    if not info or not info.get("cfg_dir"):
        return {
            "success": True,
            "output": f"Código de Partilha de {c['name']}: {c['share_code']}\nComando Consola: {c['console_cmd']}",
            "share_code": c["share_code"],
            "console_cmd": c["console_cmd"],
            "note": "CS2 não detetado no disco para guardar cfg automática, copia o código diretamente para o jogo!"
        }

    cfg_dir = info["cfg_dir"]
    target = os.path.join(cfg_dir, "midnight_crosshair.cfg")
    game_tweaks.backup_file(target)

    cmd_lines = c['console_cmd'].replace('; ', '\n')
    cfg_content = f"""// Midnight Optimizer — Mira de {c['name']} ({c['team']})
// 100% Seguro: Nao altera binds, sensibilidade ou resolucao
{cmd_lines}
host_writeconfig
echo "MIDNIGHT: Mira de {c['name']} Carregada"
"""
    try:
        with open(target, "w", encoding="utf-8") as f:
            f.write(cfg_content)
        # Liga ao autoexec sem apagar nada
        game_tweaks._ensure_exec(cfg_dir, "midnight_crosshair")
        
        # Dispara notificação no overlay in-game
        overlay.notify_process(
            title=f"Mira de {c['name']} Ativa",
            message=f"Código CS2: {c['share_code']}",
            badge="CS2 MIRA",
            theme="cyan"
        )
        return {
            "success": True,
            "output": f"✔ Mira de {c['name']} configurada em midnight_crosshair.cfg!\nCódigo CS2: {c['share_code']}\nPodes colar na consola: {c['console_cmd']}",
            "share_code": c["share_code"],
            "console_cmd": c["console_cmd"],
        }
    except Exception as e:
        return {"success": False, "output": f"Erro ao gravar cfg: {e}"}


def apply_viewmodel_safe(preset_id):
    """
    Aplica o posicionamento de arma (viewmodel) escolhido de forma 100% segura.
    Grava apenas em midnight_viewmodel.cfg e nunca altera binds ou sensibilidades.
    """
    v = BY_VIEWMODEL_ID.get(preset_id)
    if not v:
        return {"success": False, "output": "Preset de viewmodel não encontrado."}

    info = game_tweaks.find_cs2()
    if not info or not info.get("cfg_dir"):
        return {
            "success": True,
            "output": f"Comandos de Consola ({v['name']}):\n{v['console_cmd']}",
            "console_cmd": v["console_cmd"],
            "note": "CS2 não detetado no disco, copia e cola os comandos diretamente na consola (~)."
        }

    cfg_dir = info["cfg_dir"]
    target = os.path.join(cfg_dir, "midnight_viewmodel.cfg")
    game_tweaks.backup_file(target)

    vm_lines = v['console_cmd'].replace('; ', '\n')
    cfg_content = f"""// Midnight Optimizer — Viewmodel {v['name']}
// 100% Seguro: Nao mexe em binds, sensibilidade ou graficos
{vm_lines}
host_writeconfig
echo "MIDNIGHT: Viewmodel {v['name']} Carregado"
"""
    try:
        with open(target, "w", encoding="utf-8") as f:
            f.write(cfg_content)
        # Liga ao autoexec sem apagar nada
        game_tweaks._ensure_exec(cfg_dir, "midnight_viewmodel")

        # Dispara notificação no overlay in-game
        overlay.notify_process(
            title=f"Viewmodel {v['name']}",
            message="Posicionamento da arma aplicado com sucesso",
            badge="CS2 VIEWMOD",
            theme="gold"
        )
        return {
            "success": True,
            "output": f"✔ Viewmodel '{v['name']}' configurado em midnight_viewmodel.cfg!\nComandos: {v['console_cmd']}",
            "console_cmd": v["console_cmd"],
        }
    except Exception as e:
        return {"success": False, "output": f"Erro ao gravar cfg de viewmodel: {e}"}


# Aliases para compatibilidade de rotas antigas
def apply_pro(pro_id):
    """Encaminha para a aplicação segura de mira."""
    return apply_crosshair_safe(pro_id)
