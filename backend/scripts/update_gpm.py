#!/usr/bin/env python3
"""Download NASA GPM IMERG rainfall for Sarawak into backend/data/gpm_sarawak.json.

Runs in GitHub Actions (.github/workflows/gpm.yml) with the EARTHDATA_TOKEN secret
(a NASA Earthdata Login user token; the account must have authorised
"NASA GESDISC DATA ARCHIVE").

  python3 update_gpm.py --probe            check access with one monthly and one daily file
  python3 update_gpm.py                    update recent rainfall (and normals if missing)
  python3 update_gpm.py --rebuild-normals  recompute the 2001–2024 monthly normals

Only the Sarawak box is downloaded from each file (NASA OPeNDAP subsetting), so each
request is a few kilobytes instead of the 18–26 MB global file.
"""
import argparse
import io
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

import h5py
import numpy as np
import requests

CMR = "https://cmr.earthdata.nasa.gov/search/granules.umm_json"
MONTHLY = "GPM_3IMERGM"   # IMERG Final, monthly, 0.1°, mm/hr
DAILY = "GPM_3IMERGDL"    # IMERG Late, daily, 0.1°
DAILY_FINAL = "GPM_3IMERGDF"  # IMERG Final, daily (only used to check the Late run for bias)
VERSION = "07"
NORMAL_YEARS = (2001, 2024)
RECENT_DAYS = 60

# IMERG grid: 3600 x 1800 cells of 0.1°, centres from -179.95 and -89.95.
LON0, LAT0, STEP = -179.95, -89.95, 0.1
BOX = {"west": 109.55, "east": 115.75, "south": 0.85, "north": 5.05}   # Sarawak, cell centres
I0, I1 = round((BOX["west"] - LON0) / STEP), round((BOX["east"] - LON0) / STEP)
J0, J1 = round((BOX["south"] - LAT0) / STEP), round((BOX["north"] - LAT0) / STEP)
NLON, NLAT = I1 - I0 + 1, J1 - J0 + 1

OUT = Path(__file__).resolve().parent.parent / "data" / "gpm_sarawak.json"
KUCHING = (1.553, 110.359)


def session():
    token = os.environ.get("EARTHDATA_TOKEN", "").strip()
    if not token:
        sys.exit("EARTHDATA_TOKEN is not set. Add it in GitHub: Settings → Secrets and variables → Actions.")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {token}"
    s.headers["User-Agent"] = "BUMI360-gpm/1.0"
    return s


def granules(short_name, start, end):
    """[(date, opendap_url, data_url)] from NASA CMR (no login needed)."""
    out, page = [], 1
    while True:
        r = requests.get(CMR, params={
            "short_name": short_name, "version": VERSION, "page_size": 200, "page_num": page,
            "temporal": f"{start}T00:00:00Z,{end}T23:59:59Z", "sort_key": "start_date",
        }, timeout=60)
        r.raise_for_status()
        items = r.json().get("items", [])
        for it in items:
            g = it["umm"]
            day = g["TemporalExtent"]["RangeDateTime"]["BeginningDateTime"][:10]
            urls = {u.get("Subtype") or u.get("Type"): u["URL"] for u in g.get("RelatedUrls", [])}
            out.append((date.fromisoformat(day), urls.get("OPENDAP DATA"), urls.get("GET DATA")))
        if len(items) < 200:
            return out
        page += 1


def _fetch(s, url, tries=4):
    for k in range(tries):
        try:
            r = s.get(url, timeout=120)
            if r.status_code == 200:
                return r.content
            if r.status_code in (401, 403):
                raise PermissionError(
                    f"NASA refused access ({r.status_code}). Check that the EARTHDATA_TOKEN is valid (tokens last 60 days) "
                    "and that the account has authorised NASA GESDISC DATA ARCHIVE.")
            last = f"HTTP {r.status_code}: {r.text[:200]}"
        except requests.RequestException as e:
            last = str(e)
        time.sleep(2 ** k)
    raise RuntimeError(f"Download failed after {tries} tries: {url}\n{last}")


