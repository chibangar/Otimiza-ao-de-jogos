# -*- coding: utf-8 -*-
"""
Motor Avançado de Importação de Sons do Voicemod para o Pulse Gaming Optimizer.
Suporta:
- Deteção e extração direta de sons e IMAGENS ORIGINAIS do Voicemod V3 (ao vivo ou em cache)
- Desencriptação automática de áudio Ogg Opus do Voicemod via chave de cifras XOR
- Download e conversão das imagens originais dos memes (.png, .jpg, .webp) para o Soundboard
- Deteção de pastas padrão do Voicemod V2 (%LocalAppData%\\Voicemod\\memes) com ficheiros .dat
- Extração de metadados de bases de dados SQLite (memeSearch.db, database.db)
- Importação direta de pastas do sistema e arquivos comprimidos (.zip, .v2s, .vmsoundboard)
"""

import os
import re
import sys
import json
import shutil
import sqlite3
import zipfile
import tempfile
import urllib.request
import io
from pathlib import Path
import threading
import concurrent.futures

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

try:
    import soundfile as sf
    _SF_OK = True
except Exception:
    _SF_OK = False

import accounts

# Chave criptográfica padrão do Voicemod para ficheiros de áudio OGG Opus
VM_AUDIO_XOR_KEY = b"237fdkjsfhd4zxufchyptytsa"


def decrypt_voicemod_audio(raw_bytes):
    """Desencripta o fluxo de áudio OGG Opus cifrado pelo Voicemod."""
    key = VM_AUDIO_XOR_KEY
    k_len = len(key)
    return bytes([b ^ key[i % k_len] for i, b in enumerate(raw_bytes)])


def get_standard_voicemod_dirs():
    """Devolve lista de diretórios padrão onde o Voicemod guarda os seus memes/sons."""
    candidates = []
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    app_data = os.environ.get("APPDATA", "")
    user_profile = os.environ.get("USERPROFILE", "")

    if local_app_data:
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
    parts = stem.split("-")
    if len(parts) > 1 and len(parts[0]) >= 8 and re.match(r"^[0-9a-fA-F]+$", parts[0]):
        stem = "-".join(parts[1:])

    clean = re.sub(r"[_\-\.]+", " ", stem).strip()
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
    """Gera um ícone estético néon para a soundboard caso a imagem original falhe."""
    if not _PIL_OK:
        return False
    try:
        size = (256, 256)
        img = Image.new("RGBA", size, (10, 14, 26, 255))
        d = ImageDraw.Draw(img)

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

        d.text((x + 2, y + 2), letter, font=font, fill=(0, 240, 255, 120))
        d.text((x, y), letter, font=font, fill=(255, 255, 255, 255))

        img.save(output_path, "PNG")
        return True
    except Exception:
        return False


