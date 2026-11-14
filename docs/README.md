# BUMI360 (website)

Website bahasa Inggeris untuk petani. Petani isi **soil pH**, **average temperature (°C)** dan
**water available per season (mm)**. Website tunjuk kesesuaian setiap tanaman, dan sediakan panduan
penanaman, jadual perbandingan serta giliran tanaman. Reka bentuknya responsif untuk telefon, tablet dan laptop.

## Struktur

| Fail | Kegunaan |
|---|---|
| `index.html` | Struktur halaman: header, hero, Field check, Crop guide, Compare, Rotation, About |
| `assets/style.css` | Reka bentuk dan susun atur responsif (telefon < 768px, tablet 768–1023px, laptop ≥ 1024px) |
| `assets/app.js` | Logik semakan kesesuaian dan paparan data |
| `data/crops.js` | Data tanaman dalam bahasa Inggeris (dijana, jangan ubah dengan tangan) |
| `data/crops.json` | Data yang sama dalam JSON, untuk aplikasi lain atau API |

## Aliran data

```
database/seed.sql (Bahasa Melayu)
   → python3 database/build_db.py      → database/tanaman.db
   → python3 database/export_json.py   → docs/data/crops.js + crops.json (English)
                                          (guna database/translations_en.py)
```

Database dan Excel kekal dalam bahasa Melayu. Teks bahasa Inggeris datang dari
`database/translations_en.py`. Kalau awak tambah tanaman atau teks baru dalam `seed.sql`,
`export_json.py` akan berhenti dan senaraikan teks yang belum ada terjemahan. Tambah terjemahan itu
dalam `translations_en.py`, kemudian jalankan semula.

## Logik semakan

| Faktor | Suitable | Suitable with management | Less suitable |
|---|---|---|---|
| pH | Dalam julat | – | Luar julat (atau bawah pH bahaya, cth. soya < 4.5) |
| Suhu | Dalam julat optimum | Luar julat ≤ 2°C | Luar julat > 2°C |
| Air | Dalam julat | Kurang ≤ 50%, atau berlebihan | Kurang > 50% daripada minimum |

Keputusan keseluruhan ikut faktor yang paling teruk.

## Hoskan percuma di GitHub Pages

1. Gabungkan (merge) branch ini ke `main`.
2. Di GitHub: **Settings → Pages → Build and deployment**.
3. Source: **Deploy from a branch**, Branch: **main**, Folder: **/docs**, kemudian Save.
4. Selepas 1–2 minit, website ada di `https://<nama-pengguna>.github.io/<nama-repo>/`.

Untuk guna domain sendiri (cth. `bumi360.my`), isi **Custom domain** di halaman yang sama dan
tetapkan DNS di pembekal domain mengikut arahan GitHub.

## Cuba di komputer sendiri

Buka `docs/index.html` terus dalam pelayar (double-click). Ia berfungsi tanpa server.
