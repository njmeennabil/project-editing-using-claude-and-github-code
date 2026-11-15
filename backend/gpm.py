"""NASA GPM IMERG rainfall for Sarawak, read from data/gpm_sarawak.json.

The file is written every week by scripts/update_gpm.py (GitHub Actions). It holds a
0.1° (~10 km) grid over Sarawak with:
  normals  mean rainfall (mm/day) for each month, 2001–2024 (IMERG Final, monthly)
  recent   rainfall over the last 60 days, and the normal amount for those days

Values for a place are the mean of the 3 x 3 cells around it (~30 km), which smooths
out single-cell noise. If the file is missing or the place is outside the grid,
BUMI360 falls back to NASA POWER rainfall.
"""
import json
import math
import re
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "gpm_sarawak.json"
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
    """Use another dataset (tests)."""
    global _data, _loaded
    _data, _loaded = d, True


def _cells(lat, lon, radius=1):
    d = data()
    if not d:
        return []
    g = d["grid"]
    j = round((lat - g["lat0"]) / g["step"])
    i = round((lon - g["lon0"]) / g["step"])
    if not (0 <= j < g["nlat"] and 0 <= i < g["nlon"]):
        return []
    return [(jj, ii) for jj in range(j - radius, j + radius + 1) for ii in range(i - radius, i + radius + 1)
            if 0 <= jj < g["nlat"] and 0 <= ii < g["nlon"]]


def _mean(grid, cells):
    vals = [grid[j][i] for j, i in cells if grid[j][i] is not None and not math.isnan(grid[j][i])]
    return sum(vals) / len(vals) if vals else None


def normals_at(lat, lon):
    """Mean rainfall (mm/day) for Jan..Dec at a place, or None."""
    cells = _cells(lat, lon)
    if not cells:
        return None
    months = [_mean(data()["normals"]["mm_per_day"][m], cells) for m in range(12)]
    return None if any(v is None for v in months) else months


def recent_at(lat, lon):
    """Rainfall over the last 60 days compared with normal, or None."""
    cells = _cells(lat, lon)
    d = data()
    if not cells or not d or not d.get("recent"):
        return None
    r = d["recent"]
    total, normal = _mean(r["total_mm"], cells), _mean(r["normal_mm"], cells)
    if total is None or not normal:
        return None
    return {"start": r["start"], "end": r["end"], "days": r["days"],
            "total_mm": round(total), "normal_mm": round(normal), "ratio": round(total / normal, 2)}


def describe():
    d = data()
    if not d:
        return None
    return {"normals_period": d["normals"]["period"], "normals_product": d["normals"]["product"],
            "recent_product": d.get("recent", {}).get("product"), "updated": d.get("updated")}


def merge(climate, lat, lon):
    """NASA POWER climate with its rainfall replaced by GPM where available."""
    normals = normals_at(lat, lon)
    if normals is None:
        return {**climate, "rain_source": "NASA POWER"}
    return {**climate, "rain_mm_day": normals, "rain_mm_day_power": climate["rain_mm_day"],
            "rain_source": "NASA GPM IMERG", "rain_period": data()["normals"]["period"]}


def source_label(climate):
    return "NASA GPM + POWER" if climate.get("rain_source") == "NASA GPM IMERG" else "NASA POWER"


def period_label(climate):
    if climate.get("rain_source") == "NASA GPM IMERG":
        years = re.findall(r"(\d{4})", climate.get("period") or "")
        temp = f"{years[0]}–{years[-1]}" if len(years) >= 2 else "long-term"
        return f"rain {climate['rain_period']} (GPM), temperature {temp} (POWER)"
    return climate.get("period")
