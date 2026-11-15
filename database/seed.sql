-- =====================================================================
-- Data tanaman
-- =====================================================================
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- tanaman
-- ---------------------------------------------------------------------
INSERT INTO tanaman (id, kod, nama_bm, nama_en, nama_saintifik, jenis, menetapkan_n,
                     nutrien_utama, keperluan_n,
                     suhu_min_c, suhu_max_c,
                     air_min_mm, air_max_mm, air_sasaran_mm, air_nota,
                     matang_min_hari, matang_max_hari, matang_nota) VALUES
(1, 'JAGUNG', 'Jagung', 'Maize', 'Zea mays', 'bijirin', 0,
    'Nitrogen (N)', 'Tinggi — pengguna N yang tinggi',
    18, 33,
    500, 800, NULL, 'Tidak tahan banjir; perlukan parit saliran.',
    60, 70, 'Tanah rendah Malaysia'),
(2, 'SOYA', 'Soya', 'Soybean', 'Glycine max', 'legum', 1,
    'Fosforus (P) dan Kalium (K)', 'Rendah — dibekalkan oleh rhizobium',
    26, 30,
    500, 1000, 700, 'Sekitar 700 mm untuk hasil tinggi. Perlukan cuaca kering semasa masak.',
    100, 130, NULL),
(3, 'KACANG_TANAH', 'Kacang Tanah', 'Peanut', 'Arachis hypogaea', 'legum', 1,
    'Kalsium (Ca)', 'Rendah — menetapkan N sendiri',
    28, 30,
    500, 600, NULL, 'Mesti teragih sekata sepanjang musim.',
    150, 150, 'Sekitar 150 hari; bergantung varieti');

-- ---------------------------------------------------------------------
-- keperluan_tanah
-- ---------------------------------------------------------------------
INSERT INTO keperluan_tanah (tanaman_id, tekstur, saliran, ph_min, ph_max, ph_elak_bawah, nota) VALUES
(1, 'Lom atau lom berpasir', 'Baik', 5.5, 7.5, NULL, NULL),
(2, 'Lom, kaya bahan organik', 'Baik', 6.0, 7.5, 4.5, 'Elakkan pH di bawah 4.5 (aluminium toksik).'),
(3, 'Berpasir, kurang 15% liat', 'Baik', 5.5, 7.0, NULL, 'Liat keras menghalang peg menembusi tanah.');

-- ---------------------------------------------------------------------
-- peringkat_kritikal_air
-- ---------------------------------------------------------------------
INSERT INTO peringkat_kritikal_air (tanaman_id, peringkat) VALUES
(1, 'Berbunga (tasseling)'),
(1, 'Berbunga (silking)'),
(2, 'Berbunga'),
(2, 'Pembentukan buah'),
(3, 'Berbunga'),
(3, 'Pegging'),
(3, 'Pembentukan buah');

-- ---------------------------------------------------------------------
-- cadangan_baja (kg/ha)
-- ---------------------------------------------------------------------
INSERT INTO cadangan_baja (tanaman_id, sumber, keadaan,
                           n_min, n_max, p2o5_min, p2o5_max, k2o_min, k2o_max, nota) VALUES
(1, 'TNAU',  'Dos rujukan', 150, 150, 75, 75, 75, 75, NULL),
(1, 'Nepal', 'Dos rujukan', 160, 160, 60, 60, 40, 40, NULL),
(2, 'Umum',  'Ikut ujian tanah', 0, 20, 40, 100, 40, 80, 'Baja N tidak lebih 20 kg N/ha.'),
(3, 'Umum',  'Ikut ujian tanah', 8, 20, 16, 80, 0, 75, 'N sebagai baja asas (basal).'),
(3, 'TNAU',  'Tiada ujian tanah', 25, 25, 50, 50, 75, 75, NULL);

-- ---------------------------------------------------------------------
-- nutrien_khusus
-- ---------------------------------------------------------------------
INSERT INTO nutrien_khusus (tanaman_id, nutrien, kepentingan, sumber_baja,
                            kadar_min_kg_ha, kadar_max_kg_ha, masa_aplikasi) VALUES
