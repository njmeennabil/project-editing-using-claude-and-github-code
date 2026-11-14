"""Read tanaman.db and return the crop data in English.

Shared by export_json.py (static files) and the Flask API in backend/.
Malay text in the database is translated with translations_en.py.
"""
import sqlite3
from pathlib import Path

from translations_en import EN

DEFAULT_DB = Path(__file__).resolve().parent / "tanaman.db"


class MissingTranslation(Exception):
    def __init__(self, texts):
        self.texts = sorted(texts)
        super().__init__("Missing English translation for: " + "; ".join(repr(t) for t in self.texts))


def load_data(db_path=DEFAULT_DB):
    """Return {"crops": [...], "rotation": [...], "rotation_notes": [...]} in English."""
    missing = set()

    def tr(s):
        if s is None:
            return None
        if s not in EN:
            missing.add(s)
            return s
        return EN[s]

    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    def rows(sql, *args):
        return [dict(r) for r in con.execute(sql, args)]

    crops = []
    for t in rows("SELECT * FROM tanaman ORDER BY id"):
        i = t["id"]
        soil = rows("SELECT * FROM keperluan_tanah WHERE tanaman_id = ?", i)[0]
        crops.append({
            "id": i,
            "code": t["kod"],
            "name": t["nama_en"],
            "local_name": t["nama_bm"],
            "scientific_name": t["nama_saintifik"],
            "type": tr(t["jenis"]),
            "fixes_nitrogen": bool(t["menetapkan_n"]),
            "key_nutrient": tr(t["nutrien_utama"]),
            "nitrogen_need": tr(t["keperluan_n"]),
            "temp_min_c": t["suhu_min_c"],
            "temp_max_c": t["suhu_max_c"],
            "water_min_mm": t["air_min_mm"],
            "water_max_mm": t["air_max_mm"],
            "water_target_mm": t["air_sasaran_mm"],
            "water_note": tr(t["air_nota"]),
            "maturity_min_days": t["matang_min_hari"],
            "maturity_max_days": t["matang_max_hari"],
            "maturity_note": tr(t["matang_nota"]),
            "source": tr(t["sumber_rujukan"]),
            "soil": {
                "texture": tr(soil["tekstur"]),
                "drainage": tr(soil["saliran"]),
                "ph_min": soil["ph_min"],
                "ph_max": soil["ph_max"],
                "ph_danger_below": soil["ph_elak_bawah"],
                "note": tr(soil["nota"]),
            },
            "critical_water_stages": [tr(r["peringkat"]) for r in rows(
                "SELECT peringkat FROM peringkat_kritikal_air WHERE tanaman_id = ? ORDER BY id", i)],
            "npk": [{
                "source": tr(b["sumber"]), "condition": tr(b["keadaan"]),
                "n_min": b["n_min"], "n_max": b["n_max"],
                "p2o5_min": b["p2o5_min"], "p2o5_max": b["p2o5_max"],
                "k2o_min": b["k2o_min"], "k2o_max": b["k2o_max"],
                "note": tr(b["nota"]),
            } for b in rows("SELECT * FROM cadangan_baja WHERE tanaman_id = ? ORDER BY id", i)],
            "fertiliser_programme": [{
                "product": tr(p["jenis_baja"]), "rate_min": p["kadar_min"], "rate_max": p["kadar_max"],
                "unit": tr(p["unit"]), "timing": tr(p["masa_aplikasi"]), "note": tr(p["nota"]),
            } for p in rows("SELECT * FROM program_baja WHERE tanaman_id = ? ORDER BY id", i)],
            "special_nutrients": [{
                "nutrient": tr(n["nutrien"]), "role": tr(n["kepentingan"]), "product": tr(n["sumber_baja"]),
                "rate_min_kg_ha": n["kadar_min_kg_ha"], "rate_max_kg_ha": n["kadar_max_kg_ha"],
                "timing": tr(n["masa_aplikasi"]),
            } for n in rows("SELECT * FROM nutrien_khusus WHERE tanaman_id = ? ORDER BY id", i)],
            "practices": [{"category": tr(a["kategori"]), "text": tr(a["perkara"])}
                          for a in rows("SELECT * FROM amalan WHERE tanaman_id = ? ORDER BY id", i)],
            "spacing": [{
                "variety": tr(j["jenis_varieti"]),
                "row_min_cm": j["antara_baris_min_cm"], "row_max_cm": j["antara_baris_max_cm"],
                "plant_min_cm": j["dalam_baris_min_cm"], "plant_max_cm": j["dalam_baris_max_cm"],
            } for j in rows("SELECT * FROM jarak_tanaman WHERE tanaman_id = ? ORDER BY id", i)],
        })

    data = {
        "crops": crops,
        "rotation": [{
            "before": tr(g["sebelum"]), "after": tr(g["selepas"]),
            "yield_gain_pct": g["kesan_hasil_peratus"], "note": tr(g["nota"]),
        } for g in rows("""
            SELECT s.nama_bm AS sebelum, e.nama_bm AS selepas, g.kesan_hasil_peratus, g.nota
            FROM giliran_tanaman g
            JOIN tanaman s ON s.id = g.tanaman_sebelum_id
            JOIN tanaman e ON e.id = g.tanaman_selepas_id ORDER BY g.id""")],
        "rotation_notes": [tr(r["nota"]) for r in rows("SELECT nota FROM nota_giliran ORDER BY id")],
    }

    con.close()
    if missing:
        raise MissingTranslation(missing)
    return data
