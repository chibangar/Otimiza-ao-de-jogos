"""Motor de voz parametrico — Midnight Optimizer.
Cada efeito = parametros. LIVE automatico se pitch==0 e sem vibrato.
"""
import numpy as np

SR = 48000

# pitch (semitons), drive (tanh), ring (Hz, 0=off), crush (bits, 0=off),
# hp/lp (Hz, 0=off), echo [(delay_s, decay)], wet, vib (rate, depth)|None
EFFECTS = [
    {"id": "normal", "name": "Clean Mic", "emoji": "🎙️", "color": "#d4af37",
     "cats": ["Humano"], "badge": "", "desc": "Voz limpa.",
     "p": {}},
    {"id": "robot", "name": "Robot", "emoji": "🤖", "color": "#4de1ff",
     "cats": ["Robotico"], "badge": "", "desc": "Metalico 8-bit.",
     "p": {"ring": 38, "crush": 6, "drive": 1.2}},
    {"id": "cyborg", "name": "Ciborgue", "emoji": "🦾", "color": "#4de1ff",
     "cats": ["Robotico", "Ficcao"], "badge": "NOVO", "desc": "Maquina pesada.",
     "p": {"ring": 62, "crush": 5, "drive": 2.0, "echo": [(0.05, 0.25)], "wet": 0.4}},
    {"id": "radio", "name": "Radio Guerra", "emoji": "📻", "color": "#ffb02e",
     "cats": ["Dispositivos", "FPS"], "badge": "HOT", "desc": "Walkie-talkie.",
     "p": {"hp": 700, "lp": 3400, "drive": 4.0}},
    {"id": "megaphone", "name": "Megafone", "emoji": "📢", "color": "#ffb02e",
     "cats": ["Dispositivos"], "badge": "", "desc": "Voz de estadio.",
     "p": {"hp": 500, "lp": 4000, "drive": 5.0}},
    {"id": "telephone", "name": "Telefone", "emoji": "☎️", "color": "#ffb02e",
     "cats": ["Dispositivos"], "badge": "", "desc": "Chamada antiga.",
     "p": {"hp": 900, "lp": 3000, "drive": 3.0}},
    {"id": "cave", "name": "Cave", "emoji": "🦇", "color": "#6a9bff",
     "cats": ["Profundo"], "badge": "", "desc": "Eco de gruta.",
     "p": {"echo": [(0.09, 0.45), (0.18, 0.3), (0.27, 0.2)], "wet": 0.55}},
    {"id": "cathedral", "name": "Catedral", "emoji": "⛪", "color": "#6a9bff",
     "cats": ["Profundo", "Musical"], "badge": "", "desc": "Reverb gigante.",
     "p": {"echo": [(0.18, 0.5), (0.34, 0.35), (0.5, 0.25)], "wet": 0.65}},
    {"id": "deep", "name": "Deep", "emoji": "🎩", "color": "#8a7bff",
     "cats": ["Profundo"], "badge": "", "desc": "Grave encorpado.",
     "p": {"drive": 4.0, "lp": 700, "echo": [(0.08, 0.25)], "wet": 0.35}},
    {"id": "abyss", "name": "Abismo", "emoji": "🕳️", "color": "#9d4edd",
     "cats": ["Terror", "Profundo"], "badge": "", "desc": "Grave do Vazio.",
     "p": {"drive": 6.0, "lp": 900, "echo": [(0.16, 0.5), (0.32, 0.3)], "wet": 0.6}},
    {"id": "demon", "name": "Demonio", "emoji": "😈", "color": "#ff3b3b",
     "cats": ["Terror"], "badge": "HOT", "desc": "Infernal (-6).",
     "p": {"pitch": -6, "drive": 3.5, "echo": [(0.12, 0.35)], "wet": 0.4}},
    {"id": "radiodemon", "name": "Radio Demon", "emoji": "👹", "color": "#ff3b3b",
     "cats": ["Terror", "Dispositivos"], "badge": "NOVO", "desc": "Radio do inferno.",
     "p": {"pitch": -4, "hp": 700, "lp": 3400, "drive": 4.0, "echo": [(0.1, 0.3)], "wet": 0.4}},
    {"id": "ghost", "name": "Fantasma", "emoji": "👻", "color": "#bfe9ff",
     "cats": ["Terror"], "badge": "NOVO", "desc": "Sussurro etereo.",
     "p": {"hp": 1500, "echo": [(0.2, 0.45), (0.4, 0.3)], "wet": 0.7, "gain": 0.8}},
    {"id": "chipmunk", "name": "Esquilo", "emoji": "🐿️", "color": "#5dff8a",
     "cats": ["Agudo", "Memes"], "badge": "HOT", "desc": "Agudo comico (+6).",
     "p": {"pitch": 6}},
    {"id": "helium", "name": "Helio", "emoji": "🎈", "color": "#5dff8a",
     "cats": ["Agudo"], "badge": "", "desc": "Balao de helio (+9).",
     "p": {"pitch": 9}},
    {"id": "baby", "name": "Bebe", "emoji": "👶", "color": "#5dff8a",
     "cats": ["Memes", "Agudo"], "badge": "", "desc": "Voz de bebe (+8).",
     "p": {"pitch": 8}},
    {"id": "alien", "name": "Alien", "emoji": "👽", "color": "#c86bff",
     "cats": ["Ficcao"], "badge": "", "desc": "Vibrato espacial.",
     "p": {"pitch": 5, "vib": (7.0, 0.012), "ring": 55}},
    {"id": "space", "name": "Space Captain", "emoji": "🚀", "color": "#c86bff",
     "cats": ["Ficcao"], "badge": "", "desc": "Capacete espacial.",
     "p": {"ring": 90, "echo": [(0.14, 0.4), (0.28, 0.25)], "wet": 0.5}},
    {"id": "echo", "name": "Echo", "emoji": "🔊", "color": "#7ef0c1",
     "cats": ["Musical"], "badge": "", "desc": "Eco ritmado.",
     "p": {"echo": [(0.22, 0.5), (0.44, 0.32)], "wet": 0.6}},
    {"id": "choir", "name": "Coro", "emoji": "🎶", "color": "#7ef0c1",
     "cats": ["Musical"], "badge": "NOVO", "desc": "Voz angelical (+3).",
     "p": {"pitch": 3, "echo": [(0.12, 0.4), (0.25, 0.25)], "wet": 0.5}},
    {"id": "narrator", "name": "Narrador", "emoji": "🎬", "color": "#e8c872",
     "cats": ["Interpretacao"], "badge": "", "desc": "Voz de cinema.",
     "p": {"drive": 2.0, "lp": 5000, "echo": [(0.06, 0.2)], "wet": 0.25}},
    {"id": "villain", "name": "Vilao", "emoji": "🦹", "color": "#ff7b2e",
     "cats": ["Interpretacao", "Terror"], "badge": "NOVO", "desc": "Mau da fita (-3).",
     "p": {"pitch": -3, "drive": 4.0, "echo": [(0.14, 0.35)], "wet": 0.45}},
]

