#!/bin/sh
# One command: Nabil Pulang (3D Map Explainer).
#   sh build.sh              map data and fonts if missing, voice if missing + speech check, cues, events, picture, mix, master,
#                            subtitles, readcheck, poster
#   FETCH=1 sh build.sh      re-download every map tile and rebuild the terrain assets first
#   VOICE=1 sh build.sh      regenerate the narration (needs the internet: Microsoft edge-tts)
#   SS=1.5 WORKERS=3 sh build.sh   supersampling and render workers (defaults 1 and 3)
# Needs the Lemo-Opuscar library with `setup.sh deps voice` and the VSCO 2 CE + VCSL sample libraries, and ffmpeg 7+
# (a static build in .tools/ffbin is used when present). On a machine without a GPU set LEMO_ANGLE=swiftshader.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
LIB=${LIB:-/home/user/lemo-opuscar}
export LIB
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the library folder"; exit 1; }
PY="$LIB/.venv/bin/python"
NAME=nabil-pulang
[ -d "$HERE/.tools/ffbin" ] && PATH="$HERE/.tools/ffbin:$PATH" && export PATH
cd "$LIB"
"$PY" core/audio/sampler.py --need "$HERE/mix.py"
mkdir -p "$HERE/out/voice"

# map data (public tiles, see CREDITS) and baked shadows; fonts
if [ "${FETCH:-0}" = "1" ] || [ ! -f "$HERE/assets/wide_height.bin" ]; then "$PY" -I "$HERE/tools/data.py" "$HERE"; fi
if [ "${FETCH:-0}" = "1" ] || [ ! -f "$HERE/assets/wide_shadow.png" ]; then "$PY" -I "$HERE/tools/bake.py" "$HERE"; fi
[ -f "$HERE/fonts/BarlowCondensed-SemiBold.ttf" ] || python3 -I "$HERE/tools/fonts.py" "$HERE"

# narration: edge-tts ms-MY-OsmanNeural; every line must pass the speech-to-text check
if [ "${VOICE:-0}" = "1" ] || [ ! -f "$HERE/out/voice/v8.wav" ]; then
  "$PY" "$HERE/tools/tts_ms.py" "$HERE/voice/lines.json" "$HERE/out/voice" --voice ms-MY-OsmanNeural --rate=-4%
fi
"$PY" core/tts/asr_check.py "$HERE/voice/lines.json" "$HERE/out/voice" --lang ms --model small
python3 "$HERE/tools/cues.py"

# events, picture (in slices), score + foley + voice, master, subtitles
node core/render/events.mjs "$HERE"
rm -rf "$HERE/out/slices"
sh "$HERE/tools/render.sh" "$HERE" "${SS:-1}" "${WORKERS:-3}"
"$PY" "$HERE/mix.py"
sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/$NAME.mp4" 24 1
"$PY" core/render/srt.py "$HERE/voice/cues.json" "$HERE/$NAME.srt"

# checks and poster (the crossing, without the subtitle shelf)
node core/render/readcheck.mjs "$HERE" > "$HERE/out/readcheck.txt" && echo "readcheck ok" || { tail -20 "$HERE/out/readcheck.txt"; exit 1; }
node core/render/still.mjs "$HERE" 18.5 --q nosubs=1 --out "$HERE/out/poster" > /dev/null
ffmpeg -v error -y -i "$HERE/out/poster/t_18.5.jpg" -q:v 3 "$HERE/poster.jpg"
echo "done: $HERE/$NAME.mp4"
