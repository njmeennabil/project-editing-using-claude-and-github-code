"""Sound for Nabil Pulang: Malay narration + score + foley on one 56 s timeline.

96 bpm, one bar = 2.5 s, 22 bars + ring-out. D major: home, warm. Cue map in TREATMENT.md.
Cues come from events.json (exported by the page) and voice/cues.json (narration timing).
Voice compressed, music balanced ~10 dB under it (RMS over the spoken parts), music carved at 300 Hz-4 kHz and ducked under each line.

usage (library root): .venv/bin/python <project>/mix.py        writes out/mix.wav
"""
import json, os, sys
import numpy as np, soundfile as sf, soxr
LIB = os.environ.get('LIB') or '/home/user/lemo-opuscar'
sys.path.insert(0, LIB)
from core.audio import sampler as S
from core.audio.sfx import SR, bp, lp, hp, add, compress, limit, click, whoosh, thump

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'events.json')))
FULL = float(D['dur']); EV = D['ev']
CUES = json.load(open(os.path.join(HERE, 'voice', 'cues.json')))
N = int(FULL * SR) + SR
tt = np.arange(N) / SR
rng = np.random.default_rng(5)
BEAT = 60 / 96; BAR = 4 * BEAT
evs = lambda k: [e for e in EV if e['type'] == k]
bar = lambda b: (b - 1) * BAR


def env_lin(points):
    ts, vs = zip(*points); return np.interp(tt, ts, vs)


def st(x): return np.stack([x, np.roll(x, 1733)], 1)


mix = np.zeros((N, 2)); music = np.zeros((N, 2))

# ---------------- ambience: coast at Bintulu, thin air at altitude, land and sea in Selangor ----------------
coast = lp(bp(rng.standard_normal(N), 120, 900, 1), 700) * env_lin([(0, 0), (.5, .026), (5, .026), (7, .008), (9, 0), (38, 0), (40, .02), (45, .02), (46.5, 0), (FULL, 0)])
air = bp(rng.standard_normal(N), 250, 5200, 2) * env_lin([(0, 0), (5, 0), (7, .012), (12, .015), (20, .015), (22.5, .006), (25, 0), (45, 0), (47, .014), (FULL - 1, .012), (FULL, 0)])
land = lp(rng.standard_normal(N), 380, 2) * env_lin([(0, 0), (22.5, 0), (24, .03), (32.5, .03), (34.5, .016), (37.5, .016), (38.5, .028), (45, .028), (46, 0), (FULL, 0)])
for x in (coast, air, land): mix += st(x)

# ---------------- score ----------------
ev = []
CH = {'D': [38, 45, 50, 54, 57], 'Bm': [35, 42, 47, 50, 54], 'G': [31, 38, 43, 47, 50], 'A': [33, 40, 45, 49, 52], 'Em': [40, 47, 52, 55, 59]}
PULSE = {1: 'D', 2: 'D', 3: 'G', 4: 'D', 5: 'Bm', 6: 'D', 7: 'Bm', 8: 'G', 9: 'A', 10: 'G', 11: 'D', 12: 'Bm', 13: 'A',
         16: 'G', 17: 'A', 18: 'Bm'}
SPIC = {6, 7, 8, 9, 11, 12, 13, 17, 18}
for b, ch in PULSE.items():
    t0 = bar(b); c = CH[ch]
    for q in range(4):
        ev.append((t0 + q * BEAT, 'contrabass_pizz', c[0] if q % 2 == 0 else c[1], .5, .5 if q == 0 else .38, -.05, .55))
    if b in SPIC:
        pat = [2, 3, 2, 4, 2, 3, 2, 4] if b % 2 else [2, 3, 4, 3, 2, 3, 4, 3]
        for i, k in enumerate(pat):
            ev.append((t0 + i * BEAT / 2, 'cellos_spic', c[k] + 12, .25, .3 + .1 * (i % 2 == 0), .25, .45))
    if b >= 4:
        ev.append((t0, 'frame_drum', 'large_muted', None, .4, 0, .45))
# opening: bowed vibraphone high over a low cello pedal
ev += [(0.05, 'vibraphone_bowed', 'A5', 5.0, .36, -.35, .28), (0.05, 'vibraphone_bowed', 'F#5', 5.0, .32, .35, .24), (0.0, 'cellos', 'D2', 5.2, .34, 0, .3)]
# harp arpeggios over the take-off and the road to Jeram
for b in (4, 5, 16, 17, 18):
    c = CH[PULSE[b]]
    for i, k in enumerate([1, 2, 3, 4, 3, 2, 3, 4]): ev.append((bar(b) + i * BEAT / 2, 'harp', c[k] + 12, 1.2, .3 + .05 * (i == 0), -.2 + .05 * i, .36))
