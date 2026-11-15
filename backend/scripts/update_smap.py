#!/usr/bin/env python3
"""Download NASA SMAP soil moisture for Sarawak into backend/data/smap_sarawak.json.

Uses SMAP Level 4 (SPL4SMGP v008, 9 km, 3-hourly): surface (0–5 cm) and root-zone
(0–100 cm) soil moisture from SMAP satellite observations merged into a land model,
so dense forest does not leave gaps. Runs in GitHub Actions with EARTHDATA_TOKEN.

  python3 update_smap.py --probe            check access, variable names and grid position
  python3 update_smap.py                    update this week's soil moisture (and normals if missing)
  python3 update_smap.py --rebuild-normals  recompute the 2016–2025 monthly normals

SMAP uses the EASE-Grid 2.0 (9 km) map grid, where every row has one latitude and every
column one longitude, so the Sarawak box is a simple block of rows and columns.
"""
import argparse
import io
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

import h5py
import numpy as np
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from update_gpm import KUCHING, _fetch, session  # noqa: E402

CMR = "https://cmr.earthdata.nasa.gov/search/granules.umm_json"
PRODUCT, VERSION = "SPL4SMGP", "008"
NROWS, NCOLS = 1624, 3856                 # EASE-Grid 2.0 global, 9 km
BOX = {"west": 109.5, "east": 115.8, "south": 0.8, "north": 5.1}
NORMAL_YEARS = (2016, 2025)
SAMPLE_DAYS = (1, 8, 15, 22)              # days of each month used for the normals
SAMPLE_HOUR = "06:00"                     # 06:00 UTC = 14:00 in Sarawak
RECENT_DAYS = 7
OUT = Path(__file__).resolve().parent.parent / "data" / "smap_sarawak.json"


def granules(start, end):
    """[(datetime, opendap_url, data_url)] for SPL4SMGP between two ISO times."""
    out, page = [], 1
    while True:
        r = requests.get(CMR, params={"short_name": PRODUCT, "version": VERSION, "page_size": 500, "page_num": page,
                                      "temporal": f"{start},{end}", "sort_key": "start_date"}, timeout=60)
        r.raise_for_status()
        items = r.json().get("items", [])
        for it in items:
            g = it["umm"]
            t = datetime.fromisoformat(g["TemporalExtent"]["RangeDateTime"]["BeginningDateTime"].replace("Z", "+00:00"))
            urls = {u.get("Subtype") or u.get("Type"): u["URL"] for u in g.get("RelatedUrls", [])}
            out.append((t, urls.get("OPENDAP DATA"), urls.get("GET DATA")))
        if len(items) < 500:
            return out
        page += 1


def _find(h5, name):
    found = []
    h5.visititems(lambda n, o: found.append(o) if isinstance(o, h5py.Dataset) and n.split("/")[-1] == name else None)
    if not found:
        raise KeyError(f"{name} not in response; has {list(h5.keys())}")
    return found[0]


def dap(s, opendap_url, *exprs):
    """Fetch a DAP4 subset and return {variable name: numpy array}."""
    ce = ";".join(exprs)
    raw = _fetch(s, f"{opendap_url}.dap.nc4?dap4.ce={quote(ce, safe='/;')}")
    out = {}
    with h5py.File(io.BytesIO(raw), "r") as h5:
        for e in exprs:
            name = e.split("[")[0].split("/")[-1]
            ds = _find(h5, name)
            arr = np.asarray(ds[...], dtype="float64")
            fill = ds.attrs.get("_FillValue")
            if fill is not None:
                arr[arr == float(np.asarray(fill).ravel()[0])] = np.nan
            arr[arr < -1] = np.nan
            out[name] = arr
    return out


def locate(s, opendap_url):
    """Rows and columns of the Sarawak box, with their latitudes and longitudes."""
    v = dap(s, opendap_url, f"/cell_lat[0:{NROWS - 1}][{NCOLS // 2}]", f"/cell_lon[{NROWS // 2}][0:{NCOLS - 1}]")
    lats, lons = v["cell_lat"].ravel(), v["cell_lon"].ravel()
    rows = np.where((lats >= BOX["south"]) & (lats <= BOX["north"]))[0]
    cols = np.where((lons >= BOX["west"]) & (lons <= BOX["east"]))[0]
    return int(rows.min()), int(rows.max()), int(cols.min()), int(cols.max()), lats, lons


def subset(s, opendap_url, r0, r1, c0, c1):
    v = dap(s, opendap_url, f"/Geophysical_Data/sm_surface[{r0}:{r1}][{c0}:{c1}]",
            f"/Geophysical_Data/sm_rootzone[{r0}:{r1}][{c0}:{c1}]")
    return v["sm_surface"], v["sm_rootzone"]


