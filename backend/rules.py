"""BUMI360 suitability rules.

Compares a field's soil pH, average temperature and seasonal water with each
crop's requirements. Every check returns a status:

    ok    Suitable
    warn  Suitable with management
    bad   Less suitable
    info  No figure to compare (advice only, does not change the result)
    none  Reading not entered

The overall result follows the weakest check.
"""

LABELS = {
    "ok": "Suitable",
    "warn": "Suitable with management",
    "bad": "Less suitable",
    "none": "Incomplete",
}
RANK = {"ok": 0, "warn": 1, "bad": 2, "none": 3}

# Thresholds (change here to adjust the rules everywhere)
TEMP_WARN_MARGIN_C = 2.0        # up to this far outside the optimum = "warn"
WATER_BAD_SHORTFALL = 0.5       # short by more than this share of the minimum = "bad"

# Scales used by the meters in the interface
SCALE_PH = (3.5, 8.5)
SCALE_TEMP = (10.0, 40.0)
SCALE_WATER = (0.0, 1200.0)


def fmt(n):
    """Format a number without trailing .0 (5.0 -> '5', 5.25 -> '5.25')."""
    if n is None:
        return "–"
    r = round(float(n), 2)
    return str(int(r)) if r == int(r) else str(r)


def fmt_range(lo, hi):
    if lo is None and hi is None:
        return "–"
    if lo is None:
        return f"≤ {fmt(hi)}"
    if hi is None:
        return f"≥ {fmt(lo)}"
    return fmt(lo) if lo == hi else f"{fmt(lo)}–{fmt(hi)}"


def _meter(scale, lo, hi, value):
    return {"min": scale[0], "max": scale[1], "low": lo, "high": hi, "value": value}


def check_ph(crop, ph):
    soil = crop["soil"]
    lo, hi, danger = soil["ph_min"], soil["ph_max"], soil["ph_danger_below"]
    out = {
        "factor": "ph",
        "name": "Soil pH",
        "range_text": f"Range {lo:.1f}–{hi:.1f}",
        "your_value_text": None if ph is None else f"Yours: {ph:.1f}",
        "meter": _meter(SCALE_PH, lo, hi, ph),
    }
    if ph is None:
        return {**out, "status": "none", "title": None, "message": "Enter your soil pH."}
    if danger is not None and ph < danger:
        return {**out, "status": "bad", "title": "Danger",
                "message": f"Below pH {fmt(danger)} there is a risk of aluminium toxicity. Raise the pH before planting."}
    if ph < lo:
        return {**out, "status": "bad", "title": "Too acidic",
                "message": f"{lo - ph:.1f} below the minimum. Raise soil pH, for example with agricultural lime or dolomite."}
    if ph > hi:
        return {**out, "status": "bad", "title": "Too alkaline",
                "message": f"{ph - hi:.1f} above the maximum."}
    return {**out, "status": "ok", "title": "Suitable", "message": "Within the recommended range."}


def check_temp(crop, temp):
    lo, hi = crop["temp_min_c"], crop["temp_max_c"]
    out = {
        "factor": "temp",
        "name": "Temperature",
        "range_text": f"Optimum {fmt_range(lo, hi)}°C",
        "your_value_text": None if temp is None else f"Yours: {fmt(temp)}°C",
        "meter": _meter(SCALE_TEMP, lo, hi, temp),
    }
    if temp is None:
        return {**out, "status": "none", "title": None, "message": "Enter your average temperature."}
    diff = lo - temp if temp < lo else temp - hi if temp > hi else 0
    if diff == 0:
        return {**out, "status": "ok", "title": "Optimal", "message": "Within the optimum temperature range."}
    cool = temp < lo
    return {**out,
            "status": "warn" if diff <= TEMP_WARN_MARGIN_C else "bad",
            "title": "Too cool" if cool else "Too hot",
            "message": f"{fmt(diff)}°C {'below' if cool else 'above'} the optimum range. Growth and yield may be affected."}


def check_water(crop, water):
    lo, hi = crop["water_min_mm"], crop["water_max_mm"]
    if lo is None:
        return {"factor": "water", "name": "Water per season", "range_text": "No mm figure",
                "your_value_text": None, "meter": None, "status": "info",
                "title": "Keep the soil moist", "message": crop["water_note"] or ""}
    out = {
        "factor": "water",
        "name": "Water per season",
        "range_text": f"Needs {fmt_range(lo, hi)} mm",
        "your_value_text": None if water is None else f"Yours: {fmt(water)} mm",
        "meter": _meter(SCALE_WATER, lo, hi, water),
    }
    if water is None:
        return {**out, "status": "none", "title": None, "message": "Enter the water available per season."}
    if water < lo:
        short = lo - water
        return {**out, "status": "bad" if short > lo * WATER_BAD_SHORTFALL else "warn", "title": "Not enough",
                "message": f"{fmt(short)} mm short of the minimum. Plan extra irrigation."}
    if water > hi:
        note = f" {crop['water_note']}" if crop["water_note"] else ""
        return {**out, "status": "warn", "title": "Excess water",
                "message": f"{fmt(water - hi)} mm above the requirement. Make sure drainage is good.{note}"}
    target = crop["water_target_mm"]
    extra = f" Aim for about {fmt(target)} mm for high yield." if target else ""
    return {**out, "status": "ok", "title": "Sufficient", "message": f"Enough water for the season.{extra}"}


def assess(crop, ph=None, temp=None, water=None):
    checks = [check_ph(crop, ph), check_temp(crop, temp), check_water(crop, water)]
    statuses = {c["status"] for c in checks}
    overall = next(s for s in ("none", "bad", "warn") if s in statuses) if statuses & {"none", "bad", "warn"} else "ok"
    return {
        "code": crop["code"],
        "name": crop["name"],
        "local_name": crop["local_name"],
        "scientific_name": crop["scientific_name"],
        "status": overall,
        "label": LABELS[overall],
        "checks": checks,
    }


def assess_all(crops, ph=None, temp=None, water=None, per_crop=None):
    """Assess every crop and sort: most suitable first, then database order.

    per_crop(crop) may return (temp, water, extra) to give each crop its own
    temperature and water, e.g. NASA climate over that crop's growing season.
    `extra` is added to the result as "climate".
    """
    results = []
    for c in crops:
        t, w, extra = (temp, water, None) if per_crop is None else per_crop(c)
        r = assess(c, ph, t, w)
        if extra is not None:
            r["climate"] = extra
        results.append(r)
    order = {c["code"]: c["id"] for c in crops}
    results.sort(key=lambda r: (RANK[r["status"]], order[r["code"]]))
    counts = {s: sum(r["status"] == s for r in results) for s in ("ok", "warn", "bad", "none")}
    return results, counts