# a chime for every pin
for e in evs('pin'): ev.append((e['t'], 'hand_chimes', 'A5', 2.5, .48, e.get('pan', 0), .5))
for e in evs('title'): ev.append((e['t'], 'glockenspiel', 'D6', 1.6, .26, -.2, .24))
# ignitions: the flight (big), the roads (smaller)
for e in evs('ignite'):
    t = e['t']
    if e.get('small'):
        ev += [(t, 'frame_drum', 'large', None, .5, 0, .55)]
        for i, p in enumerate([74, 78, 81]): ev.append((t + i * BEAT / 2, 'glockenspiel', p, .8, .26 + .03 * i, .3 - .2 * i, .28))
    else:
        ev += [(t, 'contrabass', 'D2', 2.4, .48, 0, .38), (t, 'cellos', 'A2', 2.4, .4, -.2, .32), (t, 'vibraphone_bowed', 'A4', 2.4, .36, -.3, .24),
               (t, 'frame_drum', 'large', None, .58, 0, .7)]
        for i, p in enumerate([74, 78, 81, 86]): ev.append((t + i * BEAT / 2, 'glockenspiel', p, .9, .28 + .04 * i, .35 - .2 * i, .32))
# touchdown on the downbeat of bar 10
for e in evs('touchdown'): ev += [(e['t'], 'frame_drum', 'large', None, .6, 0, .7), (e['t'], 'timpani', 'D3', 1.5, .42, 0, .45)]
# home (bars 14-15): almost nothing. One chord held while the house is named, half a bar of silence before the road returns
for e in evs('home'):
    t = e['t']
    ev += [(t, 'hand_chimes', 'D6', 3.0, .45, .2, .45), (t, 'vibraphone_bowed', 'D5', 4.4, .3, -.2, .2), (t, 'vibraphone_bowed', 'A5', 4.4, .27, .2, .16),
           (t, 'cellos', 'D2', 4.0, .3, 0, .22)]
# the new chapter (bars 19-22): horn swells, then the final chord on bar 21 that rings out
ev += [(bar(19), 'horn', 'D3', 2.6, .4, -.1, .3), (bar(19), 'horn', 'F#3', 2.6, .36, .1, .26), (bar(19), 'contrabass', 'D2', 2.5, .4, 0, .3),
       (bar(20), 'horn', 'G3', 2.4, .42, 0, .3), (bar(20), 'horn', 'B3', 2.4, .36, 0, .24), (bar(20), 'contrabass', 'G1', 2.5, .4, 0, .3),
       (bar(19), 'frame_drum', 'large', None, .5, 0, .5), (bar(20), 'frame_drum', 'large', None, .5, 0, .5)]
for i, p in enumerate([62, 66, 69, 74]): ev.append((bar(19) + 1.25 + i * BEAT / 2, 'harp', p, 1.2, .32, -.2 + .1 * i, .34))
for e in evs('total'): ev.append((e['t'], 'glockenspiel', 'A5', 1.5, .3, .3, .28))
fin = evs('final')[0]['t']
for i, p in enumerate([38, 50, 57, 62, 64, 66, 69, 74]): ev.append((fin + i * .035, 'harp', p, 3.0, .5, -.3 + i * .08, .52))
ev += [(fin, 'vibraphone_bowed', 'E5', FULL - fin, .32, .2, .2), (fin, 'vibraphone_bowed', 'F#5', FULL - fin, .3, -.2, .18),
       (fin, 'cellos', 'D2', FULL - fin, .34, 0, .28), (fin, 'horn', 'A3', 3.0, .34, 0, .22), (fin, 'contrabass', 'D2', 3.0, .4, 0, .3)]
for e in evs('close'): ev.append((e['t'], 'hand_chimes', 'A5', 2.4, .4, .25, .36))
S.seed(13)
sc = S.render(ev, dur=FULL + 1, master=False)[:N]
f0 = 73.42                                                  # D2 pedal with 2nd and 3rd harmonics
drone = np.sin(2 * np.pi * f0 * tt) + .45 * np.sin(4 * np.pi * f0 * tt) + .22 * np.sin(6 * np.pi * f0 * tt)
drone *= env_lin([(0, 0), (1.0, .016), (7.5, .02), (22.5, .024), (32.5, .03), (37.5, .03), (38, .018), (45, .02), (50, .026), (FULL, .01)])
sc += st(drone)
sw = bp(rng.standard_normal(N), 300, 3000, 1)
swell = np.zeros(N)
for a, b in [(6.4, 7.5), (21.4, 22.5), (23.9, 25.0), (36.4, 37.5), (43.9, 45.0)]:
    swell += np.clip((tt - a) / (b - a), 0, 1) ** 3 * (tt < b)
sc += st(sw * swell * .045)
sc = np.stack([hp(sc[:, c], 32, 2) for c in range(2)], 1)
sc = S.room(sc, size=.55, mix=.22)
music += sc