BY_ID = {e["id"]: e for e in EFFECTS}
CATS = ["Todos", "Memes", "Agudo", "Humano", "Dispositivos", "Profundo",
        "Terror", "FPS", "Musical", "Ficcao", "Robotico", "Interpretacao"]


def is_live(e):
    return True


# ---------- primitivas ----------
def _pitch_shift(x, semitones):
    if not semitones or len(x) == 0:
        return x
    factor = 2.0 ** (semitones / 12.0)
    new_n = max(1, int(len(x) / factor))
    return np.interp(np.linspace(0, len(x) - 1, new_n),
                     np.arange(len(x)), x).astype(np.float32)


def _smoothstep(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def _fft_filter(x, sr, hp=0, lp=0):
    if (not hp and not lp) or len(x) == 0:
        return x
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1.0 / sr)
    mask = np.ones_like(f)
    if hp:
        mask *= _smoothstep((f - hp) / (hp * 0.25 + 50))
    if lp:
        mask *= 1.0 - _smoothstep((f - lp) / (lp * 0.25 + 50))
    return np.fft.irfft(X * mask, n).astype(np.float32)


def _echo_taps(x, sr, taps, wet):
    if not taps:
        return x
    y = x.copy()
    for delay_s, decay in taps:
        d = int(delay_s * sr)
        if 0 < d < len(x):
            tail = np.zeros_like(x)
            tail[d:] = x[:-d] * decay
            y = y + tail
    return (x * (1.0 - wet) + y * wet).astype(np.float32)


