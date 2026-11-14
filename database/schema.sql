-- =====================================================================
-- Database Tanaman: Jagung, Soya, Kacang Tanah
-- SQLite. Semua kadar baja dalam kg/ha, suhu dalam °C, air dalam mm/musim.
-- =====================================================================
PRAGMA foreign_keys = ON;

DROP VIEW  IF EXISTS v_perbandingan;
DROP TABLE IF EXISTS program_baja;
DROP TABLE IF EXISTS nota_giliran;
DROP TABLE IF EXISTS giliran_tanaman;
DROP TABLE IF EXISTS jarak_tanaman;
DROP TABLE IF EXISTS amalan;
DROP TABLE IF EXISTS nutrien_khusus;
DROP TABLE IF EXISTS cadangan_baja;
DROP TABLE IF EXISTS peringkat_kritikal_air;
DROP TABLE IF EXISTS keperluan_tanah;
DROP TABLE IF EXISTS tanaman;

-- Maklumat asas setiap tanaman
CREATE TABLE tanaman (
    id               INTEGER PRIMARY KEY,
    kod              TEXT NOT NULL UNIQUE,          -- cth. 'JAGUNG'
    nama_bm          TEXT NOT NULL,
    nama_en          TEXT NOT NULL,
    nama_saintifik   TEXT,
    jenis            TEXT NOT NULL CHECK (jenis IN ('bijirin', 'legum', 'sayur daun')),
    menetapkan_n     INTEGER NOT NULL CHECK (menetapkan_n IN (0, 1)),
    nutrien_utama    TEXT NOT NULL,                 -- nutrien paling penting
    keperluan_n      TEXT NOT NULL,                 -- ringkasan keperluan nitrogen
    suhu_min_c       REAL,
    suhu_max_c       REAL,
    air_min_mm       REAL,
    air_max_mm       REAL,
    air_sasaran_mm   REAL,                          -- sasaran untuk hasil tinggi (jika ada)
    air_nota         TEXT,
    matang_min_hari  INTEGER,
    matang_max_hari  INTEGER,
    matang_nota      TEXT,
    sumber_rujukan   TEXT                           -- sumber data (jika dinyatakan)
);

-- Keperluan tanah
CREATE TABLE keperluan_tanah (
    tanaman_id  INTEGER PRIMARY KEY REFERENCES tanaman(id) ON DELETE CASCADE,
    tekstur     TEXT NOT NULL,
    saliran     TEXT NOT NULL,
    ph_min      REAL NOT NULL,
    ph_max      REAL NOT NULL,
    ph_elak_bawah REAL,                             -- pH yang mesti dielakkan (di bawah nilai ini)
    nota        TEXT
);

-- Peringkat pertumbuhan yang kritikal untuk air
CREATE TABLE peringkat_kritikal_air (
    id          INTEGER PRIMARY KEY,
    tanaman_id  INTEGER NOT NULL REFERENCES tanaman(id) ON DELETE CASCADE,
    peringkat   TEXT NOT NULL,
    UNIQUE (tanaman_id, peringkat)
);

-- Cadangan dos baja NPK (kg/ha). NULL = tiada had dinyatakan.
CREATE TABLE cadangan_baja (
    id          INTEGER PRIMARY KEY,
    tanaman_id  INTEGER NOT NULL REFERENCES tanaman(id) ON DELETE CASCADE,
    sumber      TEXT NOT NULL,                      -- cth. 'TNAU', 'Nepal', 'Umum'
    keadaan     TEXT,                               -- bila dos ini digunakan
    n_min       REAL, n_max     REAL,
    p2o5_min    REAL, p2o5_max  REAL,
    k2o_min     REAL, k2o_max   REAL,
    nota        TEXT
);

