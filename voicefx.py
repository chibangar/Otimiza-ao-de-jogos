"""DSP dos efeitos de voz — Midnight Optimizer.
Efeitos LIVE (stream-safe, sem mudar duracao): normal, robot, radio, cave, abyss.
Efeitos OFFLINE (gravacao -> transformacao): todos + demon, chipmunk, alien.
"""
import numpy as np

SR = 48000

EFFECTS = [
    {"id": "normal", "name": "Original", "emoji": "🎙️", "live": True,
     "desc": "Voz limpa, so com ganho.", "color": "#d4af37"},
    {"id": "robot", "name": "Robot", "emoji": "🤖", "live": True,
     "desc": "Metalico, modulacao + 8-bit.", "color": "#4de1ff"},
    {"id": "radio", "name": "Radio", "emoji": "📻", "live": True,
     "desc": "Walkie-talkie com fritacao.", "color": "#ffb02e"},
    {"id": "cave", "name": "Caverna", "emoji": "🦇", "live": True,
     "desc": "Eco profundo de gruta.", "color": "#6a9bff"},
    {"id": "abyss", "name": "Abismo", "emoji": "🕳️", "live": True,
     "desc": "Grave distorcido do Vazio.", "color": "#9d4edd"},
    {"id": "demon", "name": "Demonio", "emoji": "😈", "live": False,
     "desc": "Grave infernal (-6 tons).", "color": "#ff3b3b"},
    {"id": "chipmunk", "name": "Esquilo", "emoji": "🐿️", "live": False,
     "desc": "Agudo comico (+6 tons).", "color": "#5dff8a"},
    {"id": "alien", "name": "Alien", "emoji": "👽", "live": False,
     "desc": "Vibrato espacial (+5 tons).", "color": "#c86bff"},
]

BY_ID = {e["id"]: e for e in EFFECTS}


# ---------- blocos basicos ----------
def _tanh_drive(x, drive=3.0):
    return np.tanh(x * drive).astype(np.float32)


def _bitcrush(x, bits=6):
    levels = float(2 ** bits - 1)
    return (np.round(x * levels) / levels).astype(np.float32)


def _pitch_shift(x, semitones):
    """Offline: muda o tom (muda tambem a duracao)."""
    if len(x) == 0:
        return x
    factor = 2.0 ** (semitones / 12.0)
    n = len(x)
    new_n = max(1, int(n / factor))
    idx = np.linspace(0, n - 1, new_n)
    return np.interp(idx, np.arange(n), x).astype(np.float32)


def _echo_taps(x, sr, taps=((0.09, 0.45), (0.18, 0.3), (0.27, 0.2)), wet=0.55):
    y = x.copy()
    for delay_s, decay in taps:
        d = int(delay_s * sr)
        if d < len(x):
            tail = np.zeros_like(x)
            tail[d:] = x[:-d] * decay
            y = y + tail
    m = np.max(np.abs(y))
    if m > 0.99:
        y = y * (0.99 / m)
    return (x * (1.0 - wet) + y * wet).astype(np.float32)


def _lp_dull(x, sr, fc=1200.0):
    rc = 1.0 / (2 * np.pi * fc)
    a = (1.0 / sr) / (rc + 1.0 / sr)
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


# ---------- estado LIVE ----------
def new_state(effect_id):
    return {"phase": 0.0, "lp": 0.0, "hp_prev_x": 0.0, "hp_prev_y": 0.0,
            "lp2": 0.0, "id": effect_id}


def _live_robot(x, st, sr, gain):
    # AM 38 Hz + bitcrush (fase continua entre blocos)
    n = len(x)
    t = (np.arange(n) + st["phase"]) / sr
    st["phase"] = (st["phase"] + n) % sr
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * 38.0 * t)
    y = x * mod
    y = _bitcrush(np.clip(y * 1.6, -1, 1), 6)
    return (y * gain).astype(np.float32)


