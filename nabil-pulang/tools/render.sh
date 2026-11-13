#!/bin/sh
# Render the picture in 14 s slices (?t0=&t1=, frame-exact joins), each retried once, then join them.
# usage (library root): sh <project>/tools/render.sh <project> [ss] [workers]
set -e
P=$1; SSX=${2:-1}; WK=${3:-3}
mkdir -p "$P/out/slices"
for a in 0 14 28 42; do
  b=$((a + 14)); f="$P/out/slices/s$a.mp4"
  [ -f "$f" ] && continue
  for try in 1 2; do
    if node core/render/video.mjs "$P" --fps 24 --workers "$WK" --q "ss=$SSX&t0=$a&t1=$b" --out "$f.tmp.mp4"; then mv "$f.tmp.mp4" "$f"; break; fi
    rm -f "$f.tmp.mp4"; [ $try = 2 ] && exit 1
  done
done
printf "file 's0.mp4'\nfile 's14.mp4'\nfile 's28.mp4'\nfile 's42.mp4'\n" > "$P/out/slices/list.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$P/out/slices/list.txt" -c copy "$P/out/video.mp4"
echo "video ok: $P/out/video.mp4"
