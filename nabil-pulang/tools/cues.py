"""Subtitle cues from the narration timeline (voice/subs.json start times + voice/lines.json text + out/voice/dur.json)
-> voice/cues.json. The page draws its subtitles from this file and build.sh turns it into the .srt, so both match.
Each cue: one Malay line; it stays up for the spoken line + 1.6 s (capped by the next line), never shorter than the
spoken line + 0.6 s or 1.8 s (checked here).
usage: python3 <project>/tools/cues.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subs = json.load(open(os.path.join(HERE, 'voice', 'subs.json')))
text = {l['id']: l['text'] for l in json.load(open(os.path.join(HERE, 'voice', 'lines.json')))}
dur = json.load(open(os.path.join(HERE, 'out', 'voice', 'dur.json')))
cues, bad = [], 0
for i, s in enumerate(subs):
    d = dur[s['id']]
    end = s['t'] + d + 1.6
    if i + 1 < len(subs): end = min(end, subs[i + 1]['t'] - 0.08)
    need = max(1.8, d + 0.6)
    if end - s['t'] < need - 1e-6 or (i + 1 < len(subs) and s['t'] + d > subs[i + 1]['t'] - 0.3):
        print('TOO SHORT', s['id'], round(end - s['t'], 2), 'need', round(need, 2)); bad += 1
    cues.append({'id': s['id'], 't0': s['t'], 't1': round(end, 3), 'vo_end': round(s['t'] + d, 3), 'text': text[s['id']]})
json.dump(cues, open(os.path.join(HERE, 'voice', 'cues.json'), 'w'), ensure_ascii=False, indent=1)
print('cues', len(cues), 'shortest', round(min(c['t1'] - c['t0'] for c in cues), 2), 's')
sys.exit(1 if bad else 0)
