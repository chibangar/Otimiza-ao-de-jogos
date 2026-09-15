"""Contas locais: cada pessoa guarda as suas vozes, teclas, jogos e sons."""
import hashlib
import json
import os
import re
import secrets

GUEST = "convidado"


def data_root():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    p = os.path.join(base, "MidnightOptimizer")
    os.makedirs(p, exist_ok=True)
    return p


def _users_file():
    return os.path.join(data_root(), "users.json")


def _load_users():
    try:
        with open(_users_file(), encoding="utf-8") as f:
            d = json.load(f)
            return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _save_users(d):
    with open(_users_file(), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def _hash(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 120000).hex()


def valid_name(name):
    return bool(re.match(r"^[A-Za-z0-9_.-]{3,16}$", name or ""))


def list_users():
    users = _load_users()
    return sorted(users.keys())


def register(name, pw):
    name = (name or "").strip()
    if not valid_name(name):
        return {"success": False, "output": "Nome 3-16 letras/numeros."}
    if not pw or len(pw) < 4:
        return {"success": False, "output": "Palavra-passe min. 4 caracteres."}
    users = _load_users()
    if name.lower() in [k.lower() for k in users] or name.lower() == GUEST:
        return {"success": False, "output": "Nome ja existe."}
    salt = secrets.token_hex(16)
    users[name] = {"salt": salt, "hash": _hash(pw, salt)}
    _save_users(users)
    user_dir(name)
    return {"success": True, "output": f"Conta {name} criada!"}


def check(name, pw):
    if name == GUEST:
        user_dir(GUEST)
        return {"success": True, "output": "Sessao de convidado."}
    users = _load_users()
    u = users.get(name)
    if not u or u.get("hash") != _hash(pw or "", u.get("salt", "")):
        return {"success": False, "output": "Nome ou palavra-passe errados."}
    user_dir(name)
    return {"success": True, "output": f"Bem-vindo, {name}!"}


def user_dir(name):
    p = os.path.join(data_root(), "users", re.sub(r"[^A-Za-z0-9_.-]", "_", name))
    os.makedirs(os.path.join(p, "sounds"), exist_ok=True)
    return p


def _session_file():
    return os.path.join(data_root(), "session.json")


def save_session(name):
    try:
        with open(_session_file(), "w", encoding="utf-8") as f:
            json.dump({"user": name, "token": secrets.token_hex(16)}, f)
    except Exception:
        pass


def load_session():
    try:
        with open(_session_file(), encoding="utf-8") as f:
            d = json.load(f)
        u = (d or {}).get("user", "")
        if not u:
            return None
        if u == GUEST:
            return u
        if u in _load_users():
            return u
        return None
    except Exception:
        return None


def clear_session():
    try:
        if os.path.isfile(_session_file()):
            os.remove(_session_file())
    except Exception:
        pass


def custom_sounds(name):
    out = []
    sdir = os.path.join(user_dir(name), "sounds")
    for fn in sorted(os.listdir(sdir)):
        if fn.lower().endswith((".mp3", ".wav", ".ogg")):
            sid = "u_" + os.path.splitext(fn)[0]
            png = os.path.join(sdir, os.path.splitext(fn)[0] + ".png")
            out.append({
                "id": sid, "title": os.path.splitext(fn)[0].replace("-", " ").replace("_", " "),
                "file": os.path.join(sdir, fn),
                "photo": png if os.path.isfile(png) else "",
                "custom": True, "owner": name,
            })
    return out