def _live_radio(x, st, sr, gain):
    # passa-banda simples com filtros one-pole + drive
    a_lp = 1.0 / (1.0 + sr / (2 * np.pi * 3400.0))
    a_hp = 1.0 / (1.0 + (2 * np.pi * 700.0) / sr)
    out = np.zeros_like(x)
    lp = st["lp2"]
    px, py = st["hp_prev_x"], st["hp_prev_y"]
    for i, v in enumerate(x):
        lp += a_lp * (v - lp)
        hp = a_hp * (py + lp - px)
        px, py = lp, hp
        out[i] = np.tanh(hp * 4.0)
    st["lp2"], st["hp_prev_x"], st["hp_prev_y"] = lp, px, py
    noise = (np.random.rand(len(x)).astype(np.float32) - 0.5) * 0.02
    return ((out + noise) * gain).astype(np.float32)


def _live_cave(x, st, sr, gain):
    # delay simples com buffer persistente (eco curto, sem mudar duracao)
    d = int(0.11 * sr)
    buf = st.get("buf")
    if buf is None or len(buf) != d:
        buf = np.zeros(d, dtype=np.float32)
        st["buf"] = buf
        st["pos"] = 0
    pos = st["pos"]
    out = np.zeros_like(x)
    for i, v in enumerate(x):
        echo = buf[pos]
        out[i] = v * 0.6 + echo * 0.55
        buf[pos] = v * 0.7 + echo * 0.45
        pos = (pos + 1) % d
    st["pos"] = pos
    return (out * gain).astype(np.float32)


def _live_abyss(x, st, sr, gain):
    y = _tanh_drive(x, 6.0)
    y = _lp_dull(y, sr, 900.0)
    # pequeno eco
    d = int(0.16 * sr)
    buf = st.get("buf2")
    if buf is None or len(buf) != d:
        buf = np.zeros(d, dtype=np.float32)
        st["buf2"] = buf
        st["pos2"] = 0
    pos = st["pos2"]
    out = np.zeros_like(y)
    for i, v in enumerate(y):
        echo = buf[pos]
        out[i] = v * 0.65 + echo * 0.5
        buf[pos] = v * 0.6 + echo * 0.4
        pos = (pos + 1) % d
    st["pos2"] = pos
    return (out * gain).astype(np.float32)


def process_block(x, effect_id, state, sr=SR, gain=1.5):
    x = np.asarray(x, dtype=np.float32).ravel()
    if effect_id == "robot":
        return _live_robot(x, state, sr, gain)
    if effect_id == "radio":
        return _live_radio(x, state, sr, gain)
    if effect_id == "cave":
        return _live_cave(x, state, sr, gain)
    if effect_id == "abyss":
        return _live_abyss(x, state, sr, gain)
    return (x * gain).astype(np.float32)


# ---------- transformacao OFFLINE ----------
def transform(x, effect_id, sr=SR, gain=1.5):
    x = np.asarray(x, dtype=np.float32).ravel()
    if effect_id == "normal":
        y = x
    elif effect_id == "robot":
        t = np.arange(len(x)) / sr
        y = _bitcrush(np.clip(x * (0.55 + 0.45 * np.sin(2 * np.pi * 38.0 * t)) * 1.6, -1, 1), 6)
    elif effect_id == "radio":
        y = _live_radio(x, new_state("radio"), sr, 1.0)
        y = _tanh_drive(y, 2.0)
    elif effect_id == "cave":
        y = _echo_taps(x, sr)
    elif effect_id == "abyss":
        y = _lp_dull(_tanh_drive(x, 6.0), sr, 900.0)
        y = _echo_taps(y, sr, taps=((0.16, 0.5), (0.32, 0.3)), wet=0.6)
    elif effect_id == "demon":
        y = _pitch_shift(x, -6)
        y = _tanh_drive(y, 3.5)
        y = _echo_taps(y, sr, taps=((0.12, 0.35),), wet=0.4)
    elif effect_id == "chipmunk":
        y = _pitch_shift(x, 6)
    elif effect_id == "alien":
        y = _pitch_shift(x, 5)
        t = np.arange(len(y)) / sr
        vib = 1.0 + 0.012 * np.sin(2 * np.pi * 7.0 * t)  # vibrato
        idx = np.clip(np.cumsum(vib), 0, len(y) - 1)
        y = np.interp(idx, np.arange(len(y)), y)
        y = (y * (0.6 + 0.4 * np.sin(2 * np.pi * 55.0 * t))).astype(np.float32)
    else:
        y = x
    y = y * gain
    m = np.max(np.abs(y)) if len(y) else 0
    if m > 0.99:
        y = (y * (0.99 / m)).astype(np.float32)
    return y.astype(np.float32)
