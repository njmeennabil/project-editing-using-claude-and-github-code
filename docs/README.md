# Website: Semak Kesesuaian Tanaman

Petani isi **pH tanah**, **suhu purata (°C)** dan **air tersedia semusim (mm)**. Website kemudian
tunjuk sama ada setiap tanaman sesuai, dan panduan penanamannya (baja, jarak, amalan, giliran).

## Cara ia berfungsi

```
database/tanaman.db  ──(python3 database/export_json.py)──►  docs/data/tanaman.js
                                                                  │
docs/index.html  ◄── baca data ───────────────────────────────────┘
      │
      └── semua pengiraan dibuat dalam pelayar (JavaScript). Tiada server diperlukan.
```

| Fail | Kegunaan |
|---|---|
| `index.html` | Halaman website: borang, logik semakan, paparan keputusan |
| `data/tanaman.js` | Data tanaman untuk website (dijana, jangan ubah dengan tangan) |
| `data/tanaman.json` | Data yang sama dalam JSON, untuk aplikasi lain atau API |

## Logik semakan

| Faktor | Sesuai | Perlu pengurusan | Kurang sesuai |
|---|---|---|---|
| pH | Dalam julat | – | Luar julat (atau bawah pH bahaya, cth. soya < 4.5) |
| Suhu | Dalam julat optimum | Luar julat ≤ 2°C | Luar julat > 2°C |
| Air | Dalam julat | Kurang ≤ 50% atau berlebihan | Kurang > 50% daripada minimum |

Keputusan keseluruhan ikut faktor yang paling teruk. Tanaman tanpa angka air (mm), iaitu kangkung dan sawi,
tunjuk nota kelembapan sahaja dan tidak menjejaskan keputusan.

## Kemas kini data

Selepas ubah `database/seed.sql`:

```bash
python3 database/build_db.py
python3 database/export_json.py
```

## Hoskan percuma di GitHub Pages

1. Gabungkan (merge) branch ini ke `main`.
2. Di GitHub: **Settings → Pages → Build and deployment**.
3. Source: **Deploy from a branch**, Branch: **main**, Folder: **/docs**, kemudian Save.
4. Selepas 1–2 minit, website ada di `https://<nama-pengguna>.github.io/<nama-repo>/`.

Folder ini dinamakan `docs` kerana GitHub Pages hanya boleh hoskan dari root repo atau folder `/docs`.
GitHub Pages untuk repo peribadi (private) memerlukan pelan GitHub berbayar; repo awam (public) percuma.

## Cuba di komputer sendiri

Buka `docs/index.html` terus dalam pelayar (double-click). Ia berfungsi tanpa server.
