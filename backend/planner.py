"""BUMI360 next-crop planner: scores each crop 0–100 for the season after the current crop.

    Climate fit   40 points  temperature (20, NASA POWER) and rainfall (20, NASA GPM) over the next crop's own season
    Rotation      30 points  from the rotation ratings: Excellent 30 · Good 22 · Fair 14 · Poor 4
    Soil pH       15 points  full inside the crop's range, 7.5 points less per pH unit outside
    Current       15 points  last 60 days of NASA GPM rain (7.5) and this week's NASA SMAP root-zone
                             soil moisture (7.5), each against what is usual; same for every crop

The score is a guidance index, not a guarantee. A Poor rotation caps the verdict at
"Possible with care" (the score itself is unchanged), so a repeat crop is never "Recommended".
"""
from datetime import timedelta

import nasa_power
from rules import fmt, fmt_range

ROTATION_POINTS = {"cemerlang": 30, "baik": 22, "sederhana": 14, "lemah": 4}
TEMP_MAX, WATER_MAX, SOIL_MAX, CURRENT_MAX = 20.0, 20.0, 15.0, 15.0
TEMP_LOSS_PER_C = 4.0          # 5 °C outside the optimum = 0 points
WATER_NO_FIGURE = 16.0         # crops with no seasonal mm figure (leafy vegetables): 80 %
EXCESS_FLOOR = 0.4             # too much rain never drops below 40 % (drainage can manage it)
SOIL_LOSS_PER_PH = 7.5
CURRENT_NO_DATA = 11.0         # no recent rainfall figure: about 75 %
NORMAL_BAND = (0.8, 1.3)       # recent rain within this share of normal = full points
DEFAULT_PREP_DAYS = 14


def verdict(score, rotation_rating=None):
    if rotation_rating == "lemah" and score >= 40:
        return "Possible with care"
    if score >= 80:
        return "Highly recommended"
    if score >= 60:
        return "Recommended"
    if score >= 40:
        return "Possible with care"
    return "Not recommended"


def temp_points(crop, t):
    lo, hi = crop["temp_min_c"], crop["temp_max_c"]
    diff = lo - t if t < lo else t - hi if t > hi else 0.0
    pts = max(0.0, TEMP_MAX - TEMP_LOSS_PER_C * diff)
    if diff == 0:
        note = f"Temperature {fmt(t)}°C is in the best range ({fmt_range(lo, hi)}°C)."
    else:
        note = f"Temperature {fmt(t)}°C is {fmt(round(diff, 1))}°C {'below' if t < lo else 'above'} the best range ({fmt_range(lo, hi)}°C)."
    return pts, note


def water_points(crop, w):
    lo, hi = crop["water_min_mm"], crop["water_max_mm"]
    if lo is None:
        return WATER_NO_FIGURE, f"{fmt(w)} mm of water expected. This crop has no seasonal figure; keep the soil moist."
    if w < lo:
        return WATER_MAX * max(0.0, w / lo), f"Water {fmt(w)} mm is {fmt(lo - w)} mm short of the {fmt_range(lo, hi)} mm needed. Plan irrigation."
    if w > hi:
        frac = max(EXCESS_FLOOR, 1 - 0.6 * (w - hi) / hi)
        return WATER_MAX * frac, f"Water {fmt(w)} mm is {fmt(w - hi)} mm more than needed ({fmt_range(lo, hi)} mm). Make sure drainage is good."
    return WATER_MAX, f"Water {fmt(w)} mm is within the {fmt_range(lo, hi)} mm needed."


def soil_points(crop, ph):
    s = crop["soil"]
    lo, hi, danger = s["ph_min"], s["ph_max"], s["ph_danger_below"]
    if danger is not None and ph < danger:
        return 0.0, f"Soil pH {ph:.1f} is below {fmt(danger)}: risk of aluminium toxicity."
    diff = lo - ph if ph < lo else ph - hi if ph > hi else 0.0
    if diff == 0:
        return SOIL_MAX, f"Soil pH {ph:.1f} fits ({lo:.1f}–{hi:.1f})."
    return max(0.0, SOIL_MAX - SOIL_LOSS_PER_PH * diff), \
        f"Soil pH {ph:.1f} is {diff:.1f} {'below' if ph < lo else 'above'} the range ({lo:.1f}–{hi:.1f})."


def current_points(recent):
    """Points for the last 60 days of rain against normal (None = no data)."""
    if not recent:
        return CURRENT_NO_DATA, "Recent rainfall data is not available for this place."
    r = recent["ratio"]
    lo, hi = NORMAL_BAND
    pct = round(abs(r - 1) * 100)
    summary = f"Last {recent['days']} days: {fmt(recent['total_mm'])} mm of rain (normal {fmt(recent['normal_mm'])} mm)"
    if lo <= r <= hi:
        return CURRENT_MAX, f"{summary}, close to normal."
    if r < lo:
        return CURRENT_MAX * max(0.0, (r - 0.3) / (lo - 0.3)), \
            f"{summary}, {pct}% drier than normal. Check soil moisture and plan irrigation before planting."
    return max(7.0, CURRENT_MAX - (r - hi) * 10), \
        f"{summary}, {pct}% wetter than normal. Check drainage before planting."


