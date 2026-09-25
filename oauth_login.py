"""Login social (Google + Discord) via OAuth2 com loopback local.
As chaves do Discord vêm EMBUTIDAS na app (fallback) para que QUALQUER
pessoa consiga fazer login sem configurar nada. Um oauth_config.json
(opcional, ao lado do .exe ou em %APPDATA%/MidnightOptimizer) sobrepõe-se
às chaves embutidas — útil para desenvolvimento.
Google: cliente tipo 'App para computador' (só client_id, com PKCE).
Discord: Client ID + Client Secret, com redirect http://127.0.0.1:8742/callback
registado no Portal de Programadores do Discord.
"""
import base64
import hashlib
import json
import os
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

import accounts

GOOGLE_PORT = 8741
DISCORD_PORT = 8742
TIMEOUT = 180

# Chaves embutidas oficiais da aplicação no Discord Developer Portal
BUILTIN_DISCORD_CLIENT_ID = "1549458613549006959"
BUILTIN_DISCORD_CLIENT_SECRET = "BB_TulZslPcNrnM7UwgIyst8TPRx-lzs"

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

_oauth_lock = threading.Lock()


def _base_dir():
    import sys
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def load_config():
    cfg = {}
    if BUILTIN_DISCORD_CLIENT_ID and BUILTIN_DISCORD_CLIENT_SECRET:
        cfg["discord"] = {
            "client_id": BUILTIN_DISCORD_CLIENT_ID,
            "client_secret": BUILTIN_DISCORD_CLIENT_SECRET,
        }
    seen = []
    for p in [
        os.path.join(_base_dir(), "oauth_config.json"),
        os.path.join(accounts.data_root(), "oauth_config.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "oauth_config.json"),
    ]:
        if p in seen:
            continue
        seen.append(p)
        if os.path.isfile(p):
            try:
                with open(p, encoding="utf-8") as f:
                    file_cfg = json.load(f)
                if not isinstance(file_cfg, dict):
                    continue
                for k, v in file_cfg.items():
                    if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                        merged = dict(cfg[k])
                        for kk, vv in v.items():
                            if isinstance(vv, str) and vv.strip():
                                merged[kk] = vv
                            elif not isinstance(vv, str):
                                merged[kk] = vv
                        cfg[k] = merged
                    elif isinstance(v, dict):
                        cfg[k] = v
                    else:
                        cfg[k] = v
            except Exception:
                pass
    return cfg


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
        "discord": bool(
            (cfg.get("discord") or {}).get("client_id")
            and (cfg.get("discord") or {}).get("client_secret")
        ),
    }


SUCCESS_PAGE_HTML = """<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="utf-8">
  <title>Pulse Gaming Optimizer — Autenticado com Sucesso!</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #070810;
      color: #f1f2f6;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 20px;
    }
    .card {
      background: #0f111a;
      border: 1px solid #232738;
      border-radius: 16px;
      padding: 36px 32px;
      text-align: center;
      max-width: 440px;
      width: 100%;
      box-shadow: 0 20px 50px rgba(0,0,0,0.6), 0 0 30px rgba(88,101,242,0.18);
    }
    .icon {
      width: 68px;
      height: 68px;
      background: #5865F2;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px;
      box-shadow: 0 8px 24px rgba(88,101,242,0.4);
    }
    h2 { font-size: 22px; font-weight: 700; margin-bottom: 10px; color: #ffffff; }
    p { font-size: 14px; color: #949ba4; line-height: 1.5; margin-bottom: 22px; }
    .badge {
      display: inline-block;
      background: rgba(88,101,242,0.15);
      color: #99aab5;
      padding: 8px 18px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      border: 1px solid rgba(88,101,242,0.3);
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="#ffffff">
        <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.929 1.793 8.18 1.793 12.061 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.893.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.028zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
      </svg>
    </div>
    <h2>Autenticação Concluída!</h2>
    <p>A tua conta Discord foi associada ao Pulse Gaming Optimizer.<br>Já podes fechar este separador e voltar à aplicação.</p>
    <div class="badge">✔ Sessão Iniciada — Podes voltar à app</div>
  </div>
  <script>setTimeout(function(){ try{ window.close(); }catch(e){} }, 2000);</script>
</body>
</html>"""


class _Catcher(BaseHTTPRequestHandler):
    code = None
    error = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        # Ignora pedidos de favicon ou ficheiros estáticos gerados pelo navegador
        if parsed.path.endswith((".ico", ".png", ".jpg", ".jpeg", ".css", ".js")):
            self.send_response(204)
            self.end_headers()
            return

        params = urllib.parse.parse_qs(parsed.query)
        code = (params.get("code") or [None])[0]
        err = (params.get("error") or [None])[0]

        if code or err:
            _Catcher.code = code
            _Catcher.error = err

        body = SUCCESS_PAGE_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