def probe(s):
    end = datetime.now(timezone.utc)
    g = granules((end - timedelta(days=8)).strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ"))
    print(f"{PRODUCT} v{VERSION}: {len(g)} files in the last 8 days; latest {g[-1][0]}")
    t, od, du = g[-1]
    print("opendap:", od)
    dmr = s.get(od + ".dmr.xml", timeout=60)
    print("DMR status:", dmr.status_code)
    if dmr.status_code != 200:
        print(dmr.text[:500])
        return
    for line in dmr.text.splitlines():
        if any(k in line for k in ('<Group name', 'name="sm_surface"', 'name="sm_rootzone"', 'name="cell_lat"',
                                   'name="cell_lon"', '<Dimension name')):
            print("   ", line.strip()[:120])
    r0, r1, c0, c1, lats, lons = locate(s, od)
    print(f"Sarawak rows {r0}–{r1} (lat {lats[r1]:.3f}–{lats[r0]:.3f}), cols {c0}–{c1} (lon {lons[c0]:.3f}–{lons[c1]:.3f})")
    print(f"row spacing near Sarawak: {np.diff(lats[r0:r1 + 1]).mean():.4f}°, col spacing {np.diff(lons[c0:c1 + 1]).mean():.4f}°")
    surf, root = subset(s, od, r0, r1, c0, c1)
    j = int(np.argmin(np.abs(lats[r0:r1 + 1] - KUCHING[0])))
    i = int(np.argmin(np.abs(lons[c0:c1 + 1] - KUCHING[1])))
    for name, a in (("surface", surf), ("rootzone", root)):
        print(f"{name}: shape {a.shape}, valid {np.isfinite(a).mean():.0%}, min {np.nanmin(a):.3f}, mean {np.nanmean(a):.3f}, "
              f"max {np.nanmax(a):.3f} m3/m3; Kuching {a[j, i]:.3f}")


def pick(gs, day, hour=SAMPLE_HOUR):
    """The file for one day at the sample hour (or the nearest that day)."""
    same = [x for x in gs if x[0].date() == day]
    if not same:
        return None
    target = datetime.fromisoformat(f"{day}T{hour}:00+00:00")
    return min(same, key=lambda x: abs((x[0] - target).total_seconds()))


def build_normals(s, r0, r1, c0, c1):
    y0, y1 = NORMAL_YEARS
    days = [date(y, m, d) for y in range(y0, y1 + 1) for m in range(1, 13) for d in SAMPLE_DAYS]
    chosen = []
    for y in range(y0, y1 + 1):
        gs = granules(f"{y}-01-01T00:00:00Z", f"{y}-12-31T23:59:59Z")
        chosen += [g for g in (pick(gs, d) for d in days if d.year == y) if g]
    print(f"Normals: {len(chosen)} sample files {y0}–{y1}", flush=True)
    shape = (12, r1 - r0 + 1, c1 - c0 + 1)
    acc = {k: np.zeros(shape) for k in ("s_sum", "r_sum", "r_sq", "n")}

    def one(g):
        return g[0].month - 1, subset(s, g[1], r0, r1, c0, c1)

    with ThreadPoolExecutor(max_workers=8) as pool:
        for k, (m, (surf, root)) in enumerate(pool.map(one, chosen), 1):
            ok = np.isfinite(surf) & np.isfinite(root)
            acc["s_sum"][m][ok] += surf[ok]
            acc["r_sum"][m][ok] += root[ok]
            acc["r_sq"][m][ok] += root[ok] ** 2
            acc["n"][m][ok] += 1
            if k % 60 == 0:
                print(f"  {k}/{len(chosen)}", flush=True)
    n = np.where(acc["n"] > 0, acc["n"], np.nan)
    r_mean = acc["r_sum"] / n
    r_std = np.sqrt(np.maximum(acc["r_sq"] / n - r_mean ** 2, 0))
    return {"period": f"{y0}–{y1}", "samples": len(chosen),
            "surface": np.round(acc["s_sum"] / n, 3).tolist(),
            "rootzone": np.round(r_mean, 3).tolist(), "rootzone_std": np.round(r_std, 4).tolist()}


def build_recent(s, r0, r1, c0, c1):
    end = datetime.now(timezone.utc)
    gs = granules((end - timedelta(days=RECENT_DAYS + 10)).strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ"))
    days = sorted({g[0].date() for g in gs})[-RECENT_DAYS:]
    chosen = [pick(gs, d) for d in days]
    print(f"Recent: {len(chosen)} days {days[0]}..{days[-1]}", flush=True)
    with ThreadPoolExecutor(max_workers=8) as pool:
        res = list(pool.map(lambda g: subset(s, g[1], r0, r1, c0, c1), chosen))
    surf = np.nanmean([a for a, _ in res], axis=0)
    root = np.nanmean([b for _, b in res], axis=0)
    return {"start": days[0].isoformat(), "end": days[-1].isoformat(), "days": len(days),
            "surface": np.round(surf, 3).tolist(), "rootzone": np.round(root, 3).tolist()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--rebuild-normals", action="store_true")
    args = ap.parse_args()
    s = session()
    if args.probe:
        probe(s)
        return
    end = datetime.now(timezone.utc)
    latest = granules((end - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ"))[-1]
    r0, r1, c0, c1, lats, lons = locate(s, latest[1])
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    normals = old.get("normals")
    if args.rebuild_normals or not normals or old.get("grid", {}).get("rows") != [r0, r1]:
        normals = build_normals(s, r0, r1, c0, c1)
    recent = build_recent(s, r0, r1, c0, c1)
    OUT.write_text(json.dumps({
        "source": "NASA SMAP L4 SPL4SMGP v008 via NSIDC DAAC (opendap.earthdata.nasa.gov)",
        "acknowledgement": "SMAP Level 4 soil moisture data provided by the NASA National Snow and Ice Data Center "
                           "Distributed Active Archive Center (NSIDC DAAC).",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "units": "m3/m3 (volume of water per volume of soil)",
        "grid": {"rows": [r0, r1], "cols": [c0, c1],
                 "lat": np.round(lats[r0:r1 + 1], 4).tolist(), "lon": np.round(lons[c0:c1 + 1], 4).tolist(),
                 "order": "[row][col]; row 0 is the northern edge (EASE-Grid 2.0 rows run north to south)"},
        "normals": normals,
        "recent": recent,
    }, separators=(",", ":")).replace("NaN", "null") + "\n")
    print(f"Saved {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
