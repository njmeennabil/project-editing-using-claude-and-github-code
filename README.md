# BUMI360

Website untuk petani Malaysia menyemak kesesuaian tanaman berdasarkan pH tanah, suhu purata
dan air semusim, berserta panduan penanaman setiap tanaman.

## Struktur projek

```
Petani (telefon / tablet / laptop)
        │
        ▼
frontend/   Next.js + React + Tailwind  ── hos: Vercel
        │   panggil /api/crops, /api/rotation, /api/check
        ▼
backend/    Python Flask                ── hos: Render (render.yaml)
        │   baca dan terjemah ke bahasa Inggeris
        ├─► database/   SQLite (tanaman.db) + Excel, dalam bahasa Melayu
        └─► NASA POWER  suhu dan hujan bulanan untuk 12 bahagian Sarawak / lokasi GPS
```

## Cadangan tanaman seterusnya

Petani pilih tanaman sekarang, **tarikh tanam**, lokasi dan pH tanah. BUMI360 kira tarikh tuai dan tarikh tanam
seterusnya, kemudian beri markah 0–100 kepada setiap tanaman untuk musim itu: iklim NASA 45, giliran 35, pH tanah 20.
Tiga cadangan teratas dipaparkan. Penilaian giliran disimpan dalam jadual `penilaian_giliran` (helaian
*Penilaian Giliran* dalam Excel). Kebanyakannya masih **draf** dan perlu disemak pakar; tukar `disahkan` kepada 1
selepas disemak.

## Peta Sarawak

Bahagian **Map** menunjukkan markah iklim (0–100) tanaman pilihan untuk 12 bahagian Sarawak pada tarikh tanam
yang dipilih. Petani boleh tekan mana-mana tempat pada peta untuk semak titik itu, dan hantar lokasi itu ke
*Field check* atau *Next crop*. Peta latar: CARTO (perlukan kunci percuma, `NEXT_PUBLIC_CARTO_KEY` di Vercel),
atau OpenStreetMap kelabu jika tiada kunci. Sempadan bahagian: geoBoundaries (CC BY 3.0).

## Data NASA

Petani pilih bahagian di Sarawak (atau guna GPS telefon) dan bulan tanam. Flask ambil purata suhu dan
hujan 25 tahun (2001–2025) dari NASA POWER, kemudian kira hujan dan suhu **untuk tempoh setiap tanaman**.
Contoh: jagung (65 hari) yang ditanam pada bulan Mac di Kuching dapat ~614 mm hujan; di Miri ~366 mm.

- Data 12 bahagian disimpan dalam `backend/data/sarawak_climate.json`.
  Kemas kini: `cd backend && .venv/bin/python scripts/update_climate.py`
- NASA POWER tidak perlukan akaun. GPM dan SMAP (fasa seterusnya) perlukan akaun NASA Earthdata.

| Folder | Isi |
|---|---|
| [`frontend/`](frontend/) | Website BUMI360 (Next.js 16, React 19, Tailwind 4) |
| [`backend/`](backend/) | Flask API: data tanaman dan logik semakan kesesuaian |
| [`database/`](database/) | Database tanaman (SQLite + Excel), terjemahan bahasa Inggeris |
| [`docs/`](docs/) | Versi statik lama BUMI360 (HTML biasa, untuk GitHub Pages) |

## Jalankan di komputer sendiri

Terminal 1 (API):

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/flask --app app run --port 5000
```

Terminal 2 (website):

```bash
cd frontend
npm install
npm run dev
```

Buka http://localhost:3000

## Letak online

1. **Render (API):** daftar di render.com → **New + → Blueprint** → pilih repo ini. Render baca
   `render.yaml` dan deploy Flask. Salin alamatnya, contohnya `https://bumi360-api.onrender.com`.
2. **Vercel (website):** daftar di vercel.com → **Add New → Project** → pilih repo ini.
   - **Root Directory:** `frontend`
   - **Environment Variable:** `NEXT_PUBLIC_API_URL` = alamat Render dari langkah 1
3. **Kunci API kepada website awak:** di Render, tetapkan `ALLOWED_ORIGINS` kepada alamat Vercel,
   contohnya `https://bumi360.vercel.app`.

Selepas itu, setiap kali awak push ke GitHub, Render dan Vercel akan deploy semula secara automatik.

## Kemas kini data tanaman

```bash
python3 database/build_db.py
```

Ubah `database/seed.sql` dahulu. Teks baru perlukan terjemahan dalam `database/translations_en.py`.
Selepas push, Render guna data baru, dan website memaparkannya dalam masa sejam.
