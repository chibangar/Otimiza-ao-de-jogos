"""Servidores publicos CS2: lista, estado live (A2S), ligar, historico por conta."""
import json
import os
import socket
import struct
from concurrent.futures import ThreadPoolExecutor

import accounts

BASE = os.path.dirname(os.path.abspath(__file__))
REQ = b"\xff\xff\xff\xffTSource Engine Query\x00"
MODES = ["Todos", "1v1", "Retake", "Deathmatch", "Competitivo", "Surf/KZ",
         "Jailbreak", "Zombie", "Esconde-Esconde", "Outros"]


def load():
    try:
        with open(os.path.join(BASE, "assets", "servers.json"), encoding="utf-8") as f:
            d = json.load(f)
            return d if isinstance(d, list) else []
    except Exception:
        return []


def _read_str(buf, off):
    end = buf.index(b"\x00", off)
    return buf[off:end].decode("utf-8", "ignore"), end + 1


def query(ip, port, timeout=3):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(REQ, (ip, port))
        data, _ = s.recvfrom(4096)
    except Exception:
        try:
            s.close()
        except Exception:
            pass
        return None
    finally:
        try:
            s.close()
        except Exception:
            pass
    if data[:4] != b"\xff\xff\xff\xff":
        return None
    if data[4:5] == b"A":
        chal = data[5:9]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        try:
            s.sendto(REQ + chal, (ip, port))
            data, _ = s.recvfrom(4096)
        except Exception:
            return None
        finally:
            try:
                s.close()
            except Exception:
                pass
    if data[4:5] != b"I":
        return None
    try:
        off = 6
        name, off = _read_str(data, off)
        map_, off = _read_str(data, off)
        folder, off = _read_str(data, off)
        game, off = _read_str(data, off)
        appid = struct.unpack("<H", data[off:off + 2])[0]
        off += 2
        players, maxp, bots = data[off], data[off + 1], data[off + 2]
        return {"online": True, "name": name[:90], "map": map_,
                "players": players, "max": maxp, "bots": bots}
    except Exception:
        return None


def refresh():
    """Devolve a lista com estado live atual."""
    base = {f"{s['ip']}:{s['port']}": s for s in load()}

    def one(kv):
        key, s = kv
        info = query(s["ip"], s["port"])
        out = dict(s)
        if info:
            out.update(info)
        else:
            out.update({"online": False, "name": s.get("sample_name", ""),
                        "map": s.get("sample_map", ""), "players": 0, "max": 0})
        return out

    with ThreadPoolExecutor(max_workers=20) as ex:
        return list(ex.map(one, base.items()))


def connect(ip, port):
    try:
        os.startfile(f"steam://connect/{ip}:{port}")
        return {"success": True, "output": f"A ligar a {ip}:{port}…"}
    except Exception as e:
        return {"success": False, "output": f"Falha a ligar: {e}"}


def _hist_file(user):
    return os.path.join(accounts.user_dir(user or accounts.GUEST), "servers_history.json")


def history(user):
    try:
        with open(_hist_file(user), encoding="utf-8") as f:
            d = json.load(f)
            return d if isinstance(d, list) else []
    except Exception:
        return []


def add_history(user, entry):
    try:
        h = [e for e in history(user) if f"{e.get('ip')}:{e.get('port')}" != f"{entry['ip']}:{entry['port']}"]
        import datetime
        entry = dict(entry)
        entry["when"] = datetime.datetime.now().strftime("%d/%m %H:%M")
        h.insert(0, entry)
        with open(_hist_file(user), "w", encoding="utf-8") as f:
            json.dump(h[:20], f, ensure_ascii=False, indent=1)
    except Exception:
        pass
