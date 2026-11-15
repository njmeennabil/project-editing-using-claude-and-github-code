"""English translations for text stored in Malay in tanaman.db.

export_json.py uses this table to build the English website data.
If you add a crop or new text to seed.sql, add its translation here;
export_json.py stops and lists any text that has no translation.
"""

EN = {
    # Crop types
    "bijirin": "Cereal",
    "legum": "Legume",
    "sayur daun": "Leafy vegetable",

    # Practice categories
    "baja": "Fertiliser",
    "air": "Water",
    "tanah": "Soil",
    "tanam": "Planting",
    "tuai": "Harvest",

    # Crop local names (used in rotation data)
    "Jagung": "Maize",
    "Soya": "Soybean",
    "Kacang Tanah": "Peanut",
    "Kangkung": "Water Spinach",
    "Sawi": "Mustard Greens",

    # Nutrients
    "Nitrogen (N)": "Nitrogen (N)",
    "Fosforus (P)": "Phosphorus (P)",
    "Kalium (K)": "Potassium (K)",
    "Fosforus (P) dan Kalium (K)": "Phosphorus (P) and Potassium (K)",
    "Kalsium (Ca)": "Calcium (Ca)",
    "Kalsium dan Magnesium (Ca, Mg)": "Calcium and Magnesium (Ca, Mg)",
    "Zink (Zn)": "Zinc (Zn)",
    "Molibdenum (Mo)": "Molybdenum (Mo)",

    # Nitrogen need
    "Tinggi — pengguna N yang tinggi": "High — heavy nitrogen feeder",
    "Rendah — dibekalkan oleh rhizobium": "Low — supplied by rhizobium bacteria",
    "Rendah — menetapkan N sendiri": "Low — fixes its own nitrogen",
    "Perlu N untuk pertumbuhan daun dan batang": "Needs nitrogen for leaf and stem growth",
    "Perlu N untuk pertumbuhan daun": "Needs nitrogen for leaf growth",

    # Water notes
    "Tidak tahan banjir; perlukan parit saliran.": "Does not tolerate flooding; needs drainage ditches.",
    "Sekitar 700 mm untuk hasil tinggi. Perlukan cuaca kering semasa masak.":
        "Around 700 mm for high yield. Needs dry weather during ripening.",
    "Mesti teragih sekata sepanjang musim.": "Must be evenly distributed through the season.",
    "Perlukan bekalan air mencukupi dan kelembapan tanah yang konsisten. Tidak tahan kekeringan terlalu lama.":
        "Needs an adequate water supply and consistently moist soil. Does not tolerate long dry spells.",
    "Perlukan bekalan air konsisten untuk pertumbuhan daun. Elakkan tanah terlalu kering atau air bertakung.":
        "Needs a steady water supply for leaf growth. Avoid very dry soil or standing water.",

    # Maturity notes / sources
    "Tanah rendah Malaysia": "Malaysian lowlands",
    "Sekitar 150 hari; bergantung varieti": "Around 150 days; depends on variety",
    "4–5 minggu selepas menanam": "4–5 weeks after planting",
    "Jabatan Pertanian Sarawak": "Department of Agriculture Sarawak",

    # Soil
    "Lom atau lom berpasir": "Loam or sandy loam",
    "Lom, kaya bahan organik": "Loam, rich in organic matter",
    "Berpasir, kurang 15% liat": "Sandy, less than 15% clay",
    "Gambut, liat ringan atau tanah mineral": "Peat, light clay or mineral soil",
    "Lom subur, kaya bahan organik": "Fertile loam, rich in organic matter",
    "Baik": "Good",
    "Perlu diurus dengan baik": "Must be well managed",
    "Elakkan pH di bawah 4.5 (aluminium toksik).": "Avoid pH below 4.5 (aluminium toxicity).",
    "Liat keras menghalang peg menembusi tanah.": "Hard clay stops pegs from entering the soil.",
    "pH sekitar 5.5–6.5 sebagai sasaran pengurusan tanah.": "Target pH of about 5.5–6.5 for soil management.",

    # Critical water stages
    "Berbunga": "Flowering",
    "Berbunga (tasseling)": "Flowering (tasseling)",
    "Berbunga (silking)": "Flowering (silking)",
    "Pembentukan buah": "Pod formation",
    "Pegging": "Pegging",

    # NPK recommendations
    "TNAU": "TNAU",
    "Nepal": "Nepal",
    "Umum": "General",
    "Dos rujukan": "Reference dose",
    "Ikut ujian tanah": "Based on soil test",
    "Tiada ujian tanah": "No soil test available",
    "Kadar rujukan semusim": "Reference rate per season",
    "Baja N tidak lebih 20 kg N/ha.": "No more than 20 kg N/ha of nitrogen fertiliser.",
    "N sebagai baja asas (basal).": "N applied as basal fertiliser.",
    "Dikira daripada 0.5 t/ha NPK 15:15:15 (500 kg × 15%).": "Calculated from 0.5 t/ha of NPK 15:15:15 (500 kg × 15%).",

    # Fertiliser programme
    "Baja organik": "Organic fertiliser",
    "Baja organik (tahi ayam dikomposkan)": "Organic fertiliser (composted chicken manure)",
    "NPK 15:15:15": "NPK 15:15:15",
    "NPK": "NPK",
    "Dolomit": "Dolomite",
    "Baja tambahan": "Top-up fertiliser",
    "t/ha": "t/ha",
    "t/ha/musim": "t/ha/season",
    "kg/m²": "kg/m²",
    "g/m²": "g/m²",
    "g/m²/minggu": "g/m²/week",
    "Seminggu sebelum menanam": "One week before planting",
    "Minggu ke-2 dan ke-3 selepas menanam": "Weeks 2 and 3 after planting",
    "Sebelum menanam": "Before planting",
    "Setiap minggu sehingga menuai": "Every week until harvest",
    "Digaul ke dalam tanah.": "Mixed into the soil.",
    "Kadar rujukan Jabatan Pertanian Sarawak.": "Reference rate from the Department of Agriculture Sarawak.",
    "Membantu pengurusan pH; membekalkan kalsium dan magnesium.": "Helps manage pH; supplies calcium and magnesium.",
    "Gred NPK tidak dinyatakan.": "NPK grade not specified.",
    "Sesuaikan dengan keadaan tanah dan pertumbuhan tanaman.": "Adjust to soil conditions and crop growth.",

    # Special nutrients
    "Penting untuk pertumbuhan akar": "Important for root growth",
    "Sensitif kepada kekurangan zink": "Sensitive to zinc deficiency",
    "Penting untuk penetapan N": "Important for nitrogen fixation",
    "Nutrien paling kritikal": "Most critical nutrient",
    "Penambahan berkala": "Periodic top-up",
    "Membantu perkembangan akar": "Helps root development",
    "Membantu pertumbuhan dan ketahanan tanaman": "Supports growth and plant resilience",
    "Dibekalkan melalui dolomit": "Supplied through dolomite",
    "Gipsum": "Gypsum",
    "Zink sulfat": "Zinc sulphate",
    "Puncak berbunga (40–45 hari selepas tanam)": "Peak flowering (40–45 days after planting)",
    "Sekali setiap tiga tahun": "Once every three years",
    "Sebelum menanam (100–200 g/m²)": "Before planting (100–200 g/m²)",

    # Spacing
    "Tegak": "Erect (bunch) type",
    "Menjalar": "Spreading (runner) type",

    # Practices
    "Beri N berperingkat: tidak lebih sepertiga semasa tanam.": "Split nitrogen: no more than one third at planting.",
    "Baki N diberi kira-kira 30 hari selepas tanam.": "Apply the remaining nitrogen about 30 days after planting.",
    "Sediakan parit saliran — tidak tahan banjir.": "Prepare drainage ditches — does not tolerate flooding.",
    "Inokulasi rhizobium jika tanam kali pertama di kawasan tersebut.": "Inoculate with rhizobium if planting in the field for the first time.",
    "Perlukan cuaca kering semasa masak.": "Needs dry weather during ripening.",
    "Baja tidak boleh menyentuh benih secara terus.": "Fertiliser must not touch the seed directly.",
    "Elakkan tanah liat keras — menghalang peg menembusi tanah.": "Avoid hard clay soil — it stops pegs from entering the soil.",
    "Boleh ditanam sepanjang tahun jika bekalan air dan saliran diuruskan dengan baik.":
        "Can be planted all year round if water supply and drainage are well managed.",
    "Pengairan secara manual atau sistem pemercik.": "Irrigate by hand or with a sprinkler system.",
    "Elakkan kekeringan terlalu lama; kekalkan kelembapan tanah.": "Avoid long dry spells; keep the soil moist.",
    "Gaul baja organik ke dalam tanah seminggu sebelum menanam.": "Mix organic fertiliser into the soil one week before planting.",
    "Beri NPK pada minggu ke-2 dan ke-3 selepas menanam.": "Apply NPK in weeks 2 and 3 after planting.",
    "Elakkan tanah terlalu kering atau air bertakung.": "Avoid very dry soil or standing water.",
    "Pembajaan perlu disesuaikan dengan keadaan tanah dan pertumbuhan tanaman.":
        "Adjust fertiliser to soil conditions and crop growth.",
    "Guna dolomit untuk mengurus pH tanah.": "Use dolomite to manage soil pH.",

    # Rotation
    "Tanaman selepas kacang tanah dilaporkan meningkat hasil sekitar 25%.":
        "Crops grown after peanut are reported to yield about 25% more.",
    "Legum dahulu menambah N dalam tanah untuk jagung.": "A legume first adds nitrogen to the soil for the maize that follows.",
    "Soya dan kacang tanah ialah legum yang menambah N dalam tanah.": "Soybean and peanut are legumes that add nitrogen to the soil.",
    "Susunan biasa: legum dahulu, kemudian jagung.": "Common sequence: legume first, then maize.",

    # Rotation ratings (pencadang tanaman seterusnya)
    'cemerlang': 'Excellent',
    'baik': 'Good',
    'sederhana': 'Fair',
    'lemah': 'Poor',
    'Draf BUMI360 (prinsip agronomi umum), perlu disemak': 'BUMI360 draft (general agronomy principles), awaiting review',
    'Data asal pengguna': 'Original user data',
    'Perosak dan penyakit terkumpul, dan nitrogen tanah terus berkurang.': 'Pests and diseases build up, and soil nitrogen keeps falling.',
    'Legum selepas bijirin: perlukan sedikit nitrogen dan memutuskan kitaran perosak jagung.': 'A legume after a cereal needs little nitrogen and breaks maize pest cycles.',
    'Jagung menghabiskan nitrogen; sayur daun perlukan baja tambahan.': 'Maize uses up nitrogen, so the leafy crop needs extra fertiliser.',
    'Legum menambah nitrogen dalam tanah untuk jagung.': 'The legume adds nitrogen to the soil for maize.',
    'Penyakit tanah terkumpul.': 'Soil diseases build up.',
    'Kedua-duanya legum dan berkongsi sebahagian perosak dan penyakit.': 'Both are legumes and share some pests and diseases.',
    'Baki nitrogen daripada legum membantu pertumbuhan daun.': 'Nitrogen left by the legume helps leaf growth.',
    'Hasil jagung dilaporkan meningkat sekitar 25% selepas kacang tanah.': 'Maize yield is reported to rise about 25% after peanut.',
    'Elakkan: penyakit bintik daun dan nematod terkumpul.': 'Avoid: leaf spot disease and nematodes build up.',
    'Famili tumbuhan berbeza; memutuskan kitaran perosak dan penyakit.': 'A different plant family breaks pest and disease cycles.',
    'Biasa ditanam berterusan, tetapi awasi perosak.': 'Often grown continuously, but watch for pests.',
    'Penyakit famili kubis terkumpul (cth. penyakit akar bengkak).': 'Cabbage-family diseases build up (e.g. clubroot).',
}
