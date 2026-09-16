"""Pessoas online + chat (geral + mensagens privadas) sem servidor próprio.

Usa um broker MQTT público gratuito (broker.emqx.io) só como "correio":
- Presença: tópico retained por cliente + LWT (testamento) + heartbeat 30s.
  Pares sem sinal há +150s são considerados offline.
- Chat geral: um tópico partilhado (últimas 200 msgs em memória).
- Privadas: um tópico por cliente (só o destinatário recebe).

Tudo corre em 2º plano e nunca bloqueia a UI. Sem paho-mqtt instalado,
as funções devolvem erro amigável em vez de rebentar.
"""
import json
import threading
import time
import uuid

try:
    import paho.mqtt.client as mqtt
    _MQTT_OK = True
except Exception:
    mqtt = None
    _MQTT_OK = False

BROKER = "broker.emqx.io"
PORT = 1883
ROOT = "midnightopt/v1"
HEARTBEAT = 30
EXPIRE = 150
MAX_TEXT = 500
LOBBY_KEEP = 200
DM_KEEP = 200


def _now():
    return time.strftime("%H:%M")


_lock = threading.RLock()
_client = None
_hb_stop = None
_me = {"user": "", "cid": ""}
_peers = {}   # cid -> {"name": str, "ts": float}
_lobby = []   # {"id","from","fid","text","ts","mine"}
_dms = {}     # peer_cid -> [{"id","from","from_name","text","ts","mine"}]
_seq = [0]
_connected = [False]
_error = [""]


def _next_id():
    with _lock:
        _seq[0] += 1
        return _seq[0]


def _presence_topic(cid):
    return f"{ROOT}/presence/{cid}"


def _pub_presence(client, cid, user, offline=False):
    try:
        payload = json.dumps({"u": user[:16], "ts": time.time(),
                              "off": bool(offline)}, ensure_ascii=False)
        client.publish(_presence_topic(cid), payload, qos=1, retain=True)
    except Exception:
        pass


def _prune():
    now = time.time()
    dead = [c for c, p in _peers.items() if now - p.get("ts", 0) > EXPIRE]
    for c in dead:
        _peers.pop(c, None)


def _on_connect(client, userdata, flags, rc, properties=None):
    with _lock:
        _connected[0] = (rc == 0)
        _error[0] = "" if rc == 0 else f"Broker recusou (código {rc})."
    if rc != 0:
        return
    try:
        cid = _me.get("cid", "")
        client.subscribe(f"{ROOT}/presence/+", qos=1)
        client.subscribe(f"{ROOT}/lobby", qos=1)
        client.subscribe(f"{ROOT}/dm/{cid}", qos=1)
        _pub_presence(client, cid, _me.get("user", ""))
    except Exception as e:
        with _lock:
            _error[0] = str(e)


def _on_disconnect(client, userdata, flags, rc, properties=None):
    with _lock:
        _connected[0] = False


def _on_message(client, userdata, msg):
    try:
        topic = msg.topic or ""
        data = json.loads(msg.payload.decode("utf-8", "ignore") or "{}")
    except Exception:
        return
    if not isinstance(data, dict):
        return
    with _lock:
        mine_cid = _me.get("cid", "")
        if topic.startswith(f"{ROOT}/presence/"):
            cid = topic.rsplit("/", 1)[-1]
            if cid == mine_cid:
                return
            if data.get("off"):
                _peers.pop(cid, None)
            else:
                name = str(data.get("u", "?"))[:16] or "?"
                _peers[cid] = {"name": name, "ts": float(data.get("ts", 0) or 0)}
        elif topic == f"{ROOT}/lobby":
            text = str(data.get("t", ""))[:MAX_TEXT]
            if not text.strip():
                return
            _lobby.append({"id": _next_id(),
                           "from": str(data.get("f", "?"))[:16],
                           "fid": str(data.get("fi", ""))[:16],
                           "text": text, "ts": str(data.get("ts") or _now()),
                           "mine": str(data.get("fi", "")) == mine_cid})
            del _lobby[:-LOBBY_KEEP]
        elif topic == f"{ROOT}/dm/{mine_cid}":
            text = str(data.get("t", ""))[:MAX_TEXT]
            sender = str(data.get("fi", ""))[:16]
            if not text.strip() or not sender:
                return
            _dms.setdefault(sender, []).append(
                {"id": _next_id(), "from": sender,
                 "from_name": str(data.get("f", "?"))[:16],
                 "text": text, "ts": str(data.get("ts") or _now()),
                 "mine": False})
            if len(_dms[sender]) > DM_KEEP:
                del _dms[sender][:-DM_KEEP]


def _heartbeat_loop(cid):
    while True:
        for _ in range(HEARTBEAT * 2):
            time.sleep(0.5)
            if _hb_stop is not None and _hb_stop.is_set():
                return
        try:
            c = None
            with _lock:
                c = _client
                user = _me.get("user", "")
            if c is not None:
                _pub_presence(c, cid, user)
        except Exception:
            pass


def _clean_name(name):
    name = (name or "").strip()[:16] or "player"
    return "".join(c for c in name if c.isprintable()) or "player"