def save_image_from_bytes_or_url(source, output_png_path, fallback_title="P"):
    """
    Descarrega ou converte uma imagem original (.jpg, .png, .webp) para PNG de alta qualidade.
    """
    if not _PIL_OK:
        return False
    try:
        raw = None
        if isinstance(source, bytes):
            raw = source
        elif isinstance(source, str):
            if source.startswith(("http://", "https://")):
                req = urllib.request.Request(source, headers={"User-Agent": "PulseGamingOptimizer/4.2"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    raw = resp.read()
            elif os.path.isfile(source):
                with open(source, "rb") as f:
                    raw = f.read()

        if not raw:
            return generate_sound_icon(output_png_path, fallback_title)

        img = Image.open(io.BytesIO(raw))
        # Converter para RGBA se tiver transparência ou RGB
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")

        # Redimensiona para formato quadrado ideal mantendo resolução limpa
        size = (256, 256)
        img = img.resize(size, Image.Resampling.LANCZOS)
        img.save(output_png_path, "PNG")
        return True
    except Exception:
        return generate_sound_icon(output_png_path, fallback_title)


# =========================================================================
# EXTRAÇÃO AUTOMÁTICA DIRETA DO VOICEMOD V3 (COM IMAGENS ORIGINAIS)
# =========================================================================

def scan_voicemod_v3_sounds_from_memory():
    """
    Inspeciona a memória dos processos ativos do Voicemod.exe para extrair
    todos os sons, URLs de áudio e URLs DAS IMAGENS ORIGINAIS da aba atual.
    """
    import ctypes
    from ctypes import wintypes

    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    OpenProcess = ctypes.windll.kernel32.OpenProcess
    CloseHandle = ctypes.windll.kernel32.CloseHandle
    ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
    VirtualQueryEx = ctypes.windll.kernel32.VirtualQueryEx

    class MEMORY_BASIC_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BaseAddress", ctypes.c_void_p),
            ("AllocationBase", ctypes.c_void_p),
            ("AllocationProtect", wintypes.DWORD),
            ("PartitionId", wintypes.WORD),
            ("RegionSize", ctypes.c_size_t),
            ("State", wintypes.DWORD),
            ("Protect", wintypes.DWORD),
            ("Type", wintypes.DWORD),
        ]

    # Procura PIDs de Voicemod.exe
    import psutil
    target_pids = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            if p.info["name"] and "voicemod.exe" in p.info["name"].lower():
                target_pids.append(p.info["pid"])
        except Exception:
            pass

    if not target_pids:
        return []

    collected_sounds = []
    seen_names = set()

    for pid in target_pids:
        h = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if not h:
            continue
        try:
            mbi = MEMORY_BASIC_INFORMATION()
            addr = 0
            while VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
                if mbi.State == 0x1000 and (mbi.Protect & 0xFF) in [0x04, 0x02, 0x20, 0x40]:
                    buf = ctypes.create_string_buffer(mbi.RegionSize)
                    read = ctypes.c_size_t()
                    if ReadProcessMemory(h, ctypes.c_void_p(addr), buf, mbi.RegionSize, ctypes.byref(read)):
                        data = buf.raw[:read.value]
                        if b'"type":"sound"' in data and b'"assets":' in data:
                            pos = 0
                            while True:
                                idx = data.find(b'"type":"sound"', pos)
                                if idx == -1:
                                    break
                                start = data.rfind(b'{"assets":', 0, idx)
                                if start == -1:
                                    start = data.rfind(b'{"', 0, idx)
                                brace_count = 0
                                actual_end = -1
                                for i in range(start, min(len(data), start + 16384)):
                                    ch = data[i:i+1]
                                    if ch == b'{':
                                        brace_count += 1
                                    elif ch == b'}':
                                        brace_count -= 1
                                        if brace_count == 0:
                                            actual_end = i
                                            break
                                if actual_end != -1:
                                    try:
                                        chunk = data[start:actual_end+1]
                                        obj = json.loads(chunk.decode("utf-8"))
                                        name = obj.get("name")
                                        if name and name not in seen_names:
                                            seen_names.add(name)
                                            collected_sounds.append(obj)
                                    except Exception:
                                        pass
                                pos = idx + 14
                addr += mbi.RegionSize
        finally:
            CloseHandle(h)

    return collected_sounds


def import_voicemod_v3_catalog(user_name):
    """
    Importa diretamente a coleção do Voicemod V3 com áudio desobfuscado
    e AS IMAGENS ORIGINAIS de cada som.
    """
    sounds_data = scan_voicemod_v3_sounds_from_memory()
    
    # Se não apanhou da memória (ex: Voicemod fechado), tenta ficheiro de cache local
    if not sounds_data:
        cache_json = os.path.join(accounts.data_root(), "voicemod_sounds.json")
        if not os.path.isfile(cache_json):
            cache_json = os.path.join(os.path.dirname(__file__), "voicemod_sounds.json")
        if os.path.isfile(cache_json):
            try:
                with open(cache_json, "r", encoding="utf-8") as f:
                    sounds_data = json.load(f)
            except Exception:
                pass

    if not sounds_data:
        return {"success": False, "count": 0, "output": "Nenhum som detetado no Voicemod V3."}

    target_dir = os.path.join(accounts.user_dir(user_name), "sounds")
    os.makedirs(target_dir, exist_ok=True)

    meta_path = os.path.join(target_dir, "metadata.json")
    meta = {}
    if os.path.isfile(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as mf:
                meta = json.load(mf)
        except Exception:
            pass

    meta_lock = threading.Lock()
    imported_list = []

    def _process_item(item):
        name = item.get("name")
        if not name:
            return None

        assets = item.get("assets", [])
        audio_url = None
        icon_url = None

        if assets:
            for a in assets:
                t = a.get("type")
                if t == "audio" and not audio_url:
                    audio_url = a.get("url")
                elif t == "icon" and not icon_url:
                    icon_url = a.get("url")
        else:
            audio_url = item.get("audio_url")
            icon_url = item.get("icon_url")

        if not audio_url:
            return None

        safe_stem = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")[:40] or "som"
        dest_wav = os.path.join(target_dir, f"{safe_stem}.wav")
        dest_png = os.path.join(target_dir, f"{safe_stem}.png")

        # Se já existir e for válido, reutiliza de imediato
        if os.path.isfile(dest_wav) and os.path.getsize(dest_wav) > 1000 and os.path.isfile(dest_png) and os.path.getsize(dest_png) > 300:
            fn = os.path.basename(dest_wav)
            with meta_lock:
                meta[fn] = {
                    "title": name,
                    "icon": os.path.basename(dest_png),
                    "source": "voicemod_v3"
                }
            return {"title": name, "file": dest_wav, "photo": dest_png}

        try:
            req = urllib.request.Request(audio_url, headers={"User-Agent": "PulseGamingOptimizer/4.2"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw_enc = resp.read()

            dec_ogg = decrypt_voicemod_audio(raw_enc)

            if _SF_OK:
                try:
                    data_arr, samplerate = sf.read(io.BytesIO(dec_ogg))
                    sf.write(dest_wav, data_arr, samplerate, subtype="PCM_16")
                except Exception:
                    with open(dest_wav.replace(".wav", ".ogg"), "wb") as f:
                        f.write(dec_ogg)
                    dest_wav = dest_wav.replace(".wav", ".ogg")
            else:
                with open(dest_wav.replace(".wav", ".ogg"), "wb") as f:
                    f.write(dec_ogg)
                dest_wav = dest_wav.replace(".wav", ".ogg")

            if icon_url:
                save_image_from_bytes_or_url(icon_url, dest_png, fallback_title=name)
            else:
                generate_sound_icon(dest_png, name)

            fn = os.path.basename(dest_wav)
            with meta_lock:
                meta[fn] = {
                    "title": name,
                    "icon": os.path.basename(dest_png),
                    "source": "voicemod_v3"
                }

            return {"title": name, "file": dest_wav, "photo": dest_png}
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(_process_item, item) for item in sounds_data]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                imported_list.append(res)

    # Guarda o ficheiro de metadados consolidado
    try:
        with open(meta_path, "w", encoding="utf-8") as mf:
            json.dump(meta, mf, indent=2, ensure_ascii=False)
    except Exception:
        pass

    imported_count = len(imported_list)
    return {
        "success": imported_count > 0,
        "count": imported_count,
        "sounds": imported_list,
        "output": f"Sucesso! {imported_count} sons do Voicemod com IMAGENS ORIGINAIS foram importados para o Soundboard."
    }


# =========================================================================
# IMPORTAÇÃO TRADICIONAL (PASTAS V2, FICHEIROS E ARQUIVOS ZIP)
# =========================================================================

def import_sounds_from_directory(source_dir, user_name, metadata_map=None):
    """
    Importa recursivamente todos os sons válidos de um diretório para
    a pasta de sons da conta atual do Pulse Gaming Optimizer.
    """
    if metadata_map is None:
        metadata_map = extract_metadata_from_db(source_dir)

    target_dir = os.path.join(accounts.user_dir(user_name), "sounds")
    os.makedirs(target_dir, exist_ok=True)

    meta_path = os.path.join(target_dir, "metadata.json")
    meta = {}
    if os.path.isfile(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as mf:
                meta = json.load(mf)
        except Exception:
            pass

    imported = []
    skipped = 0

    for root, _, files in os.walk(source_dir):
        for f in files:
            full_path = os.path.join(root, f)
            if f.startswith("~") or f.startswith("."):
                continue

            audio_fmt = detect_audio_type(full_path)
            if not audio_fmt:
                skipped += 1
                continue

            stem = os.path.splitext(f)[0].lower()
            title = metadata_map.get(f.lower()) or metadata_map.get(stem)
            if not title:
                title = clean_sound_title(f)

            safe_base = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")[:40] or "som"
            dest_ext = "." + audio_fmt
            dest_file = os.path.join(target_dir, safe_base + dest_ext)

            idx = 1
            while os.path.exists(dest_file):
                dest_file = os.path.join(target_dir, f"{safe_base}-{idx}{dest_ext}")
                idx += 1

            shutil.copy2(full_path, dest_file)

            # Procura por imagem original na pasta de origem (.png, .jpg, .webp)
            icon_file = os.path.join(target_dir, os.path.splitext(os.path.basename(dest_file))[0] + ".png")
            found_orig_image = None
            orig_base = os.path.splitext(full_path)[0]
            for img_ext in (".png", ".jpg", ".jpeg", ".webp"):
                candidate_img = orig_base + img_ext
                if os.path.isfile(candidate_img):
                    found_orig_image = candidate_img
                    break

            if found_orig_image:
                save_image_from_bytes_or_url(found_orig_image, icon_file, fallback_title=title)
            else:
                generate_sound_icon(icon_file, title)

            meta[os.path.basename(dest_file)] = {
                "title": title,
                "icon": os.path.basename(icon_file),
                "source": "local_import"
            }

            imported.append({
                "title": title,
                "file": dest_file,
                "format": audio_fmt
            })

    try:
        with open(meta_path, "w", encoding="utf-8") as mf:
            json.dump(meta, mf, indent=2, ensure_ascii=False)
    except Exception:
        pass

    return {
        "success": True,
        "count": len(imported),
        "skipped": skipped,
        "sounds": imported,
        "output": f"Importados com sucesso {len(imported)} sons com imagens!"
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


def import_all_voicemod(user_name):
    """
    Importa TUDO do Voicemod da pessoa:
    - Todos os memes e sons da memória ativa e abas (V3)
    - Todas as IMAGENS ORIGINAIS associadas
    - Todas as pastas padrão do Voicemod (V2 memes, V3 cache, resources)
    - Arquivos de som (.v2s, .vmsoundboard, backups zip) em Downloads, Documentos e Desktop
    - Deduplicação inteligente e limpeza de ficheiros redundantes
    """
    target_dir = os.path.join(accounts.user_dir(user_name), "sounds")
    os.makedirs(target_dir, exist_ok=True)

    all_sounds = []
    seen_titles = set()

    # 1. Catálogo V3 (memória ativa e cache com fotos originais)
    try:
        res_v3 = import_voicemod_v3_catalog(user_name)
        if res_v3.get("success"):
            for s in res_v3.get("sounds", []):
                t = s.get("title", "").strip().lower()
                if t and t not in seen_titles:
                    seen_titles.add(t)
                    all_sounds.append(s)
    except Exception:
        pass

    # 2. Pastas padrão do Voicemod (V2 memes, databases, V3 resources)
    dirs = get_standard_voicemod_dirs()
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        res_dir = os.path.join(local_app_data, "VoicemodV3", "userCache", "resources")
        if os.path.isdir(res_dir) and res_dir not in dirs:
            dirs.append(res_dir)

    for d in dirs:
        try:
            r = import_sounds_from_directory(d, user_name)
            if r.get("success"):
                for s in r.get("sounds", []):
                    t = s.get("title", "").strip().lower()
                    if t and t not in seen_titles:
                        seen_titles.add(t)
                        all_sounds.append(s)
        except Exception:
            pass

    # 3. Procura por ficheiros de backup/exportação (.v2s, .vmsoundboard, voicemod*.zip)
    user_prof = os.environ.get("USERPROFILE", "")
    if user_prof:
        check_folders = [
            os.path.join(user_prof, "Downloads"),
            os.path.join(user_prof, "Documents"),
            os.path.join(user_prof, "Desktop")
        ]
        for cf in check_folders:
            if not os.path.isdir(cf):
                continue
            for root, _, files in os.walk(cf):
                for f in files:
                    fl = f.lower()
                    if fl.endswith((".v2s", ".vmsoundboard")) or ("voicemod" in fl and fl.endswith(".zip")):
                        archive_path = os.path.join(root, f)
                        try:
                            r = import_sounds_from_archive(archive_path, user_name)
                            if r.get("success"):
                                for s in r.get("sounds", []):
                                    t = s.get("title", "").strip().lower()
                                    if t and t not in seen_titles:
                                        seen_titles.add(t)
                                        all_sounds.append(s)
                        except Exception:
                            pass
                break # apenas topo de cada pasta para máxima velocidade

    # 4. Limpeza de ficheiros .ogg redundantes se já existir .wav correspondente
    for fn in os.listdir(target_dir):
        if fn.lower().endswith(".ogg"):
            stem = os.path.splitext(fn)[0]
            wav_path = os.path.join(target_dir, stem + ".wav")
            if os.path.isfile(wav_path):
                try:
                    os.remove(os.path.join(target_dir, fn))
                except Exception:
                    pass

    total = len(all_sounds)
    if total > 0:
        return {
            "success": True,
            "count": total,
            "sounds": all_sounds,
            "output": f"Sucesso total! {total} sons e memes do Voicemod com IMAGENS ORIGINAIS foram importados para o teu Soundboard."
        }
    else:
        return {
            "success": False,
            "needs_selection": True,
            "output": "Nenhum som encontrado automaticamente no Voicemod. Podes escolher a pasta ou backup manualmente."
        }


def auto_import_voicemod(user_name):
    """Executa a importação completa de todos os sons do Voicemod."""
    return import_all_voicemod(user_name)


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
            return import_sounds_from_directory(os.path.dirname(file_path), user_name)
    except Exception as e:
        return {"success": False, "output": f"Erro ao processar ficheiro: {e}"}