def _norm(y, gain=1.0):
    y = y * gain
    m = np.max(np.abs(y)) if len(y) else 0
    if m > 0.99:
        y = (y * (0.99 / m)).astype(np.float32)
    return y.astype(np.float32)


# ---------- OFFLINE (todos) ----------
def transform(x, effect_id, sr=SR, gain=1.5):
    x = np.asarray(x, dtype=np.float32).ravel()
    e = BY_ID.get(effect_id, BY_ID["normal"])
    p = e["p"]
    y = _pitch_shift(x, p.get("pitch", 0))
    vib = p.get("vib")
    if vib and len(y):
        rate, depth = vib
        t = np.arange(len(y)) / sr
        idx = np.clip(np.cumsum(1.0 + depth * 40 * np.sin(2 * np.pi * rate * t)), 0, len(y) - 1)
        y = np.interp(idx, np.arange(len(y)), y).astype(np.float32)
    if p.get("ring"):
        t = np.arange(len(y)) / sr
        y = (y * (0.6 + 0.4 * np.sin(2 * np.pi * p["ring"] * t))).astype(np.float32)
    if p.get("crush"):
        lv = float(2 ** p["crush"] - 1)
        y = (np.round(np.clip(y * 1.6, -1, 1) * lv) / lv).astype(np.float32)
    y = _fft_filter(y, sr, p.get("hp", 0), p.get("lp", 0))
    if p.get("drive", 0):
        y = np.tanh(y * p["drive"]).astype(np.float32)
    if effect_id == "radio":
        y = (y + (np.random.rand(len(y)).astype(np.float32) - 0.5) * 0.02).astype(np.float32)
    y = _echo_taps(y, sr, p.get("echo", []), p.get("wet", 0.5))
    return _norm(y, gain * p.get("gain", 1.0))


# ---------- LIVE (tudo ao vivo; pitch via reamostragem em anel) ----------
def new_state(effect_id):
    maxd = int(0.55 * SR) + 16
    return {"id": effect_id, "phase": 0.0, "lp": 0.0, "lp2": 0.0,
            "hpx": 0.0, "hpy": 0.0, "buf": np.zeros(maxd, dtype=np.float32), "pos": 0,
            "pring": np.zeros(8192, dtype=np.float32), "pwpos": 0,
            "ptail": np.zeros(128, dtype=np.float32),
            "vphase": 0.0, "vring": np.zeros(2048, dtype=np.float32), "vwpos": 0}


def _live_pitch(x, st, sr, semitones):
    """Muda o tom em tempo real: janelas adjacentes + micro-cortes com crossfade.
    Mantem o tom certo; textura levemente granular (aceitavel p/ brinquedo)."""
    f = 2.0 ** (semitones / 12.0)
    n = len(x)
    R = len(st["pring"])
    ring = st["pring"]
    wpos = st["pwpos"]
    idx = (wpos + np.arange(n)) % R
    ring[idx] = x
    wpos += n
    M = max(1, int(round(n * f)))
    if st.get("pitch_f") != f or "rpos" not in st:
        st["rpos"] = float(wpos - M)
        st["pitch_f"] = f
    rpos = st["rpos"] + M  # janelas adjacentes (sem buracos)
    lag = wpos - rpos
    if lag > 3072:      # a descer: larga o excesso (ms, inaudivel)
        rpos += lag - 3072
    elif lag < 1024:    # a subir: repete o excesso
        rpos -= 1024 - lag
    if rpos < wpos - R + 8:
        rpos = float(wpos - R + 8)
    if rpos + M > wpos - 8:
        rpos = float(wpos - 8 - M)
    base = int(np.floor(rpos))
    frac = rpos - base
    g0 = ring[(base + np.arange(M)) % R]
    g1 = ring[(base + 1 + np.arange(M)) % R]
    win = g0 * (1 - frac) + g1 * frac
    y = np.interp(np.linspace(0, M - 1, n), np.arange(M), win).astype(np.float32)
    st["rpos"] = rpos
    st["pwpos"] = wpos
    K = min(128, n)
    fade = np.linspace(0, 1, K, dtype=np.float32)
    y[:K] = st["ptail"][:K] * (1 - fade) + y[:K] * fade
    st["ptail"] = y[-128:].copy() if n >= 128 else np.concatenate([st["ptail"][n:], y])[-128:]
    return y


