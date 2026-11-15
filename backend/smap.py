"""NASA SMAP soil moisture for Sarawak, read from data/smap_sarawak.json.

The file is written every week by scripts/update_smap.py (GitHub Actions) from SMAP
Level 4 (SPL4SMGP, 9 km). It holds, for a block of the EASE-Grid 2.0 over Sarawak:
  normals  monthly mean surface and root-zone soil moisture (and its spread), 2016–2025
  recent   the mean of the last 7 days

Values are m³/m³ (volume of water per volume of soil); BUMI360 shows them as %.
A place uses the mean of the 3 x 3 cells around it (~27 km).
"""
import json
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "smap_sarawak.json"
_data = None
_loaded = False


def data():
    global _data, _loaded
    if not _loaded:
        try:
            _data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            _data = None
        _loaded = True
    return _data


def set_data(d):
    global _data, _loaded
    _data, _loaded = d, True


def _cells(lat, lon, radius=1):
    d = data()
    if not d:
        return []
    lats, lons = d["grid"]["lat"], d["grid"]["lon"]
    j = min(range(len(lats)), key=lambda k: abs(lats[k] - lat))
    i = min(range(len(lons)), key=lambda k: abs(lons[k] - lon))
    step_lat = abs(lats[1] - lats[0]) if len(lats) > 1 else 0.1
    step_lon = abs(lons[1] - lons[0]) if len(lons) > 1 else 0.1
    if abs(lats[j] - lat) > step_lat or abs(lons[i] - lon) > step_lon:
        return []
    return [(jj, ii) for jj in range(j - radius, j + radius + 1) for ii in range(i - radius, i + radius + 1)
            if 0 <= jj < len(lats) and 0 <= ii < len(lons)]


def _mean(grid, cells):
    vals = [grid[j][i] for j, i in cells if grid[j][i] is not None]
    return sum(vals) / len(vals) if vals else None


def label(z):
    if z is None:
        return "no usual value to compare with"
    if z <= -1.0:
        return "much drier than usual"
    if z < -0.4:
        return "drier than usual"
    if z <= 0.4:
        return "about usual"
    if z < 1.0:
        return "wetter than usual"
    return "much wetter than usual"


def at(lat, lon):
    """This week's soil moisture at a place, compared with the usual for the month."""
    d = data()
    cells = _cells(lat, lon)
    if not d or not cells or not d.get("recent"):
        return None
    r, n = d["recent"], d["normals"]
    root, surf = _mean(r["rootzone"], cells), _mean(r["surface"], cells)
    if root is None:
        return None
    m = date.fromisoformat(r["end"]).month - 1
    usual, spread = _mean(n["rootzone"][m], cells), _mean(n["rootzone_std"][m], cells)
    z = None if usual is None or not spread else (root - usual) / spread
    return {
        "start": r["start"], "end": r["end"], "days": r["days"],
        "rootzone_pct": round(root * 100, 1),
        "surface_pct": None if surf is None else round(surf * 100, 1),
        "usual_rootzone_pct": None if usual is None else round(usual * 100, 1),
        "z": None if z is None else round(z, 2),
        "label": label(z),
        "normals_period": n["period"],
    }


def describe():
    d = data()
    if not d:
        return None
    return {"normals_period": d["normals"]["period"], "recent": [d["recent"]["start"], d["recent"]["end"]], "updated": d.get("updated")}
