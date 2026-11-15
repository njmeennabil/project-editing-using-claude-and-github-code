"""Simple synthesised sound effects for the BUMI360 promo (no outside sound files needed).

python3 sfx.py <folder>  writes pop.wav, whoosh.wav, chime.wav … (48 kHz, mono, 16-bit).
"""
import math
import random
import struct
import sys
import wave
from pathlib import Path

SR = 48000


def _write(path, samples):
    peak = max(1e-9, max(abs(s) for s in samples))
    gain = 0.9 / peak
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s * gain)) * 32767)) for s in samples))


def _sweep(f0, f1, dur, decay, curve=1.0):
    out, ph = [], 0.0
    n = int(SR * dur)
    for i in range(n):
        x = i / n
        f = f0 + (f1 - f0) * (x ** curve)
        ph += 2 * math.pi * f / SR
        env = min(1.0, i / (SR * 0.004)) * math.exp(-i / (SR * decay))
        out.append(math.sin(ph) * env)
    return out


def _noise(dur, cutoff_fn, env_fn, seed=1, highpass=False):
    rnd = random.Random(seed)
    out, y, prev = [], 0.0, 0.0
    n = int(SR * dur)
    for i in range(n):
        x = i / n
        a = 1 - math.exp(-2 * math.pi * cutoff_fn(x) / SR)
        s = rnd.uniform(-1, 1)
        y += a * (s - y)
        v = (s - y) if highpass else y
        out.append(v * env_fn(x))
    return out


def _bell(freqs, dur, decay, amps=None):
    amps = amps or [1.0] * len(freqs)
    n = int(SR * dur)
    return [sum(a * math.sin(2 * math.pi * f * i / SR) * math.exp(-i / (SR * decay * (1 + 0.3 * k)))
                for k, (f, a) in enumerate(zip(freqs, amps))) * min(1.0, i / (SR * 0.003)) for i in range(n)]


def _mix(*parts):
    n = max(len(p) for _, p in parts)
    out = [0.0] * n
    for off, p in parts:
        o = int(off * SR)
        for i, v in enumerate(p):
            if o + i < n + int(0.5 * SR):
                if o + i >= len(out):
                    out.extend([0.0] * (o + i - len(out) + 1))
                out[o + i] += v
    return out


def sounds():
    return {
        "pop": _sweep(380, 920, 0.11, 0.035, 0.6),
        "bloop": _sweep(620, 1500, 0.16, 0.06, 0.5),
        "sprout": _sweep(260, 760, 0.42, 0.25, 0.8),
        "wilt": [v * (1 + 0.15 * math.sin(2 * math.pi * 6 * i / SR)) for i, v in enumerate(_sweep(520, 170, 0.8, 0.5, 1.0))],
        "coin": _mix((0, _bell([1976, 3950], 0.25, 0.05, [1, 0.3])), (0.06, _bell([2637, 5274], 0.35, 0.08, [1, 0.3]))),
        "flip": _noise(0.08, lambda x: 6000, lambda x: math.exp(-x * 6), seed=3, highpass=True),
        "swish": _noise(0.3, lambda x: 800 + 3000 * math.sin(math.pi * x), lambda x: math.sin(math.pi * x) ** 2, seed=5),
        "whoosh": _noise(0.5, lambda x: 400 + 2600 * math.sin(math.pi * x), lambda x: math.sin(math.pi * x) ** 2, seed=7),
        "wind": _noise(0.9, lambda x: 300 + 700 * math.sin(math.pi * x), lambda x: math.sin(math.pi * x) ** 2, seed=9),
        "chime": _mix((0, _bell([880, 1318.5, 2428], 1.2, 0.35, [1, 0.6, 0.15])), (0.09, _bell([1318.5, 1760], 1.1, 0.35, [0.7, 0.4]))),
        "chime_big": _mix((0, _bell([659.3, 1318.5, 1975.5], 1.8, 0.55, [1, 0.5, 0.25])),
                          (0.12, _bell([987.8, 1975.5], 1.6, 0.5, [0.8, 0.3])),
                          (0.24, _bell([1318.5, 2637], 1.5, 0.5, [0.8, 0.3]))),
        "tap": _mix((0, _sweep(1800, 1500, 0.04, 0.012)), (0, _noise(0.02, lambda x: 4000, lambda x: 1 - x, seed=11, highpass=True))),
        "tick": _mix((0, _bell([1046.5], 0.18, 0.05)), (0.07, _bell([1568], 0.3, 0.08))),
        "beeps": _mix(*[(k * 0.13, [math.copysign(1, math.sin(2 * math.pi * 1200 * i / SR)) * 0.35 * math.exp(-i / (SR * 0.05))
                                    for i in range(int(SR * 0.07))]) for k in range(3)]),
    }


def write_all(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name, samples in sounds().items():
        _write(folder / f"{name}.wav", samples)


if __name__ == "__main__":
    write_all(sys.argv[1] if len(sys.argv) > 1 else "assets/sfx")
