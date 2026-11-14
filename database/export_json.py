#!/usr/bin/env python3
"""Eksport tanaman.db ke docs/data/ untuk website (tanaman.json dan tanaman.js)."""
import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "docs" / "data"
OUT.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(HERE / "tanaman.db")
con.row_factory = sqlite3.Row


def rows(sql, *args):
    return [dict(r) for r in con.execute(sql, args)]


crops = []
for t in rows("SELECT * FROM tanaman ORDER BY id"):
    i = t["id"]
    t["menetapkan_n"] = bool(t["menetapkan_n"])
    t["tanah"] = rows("SELECT tekstur, saliran, ph_min, ph_max, ph_elak_bawah, nota "
                      "FROM keperluan_tanah WHERE tanaman_id = ?", i)[0]
    t["air_kritikal"] = [r["peringkat"] for r in rows(
        "SELECT peringkat FROM peringkat_kritikal_air WHERE tanaman_id = ? ORDER BY id", i)]
    t["baja_npk"] = rows("SELECT sumber, keadaan, n_min, n_max, p2o5_min, p2o5_max, k2o_min, k2o_max, nota "
                         "FROM cadangan_baja WHERE tanaman_id = ? ORDER BY id", i)
    t["program_baja"] = rows("SELECT jenis_baja, kadar_min, kadar_max, unit, masa_aplikasi, nota "
                             "FROM program_baja WHERE tanaman_id = ? ORDER BY id", i)
    t["nutrien_khusus"] = rows("SELECT nutrien, kepentingan, sumber_baja, kadar_min_kg_ha, kadar_max_kg_ha, masa_aplikasi "
                               "FROM nutrien_khusus WHERE tanaman_id = ? ORDER BY id", i)
    t["amalan"] = rows("SELECT kategori, perkara FROM amalan WHERE tanaman_id = ? ORDER BY id", i)
    t["jarak"] = rows("SELECT jenis_varieti, antara_baris_min_cm, antara_baris_max_cm, "
                      "dalam_baris_min_cm, dalam_baris_max_cm FROM jarak_tanaman WHERE tanaman_id = ? ORDER BY id", i)
    crops.append(t)

data = {
    "tanaman": crops,
    "giliran": rows("""
        SELECT s.nama_bm AS sebelum, e.nama_bm AS selepas, g.kesan_hasil_peratus, g.nota
        FROM giliran_tanaman g
        JOIN tanaman s ON s.id = g.tanaman_sebelum_id
        JOIN tanaman e ON e.id = g.tanaman_selepas_id ORDER BY g.id"""),
    "nota_giliran": [r["nota"] for r in rows("SELECT nota FROM nota_giliran ORDER BY id")],
}

text = json.dumps(data, ensure_ascii=False, indent=1)
(OUT / "tanaman.json").write_text(text + "\n", encoding="utf-8")
(OUT / "tanaman.js").write_text(
    "// Dijana oleh database/export_json.py. Jangan ubah dengan tangan.\n"
    f"window.DATA_TANAMAN = {text};\n", encoding="utf-8")
print(f"Siap: {OUT / 'tanaman.json'} dan tanaman.js ({len(crops)} tanaman)")
