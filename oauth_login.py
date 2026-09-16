"""Login social (Google + Discord) via OAuth2 com loopback local.
Precisa de oauth_config.json (ver oauth_config.example.json).
Google: cliente tipo 'App para computador' (so client_id, com PKCE).
Discord: Client ID + Client Secret, com redirect http://127.0.0.1:8742/callback
registado no Portal de Programador.
"""
import base64
import hashlib
import json
import os
import secrets
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

import accounts

GOOGLE_PORT = 8741
DISCORD_PORT = 8742
TIMEOUT = 180
BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def _base_dir():
    import sys
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def load_config():
    seen = []
    for p in [os.path.join(_base_dir(), "oauth_config.json"),
              os.path.join(accounts.data_root(), "oauth_config.json"),
              os.path.join(os.path.dirname(os.path.abspath(__file__)), "oauth_config.json")]:
        if p in seen:
            continue
        seen.append(p)
        if os.path.isfile(p):
            try:
                with open(p, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


def save_discord_config(client_id, client_secret):
    """Guarda as chaves do Discord em local sempre gravável (sem admin)."""
    cid = (client_id or "").strip()
    csec = (client_secret or "").strip()
    if not cid or not csec:
        return {"success": False, "output": "Cola o Client ID e o Client Secret."}
    try:
        current = load_config()
    except Exception:
        current = {}
    if not isinstance(current, dict):
        current = {}
    current["discord"] = {"client_id": cid, "client_secret": csec}
    try:
        dest = os.path.join(accounts.data_root(), "oauth_config.json")
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=1)
    except Exception as e:
        return {"success": False, "output": f"Não consegui guardar: {e}"}
    ok = status().get("discord", False)
    if not ok:
        return {"success": False, "output": "Guardei mas o Discord continua inativo."}
    return {"success": True, "output": "Discord ativo! OK"}


def status():
    cfg = load_config()
    return {
        "google": bool((cfg.get("google") or {}).get("client_id")),
        "discord": bool((cfg.get("discord") or {}).get("client_id")
                        and (cfg.get("discord") or {}).get("client_secret")),
    }


class _Catcher(BaseHTTPRequestHandler):
    code = None
    error = None

    def do_GET(self):
        q = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(q)
        _Catcher.code = (params.get("code") or [None])[0]
        _Catcher.error = (params.get("error") or [None])[0]
        body = ("<html><body style='background:#060714;color:#e8e6f0;font-family:sans-serif;"
                "'><h2>Podes fechar esta janela e voltar a app. ✅</h2></body></html>").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def _wait_code(port):
    _Catcher.code, _Catcher.error = None, None
    srv = HTTPServer(("127.0.0.1", port), _Catcher)
    srv.timeout = TIMEOUT
    t = threading.Thread(target=srv.handle_request, daemon=True)
    t.start()
    t.join(TIMEOUT + 5)
    srv.server_close()
    if _Catcher.error:
        return None, f"Autorizacao recusada: {_Catcher.error}"
    if not _Catcher.code:
        return None, "Tempo esgotado. Tenta outra vez."
    return _Catcher.code, None


def _post(url, fields):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=data,
                                 headers={"User-Agent": BROWSER_UA,
                                          "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _get_json(url, token):
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA,
                                               "Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _pkce():
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b"=").decode()
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def _open_browser(url):
    import webbrowser
    webbrowser.open(url)


