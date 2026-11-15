#!/usr/bin/env bash
# Prepare the voice-over and screen-recording tracks for the BUMI360 promo.
# Usage: ./prepare.sh <folder containing scene1.m4a … scene7.m4a and screenrec.mov>
# Output: assets/voiceover.m4a (43 s) and assets/screen-track.mp4 (432x912, 43 s)
set -euo pipefail
SRC="$1"
OUT="$(cd "$(dirname "$0")" && pwd)/assets"
mkdir -p "$OUT"
REC="$(ls "$SRC"/screenrec.* | head -1)"

# Voice-over: trim the silence after each scene and place it on the timeline (seconds).
#            scene: keep  start
#                1: 5.25  0.40   "Every season, farmers in Sarawak..."
#                2: 5.70  5.95   "Guess wrong..."
#                3: 1.95 12.00   "Meet BUMI360."
#                4: 8.80 14.05   "Enter your soil pH..."
#                5: 6.70 23.20   "In seconds..."
#                6: 6.40 30.25   "Then follow a full growing guide..."
#                7: 4.00 37.00   "BUMI360. Know what your land can grow."
ffmpeg -y -loglevel error \
  -i "$SRC/scene1.m4a" -i "$SRC/scene2.m4a" -i "$SRC/scene3.m4a" -i "$SRC/scene4.m4a" \
  -i "$SRC/scene5.m4a" -i "$SRC/scene6.m4a" -i "$SRC/scene7.m4a" \
  -filter_complex "\
[0]atrim=0:5.25,afade=t=out:st=5.05:d=0.2,adelay=400:all=1[a1];\
[1]atrim=0:5.70,afade=t=out:st=5.50:d=0.2,adelay=5950:all=1[a2];\
[2]atrim=0:1.95,afade=t=out:st=1.75:d=0.2,adelay=12000:all=1[a3];\
[3]atrim=0:8.80,afade=t=out:st=8.60:d=0.2,adelay=14050:all=1[a4];\
[4]atrim=0:6.70,afade=t=out:st=6.50:d=0.2,adelay=23200:all=1[a5];\
[5]atrim=0:6.40,afade=t=out:st=6.20:d=0.2,adelay=30250:all=1[a6];\
[6]atrim=0:4.00,afade=t=out:st=3.80:d=0.2,adelay=37000:all=1[a7];\
[a1][a2][a3][a4][a5][a6][a7]amix=inputs=7:normalize=0,apad=whole_dur=43,atrim=0:43,loudnorm=I=-16:TP=-1.5:LRA=11[out]" \
  -map "[out]" -ar 48000 -c:a aac -b:a 192k "$OUT/voiceover.m4a"

# Screen recording: pick the clips for scenes 4–6, scale to the phone screen (432x912),
# start at 13.8 s and hold the last frame until the end.
#   source start  length  played as  shows
#   2.6           9.2     9.2 s      home -> Field check: soil pH, location, planting month, Check  (scene 4)
#   11.8          6.4     7.1 s      result: 3 of 5 crops suit your field, crop cards               (scene 5)
#   35.6          2.7     3.6 s      Crop guide: maize, fertiliser, good practice, rotation        (scene 6)
#   44.2          3.1     3.1 s      Rotation tab: plant legumes first                             (scene 6)
# Scale so the phone status bar (clock, recording dot) is cropped off the top.
V="fps=30,scale=-2:976,crop=432:912:(iw-432)/2:62,setsar=1"
ffmpeg -y -loglevel error -i "$REC" -filter_complex "\
[0:v]trim=start=2.6:duration=9.2,setpts=PTS-STARTPTS,$V[c1];\
[0:v]trim=start=11.8:duration=6.4,setpts=(PTS-STARTPTS)*1.109375,$V[c2];\
[0:v]trim=start=35.6:duration=2.7,setpts=(PTS-STARTPTS)*1.333333,$V[c3];\
[0:v]trim=start=44.2:duration=3.1,setpts=PTS-STARTPTS,$V[c4];\
[c1][c2][c3][c4]concat=n=4:v=1:a=0,tpad=start_duration=13.8:start_mode=add:color=black:stop_mode=clone:stop_duration=7,trim=0:43,setpts=PTS-STARTPTS[v]" \
  -map "[v]" -an -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium "$OUT/screen-track.mp4"

echo "Done: $OUT/voiceover.m4a and $OUT/screen-track.mp4"