def start(user):
    """Liga ao broker como `user`. Idempotente (mesmo user = mantém)."""
    global _client, _hb_stop
    if not _MQTT_OK:
        return {"success": False,
                "output": "Falta: pip install paho-mqtt (corre o build_exe.bat)."}
    user = _clean_name(user)
    with _lock:
        if _client is not None and _me.get("user") == user and _connected[0]:
            return {"success": True, "output": f"Online como {user}. ✔"}
    stop()
    cid = "mid-" + uuid.uuid4().hex[:8]
    try:
        c = mqtt.Client(client_id=cid, protocol=mqtt.MQTTv5)
    except Exception:
        try:
            c = mqtt.Client(client_id=cid)
        except Exception as e:
            return {"success": False, "output": f"MQTT falhou: {e}"}
    try:
        c.will_set(_presence_topic(cid),
                   json.dumps({"u": user, "ts": time.time(), "off": True}),
                   qos=1, retain=True)
    except Exception:
        pass
    c.on_connect = _on_connect
    c.on_disconnect = _on_disconnect
    c.on_message = _on_message
    with _lock:
        _client = c
        _me.update({"user": user, "cid": cid})
        _peers.clear()
        _error[0] = ""
    try:
        c.connect_async(BROKER, PORT, keepalive=60)
        c.loop_start()
    except Exception as e:
        with _lock:
            _error[0] = str(e)
            _client = None
        return {"success": False, "output": f"Sem ligação ao broker: {e}"}
    with _lock:
        _hb_stop = threading.Event()
    threading.Thread(target=_heartbeat_loop, args=(cid,), daemon=True).start()
    return {"success": True, "output": f"A ligar como {user}…"}


def stop():
    global _client, _hb_stop
    with _lock:
        c, cid, user = _client, _me.get("cid", ""), _me.get("user", "")
        _client = None
        _connected[0] = False
        hb = _hb_stop
        _hb_stop = None
    try:
        if hb is not None:
            hb.set()
    except Exception:
        pass
    try:
        if c is not None:
            if cid:
                _pub_presence(c, cid, user, offline=True)
            c.disconnect()
            c.loop_stop()
    except Exception:
        pass
    return {"success": True}


def state():
    with _lock:
        _prune()
        users = [{"id": c, "name": p["name"]}
                 for c, p in sorted(_peers.items(),
                                    key=lambda kv: kv[1]["name"].lower())]
        return {"success": True, "connected": _connected[0],
                "me": dict(_me), "users": users, "error": _error[0]}


def _check_ready():
    if not _MQTT_OK:
        return {"success": False, "output": "Falta: pip install paho-mqtt."}
    with _lock:
        ok = _client is not None and _connected[0]
        err = _error[0]
    if not ok:
        return {"success": False,
                "output": err or "Ainda a ligar… tenta dentro de segundos."}
    return None


def lobby_send(text):
    bad = _check_ready()
    if bad:
        return bad
    text = (text or "").strip()[:MAX_TEXT]
    if not text:
        return {"success": False, "output": "Escreve primeiro."}
    with _lock:
        c, user, cid = _client, _me["user"], _me["cid"]
    try:
        c.publish(f"{ROOT}/lobby",
                  json.dumps({"f": user, "fi": cid, "t": text, "ts": _now()},
                             ensure_ascii=False), qos=1)
        return {"success": True}
    except Exception as e:
        return {"success": False, "output": f"Falha a enviar: {e}"}


def lobby_fetch(after=0):
    try:
        after = int(after)
    except Exception:
        after = 0
    with _lock:
        return {"success": True, "msgs": [m for m in _lobby if m["id"] > after]}


def dm_send(peer_cid, text):
    bad = _check_ready()
    if bad:
        return bad
    peer_cid = (peer_cid or "").strip()[:16]
    text = (text or "").strip()[:MAX_TEXT]
    if not peer_cid:
        return {"success": False, "output": "Escolhe uma pessoa."}
    if not text:
        return {"success": False, "output": "Escreve primeiro."}
    with _lock:
        c, user, cid = _client, _me["user"], _me["cid"]
        peer_name = _peers.get(peer_cid, {}).get("name", "")
        if not peer_name:
            for msgs in _dms.values():
                for m in msgs:
                    if m.get("from") == peer_cid and m.get("from_name"):
                        peer_name = m["from_name"]
                        break
    try:
        c.publish(f"{ROOT}/dm/{peer_cid}",
                  json.dumps({"f": user, "fi": cid, "t": text, "ts": _now()},
                             ensure_ascii=False), qos=1)
    except Exception as e:
        return {"success": False, "output": f"Falha a enviar: {e}"}
    with _lock:
        _dms.setdefault(peer_cid, []).append(
            {"id": _next_id(), "from": cid, "from_name": user,
             "text": text, "ts": _now(), "mine": True,
             "to_name": peer_name})
        if len(_dms[peer_cid]) > DM_KEEP:
            del _dms[peer_cid][:-DM_KEEP]
    return {"success": True}


def dm_fetch(peer_cid, after=0):
    try:
        after = int(after)
    except Exception:
        after = 0
    with _lock:
        msgs = _dms.get((peer_cid or "").strip()[:16], [])
        return {"success": True,
                "msgs": [m for m in msgs if m["id"] > after]}


def dm_threads():
    with _lock:
        _prune()
        out = []
        for cid, msgs in _dms.items():
            if not msgs:
                continue
            name = _peers.get(cid, {}).get("name", "")
            if not name:
                for m in reversed(msgs):
                    if not m.get("mine") and m.get("from_name"):
                        name = m["from_name"]
                        break
                    if m.get("mine") and m.get("to_name"):
                        name = m["to_name"]
                        break
            out.append({"id": cid, "name": name or "?", "last": msgs[-1]["text"][:60],
                        "n": len(msgs),
                        "online": cid in _peers})
        out.sort(key=lambda t: t["name"].lower())
        return {"success": True, "threads": out}
