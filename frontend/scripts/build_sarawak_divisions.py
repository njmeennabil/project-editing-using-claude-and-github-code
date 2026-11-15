#!/usr/bin/env python3
"""Build public/data/sarawak-divisions.geojson: Sarawak's 12 divisions.

Source: geoBoundaries gbOpen MYS ADM2 (districts), from citypopulation.de,
Creative Commons Attribution 3.0. Changes: the 40 Sarawak districts are merged
into their 12 divisions, simplified and rounded.

Usage:
  python3 build_sarawak_divisions.py geoBoundaries-MYS-ADM2_simplified.geojson
Download the input from
  https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/9469f09/releaseData/gbOpen/MYS/ADM2/geoBoundaries-MYS-ADM2_simplified.geojson
Needs: shapely
"""
import json
import sys
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

DIVISIONS = {
    "KUCHING": ["Kuching", "Bau", "Lundu"],
    "SAMARAHAN": ["Samarahan", "Asajaya", "Simunjan"],
    "SERIAN": ["Serian", "Tebedu"],
    "SRI_AMAN": ["Sri Aman", "Lubok Antu"],
    "BETONG": ["Betong", "Saratok", "Pusa", "Kabong"],
    "SARIKEI": ["Sarikei", "Maradong", "Julau", "Pakan"],
    "SIBU": ["Sibu", "Kanowit", "Selangau"],
    "MUKAH": ["Mukah", "Dalat", "Daro", "Matu", "Tanjung Manis"],
    "KAPIT": ["Kapit", "Song", "Belaga", "Bukit Mabong"],
    "BINTULU": ["Bintulu", "Tatau", "Sebauh"],
    "MIRI": ["Miri", "Marudi", "Subis", "Beluru", "Telang Usan"],
    "LIMBANG": ["Limbang", "Lawas"],
}
NAMES = {"SRI_AMAN": "Sri Aman"}
SIMPLIFY = 0.004   # degrees, about 400 m
DECIMALS = 4


def rounded(geom):
    def r(c):
        return [r(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], DECIMALS), round(c[1], DECIMALS)]
    g = mapping(geom)
    return {"type": g["type"], "coordinates": r(g["coordinates"])}


src = json.load(open(sys.argv[1]))
by_name = {}
for f in src["features"]:
    by_name.setdefault(f["properties"]["shapeName"], []).append(shape(f["geometry"]))

features = []
for code, districts in DIVISIONS.items():
    missing = [d for d in districts if d not in by_name]
    if missing:
        sys.exit(f"Missing districts for {code}: {missing}")
    geom = unary_union([g.buffer(0) for d in districts for g in by_name[d]]).simplify(SIMPLIFY, preserve_topology=True)
    features.append({
        "type": "Feature",
        "properties": {"code": code, "name": NAMES.get(code, code.title()), "districts": districts},
        "geometry": rounded(geom),
    })

out = Path(__file__).resolve().parent.parent / "public" / "data" / "sarawak-divisions.geojson"
out.write_text(json.dumps({
    "type": "FeatureCollection",
    "attribution": "Boundaries: geoBoundaries (citypopulation.de), CC BY 3.0. Districts merged into divisions by BUMI360.",
    "features": features,
}, separators=(",", ":")))
print(f"Saved {out} ({out.stat().st_size // 1024} KB, {len(features)} divisions)")