def _live_vibrato(x, st, sr, rate, depth):
    """Vibrato com linha de atraso modulada (com estado)."""
    n = len(x)
    VR = len(st["vring"])
    vring, wpos = st["vring"], st["vwpos"]
    idx = (wpos + np.arange(n)) % VR
    vring[idx] = x
    wpos += n
    st["vwpos"] = wpos
    t = (np.arange(n) + st["vphase"]) / sr
    st["vphase"] = (st["vphase"] + n) % sr
    d0, amp = 0.004 * sr, depth * sr * 0.15
    delay = d0 + amp * np.sin(2 * np.pi * rate * t)
    rpos = wpos - n + np.arange(n) - delay
    lo = np.floor(rpos).astype(int)
    frac = (rpos - lo).astype(np.float32)
    y = vring[lo % VR] * (1 - frac) + vring[(lo + 1) % VR] * frac
    return y.astype(np.float32)


def process_block(x, effect_id, state, sr=SR, gain=1.5):
    x = np.asarray(x, dtype=np.float32).ravel()
    e = BY_ID.get(effect_id, BY_ID["normal"])
    p = e["p"]
    n = len(x)
    y = x.astype(np.float32)

    if p.get("pitch"):
        y = _live_pitch(y, state, sr, p["pitch"])
    vib = p.get("vib")
    if vib:
        y = _live_vibrato(y, state, sr, vib[0], vib[1])
    if p.get("ring"):
        t = (np.arange(n) + state["phase"]) / sr
        state["phase"] = (state["phase"] + n) % sr
        y = (y * (0.6 + 0.4 * np.sin(2 * np.pi * p["ring"] * t))).astype(np.float32)
    if p.get("crush"):
        lv = float(2 ** p["crush"] - 1)
        y = (np.round(np.clip(y * 1.6, -1, 1) * lv) / lv).astype(np.float32)
    if p.get("hp"):
        a = 1.0 / (1.0 + (2 * np.pi * p["hp"]) / sr)
        out = np.zeros_like(y)
        px, py = state["hpx"], state["hpy"]
        for i, v in enumerate(y):
            hp = a * (py + v - px)
            px, py = v, hp
            out[i] = hp
        y = out
        state["hpx"], state["hpy"] = px, py
    if p.get("lp"):
        a = 1.0 / (1.0 + sr / (2 * np.pi * p["lp"]))
        out = np.zeros_like(y)
        acc = state["lp"]
        for i, v in enumerate(y):
            acc += a * (v - acc)
            out[i] = acc
        y = out
        state["lp"] = acc
    if p.get("drive"):
        y = np.tanh(y * p["drive"]).astype(np.float32)
    taps = p.get("echo", [])
    if taps:
        buf, pos = state["buf"], state["pos"]
        maxd = max(int(dd * sr) for dd, _ in taps) + 1
        out = np.zeros_like(y)
        wet = p.get("wet", 0.5)
        for i, v in enumerate(y):
            acc = 0.0
            for dd, dec in taps:
                acc += buf[(pos - int(dd * sr)) % len(buf)] * dec
            out[i] = v * (1.0 - wet) + (v + acc) * wet
            buf[pos] = v + acc * 0.5
            pos = (pos + 1) % len(buf)
        y = out
        state["pos"] = pos
    return _norm(y, gain * p.get("gain", 1.0))


def live_ok(effect_id):
    return BY_ID.get(effect_id) is not None