def _variable(h5, monthly):
    for name in (["Grid/precipitation", "precipitation"] if monthly else ["precipitation", "Grid/precipitation"]):
        if name in h5:
            return h5[name]
    raise KeyError(f"precipitation not found; file has: {list(h5.keys())}")


def subset(s, opendap_url, data_url, monthly):
    """Sarawak box as an array [lat][lon] in mm/day."""
    var = "/Grid/precipitation" if monthly else "/precipitation"
    ce = f"{var}[0:0][{I0}:{I1}][{J0}:{J1}]"
    try:
        raw = _fetch(s, f"{opendap_url}.dap.nc4?dap4.ce={quote(ce, safe='/')}")
        with h5py.File(io.BytesIO(raw), "r") as h5:
            v = _variable(h5, monthly)
            arr = np.asarray(v[...], dtype="float64").reshape(NLON, NLAT)
            units = v.attrs.get("units", b"")
    except PermissionError:
        raise
    except Exception as e:  # fall back to the whole file
        print(f"  OPeNDAP subset failed ({type(e).__name__}: {str(e)[:160]}); downloading the full file", flush=True)
        raw = _fetch(s, data_url)
        with h5py.File(io.BytesIO(raw), "r") as h5:
            v = _variable(h5, monthly)
            arr = np.asarray(v[0, I0:I1 + 1, J0:J1 + 1], dtype="float64")
            units = v.attrs.get("units", b"")
    units = units.decode() if isinstance(units, bytes) else str(units)
    arr[arr < 0] = np.nan          # fill values
    if "hr" in units:              # monthly product is mm/hr
        arr = arr * 24.0
    return arr.T                   # -> [lat][lon]


def cell(lat, lon):
    return round((lat - (LAT0 + J0 * STEP)) / STEP), round((lon - (LON0 + I0 * STEP)) / STEP)


def probe(s):
    print(f"Sarawak box: lon {BOX['west']}–{BOX['east']}, lat {BOX['south']}–{BOX['north']} → {NLON} x {NLAT} cells "
          f"(indices lon {I0}:{I1}, lat {J0}:{J1})")
    for short, monthly, start, end in [(MONTHLY, True, "2024-01-01", "2024-01-31"), (DAILY, False, None, None)]:
        if start is None:
            end_d = date.today()
            start, end = (end_d - timedelta(days=5)).isoformat(), end_d.isoformat()
        g = granules(short, start, end)
        print(f"\n== {short}: {len(g)} file(s) found for {start}..{end}")
        day, od, du = g[-1]
        print("   file date:", day, "\n   opendap:", od)
        dmr = s.get(od + ".dmr.xml", timeout=60)
        print("   DMR status:", dmr.status_code)
        for line in dmr.text.splitlines():
            if any(k in line for k in ("<Float32 name=\"precipitation", "<Float64 name=\"lon", "<Float32 name=\"lon",
                                       "<Dim name=", "units", "<Group name")):
                print("     ", line.strip()[:140])
        a = subset(s, od, du, monthly)
        j, i = cell(*KUCHING)
        print(f"   subset shape {a.shape}, min {np.nanmin(a):.2f}, mean {np.nanmean(a):.2f}, max {np.nanmax(a):.2f} mm/day")
        print(f"   Kuching cell [{j},{i}] = {a[j, i]:.2f} mm/day")


