# -*- coding: utf-8 -*-
"""
Motor de Importação de Sons do Voicemod para o Pulse Gaming Optimizer.
Suporta:
- Deteção automática das pastas do Voicemod V2/V3 (%LocalAppData%\\Voicemod\\memes)
- Descodificação de ficheiros .dat (que são áudios MP3/WAV/OGG nativos do Voicemod)
- Extração de nomes originais e metadados de bases de dados SQLite (memeSearch.db) e JSON
- Importação direta de pastas personalizadas de áudio
- Extração e importação de ficheiros de backup / arquivos comprimidos (.zip, .v2s, .vmsoundboard)
- Geração automática de ícones/badges para a interface do Soundboard
"""

import os
import re
import sys
import json
import shutil
import sqlite3
import zipfile
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_OK = True
except Exception:
    _PIL_OK = False

try:
    import miniaudio
    _MA_OK = True
except Exception:
    _MA_OK = False

import accounts


def get_standard_voicemod_dirs():
    """Devolve lista de diretórios padrão onde o Voicemod guarda os seus memes/sons."""
    candidates = []
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    app_data = os.environ.get("APPDATA", "")
    user_profile = os.environ.get("USERPROFILE", "")

    if local_app_data:
        # Voicemod V2 local memes folder
        candidates.append(os.path.join(local_app_data, "Voicemod", "memes"))
        candidates.append(os.path.join(local_app_data, "Voicemod"))
        candidates.append(os.path.join(local_app_data, "VoicemodV3", "sounds"))
        candidates.append(os.path.join(local_app_data, "VoicemodV3"))
    if app_data:
        candidates.append(os.path.join(app_data, "Voicemod", "memes"))
        candidates.append(os.path.join(app_data, "Voicemod"))
        candidates.append(os.path.join(app_data, "VoicemodV3"))
    if user_profile:
        candidates.append(os.path.join(user_profile, "Documents", "Voicemod"))
        candidates.append(os.path.join(user_profile, "Downloads", "Voicemod"))

    existing = [os.path.abspath(p) for p in candidates if os.path.isdir(p)]
    # Remove duplicados preservando ordem
    seen = set()
    result = []
    for p in existing:
        if p.lower() not in seen:
            seen.add(p.lower())
            result.append(p)
    return result


