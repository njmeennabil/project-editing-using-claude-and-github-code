# Video promosi BUMI360

Video animasi dalam gaya angkasa malam BUMI360 (1920×1080, 30 fps), sama dengan website: langit
gelap berbintang dengan cahaya senja, ladang hijau di bawah. Dari sudut pandang seorang petani di
Sarawak, dengan voice-over pasukan (noise latar dibuang) dan rakaman skrin website baru. Dua versi:

| Versi | Fail | Isi |
|---|---|---|
| Penuh, ~43 saat | `bumi360-promo.mp4` | VO pada kelajuan asal |
| **30 saat** | `bumi360-promo-30s.mp4` | Jeda panjang dalam VO dipendekkan, VO 1.25× lebih laju, **dengan kesan bunyi** |

| Fail | Kegunaan |
|---|---|
| `bumi360-promo.mp4` | Video siap |
| `bumi360-promo.html` | Animasi (petani, benih, telefon, satelit NASA, kad penutup) |
| `assets/voiceover.m4a` | 7 VO yang dipotong dan disusun mengikut babak |
| `assets/screen-track.mp4` | Klip rakaman skrin website untuk skrin telefon (babak 4–6) |
| `clean_voice.sh` | Buang noise latar daripada VO (RNNoise + pengurangan noise ringan), suara sahaja |
| `prepare.sh` | Bina `assets/` daripada fail VO dan rakaman skrin asal |
| `render.js` | Gabungkan animasi + rakaman skrin + audio menjadi MP4 (`--cut30` untuk versi 30 saat) |
| `make30.py` | Bina versi 30 saat: pendekkan jeda VO, peta masa (`assets/cut30.json`), rakaman skrin 30 saat, campur kesan bunyi (`assets/audio-30.m4a`) |
| `sfx.py` | Kesan bunyi yang dijana sendiri (pop, whoosh, syiling, loceng, bip satelit…), tiada fail luar |

## Babak dan masa

| Babak | Masa | VO | Visual |
|---|---|---|---|
| 1 | 0:00–0:05 | "Every season, farmers in Sarawak face the same question…" | Petani, 3 paket benih, tanda soal, cuaca |
| 2 | 0:06–0:11 | "Guess wrong, and you lose seed, fertiliser…" | Tanaman layu, duit terbang, kalendar berlalu |
| 3 | 0:12–0:13 | "Meet BUMI360." | Petani keluarkan telefon, logo BUMI360 |
| 4 | 0:14–0:23 | "Enter your soil pH, choose your location…" | Rakaman skrin: halaman utama → Field check, isi borang. Langkah 1-2-3, satelit NASA |
| 5 | 0:23–0:30 | "In seconds, see which crops suit your field…" | Rakaman skrin: "3 of 5 crops suit your field". Simbol ✓ ! ✕ |
| 6 | 0:30–0:36 | "Then follow a full growing guide…" | Rakaman skrin: Crop guide (baja, amalan) dan tab Rotation |
| 7 | 0:37–0:43 | "BUMI360. Know what your land can grow." | Petani gembira, tanaman subur, logo, pautan |

## Bina semula

Perlukan Node.js, Playwright (Chromium) dan ffmpeg.

```bash
./clean_voice.sh /folder/asal/scene1.m4a…scene7.m4a /folder/bersih   # buang noise suara
# letak screenrec.mov dalam /folder/bersih juga
./prepare.sh /folder/bersih
node render.js                         # versi penuh
python3 make30.py /folder/bersih    # sediakan versi 30 saat
node render.js --cut30                 # versi 30 saat dengan kesan bunyi
```

Kesan bunyi dan masanya disenaraikan dalam `EVENTS` di `make30.py`.

Masa VO dan klip rakaman skrin ditetapkan dalam `prepare.sh`. Masa animasi ditetapkan dalam
`bumi360-promo.html` (fungsi `renderAt`).