def _save_avatar(name, url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
        if raw[:4] == b"\x89PNG" or raw[:2] == b"\xff\xd8":
            dest = os.path.join(accounts.user_dir(name), "avatar.png")
            with open(dest, "wb") as f:
                f.write(raw)
            return dest
    except Exception:
        pass
    return ""


def _ensure_local_user(base, provider, pid, avatar_url=""):
    users = accounts._load_users()
    for uname, u in users.items():
        if u.get("provider") == provider and u.get("provider_id") == pid:
            if avatar_url:
                u["avatar"] = _save_avatar(uname, avatar_url) or u.get("avatar", "")
                accounts._save_users(users)
            return uname
    stem = "".join(c if (c.isalnum() or c in "._-") else "_" for c in base)[:14] or "player"
    uname, i = stem, 1
    taken = [k.lower() for k in users] + [accounts.GUEST]
    while uname.lower() in taken:
        i += 1
        uname = f"{stem[:12]}{i}"
    salt = secrets.token_hex(16)
    users[uname] = {"salt": salt, "hash": accounts._hash(secrets.token_hex(32), salt),
                    "provider": provider, "provider_id": pid, "avatar": ""}
    accounts._save_users(users)
    if avatar_url:
        users[uname]["avatar"] = _save_avatar(uname, avatar_url)
        accounts._save_users(users)
    accounts.user_dir(uname)
    return uname


def login_google():
    cfg = (load_config().get("google") or {})
    cid = (cfg.get("client_id") or "").strip()
    if not cid:
        return {"success": False, "output": "Google nao configurado. Ve oauth_config.example.json."}
    verifier, challenge = _pkce()
    redirect = f"http://127.0.0.1:{GOOGLE_PORT}/callback"
    params = urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code",
        "scope": "openid email profile", "code_challenge": challenge,
        "code_challenge_method": "S256", "prompt": "select_account",
    })
    _open_browser("https://accounts.google.com/o/oauth2/v2/auth?" + params)
    code, err = _wait_code(GOOGLE_PORT)
    if err:
        return {"success": False, "output": err}
    try:
        tok = _post("https://oauth2.googleapis.com/token", {
            "code": code, "client_id": cid, "code_verifier": verifier,
            "grant_type": "authorization_code", "redirect_uri": redirect})
        me = _get_json("https://openidconnect.googleapis.com/v1/userinfo", tok["access_token"])
    except Exception as e:
        return {"success": False, "output": f"Google falhou: {e}"}
    uname = _ensure_local_user((me.get("email") or me.get("name") or "google").split("@")[0],
                               "google", me.get("sub", ""), me.get("picture", ""))
    return {"success": True, "user": uname, "output": f"Bem-vindo, {uname} (Google)!"}


def login_discord():
    cfg = (load_config().get("discord") or {})
    cid = (cfg.get("client_id") or "").strip()
    csec = (cfg.get("client_secret") or "").strip()
    if not (cid and csec):
        return {"success": False, "output": "Discord nao configurado. Ve oauth_config.example.json."}
    redirect = f"http://127.0.0.1:{DISCORD_PORT}/callback"
    # prompt=consent = mostra sempre o ecrã "Autorizar" (o mais fiável).
    # (prompt=none falhava logo se a pessoa não estivesse logada no browser.)
    params = urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code",
        "scope": "identify email", "prompt": "consent",
    })
    _open_browser("https://discord.com/oauth2/authorize?" + params)
    code, err = _wait_code(DISCORD_PORT)
    if err:
        if "access_denied" in err:
            return {"success": False,
                    "output": "Cancelaste no browser. Prime outra vez e carrega em Autorizar."}
        if "Tempo esgotado" in err:
            return {"success": False,
                    "output": "Tempo esgotado. Confirma no portal do Discord que o redirect "
                              "http://127.0.0.1:8742/callback está registado e autoriza no browser."}
        return {"success": False, "output": err}
    try:
        tok = _post("https://discord.com/api/oauth2/token", {
            "client_id": cid, "client_secret": csec, "grant_type": "authorization_code",
            "code": code, "redirect_uri": redirect})
        me = _get_json("https://discord.com/api/users/@me", tok["access_token"])
    except Exception as e:
        return {"success": False, "output": f"Discord falhou: {e}. Confirma o redirect no portal."}
    av = ""
    if me.get("avatar"):
        av = f"https://cdn.discordapp.com/avatars/{me['id']}/{me['avatar']}.png"
    uname = _ensure_local_user(me.get("username") or "discord", "discord", me.get("id", ""), av)
    return {"success": True, "user": uname, "output": f"Bem-vindo, {uname} (Discord)!"}