def soil_moisture_points(sm, max_points=CURRENT_MAX / 2):
    """Points for this week's root-zone soil moisture against the usual for the month (None = no data)."""
    if not sm or sm.get("z") is None:
        return None, None
    z = sm["z"]
    note = (f"Soil moisture this week (root zone, NASA SMAP): {sm['rootzone_pct']:.0f}%, {sm['label']} "
            f"(usual {sm['usual_rootzone_pct']:.0f}%).")
    if abs(z) <= 0.4:
        return max_points, note
    if z < 0:
        return max_points * max(0.0, 1 - (-z - 0.4) / 1.6), note + " Water the seedbed before planting."
    return max(max_points * 0.45, max_points - (z - 0.4) * max_points * 0.4), note + " Allow the soil to drain before planting."


def conditions_points(recent, sm):
    """Current conditions (15): GPM recent rain and SMAP soil moisture, half each when both exist."""
    rain_pts, rain_note = current_points(recent)
    soil_pts, soil_note = soil_moisture_points(sm)
    if soil_pts is None:
        return rain_pts, [rain_note]
    if not recent:
        return soil_pts * 2, [soil_note]
    return rain_pts / 2 + soil_pts, [rain_note, soil_note]


def plan(data, current_code, planted, climate, place, ph, irrigation=0.0, prep_days=DEFAULT_PREP_DAYS, recent=None,
         soil_moisture=None):
    crops = data["crops"]
    by_code = {c["code"]: c for c in crops}
    current = by_code[current_code]
    ratings = {(r["before"], r["after"]): r for r in data["rotation_ratings"]}

    grow_days, grow_assumed = nasa_power.crop_season_days(current)
    harvest = planted + timedelta(days=grow_days)
    next_start = harvest + timedelta(days=prep_days)

    cp, c_notes = conditions_points(recent, soil_moisture)
    options = []
    for c in crops:
        days, assumed = nasa_power.crop_season_days(c)
        sea = nasa_power.season_from_date(climate, next_start, days)
        water = sea["rain_mm"] + irrigation
        tp, t_note = temp_points(c, sea["temp_c"])
        wp, w_note = water_points(c, water)
        rot = ratings[(current_code, c["code"])]
        sp, s_note = soil_points(c, ph)

        parts = {"climate": round(tp + wp), "rotation": ROTATION_POINTS[rot["rating"]], "soil": round(sp),
                 "current": round(cp)}
        score = sum(parts.values())
        options.append({
            "code": c["code"],
            "name": c["name"],
            "local_name": c["local_name"],
            "score": score,
            "verdict": verdict(score, rot["rating"]),
            "breakdown": parts,
            "max": {"climate": 40, "rotation": 30, "soil": 15, "current": 15},
            "rotation": {"rating": rot["label"], "reason": rot["reason"], "verified": rot["verified"], "source": rot["source"]},
            "season": {**sea, "days": days, "days_assumed": assumed, "irrigation_mm": irrigation, "water_mm": water},
            "notes": [t_note, w_note, s_note, *c_notes],
            "_order": c["id"],
        })
    options.sort(key=lambda o: (-o["score"], o["_order"]))
    for o in options:
        del o["_order"]

    return {
        "timeline": {
            "current": {"code": current["code"], "name": current["name"], "local_name": current["local_name"]},
            "planted": planted.isoformat(),
            "growing_days": grow_days,
            "growing_days_assumed": grow_assumed,
            "harvest": harvest.isoformat(),
            "prep_days": prep_days,
            "next_planting": next_start.isoformat(),
        },
        "location": place,
        "recent": recent,
        "soil_moisture": soil_moisture,
        "recommendations": options[:3],
        "others": options[3:],
    }


def climate_score(crop, climate, start, irrigation=0.0):
    """Climate-only suitability (0–100) for one crop planted on `start`, used by the map."""
    days, assumed = nasa_power.crop_season_days(crop)
    sea = nasa_power.season_from_date(climate, start, days)
    water = sea["rain_mm"] + irrigation
    tp, t_note = temp_points(crop, sea["temp_c"])
    wp, w_note = water_points(crop, water)
    score = round((tp + wp) / (TEMP_MAX + WATER_MAX) * 100)
    return {
        "score": score,
        "verdict": verdict(score),
        "temp_points": round(tp / TEMP_MAX * 50),
        "water_points": round(wp / WATER_MAX * 50),
        "season": {**sea, "days": days, "days_assumed": assumed, "irrigation_mm": irrigation, "water_mm": water},
        "notes": [t_note, w_note],
    }