(1, 'Fosforus (P)',   'Penting untuk pertumbuhan akar', NULL, NULL, NULL, NULL),
(1, 'Zink (Zn)',      'Sensitif kepada kekurangan zink', NULL, NULL, NULL, NULL),
(2, 'Molibdenum (Mo)','Penting untuk penetapan N', NULL, NULL, NULL, NULL),
(3, 'Kalsium (Ca)',   'Nutrien paling kritikal', 'Gipsum', 200, 400,
    'Puncak berbunga (40–45 hari selepas tanam)'),
(3, 'Zink (Zn)',      'Penambahan berkala', 'Zink sulfat', 10, 20,
    'Sekali setiap tiga tahun');

-- ---------------------------------------------------------------------
-- amalan
-- ---------------------------------------------------------------------
INSERT INTO amalan (tanaman_id, kategori, perkara) VALUES
(1, 'baja',  'Beri N berperingkat: tidak lebih sepertiga semasa tanam.'),
(1, 'baja',  'Baki N diberi kira-kira 30 hari selepas tanam.'),
(1, 'air',   'Sediakan parit saliran — tidak tahan banjir.'),
(2, 'tanam', 'Inokulasi rhizobium jika tanam kali pertama di kawasan tersebut.'),
(2, 'tuai',  'Perlukan cuaca kering semasa masak.'),
(3, 'baja',  'Baja tidak boleh menyentuh benih secara terus.'),
(3, 'tanah', 'Elakkan tanah liat keras — menghalang peg menembusi tanah.');

-- ---------------------------------------------------------------------
-- jarak_tanaman (cm)
-- ---------------------------------------------------------------------
INSERT INTO jarak_tanaman (tanaman_id, jenis_varieti,
                           antara_baris_min_cm, antara_baris_max_cm,
                           dalam_baris_min_cm, dalam_baris_max_cm) VALUES
(2, NULL,       40, 60, NULL, NULL),
(3, 'Tegak',    30, 40, 10, 15),
(3, 'Menjalar', 45, 60, 15, 20);

-- ---------------------------------------------------------------------
-- giliran_tanaman
-- ---------------------------------------------------------------------
INSERT INTO giliran_tanaman (tanaman_sebelum_id, tanaman_selepas_id, kesan_hasil_peratus, nota) VALUES
(3, 1, 25,   'Tanaman selepas kacang tanah dilaporkan meningkat hasil sekitar 25%.'),
(2, 1, NULL, 'Legum dahulu menambah N dalam tanah untuk jagung.');

INSERT INTO nota_giliran (nota) VALUES
('Soya dan kacang tanah ialah legum yang menambah N dalam tanah.'),
('Tanaman selepas kacang tanah dilaporkan meningkat hasil sekitar 25%.'),
('Susunan biasa: legum dahulu, kemudian jagung.');

-- =====================================================================
-- TANAMAN LOKAL: SAYUR DAUN (7. Kangkung, 8. Sawi)
-- =====================================================================
INSERT INTO tanaman (id, kod, nama_bm, nama_en, nama_saintifik, jenis, menetapkan_n,
                     nutrien_utama, keperluan_n,
                     suhu_min_c, suhu_max_c,
                     air_min_mm, air_max_mm, air_sasaran_mm, air_nota,
                     matang_min_hari, matang_max_hari, matang_nota, sumber_rujukan) VALUES
(4, 'KANGKUNG', 'Kangkung', 'Water Spinach', 'Ipomoea aquatica', 'sayur daun', 0,
    'Nitrogen (N)', 'Perlu N untuk pertumbuhan daun dan batang',
    23, 30,
    NULL, NULL, NULL, 'Perlukan bekalan air mencukupi dan kelembapan tanah yang konsisten. Tidak tahan kekeringan terlalu lama.',
    28, 35, '4–5 minggu selepas menanam', 'Jabatan Pertanian Sarawak'),
