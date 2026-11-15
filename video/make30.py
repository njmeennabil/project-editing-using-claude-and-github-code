#!/usr/bin/env python3
"""Build the 30-second cut of the BUMI360 promo (voice-over, screen track, sound effects).

Usage:  python3 make30.py <folder with scene1.m4a … scene7.m4a>
Needs ffmpeg. Run after prepare.sh (uses assets/screen-track.mp4).

1. Shortens long pauses inside each voice-over and speeds it up just enough to fit 30 s.
2. Writes assets/cut30.json: how 30-s time maps onto the 43-s animation, so pictures stay
   in sync with the words.
3. Builds assets/screen-track-30.mp4 and assets/audio-30.m4a (voice-over + sound effects).
"""
import json
import subprocess
import sys
from pathlib import Path

import sfx

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
SRC = Path(sys.argv[1])

TOTAL = 30.0
FIRST = 0.15          # first words start here
GAP = 0.10            # between scenes
HOLD = 1.1            # end card stays after the last word
PAUSE = 0.12          # long pauses inside a scene shrink to this
MIN_PAUSE = 0.30      # pauses at least this long get shortened
BLOCK = 0.05          # analysis window (s)
SPEECH_DB = -42.0

# The 43-s version (prepare.sh): seconds kept from each file, and where it starts.
KEEP43 = [5.25, 5.70, 1.95, 8.80, 6.70, 6.40, 4.00]
START43 = [0.40, 5.95, 12.00, 14.05, 23.20, 30.25, 37.00]
END43 = 43.0


def run(cmd):
    subprocess.run(cmd, check=True)


def rms_blocks(path, keep):
    """RMS level (dB) per 50 ms block of the first `keep` seconds."""
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-t", str(keep), "-i", str(path), "-ac", "1", "-ar", "48000",
         "-af", f"asetnsamples={int(48000 * BLOCK)},astats=metadata=1:reset=1,"
                "ametadata=print:key=lavfi.astats.Overall.RMS_level", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    vals = []
    for line in out.splitlines():
        if "RMS_level=" in line:
            v = line.split("RMS_level=")[1].strip()
            vals.append(-120.0 if v.startswith("-inf") else float(v))
    return vals


def speech_segments(levels, keep):
    """Speech runs [(start, end)] split wherever there is a pause of MIN_PAUSE or more."""
    talk = [v > SPEECH_DB for v in levels]
    idx = [i for i, t in enumerate(talk) if t]
    if not idx:
        return [(0.0, keep)]
    segs, start, last = [], idx[0], idx[0]
    for i in idx[1:]:
        if (i - last - 1) * BLOCK >= MIN_PAUSE:
            segs.append((start, last))
            start = i
        last = i
    segs.append((start, last))
    out = []
    for a, b in segs:
        s = max(0.0, a * BLOCK - 0.05)
        e = min(keep, (b + 1) * BLOCK + 0.08)
        out.append((round(s, 3), round(e, 3)))
    return out


# ---------- 1. analyse the voice-overs ----------
scenes = []
for i in range(7):
    path = SRC / f"scene{i + 1}.m4a"
    segs = speech_segments(rms_blocks(path, KEEP43[i]), KEEP43[i])
    length = sum(e - s for s, e in segs) + PAUSE * (len(segs) - 1)
    scenes.append({"path": path, "segs": segs, "len": length})

speech = sum(s["len"] for s in scenes)
tempo = max(1.0, speech / (TOTAL - FIRST - GAP * 6 - HOLD))
print(f"speech after shortening pauses: {speech:.2f}s  ->  tempo {tempo:.3f}x")
for i, s in enumerate(scenes):
    print(f"  scene{i + 1}: {len(s['segs'])} parts, {s['len']:.2f}s -> {s['len'] / tempo:.2f}s")

# ---------- 2. placement and time map (43-s time  <->  30-s time) ----------
anchors = [(0.0, 0.0)]
t = FIRST
for i, s in enumerate(scenes):
    s["start30"] = t
    pos = 0.0
    for a, b in s["segs"]:
        anchors.append((START43[i] + a, t + pos / tempo))
        pos += b - a
        anchors.append((START43[i] + b, t + pos / tempo))
        pos += PAUSE
    t += s["len"] / tempo
    anchors.append((START43[i] + KEEP43[i], t))
    t += GAP
anchors.append((END43, TOTAL))
# keep strictly increasing in both directions
clean = [anchors[0]]
for a in anchors[1:]:
    if a[0] > clean[-1][0] + 1e-6 and a[1] >= clean[-1][1]:
        clean.append(a)
anchors = clean


def to30(t43):
    for (o0, n0), (o1, n1) in zip(anchors, anchors[1:]):
        if t43 <= o1:
            return n0 + (n1 - n0) * (t43 - o0) / (o1 - o0)
    return TOTAL


slide = [round(to30(36.5), 3), round(to30(37.2), 3)]
(ASSETS / "cut30.json").write_text(json.dumps({"duration": TOTAL, "anchors": anchors, "slide": slide}, indent=1))

