"""NASA POWER climate data for BUMI360.

Uses the POWER Climatology API (no account needed): long-term monthly averages of
air temperature at 2 m (T2M, °C) and corrected precipitation (PRECTOTCORR, mm/day).

* The 12 Sarawak divisions are read from data/sarawak_climate.json, which
  scripts/update_climate.py downloads ahead of time, so they work even if NASA is slow.
* Any other point (e.g. a farmer's GPS location) is fetched live and kept in memory.

Data acknowledgement: data obtained from the NASA Langley Research Center (LaRC)
POWER Project funded through the NASA Earth Science/Applied Science Program.
"""
import json
import threading
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
FILL_VALUE = -999.0
DEFAULT_SEASON_DAYS = 30  # used when a crop has no maturity figure

SAVED_FILE = Path(__file__).resolve().parent / "data" / "sarawak_climate.json"

_live_cache = {}
_lock = threading.Lock()


class ClimateUnavailable(Exception):
    pass


def fetch_climatology(lat, lon, timeout=20):
    """Download monthly climatology for one point from NASA POWER."""
    query = urlencode({
        "parameters": "T2M,PRECTOTCORR",
        "community": "AG",
        "latitude": f"{lat:.4f}",
        "longitude": f"{lon:.4f}",
        "format": "JSON",
    })
    req = Request(f"{POWER_URL}?{query}", headers={"User-Agent": "BUMI360/1.0"})
    try:
        with urlopen(req, timeout=timeout) as res:
            body = json.load(res)
    except (URLError, TimeoutError, ValueError) as e:
        raise ClimateUnavailable("NASA POWER is not responding right now. Try again, or enter your readings manually.") from e

    try:
        p = body["properties"]["parameter"]
        temp = [float(p["T2M"][m]) for m in MONTHS]
        rain = [float(p["PRECTOTCORR"][m]) for m in MONTHS]
    except (KeyError, TypeError, ValueError) as e:
        raise ClimateUnavailable("NASA POWER returned data BUMI360 could not read.") from e
    if FILL_VALUE in temp or FILL_VALUE in rain:
        raise ClimateUnavailable("NASA POWER has no data for this location.")

    header = body.get("header", {})
    return {
        "temp_c": temp,
        "rain_mm_day": rain,
        "period": header.get("range", "long-term average"),
        "model": ", ".join(header.get("sources", [])) or None,
    }


def load_saved():
    try:
        return json.loads(SAVED_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"locations": {}}


_saved = load_saved()


def climate_for_location(code):
    """Saved climate for a Sarawak division code, or None if unknown."""
    return _saved["locations"].get(code)


def climate_for_point(lat, lon):
    """Live climate for any point, cached in memory (rounded to about 5 km)."""
    key = (round(lat, 2), round(lon, 2))
    with _lock:
        if key in _live_cache:
            return _live_cache[key]
    data = fetch_climatology(lat, lon)
    with _lock:
        if len(_live_cache) > 500:
            _live_cache.clear()
        _live_cache[key] = data
    return data


def crop_season_days(crop):
    """Length of the growing season for a crop, and whether it was assumed."""
    lo, hi = crop["maturity_min_days"], crop["maturity_max_days"]
    if lo is None and hi is None:
        return DEFAULT_SEASON_DAYS, True
    lo = lo if lo is not None else hi
    hi = hi if hi is not None else lo
    return round((lo + hi) / 2), False


def season(climate, start_month, days):
    """Average temperature and total rainfall from the 1st of start_month for `days` days."""
    m = start_month - 1
    left = days
    rain = 0.0
    temp_sum = 0.0
    months = []
    while left > 0:
        n = min(DAYS_IN_MONTH[m], left)
        rain += climate["rain_mm_day"][m] * n
        temp_sum += climate["temp_c"][m] * n
        months.append(m)
        left -= n
        m = (m + 1) % 12
    label = MONTH_NAMES[months[0]] if len(months) == 1 else f"{MONTH_NAMES[months[0]]}–{MONTH_NAMES[months[-1]]}"
    return {"temp_c": round(temp_sum / days, 1), "rain_mm": round(rain), "months": label}
