#!/usr/bin/env bash
# Remove background noise from the voice-over recordings, keeping only the voice.
# Usage: ./clean_voice.sh <folder with scene1.m4a … scene7.m4a> <output folder>
# Uses ffmpeg's RNNoise filter (arnndn) with the "somnolent-hogwash" speech model, then a light
# FFT noise reduction. Mixes in 10% of the original so the voice stays natural.
set -euo pipefail
SRC="$1"
OUT="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"
MODEL="$HERE/.cache/sh.rnnn"
mkdir -p "$OUT" "$HERE/.cache"
if [ ! -s "$MODEL" ]; then
  curl -sSL -o "$MODEL" https://raw.githubusercontent.com/GregorR/rnnoise-models/master/somnolent-hogwash-2018-09-01/sh.rnnn
fi
for i in 1 2 3 4 5 6 7; do
  ffmpeg -y -loglevel error -i "$SRC/scene$i.m4a" \
    -af "highpass=f=80,arnndn=m=$MODEL:mix=0.9,afftdn=nr=8:nf=-55,lowpass=f=14000" \
    -ac 1 -ar 48000 -c:a aac -b:a 256k "$OUT/scene$i.m4a"
done
echo "Done: cleaned voice-overs in $OUT"