class _ReusableServer(HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def _wait_code(port):
    _Catcher.code, _Catcher.error = None, None
    try:
        srv = _ReusableServer(("127.0.0.1", port), _Catcher)
    except OSError as e:
        return None, f"Porta {port} ocupada no Windows: {e}. Tenta novamente em segundos."

    deadline = time.time() + TIMEOUT
    srv.timeout = 1.0
    while time.time() < deadline:
        srv.handle_request()
        if _Catcher.code or _Catcher.error:
            break

    try:
        srv.server_close()
    except Exception:
        pass

    if _Catcher.error:
        return None, f"Autorização recusada pelo utilizador: {_Catcher.error}"
    if not _Catcher.code:
        return None, "Tempo esgotado. Não foi recebida autorização do Discord a tempo."
    return _Catcher.code, None


def _post(url, fields):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": BROWSER_UA,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as he:
        body = ""
        try:
            body = he.read().decode("utf-8", errors="ignore")
        except Exception:
            pass
        raise RuntimeError(f"HTTP {he.code}: {body or he.reason}")


def _get_json(url, token):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": BROWSER_UA,
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as he:
        body = ""
        try:
            body = he.read().decode("utf-8", errors="ignore")
        except Exception:
            pass
        raise RuntimeError(f"HTTP {he.code}: {body or he.reason}")


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
        if len(raw) > 32 and (
            raw[:4] == b"\x89PNG"
            or raw[:2] == b"\xff\xd8"
            or (raw[:4] == b"RIFF" and b"WEBP" in raw[:16])
            or raw[:4] in (b"GIF8", b"GIF9")
        ):
            dest = os.path.join(accounts.user_dir(name), "avatar.png")
            with open(dest, "wb") as f:
                f.write(raw)
            return dest
    except Exception:
        pass
    return ""


def _ensure_local_user(base, provider, pid, avatar_url=""):
    users = accounts._load_users()
    # 1. Verifica se já existe utilizador com este mesmo provider e provider_id
    for uname, u in users.items():
        if u.get("provider") == provider and str(u.get("provider_id")) == str(pid):
            if avatar_url:
                u["avatar"] = _save_avatar(uname, avatar_url) or u.get("avatar", "")
                accounts._save_users(users)
            accounts.user_dir(uname)
            return uname

    stem = "".join(c if (c.isalnum() or c in "._-") else "_" for c in base)[:14] or "player"

    # 2. Se já existe uma conta local com o mesmo nome e sem provider associado, associa
    if stem in users and not users[stem].get("provider"):
        users[stem]["provider"] = provider
        users[stem]["provider_id"] = str(pid)
        if avatar_url:
            users[stem]["avatar"] = _save_avatar(stem, avatar_url) or users[stem].get("avatar", "")
        accounts._save_users(users)
        accounts.user_dir(stem)
        return stem

    # 3. Cria nova conta para o utilizador
    uname, i = stem, 1
    taken = [k.lower() for k in users] + [accounts.GUEST]
    while uname.lower() in taken:
        i += 1
        uname = f"{stem[:12]}{i}"
    salt = secrets.token_hex(16)
    users[uname] = {
        "salt": salt,
        "hash": accounts._hash(secrets.token_hex(32), salt),
        "provider": provider,
        "provider_id": str(pid),
        "avatar": "",
    }
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
        return {"success": False, "output": "Google não configurado. Vê oauth_config.example.json."}
    verifier, challenge = _pkce()
    redirect = f"http://127.0.0.1:{GOOGLE_PORT}/callback"
    params = urllib.parse.urlencode({
        "client_id": cid,
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": "openid email profile",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "prompt": "select_account",
    })
    _open_browser("https://accounts.google.com/o/oauth2/v2/auth?" + params)
    code, err = _wait_code(GOOGLE_PORT)
    if err:
        return {"success": False, "output": err}
    try:
        tok = _post("https://oauth2.googleapis.com/token", {
            "code": code,
            "client_id": cid,
            "code_verifier": verifier,
            "grant_type": "authorization_code",
            "redirect_uri": redirect,
        })
        me = _get_json("https://openidconnect.googleapis.com/v1/userinfo", tok["access_token"])
    except Exception as e:
        return {"success": False, "output": f"Google falhou: {e}"}
    uname = _ensure_local_user(
        (me.get("email") or me.get("name") or "google").split("@")[0],
        "google",
        me.get("sub", ""),
        me.get("picture", ""),
    )
    return {"success": True, "user": uname, "output": f"Bem-vindo, {uname} (Google)!"}


def login_discord():
    if not _oauth_lock.acquire(blocking=False):
        return {"success": False, "output": "Já está uma tentativa de autenticação em curso no teu browser."}
    try:
        cfg = (load_config().get("discord") or {})
        cid = (cfg.get("client_id") or "").strip()
        csec = (cfg.get("client_secret") or "").strip()
        if not (cid and csec):
            return {
                "success": False,
                "output": "Login Discord indisponível nesta versão. Fala com o programador.",
            }
        redirect = f"http://127.0.0.1:{DISCORD_PORT}/callback"
        params = urllib.parse.urlencode({
            "client_id": cid,
            "redirect_uri": redirect,
            "response_type": "code",
            "scope": "identify email",
            "prompt": "consent",
        })
        _open_browser("https://discord.com/oauth2/authorize?" + params)
        code, err = _wait_code(DISCORD_PORT)
        if err:
            if "access_denied" in err:
                return {
                    "success": False,
                    "output": "Cancelaste a autorização no browser. Clica novamente e autoriza a aplicação.",
                }
            if "Tempo esgotado" in err:
                return {
                    "success": False,
                    "output": "Tempo esgotado. Certifica-te de que aprovas a aplicação na janela do Discord no browser.",
                }
            return {"success": False, "output": err}
        try:
            tok = _post("https://discord.com/api/oauth2/token", {
                "client_id": cid,
                "client_secret": csec,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect,
            })
            me = _get_json("https://discord.com/api/users/@me", tok["access_token"])
        except Exception as e:
            return {"success": False, "output": f"Falha ao comunicar com Discord: {e}"}

        av = ""
        if me.get("avatar"):
            av = f"https://cdn.discordapp.com/avatars/{me['id']}/{me['avatar']}.png"
        uname = _ensure_local_user(me.get("username") or "discord", "discord", me.get("id", ""), av)
        return {"success": True, "user": uname, "output": f"Bem-vindo(a), {uname} (Discord)!"}
    finally:
        _oauth_lock.release()