(5, 'SAWI', 'Sawi', 'Mustard Greens', 'Brassica juncea', 'sayur daun', 0,
    'Nitrogen (N)', 'Perlu N untuk pertumbuhan daun',
    20, 30,
    NULL, NULL, NULL, 'Perlukan bekalan air konsisten untuk pertumbuhan daun. Elakkan tanah terlalu kering atau air bertakung.',
    NULL, NULL, NULL, NULL);

INSERT INTO keperluan_tanah (tanaman_id, tekstur, saliran, ph_min, ph_max, ph_elak_bawah, nota) VALUES
(4, 'Gambut, liat ringan atau tanah mineral', 'Perlu diurus dengan baik', 5.5, 6.5, NULL, NULL),
(5, 'Lom subur, kaya bahan organik', 'Baik', 5.5, 6.5, NULL, 'pH sekitar 5.5–6.5 sebagai sasaran pengurusan tanah.');

-- Kangkung: dos nutrien dikira daripada 0.5 t/ha NPK 15:15:15 (500 kg × 15% = 75 kg/ha).
-- Sawi: gred NPK tidak dinyatakan, jadi dos nutrien tidak dikira (lihat program_baja).
INSERT INTO cadangan_baja (tanaman_id, sumber, keadaan,
                           n_min, n_max, p2o5_min, p2o5_max, k2o_min, k2o_max, nota) VALUES
(4, 'Jabatan Pertanian Sarawak', 'Kadar rujukan semusim', 75, 75, 75, 75, 75, 75,
    'Dikira daripada 0.5 t/ha NPK 15:15:15 (500 kg × 15%).');

INSERT INTO program_baja (tanaman_id, jenis_baja, kadar_min, kadar_max, unit, masa_aplikasi, nota) VALUES
(4, 'Baja organik',  4,   4,   't/ha',        'Seminggu sebelum menanam', 'Digaul ke dalam tanah.'),
(4, 'NPK 15:15:15',  0.5, 0.5, 't/ha/musim',  'Minggu ke-2 dan ke-3 selepas menanam', 'Kadar rujukan Jabatan Pertanian Sarawak.'),
(5, 'Baja organik (tahi ayam dikomposkan)', 1, 2, 'kg/m²', 'Sebelum menanam', NULL),
(5, 'Dolomit',       100, 200, 'g/m²',        'Sebelum menanam', 'Membantu pengurusan pH; membekalkan kalsium dan magnesium.'),
(5, 'NPK',           30,  30,  'g/m²',        'Sebelum menanam', 'Gred NPK tidak dinyatakan.'),
(5, 'Baja tambahan', 30,  40,  'g/m²/minggu', 'Setiap minggu sehingga menuai', 'Sesuaikan dengan keadaan tanah dan pertumbuhan tanaman.');

INSERT INTO nutrien_khusus (tanaman_id, nutrien, kepentingan, sumber_baja,
                            kadar_min_kg_ha, kadar_max_kg_ha, masa_aplikasi) VALUES
(5, 'Fosforus (P)', 'Membantu perkembangan akar', NULL, NULL, NULL, NULL),
(5, 'Kalium (K)',   'Membantu pertumbuhan dan ketahanan tanaman', NULL, NULL, NULL, NULL),
(5, 'Kalsium dan Magnesium (Ca, Mg)', 'Dibekalkan melalui dolomit', 'Dolomit', 1000, 2000,
    'Sebelum menanam (100–200 g/m²)');

INSERT INTO amalan (tanaman_id, kategori, perkara) VALUES
(4, 'tanam', 'Boleh ditanam sepanjang tahun jika bekalan air dan saliran diuruskan dengan baik.'),
(4, 'air',   'Pengairan secara manual atau sistem pemercik.'),
(4, 'air',   'Elakkan kekeringan terlalu lama; kekalkan kelembapan tanah.'),
(4, 'baja',  'Gaul baja organik ke dalam tanah seminggu sebelum menanam.'),
(4, 'baja',  'Beri NPK pada minggu ke-2 dan ke-3 selepas menanam.'),
(5, 'air',   'Elakkan tanah terlalu kering atau air bertakung.'),
(5, 'baja',  'Pembajaan perlu disesuaikan dengan keadaan tanah dan pertumbuhan tanaman.'),
(5, 'tanah', 'Guna dolomit untuk mengurus pH tanah.');

