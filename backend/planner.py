"""BUMI360 next-crop planner: scores each crop 0–100 for the season after the current crop.

    Climate fit   45 points  NASA temperature (22.5) and rainfall (22.5) over the next crop's own season
    Rotation      35 points  from the rotation ratings: Excellent 35 · Good 26 · Fair 16 · Poor 5
    Soil pH       20 points  full inside the crop's range, 10 points less per pH unit outside

The score is a guidance index, not a guarantee. A Poor rotation caps the verdict at
"Possible with care" (the score itself is unchanged), so a repeat crop is never "Recommended".
"""
from datetime import timedelta

import nasa_power
from rules import fmt, fmt_range

ROTATION_POINTS = {"cemerlang": 35, "baik": 26, "sederhana": 16, "lemah": 5}
TEMP_MAX, WATER_MAX, SOIL_MAX = 22.5, 22.5, 20.0
TEMP_LOSS_PER_C = 4.5          # 5 °C outside the optimum = 0 points
WATER_NO_FIGURE = 18.0         # crops with no seasonal mm figure (leafy vegetables)
EXCESS_FLOOR = 0.4             # too much rain never drops below 40 % (drainage can manage it)
SOIL_LOSS_PER_PH = 10.0
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


def plan(data, current_code, planted, climate, place, ph, irrigation=0.0, prep_days=DEFAULT_PREP_DAYS):
    crops = data["crops"]
    by_code = {c["code"]: c for c in crops}
    current = by_code[current_code]
    ratings = {(r["before"], r["after"]): r for r in data["rotation_ratings"]}

    grow_days, grow_assumed = nasa_power.crop_season_days(current)
    harvest = planted + timedelta(days=grow_days)
    next_start = harvest + timedelta(days=prep_days)

    options = []
    for c in crops:
        days, assumed = nasa_power.crop_season_days(c)
        sea = nasa_power.season_from_date(climate, next_start, days)
        water = sea["rain_mm"] + irrigation
        tp, t_note = temp_points(c, sea["temp_c"])
        wp, w_note = water_points(c, water)
        rot = ratings[(current_code, c["code"])]
        sp, s_note = soil_points(c, ph)

        parts = {"climate": round(tp + wp), "rotation": ROTATION_POINTS[rot["rating"]], "soil": round(sp)}
        score = parts["climate"] + parts["rotation"] + parts["soil"]
        options.append({
            "code": c["code"],
            "name": c["name"],
            "local_name": c["local_name"],
            "score": score,
            "verdict": verdict(score, rot["rating"]),
            "breakdown": parts,
            "max": {"climate": 45, "rotation": 35, "soil": 20},
            "rotation": {"rating": rot["label"], "reason": rot["reason"], "verified": rot["verified"], "source": rot["source"]},
            "season": {**sea, "days": days, "days_assumed": assumed, "irrigation_mm": irrigation, "water_mm": water},
            "notes": [t_note, w_note, s_note],
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
        "recommendations": options[:3],
        "others": options[3:],
    }
