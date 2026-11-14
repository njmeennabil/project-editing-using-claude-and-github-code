# Database Tanaman

Database SQLite untuk keperluan agronomi jagung, soya, kacang tanah, kangkung dan sawi: suhu, air, tanah, baja, jarak tanaman dan giliran tanaman.

## Fail

| Fail | Kegunaan |
|---|---|
| `schema.sql` | Struktur jadual dan view |
| `seed.sql` | Data tanaman |
| `build_db.py` | Bina semula `tanaman.db` daripada dua fail di atas |
| `tanaman.db` | Database SQLite yang sudah siap |
| `export_excel.py` | Eksport database ke `tanaman.xlsx` |
| `tanaman.xlsx` | Versi Excel: satu helaian bagi setiap jadual + helaian *Semak Kesesuaian* |

Untuk bina semula selepas mengubah `seed.sql`:

```bash
python3 build_db.py
python3 export_excel.py
```

## Jadual

| Jadual | Isi |
|---|---|
| `tanaman` | Maklumat asas: nama, jenis, suhu, air, tempoh matang, nutrien utama |
| `keperluan_tanah` | Tekstur, saliran, julat pH |
| `peringkat_kritikal_air` | Peringkat pertumbuhan yang paling memerlukan air |
| `cadangan_baja` | Dos N, P₂O₅, K₂O (kg/ha) mengikut sumber (TNAU, Nepal, umum) |
| `program_baja` | Jadual pembajaan ikut produk (baja organik, NPK, dolomit) dalam unit asal (t/ha, g/m²) |
| `nutrien_khusus` | Nutrien sekunder/mikro: Ca, Zn, Mo, P dan kadar aplikasi |
| `amalan` | Nota pengurusan (baja, air, tanah, tanam, tuai) |
| `jarak_tanaman` | Jarak antara baris dan dalam baris (cm) |
| `giliran_tanaman` | Tanaman sebelum → selepas dan kesan hasil |
| `nota_giliran` | Nota umum giliran tanaman |
| `v_perbandingan` | View ringkasan perbandingan cepat |

Unit: suhu °C, air mm/musim, baja kg/ha, jarak cm, tempoh dalam hari.

## Contoh query

```sql
-- Perbandingan cepat
SELECT * FROM v_perbandingan;

-- Tanaman yang sesuai untuk tanah pH 5.8
SELECT t.nama_bm FROM tanaman t
JOIN keperluan_tanah k ON k.tanaman_id = t.id
WHERE 5.8 BETWEEN k.ph_min AND k.ph_max;

-- Semua cadangan baja
SELECT t.nama_bm, b.sumber, b.keadaan,
       b.n_min, b.n_max, b.p2o5_min, b.p2o5_max, b.k2o_min, b.k2o_max
FROM cadangan_baja b JOIN tanaman t ON t.id = b.tanaman_id;

-- Giliran tanaman
SELECT s.nama_bm AS sebelum, e.nama_bm AS selepas, g.kesan_hasil_peratus, g.nota
FROM giliran_tanaman g
JOIN tanaman s ON s.id = g.tanaman_sebelum_id
JOIN tanaman e ON e.id = g.tanaman_selepas_id;
```

Dari Python:

```python
import sqlite3
con = sqlite3.connect("database/tanaman.db")
for row in con.execute("SELECT * FROM v_perbandingan"):
    print(row)
```
