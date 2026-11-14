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
#   source start  length  shows
#   2.5           2.25    form with soil pH          (scene 4)
#   6.0           1.45    choosing the location      (scene 4)
#   11.6          5.50    choosing the planting month (scene 4)
#   22.5          7.10    result: Water Spinach suitable, NASA POWER (scene 5)
#   34.0          3.20    growing guide tabs         (scene 6)
#   41.4          3.50    maize guide: NPK, practices, rotation (scene 6)
# Scale so the phone status bar (clock, recording dot) is cropped off the top.
V="fps=30,scale=-2:976,crop=432:912:(iw-432)/2:62,setsar=1"
ffmpeg -y -loglevel error -i "$REC" -filter_complex "\
[0:v]trim=start=2.5:duration=2.25,setpts=PTS-STARTPTS,$V[c1];\
[0:v]trim=start=6.0:duration=1.45,setpts=PTS-STARTPTS,$V[c2];\
[0:v]trim=start=11.6:duration=5.5,setpts=PTS-STARTPTS,$V[c3];\
[0:v]trim=start=22.5:duration=7.1,setpts=PTS-STARTPTS,$V[c4];\
[0:v]trim=start=34.0:duration=3.2,setpts=PTS-STARTPTS,$V[c5];\
[0:v]trim=start=41.4:duration=3.5,setpts=PTS-STARTPTS,$V[c6];\
[c1][c2][c3][c4][c5][c6]concat=n=6:v=1:a=0,tpad=start_duration=13.8:start_mode=add:color=black:stop_mode=clone:stop_duration=7,trim=0:43,setpts=PTS-STARTPTS[v]" \
  -map "[v]" -an -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium "$OUT/screen-track.mp4"

echo "Done: $OUT/voiceover.m4a and $OUT/screen-track.mp4"
