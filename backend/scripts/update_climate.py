#!/usr/bin/env python3
"""Download NASA POWER climate for Sarawak's 12 divisions into data/sarawak_climate.json.

Run from the backend folder:  python3 scripts/update_climate.py
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from locations import SARAWAK_DIVISIONS  # noqa: E402
from nasa_power import SAVED_FILE, fetch_climatology  # noqa: E402

out = {
    "source": "NASA POWER Climatology API (power.larc.nasa.gov)",
    "acknowledgement": "Data obtained from the NASA Langley Research Center (LaRC) POWER Project "
                       "funded through the NASA Earth Science/Applied Science Program.",
    "parameters": {"temp_c": "T2M, air temperature at 2 m (°C)", "rain_mm_day": "PRECTOTCORR, precipitation (mm/day)"},
    "downloaded": date.today().isoformat(),
    "locations": {},
}
for d in SARAWAK_DIVISIONS:
    c = fetch_climatology(d["lat"], d["lon"])
    out["locations"][d["code"]] = {**c, "name": d["name"], "lat": d["lat"], "lon": d["lon"]}
    print(f"  {d['name']:10} {sum(r * n for r, n in zip(c['rain_mm_day'], [31,28,31,30,31,30,31,31,30,31,30,31])):6.0f} mm/year  "
          f"{sum(c['temp_c']) / 12:.1f} °C")

SAVED_FILE.parent.mkdir(exist_ok=True)
SAVED_FILE.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Saved {SAVED_FILE}")