# ---------- 3a. voice-over, 30 s ----------
inputs, parts, labels = [], [], []
for i, s in enumerate(scenes):
    inputs += ["-i", str(s["path"])]
    chain = []
    for j, (a, b) in enumerate(s["segs"]):
        lab = f"s{i}p{j}"
        parts.append(f"[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                     f"afade=t=in:d=0.02,afade=t=out:st={max(0, b - a - 0.04):.3f}:d=0.04[{lab}]")
        chain.append(f"[{lab}]")
        if j < len(s["segs"]) - 1:
            sl = f"s{i}g{j}"
            parts.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{PAUSE}[{sl}]")
            chain.append(f"[{sl}]")
    parts.append(f"{''.join(chain)}concat=n={len(chain)}:v=0:a=1,atempo={tempo:.4f},"
                 f"adelay={int(round(s['start30'] * 1000))}:all=1[v{i}]")
    labels.append(f"[v{i}]")
parts.append(f"{''.join(labels)}amix=inputs=7:normalize=0,apad=whole_dur={TOTAL},atrim=0:{TOTAL}[vo]")
vo30 = ASSETS / "voiceover-30.wav"
run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[vo]", "-ar", "48000", str(vo30)])

# ---------- 3b. screen track, 30 s ----------
# Each recorded scene keeps its clips, sped up to the scene's new length.
marks43 = [13.8, 14.05, 23.2, 30.25, 37.0, 38.2]
marks30 = [to30(m) for m in marks43]
vf, cat = [], []
for k in range(len(marks43) - 1):
    a43, b43, a30, b30 = marks43[k], marks43[k + 1], marks30[k], marks30[k + 1]
    vf.append(f"[0:v]trim=start={a43}:end={b43},setpts=(PTS-STARTPTS)*{(b30 - a30) / (b43 - a43):.5f},fps=30[r{k}]")
    cat.append(f"[r{k}]")
vf.append(f"{''.join(cat)}concat=n={len(cat)}:v=1:a=0,tpad=start_duration={marks30[0]:.3f}:start_mode=add:color=black:"
          f"stop_mode=clone:stop_duration=10,trim=0:{TOTAL},setpts=PTS-STARTPTS[v]")
run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ASSETS / "screen-track.mp4"), "-filter_complex", ";".join(vf),
     "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(ASSETS / "screen-track-30.mp4")])

# ---------- 3c. sound effects ----------
# Times are on the 43-s animation timeline ("T"), or on the original drawing timeline ("o").
MAP = [[0, 0], [5.0, 5.8], [9.4, 11.7], [12.0, 13.9], [18.0, 23.0], [23.9, 30.1], [26.8, 36.8], [30, 43]]


def o_to_T(o):
    for (o0, n0), (o1, n1) in zip(MAP, MAP[1:]):
        if o <= o1:
            return n0 + (n1 - n0) * (o - o0) / (o1 - o0)
    return 43.0


EVENTS = [  # (sound, time, timeline, volume)
    ("pop", 0.5, "o", 0.55), ("pop", 0.8, "o", 0.55), ("pop", 1.1, "o", 0.55),
    ("bloop", 1.6, "o", 0.45), ("bloop", 1.85, "o", 0.45), ("bloop", 2.1, "o", 0.45),
    ("wind", 2.3, "o", 0.35),
    ("sprout", 5.0, "o", 0.35),
    ("coin", 6.4, "o", 0.40), ("coin", 6.84, "o", 0.35), ("coin", 7.28, "o", 0.30),
    ("wilt", 6.6, "o", 0.45),
    ("flip", 6.78, "o", 0.45), ("flip", 7.26, "o", 0.45), ("flip", 7.74, "o", 0.45), ("flip", 8.22, "o", 0.45),
    ("swish", 9.0, "o", 0.35),
    ("whoosh", 9.8, "o", 0.45),
    ("chime", 10.3, "o", 0.45),
    ("whoosh", 13.85, "T", 0.30),
    ("tap", 14.05, "T", 0.50), ("tap", 16.0, "T", 0.50), ("tap", 17.45, "T", 0.50),
    ("whoosh", 19.0, "T", 0.35), ("beeps", 19.8, "T", 0.30), ("pop", 20.4, "T", 0.45),
    ("swish", 23.2, "T", 0.30),
    ("tick", 25.0, "T", 0.45), ("tick", 25.5, "T", 0.45), ("tick", 26.0, "T", 0.45),
    ("swish", 30.25, "T", 0.30),
    ("pop", 34.1, "T", 0.45), ("pop", 34.7, "T", 0.45), ("pop", 35.4, "T", 0.45),
    ("whoosh", 36.5, "T", 0.45),
    ("chime_big", 37.15, "T", 0.50),
    ("sprout", o_to_T(27.3), "T", 0.30),
]
sfx_dir = ASSETS / "sfx"
sfx.write_all(sfx_dir)
names = sorted({e[0] for e in EVENTS})
inputs = ["-i", str(vo30)] + sum([["-i", str(sfx_dir / f"{n}.wav")] for n in names], [])
uses = {n: [e for e in EVENTS if e[0] == n] for n in names}
parts, mix = ["[0:a]aformat=sample_rates=48000:channel_layouts=stereo[vo]"], ["[vo]"]
for k, n in enumerate(names, start=1):
    outs = [f"[{n}{j}]" for j in range(len(uses[n]))]
    parts.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit={len(outs)}{''.join(outs)}" if len(outs) > 1
                 else f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo{outs[0]}")
    for j, (_, when, line, vol) in enumerate(uses[n]):
        t30 = to30(o_to_T(when) if line == "o" else when)
        parts.append(f"[{n}{j}]volume={vol},adelay={int(round(t30 * 1000))}:all=1[e{n}{j}]")
        mix.append(f"[e{n}{j}]")
parts.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0,atrim=0:{TOTAL},"
             f"loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[out]")
run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[out]",
     "-c:a", "aac", "-b:a", "192k", str(ASSETS / "audio-30.m4a")])
vo30.unlink()
print("Done: assets/cut30.json, assets/screen-track-30.mp4, assets/audio-30.m4a")