INSERT INTO jarak_tanaman (tanaman_id, jenis_varieti,
                           antara_baris_min_cm, antara_baris_max_cm,
                           dalam_baris_min_cm, dalam_baris_max_cm) VALUES
(4, NULL, 20, 20, 10, 10),
(5, NULL, NULL, NULL, 20, 25);

-- =====================================================================
-- PENILAIAN GILIRAN (5 x 5) untuk pencadang tanaman seterusnya.
-- Hanya soya -> jagung dan kacang tanah -> jagung datang daripada data asal;
-- yang lain ialah draf berdasarkan prinsip agronomi umum (disahkan = 0).
-- =====================================================================
INSERT INTO penilaian_giliran (tanaman_sebelum_id, tanaman_selepas_id, penilaian, sebab, sumber, disahkan) VALUES
(1, 1, 'lemah', 'Perosak dan penyakit terkumpul, dan nitrogen tanah terus berkurang.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(1, 2, 'cemerlang', 'Legum selepas bijirin: perlukan sedikit nitrogen dan memutuskan kitaran perosak jagung.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(1, 3, 'cemerlang', 'Legum selepas bijirin: perlukan sedikit nitrogen dan memutuskan kitaran perosak jagung.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(1, 4, 'sederhana', 'Jagung menghabiskan nitrogen; sayur daun perlukan baja tambahan.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(1, 5, 'sederhana', 'Jagung menghabiskan nitrogen; sayur daun perlukan baja tambahan.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(2, 1, 'cemerlang', 'Legum menambah nitrogen dalam tanah untuk jagung.', 'Data asal pengguna', 1),
(2, 2, 'lemah', 'Penyakit tanah terkumpul.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(2, 3, 'sederhana', 'Kedua-duanya legum dan berkongsi sebahagian perosak dan penyakit.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(2, 4, 'baik', 'Baki nitrogen daripada legum membantu pertumbuhan daun.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(2, 5, 'baik', 'Baki nitrogen daripada legum membantu pertumbuhan daun.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(3, 1, 'cemerlang', 'Hasil jagung dilaporkan meningkat sekitar 25% selepas kacang tanah.', 'Data asal pengguna', 1),
(3, 2, 'sederhana', 'Kedua-duanya legum dan berkongsi sebahagian perosak dan penyakit.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(3, 3, 'lemah', 'Elakkan: penyakit bintik daun dan nematod terkumpul.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(3, 4, 'baik', 'Baki nitrogen daripada legum membantu pertumbuhan daun.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(3, 5, 'baik', 'Baki nitrogen daripada legum membantu pertumbuhan daun.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(4, 1, 'baik', 'Famili tumbuhan berbeza; memutuskan kitaran perosak dan penyakit.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(4, 2, 'baik', 'Famili tumbuhan berbeza; memutuskan kitaran perosak dan penyakit.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(4, 3, 'baik', 'Famili tumbuhan berbeza; memutuskan kitaran perosak dan penyakit.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(4, 4, 'sederhana', 'Biasa ditanam berterusan, tetapi awasi perosak.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(4, 5, 'baik', 'Famili tumbuhan berbeza; memutuskan kitaran perosak dan penyakit.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(5, 1, 'baik', 'Famili tumbuhan berbeza; memutuskan kitaran perosak dan penyakit.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(5, 2, 'baik', 'Famili tumbuhan berbeza; memutuskan kitaran perosak dan penyakit.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(5, 3, 'baik', 'Famili tumbuhan berbeza; memutuskan kitaran perosak dan penyakit.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(5, 4, 'baik', 'Famili tumbuhan berbeza; memutuskan kitaran perosak dan penyakit.', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0),
(5, 5, 'lemah', 'Penyakit famili kubis terkumpul (cth. penyakit akar bengkak).', 'Draf BUMI360 (prinsip agronomi umum), perlu disemak', 0);