-- Program pembajaan ikut produk baja, dalam unit asal sumber
-- (cth. t/ha, g/m²). Untuk dos dalam kg nutrien/ha, lihat cadangan_baja.
CREATE TABLE program_baja (
    id            INTEGER PRIMARY KEY,
    tanaman_id    INTEGER NOT NULL REFERENCES tanaman(id) ON DELETE CASCADE,
    jenis_baja    TEXT NOT NULL,                    -- cth. 'NPK 15:15:15', 'Dolomit'
    kadar_min     REAL,
    kadar_max     REAL,
    unit          TEXT NOT NULL,                    -- cth. 't/ha', 'g/m²', 'g/m²/minggu'
    masa_aplikasi TEXT,
    nota          TEXT
);

-- Nutrien sekunder / mikro yang penting
CREATE TABLE nutrien_khusus (
    id            INTEGER PRIMARY KEY,
    tanaman_id    INTEGER NOT NULL REFERENCES tanaman(id) ON DELETE CASCADE,
    nutrien       TEXT NOT NULL,                    -- cth. 'Kalsium (Ca)'
    kepentingan   TEXT NOT NULL,
    sumber_baja   TEXT,                             -- cth. 'Gipsum'
    kadar_min_kg_ha REAL,
    kadar_max_kg_ha REAL,
    masa_aplikasi TEXT
);

-- Amalan agronomi / nota pengurusan
CREATE TABLE amalan (
    id          INTEGER PRIMARY KEY,
    tanaman_id  INTEGER NOT NULL REFERENCES tanaman(id) ON DELETE CASCADE,
    kategori    TEXT NOT NULL CHECK (kategori IN ('baja', 'air', 'tanah', 'tanam', 'tuai')),
    perkara     TEXT NOT NULL
);

-- Jarak tanaman (cm)
CREATE TABLE jarak_tanaman (
    id               INTEGER PRIMARY KEY,
    tanaman_id       INTEGER NOT NULL REFERENCES tanaman(id) ON DELETE CASCADE,
    jenis_varieti    TEXT,                          -- cth. 'tegak', 'menjalar'
    antara_baris_min_cm REAL,
    antara_baris_max_cm REAL,
    dalam_baris_min_cm  REAL,
    dalam_baris_max_cm  REAL
);

-- Hubungan giliran tanaman: tanaman sebelum -> tanaman selepas
CREATE TABLE giliran_tanaman (
    id                   INTEGER PRIMARY KEY,
    tanaman_sebelum_id   INTEGER NOT NULL REFERENCES tanaman(id) ON DELETE CASCADE,
    tanaman_selepas_id   INTEGER NOT NULL REFERENCES tanaman(id) ON DELETE CASCADE,
    kesan_hasil_peratus  REAL,                      -- peningkatan hasil dilaporkan (%)
    nota                 TEXT,
    UNIQUE (tanaman_sebelum_id, tanaman_selepas_id)
);

-- Nota umum giliran tanaman
CREATE TABLE nota_giliran (
    id    INTEGER PRIMARY KEY,
    nota  TEXT NOT NULL
);

-- Paparan perbandingan cepat
CREATE VIEW v_perbandingan AS
SELECT
    t.nama_bm                                   AS tanaman,
    t.jenis,
    printf('%.1f–%.1f', kt.ph_min, kt.ph_max)              AS julat_ph,
    printf('%g–%g', t.suhu_min_c, t.suhu_max_c)        AS suhu_c,
    CASE WHEN t.air_min_mm IS NULL THEN 'Konsisten (tiada angka mm)'
         ELSE printf('%g–%g', t.air_min_mm, t.air_max_mm) END AS air_mm,
    t.keperluan_n                               AS nitrogen,
    t.nutrien_utama,
    (SELECT group_concat(p.peringkat, ', ')
       FROM peringkat_kritikal_air p WHERE p.tanaman_id = t.id) AS peringkat_kritikal_air,
    CASE WHEN t.matang_min_hari IS NULL THEN NULL
         WHEN t.matang_min_hari = t.matang_max_hari
         THEN '~' || t.matang_min_hari
         ELSE t.matang_min_hari || '–' || t.matang_max_hari END AS matang_hari
FROM tanaman t
JOIN keperluan_tanah kt ON kt.tanaman_id = t.id
ORDER BY t.id;