def detect_audio_type(file_path):
    """
    Inspeciona os primeiros bytes do ficheiro para identificar se é um ficheiro
    de áudio suportado (mesmo com extensão .dat do Voicemod).
    Devolve: 'wav', 'mp3', 'ogg', 'flac' ou None.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".mp3", ".wav", ".ogg", ".flac"):
        return ext.lstrip(".")

    try:
        with open(file_path, "rb") as f:
            header = f.read(64)
        if len(header) < 4:
            return None

        # WAV: RIFF....WAVE
        if header.startswith(b"RIFF") and len(header) >= 12 and header[8:12] == b"WAVE":
            return "wav"
        # OGG: OggS
        if header.startswith(b"OggS"):
            return "ogg"
        # FLAC: fLaC
        if header.startswith(b"fLaC"):
            return "flac"
        # MP3 com tag ID3
        if header.startswith(b"ID3"):
            return "mp3"
        # MP3 sync frame (0xFF seguido de 0xFB, 0xF3, 0xF2, etc.)
        if header[0] == 0xFF and len(header) > 1 and (header[1] & 0xE0) == 0xE0:
            return "mp3"
    except Exception:
        pass

    return None


def clean_sound_title(filename):
    """Gera um título limpo e legível a partir do nome do ficheiro."""
    stem = os.path.splitext(os.path.basename(filename))[0]
    # Se o nome começar por UUID ou hash (comum no Voicemod), limpa prefixos
    # ex: 8f4e2c1a-89a1-4321-9988-bruh -> bruh
    parts = stem.split("-")
    if len(parts) > 1 and len(parts[0]) >= 8 and re.match(r"^[0-9a-fA-F]+$", parts[0]):
        stem = "-".join(parts[1:])

    # Substitui separadores por espaços
    clean = re.sub(r"[_\-\.]+", " ", stem).strip()
    # Remove sufixos numéricos redundantes ou .dat
    clean = re.sub(r"\s+\d+$", "", clean)
    if not clean:
        clean = "Som Voicemod"
    return clean.title()


def extract_metadata_from_db(dir_path):
    """
    Procura bases de dados SQLite do Voicemod (como memeSearch.db ou database.db)
    para extrair os nomes originais dos sons associados aos ficheiros .dat.
    """
    mapping = {}
    db_candidates = ["memeSearch.db", "database.db", "voicemod.db"]

    for root, _, files in os.walk(dir_path):
        for f in files:
            if f.lower() in [c.lower() for c in db_candidates] or f.lower().endswith(".db"):
                db_path = os.path.join(root, f)
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [r[0] for r in cur.fetchall()]

                    for tbl in tables:
                        try:
                            cur.execute(f"PRAGMA table_info({tbl});")
                            cols = [c[1].lower() for c in cur.fetchall()]
                            # Procura colunas como name/title e filename/file/id
                            name_col = next((c for c in cols if c in ("name", "title", "soundname", "meme_name")), None)
                            file_col = next((c for c in cols if c in ("filename", "file", "path", "id", "guid")), None)

                            if name_col and file_col:
                                cur.execute(f"SELECT {name_col}, {file_col} FROM {tbl};")
                                for row in cur.fetchall():
                                    if row[0] and row[1]:
                                        s_name = str(row[0]).strip()
                                        s_file = str(row[1]).strip()
                                        if s_name and s_file:
                                            mapping[s_file.lower()] = s_name
                                            mapping[os.path.basename(s_file).lower()] = s_name
                                            mapping[os.path.splitext(os.path.basename(s_file))[0].lower()] = s_name
                        except Exception:
                            continue
                    conn.close()
                except Exception:
                    pass
    return mapping


def generate_sound_icon(output_path, title):
    """Gera um ícone estético com as cores do Pulse (Cyan/Violeta/Ouro) para a soundboard."""
    if not _PIL_OK:
        return False
    try:
        size = (256, 256)
        img = Image.new("RGBA", size, (10, 14, 26, 255))
        d = ImageDraw.Draw(img)

        # Círculo externo brilhante
        d.ellipse([18, 18, 238, 238], outline=(0, 240, 255, 230), width=6)
        d.ellipse([26, 26, 230, 230], outline=(157, 78, 221, 160), width=3)

        letter = (title.strip() or "P")[0].upper()
        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except Exception:
            font = ImageFont.load_default()

        bb = d.textbbox((0, 0), letter, font=font)
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        x = (256 - w) / 2 - bb[0]
        y = (256 - h) / 2 - bb[1] - 6

        # Sombra do texto
        d.text((x + 2, y + 2), letter, font=font, fill=(0, 240, 255, 120))
        # Letra principal
        d.text((x, y), letter, font=font, fill=(255, 255, 255, 255))

        img.save(output_path, "PNG")
        return True
    except Exception:
        return False


def import_sounds_from_directory(source_dir, user_name, metadata_map=None):
    """
    Importa recursivamente todos os sons válidos de um diretório para
    a pasta de sons da conta atual do Pulse Gaming Optimizer.
    """
    if metadata_map is None:
        metadata_map = extract_metadata_from_db(source_dir)

    target_dir = os.path.join(accounts.user_dir(user_name), "sounds")
    os.makedirs(target_dir, exist_ok=True)

    imported = []
    skipped = 0

    for root, _, files in os.walk(source_dir):
        for f in files:
            full_path = os.path.join(root, f)
            # Ignora ficheiros temporários ou de lock
            if f.startswith("~") or f.startswith("."):
                continue

            audio_fmt = detect_audio_type(full_path)
            if not audio_fmt:
                skipped += 1
                continue

            # Determina o título
            stem = os.path.splitext(f)[0].lower()
            title = metadata_map.get(f.lower()) or metadata_map.get(stem)
            if not title:
                title = clean_sound_title(f)

            # Valida com miniaudio se disponível
            if _MA_OK:
                try:
                    # Copia para ficheiro temporário com a extensão detetada para validar decode
                    tmp_val = tempfile.mktemp("." + audio_fmt)
                    shutil.copyfile(full_path, tmp_val)
                    try:
                        miniaudio.decode_file(tmp_val)
                    finally:
                        try:
                            os.remove(tmp_val)
                        except Exception:
                            pass
                except Exception:
                    skipped += 1
                    continue

            # Nome base seguro no destino
            safe_base = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")[:40] or "som"
            dest_ext = "." + audio_fmt
            dest_file = os.path.join(target_dir, safe_base + dest_ext)

            idx = 1
            while os.path.exists(dest_file):
                dest_file = os.path.join(target_dir, f"{safe_base}-{idx}{dest_ext}")
                idx += 1

            shutil.copy2(full_path, dest_file)

            # Ícone
            icon_file = os.path.join(target_dir, os.path.splitext(os.path.basename(dest_file))[0] + ".png")
            # Verifica se existe um PNG com o mesmo nome na origem
            orig_png = os.path.join(root, os.path.splitext(f)[0] + ".png")
            if os.path.isfile(orig_png):
                try:
                    shutil.copy2(orig_png, icon_file)
                except Exception:
                    generate_sound_icon(icon_file, title)
            else:
                generate_sound_icon(icon_file, title)

            imported.append({
                "title": title,
                "file": dest_file,
                "format": audio_fmt
            })

    return {
        "success": True,
        "count": len(imported),
        "skipped": skipped,
        "sounds": imported,
        "output": f"Importados com sucesso {len(imported)} sons do Voicemod!"
    }


def import_sounds_from_archive(archive_path, user_name):
    """Extrai um arquivo ZIP ou backup do Voicemod e importa os sons."""
    if not zipfile.is_zipfile(archive_path):
        return {"success": False, "output": "O ficheiro selecionado não é um arquivo ZIP ou backup válido."}

    tmp_dir = tempfile.mkdtemp(prefix="pulse_voicemod_import_")
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(tmp_dir)
        return import_sounds_from_directory(tmp_dir, user_name)
    finally:
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass


def auto_import_voicemod(user_name):
    """
    Executa a deteção automática do Voicemod.
    Se encontrar uma ou mais pastas padrão com ficheiros de áudio, importa automaticamente.
    Caso contrário, devolve indicação para abrir o diálogo de escolha de pasta/ficheiro.
    """
    dirs = get_standard_voicemod_dirs()
    if not dirs:
        return {
            "success": False,
            "needs_selection": True,
            "output": "Nenhuma pasta padrão do Voicemod encontrada no teu computador. Por favor escolhe a pasta ou ficheiro com os teus sons."
        }

    total_imported = 0
    all_sounds = []

    for d in dirs:
        res = import_sounds_from_directory(d, user_name)
        if res.get("success") and res.get("count", 0) > 0:
            total_imported += res["count"]
            all_sounds.extend(res["sounds"])

    if total_imported > 0:
        return {
            "success": True,
            "needs_selection": False,
            "count": total_imported,
            "sounds": all_sounds,
            "output": f"Sucesso! {total_imported} sons do Voicemod foram detetados e importados para o Soundboard."
        }
    else:
        return {
            "success": False,
            "needs_selection": True,
            "output": "As pastas do Voicemod foram localizadas, mas não continham sons. Por favor escolhe a pasta onde tens os teus ficheiros de áudio."
        }


def pick_and_import_folder(user_name):
    """Abre o diálogo nativo do Windows para o utilizador escolher uma pasta."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Seleciona a pasta com os sons do Voicemod")
        root.destroy()

        if not folder:
            return {"success": False, "output": "Operação cancelada pelo utilizador."}

        return import_sounds_from_directory(folder, user_name)
    except Exception as e:
        return {"success": False, "output": f"Erro ao abrir seletor: {e}"}


def pick_and_import_file(user_name):
    """Abre o diálogo nativo do Windows para o utilizador escolher um ficheiro ou arquivo de backup."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = filedialog.askopenfilename(
            title="Seleciona um backup (.zip/.v2s) ou ficheiro de áudio do Voicemod",
            filetypes=[
                ("Backups e Áudio Voicemod", "*.zip *.v2s *.vmsoundboard *.dat *.mp3 *.wav *.ogg"),
                ("Todos os Ficheiros", "*.*")
            ]
        )
        root.destroy()

        if not file_path:
            return {"success": False, "output": "Operação cancelada pelo utilizador."}

        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".zip", ".v2s", ".vmsoundboard") or zipfile.is_zipfile(file_path):
            return import_sounds_from_archive(file_path, user_name)
        else:
            # Importa a pasta onde o ficheiro se encontra ou o próprio ficheiro
            return import_sounds_from_directory(os.path.dirname(file_path), user_name)
    except Exception as e:
        return {"success": False, "output": f"Erro ao processar ficheiro: {e}"}