def bias_check(s, start="2025-07-01", end="2025-09-30"):
    """Compare IMERG Late with IMERG Final over the same days (Final is gauge-corrected)."""
    late = {d: (o, u) for d, o, u in granules(DAILY, start, end)}
    final = {d: (o, u) for d, o, u in granules(DAILY_FINAL, start, end)}
    days = sorted(set(late) & set(final))
    print(f"Bias check {start}..{end}: {len(days)} days with both Late and Final", flush=True)

    def one(day):
        return subset(s, *late[day], False), subset(s, *final[day], False)

    tl = np.zeros((NLAT, NLON))
    tf = np.zeros((NLAT, NLON))
    with ThreadPoolExecutor(max_workers=8) as pool:
        for a, b in pool.map(one, days):
            tl += np.nan_to_num(a)
            tf += np.nan_to_num(b)
    ratio = tl / np.where(tf > 0, tf, np.nan)
    print(f"  Sarawak mean: Late {np.nanmean(tl):.0f} mm, Final {np.nanmean(tf):.0f} mm, Late/Final = {np.nanmean(tl) / np.nanmean(tf):.2f}")
    print(f"  per-cell Late/Final ratio: 10th pct {np.nanpercentile(ratio, 10):.2f}, median {np.nanmedian(ratio):.2f}, "
          f"90th pct {np.nanpercentile(ratio, 90):.2f}")
    for name, (la, lo) in {"Kuching": KUCHING, "Sibu": (2.287, 111.830), "Miri": (4.399, 113.991), "Limbang": (4.755, 115.009)}.items():
        j, i = cell(la, lo)
        print(f"  {name:8} Late {tl[j, i]:6.0f} mm  Final {tf[j, i]:6.0f} mm  ratio {tl[j, i] / tf[j, i]:.2f}")


def build_normals(s):
    y0, y1 = NORMAL_YEARS
    g = granules(MONTHLY, f"{y0}-01-01", f"{y1}-12-31")
    print(f"Normals: {len(g)} monthly files {y0}–{y1}", flush=True)
    sums = np.zeros((12, NLAT, NLON))
    counts = np.zeros((12, NLAT, NLON))

    def one(item):
        day, od, du = item
        return day.month - 1, subset(s, od, du, True)

    with ThreadPoolExecutor(max_workers=8) as pool:
        for n, (m, a) in enumerate(pool.map(one, g), 1):
            ok = ~np.isnan(a)
            sums[m][ok] += a[ok]
            counts[m][ok] += 1
            if n % 24 == 0:
                print(f"  {n}/{len(g)}", flush=True)
    normals = np.where(counts > 0, sums / np.maximum(counts, 1), np.nan)
    return {"product": f"{MONTHLY} v{VERSION} (IMERG Final, monthly)", "period": f"{y0}–{y1}",
            "files": len(g), "mm_per_day": np.round(normals, 2).tolist()}


def build_recent(s, normals):
    end = date.today()
    g = granules(DAILY, (end - timedelta(days=RECENT_DAYS + 10)).isoformat(), end.isoformat())
    g = g[-RECENT_DAYS:]
    print(f"Recent: {len(g)} daily files {g[0][0]}..{g[-1][0]}", flush=True)

    def one(item):
        return item[0], subset(s, item[1], item[2], False)

    total = np.zeros((NLAT, NLON))
    normal = np.zeros((NLAT, NLON))
    norm = np.array(normals["mm_per_day"], dtype="float64")
    with ThreadPoolExecutor(max_workers=8) as pool:
        for day, a in pool.map(one, g):
            total += np.nan_to_num(a)
            normal += np.nan_to_num(norm[day.month - 1])
    return {"product": f"{DAILY} v{VERSION} (IMERG Late, daily)", "start": g[0][0].isoformat(), "end": g[-1][0].isoformat(),
            "days": len(g), "total_mm": np.round(total, 1).tolist(), "normal_mm": np.round(normal, 1).tolist()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--rebuild-normals", action="store_true")
    ap.add_argument("--bias-check", action="store_true")
    args = ap.parse_args()
    s = session()
    if args.probe:
        probe(s)
        return
    if args.bias_check:
        bias_check(s)
        return
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    normals = old.get("normals")
    if args.rebuild_normals or not normals:
        normals = build_normals(s)
    recent = build_recent(s, normals)
    OUT.write_text(json.dumps({
        "source": "NASA GPM IMERG V07 via GES DISC (opendap.earthdata.nasa.gov)",
        "acknowledgement": "GPM IMERG data provided by NASA Goddard Earth Sciences Data and Information Services Center (GES DISC).",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "grid": {"lon0": round(LON0 + I0 * STEP, 2), "lat0": round(LAT0 + J0 * STEP, 2), "step": STEP, "nlon": NLON, "nlat": NLAT,
                 "order": "[lat][lon], row 0 is the southern edge"},
        "normals": normals,
        "recent": recent,
    }, separators=(",", ":")) + "\n")
    print(f"Saved {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