# ---------------- foley tied to the picture ----------------
for e in EV:
    k, t = e['type'], e['t']
    if k == 'pin' or k == 'tick':
        for d in (0, .07): add(mix, hp(click(pitch=.9, v=1.0), 1200) * .07, t + d, 1, e.get('pan', .2))
    elif k in ('crane', 'whoosh', 'rise'): add(mix, lp(whoosh(1.8, 1.0), 1800) * .08, t, 1, 0)
    elif k == 'dive': add(mix, lp(whoosh(1.6, 1.0), 2400) * .1, t, 1, 0)
    elif k == 'ignite':
        add(mix, thump(1.0, 52) * (.14 if e.get('small') else .24), t, 1, 0)
        n = int(2.0 * SR); x = np.arange(n) / SR
        buzz = bp(np.sin(2 * np.pi * 110 * x) + .5 * np.sin(2 * np.pi * 220.7 * x) + .3 * rng.standard_normal(n), 150, 2400, 1) * np.exp(-x / .7) * np.minimum(1, x / .05)
        add(mix, buzz * (.02 if e.get('small') else .03), t, 1, .15)
    elif k == 'takeoff':                                    # a distant jet: filtered roar swelling as the aircraft climbs, then far away
        n = int(6.0 * SR); x = np.arange(n) / SR
        roar = lp(bp(rng.standard_normal(n), 90, 3000, 1), 1400) * np.sin(np.pi * np.clip(x / 6.0, 0, 1)) ** 1.4
        add(mix, roar * .07, t, 1, .1)
    elif k == 'touchdown':
        add(mix, thump(1.0, 46) * .2, t, 1, 0)
        n = int(1.4 * SR); x = np.arange(n) / SR
        add(mix, bp(rng.standard_normal(n), 200, 1800, 1) * np.exp(-x / .45) * .05, t + .03, 1, 0)
    elif k == 'car':                                        # a soft road hum while the car runs
        n = int((e['end'] - t + .6) * SR); x = np.arange(n) / SR
        hum = bp(np.sin(2 * np.pi * 62 * x) + .6 * rng.standard_normal(n), 70, 700, 1) * np.minimum(1, x / .4) * np.minimum(1, (x[-1] - x) / .5)
        add(mix, hum * .025, t, 1, -.1)
    elif k == 'ruler':
        for i in range(4): add(mix, hp(click(pitch=1.0 + .1 * i, v=1.0), 1500) * .06, t + i * .18, 1, -.2 + .15 * i)
    elif k == 'total':
        for i in range(5): add(mix, hp(click(pitch=1.2 + .08 * i, v=1.0), 1800) * .04, t + i * .08, 1, .2)

# carve the voice band out of the music, then duck it under every line
mid = np.stack([bp(music[:, c], 300, 4000, 2) for c in range(2)], 1)
music = music - mid * (1 - 10 ** (-4 / 20))

# ---------------- narration ----------------
voice = np.zeros(N); active = np.zeros(N)
for c in CUES:
    x, sr = sf.read(os.path.join(HERE, 'out', 'voice', c['id'] + '.wav'), dtype='float64')
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = soxr.resample(x, sr, SR)
    i = int(c['t0'] * SR); j = min(N, i + len(x)); voice[i:j] += x[:j - i]; active[i:j] = 1
voice = hp(voice, 80, 2)
voice = compress(voice, thr=.18, ratio=3.0)
duck = np.convolve(active, np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
duck = 1 - .45 * np.clip(duck * 1.4, 0, 1)
music = music * duck[:, None]
vr = np.sqrt((voice[active > 0] ** 2).mean())
voice *= .16 / vr
mr = np.sqrt((music[active > 0] ** 2).mean())
music *= (.16 * 10 ** (-10 / 20)) / mr
fx_r = np.sqrt((mix[active > 0] ** 2).mean())
mix *= min(1.0, (.16 * 10 ** (-12 / 20)) / max(fx_r, 1e-9))
mix += music + np.stack([voice, voice], 1)

out = mix[:int(FULL * SR)].copy()
nf = int(1.0 * SR); out[-nf:] *= np.linspace(1, 0, nf)[:, None] ** 1.5
out = np.stack([compress(out[:, 0], thr=.35, ratio=2.0), compress(out[:, 1], thr=.35, ratio=2.0)], 1)
out = np.stack([limit(out[:, 0]), limit(out[:, 1])], 1)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
sf.write(os.path.join(HERE, 'out', 'mix.wav'), out.astype(np.float32), SR)
used = ['hand_chimes', 'vibraphone_bowed', 'contrabass_pizz', 'cellos_spic', 'contrabass', 'cellos', 'glockenspiel', 'harp', 'frame_drum', 'timpani', 'horn']
cr = S.credits(used)
open(os.path.join(HERE, 'out', 'instruments.txt'), 'w').write('\n'.join(cr) if isinstance(cr, list) else str(cr))
# low-end check: energy 20-120 Hz relative to the rest
def band(x, a, b): return 10 * np.log10(np.mean(bp(x, a, b, 2) ** 2) + 1e-12)
m = out.mean(1)
vo_db = 20 * np.log10(np.sqrt((voice[active > 0] ** 2).mean())); mu_db = 20 * np.log10(np.sqrt((music[active > 0] ** 2).mean()))
print(f'mix peak {np.abs(out).max():.3f}  voice {vo_db:.1f} dB  music under voice {mu_db:.1f} dB  (gap {vo_db - mu_db:.1f} dB)  low 20-120 Hz vs 120-8k: {band(m, 20, 120) - band(m, 120, 8000):.1f} dB')
