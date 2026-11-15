"""BUMI360 API (Flask).

Endpoints
    GET  /api/health                 Service status
    GET  /api/crops                  All crops with full growing guides
    GET  /api/crops/<code>           One crop by its database code, e.g. /api/crops/JAGUNG (maize)
    GET  /api/rotation               Crop rotation pairs and notes
    POST /api/rotation/plan  {"current": "JAGUNG", "planted": "2026-03-02", "location": "KUCHING", "ph": 6.2}
         scores the 5 crops 0–100 for the next season and returns the top 3
    GET  /api/map/suitability?crop=JAGUNG&planted=2026-03-02[&lat=&lon=][&irrigation=]
         climate suitability (0–100) of one crop in all 12 Sarawak divisions, plus an optional map point
    GET  /api/locations              Sarawak divisions with NASA climate data
    GET  /api/climate?location=KUCHING   (or ?lat=1.55&lon=110.35) monthly NASA POWER climate
    GET  /api/check?ph=&temp=&water=&crop=
    POST /api/check  {"ph": 5.8, "temp": 28, "water": 600, "crop": "all"}
    POST /api/check  {"ph": 5.8, "location": "KUCHING", "month": 3, "irrigation": 0, "crop": "all"}
         (or "lat"/"lon" instead of "location") uses NASA climate for each crop's season

Run locally:
    pip install -r requirements-dev.txt
    flask --app app run --port 5000
"""
import os
import sys
from datetime import date
from functools import lru_cache
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "database"))

from crop_data import DEFAULT_DB, load_data  # noqa: E402

import nasa_power  # noqa: E402
import planner  # noqa: E402
import rules  # noqa: E402
from locations import BY_CODE, SARAWAK_DIVISIONS  # noqa: E402

LIMITS = {
    "ph": (0.0, 14.0), "temp": (-10.0, 60.0), "water": (0.0, 20000.0),
    "month": (1, 12), "irrigation": (0.0, 5000.0), "lat": (-90.0, 90.0), "lon": (-180.0, 180.0),
    "prep_days": (0, 180),
}
NAMES = {
    "ph": "Soil pH", "temp": "Average temperature", "water": "Water per season",
    "month": "Planting month", "irrigation": "Extra irrigation", "lat": "Latitude", "lon": "Longitude",
    "prep_days": "Days between harvest and next planting",
}
POWER_SOURCE = "NASA POWER"


class BadInput(Exception):
    pass


class Upstream(Exception):
    pass


@lru_cache(maxsize=1)
def get_data():
    return load_data(os.environ.get("BUMI_DB_PATH", DEFAULT_DB))


def parse_number(raw, field):
    if raw is None or (isinstance(raw, str) and raw.strip() == ""):
        return None
    try:
        value = float(str(raw).replace(",", "."))
    except ValueError:
        raise BadInput(f"{NAMES[field]} must be a number.")
    lo, hi = LIMITS[field]
    if not lo <= value <= hi:
        raise BadInput(f"{NAMES[field]} must be between {rules.fmt(lo)} and {rules.fmt(hi)}.")
    return value


def parse_date(raw):
    try:
        d = date.fromisoformat(str(raw or "").strip())
    except ValueError:
        raise BadInput("Planting date must look like 2026-03-02 (year-month-day).")
    if not date(2000, 1, 1) <= d <= date(2100, 12, 31):
        raise BadInput("Planting date must be between 2000 and 2100.")
    return d


def resolve_climate(src):
    """Return (place, climate) from a 'location' code or 'lat'/'lon', or (None, None)."""
    code = str(src.get("location") or "").strip().upper()
    lat = parse_number(src.get("lat"), "lat")
    lon = parse_number(src.get("lon"), "lon")
    if code and code != "GPS":
        div = BY_CODE.get(code)
        if div is None:
            raise BadInput(f"Unknown location {code!r}. Use one of: " + ", ".join(BY_CODE) + ".")
        data = nasa_power.climate_for_location(code)
        if data is None:
            try:
                data = nasa_power.climate_for_point(div["lat"], div["lon"])
            except nasa_power.ClimateUnavailable as e:
                raise Upstream(str(e))
        return {"code": code, "name": div["name"], "lat": div["lat"], "lon": div["lon"]}, data
    if lat is not None or lon is not None:
        if lat is None or lon is None:
            raise BadInput("Give both 'lat' and 'lon'.")
        try:
            data = nasa_power.climate_for_point(lat, lon)
        except nasa_power.ClimateUnavailable as e:
            raise Upstream(str(e))
        label = "Map point" if str(src.get("point") or "").lower() == "map" else "Your location"
        return {"code": "GPS", "name": f"{label} ({lat:.2f}, {lon:.2f})", "lat": lat, "lon": lon}, data
    return None, None


def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False
    app.json.ensure_ascii = False

    origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    @app.errorhandler(BadInput)
    def bad_input(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(Upstream)
    def upstream(e):
        return jsonify(error=str(e)), 502

    @app.errorhandler(HTTPException)
    def http_error(e):
        return jsonify(error=e.description), e.code

    @app.get("/")
    def index():
        return jsonify(service="BUMI360 API", docs="See /api/health, /api/crops, /api/rotation, /api/check")

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", crops=len(get_data()["crops"]))

    @app.get("/api/crops")
    def crops():
        return jsonify(crops=get_data()["crops"])

    @app.get("/api/crops/<code>")
    def crop(code):
        for c in get_data()["crops"]:
            if c["code"] == code.upper():
                return jsonify(c)
        return jsonify(error=f"No crop with code {code!r}."), 404

    @app.get("/api/rotation")
    def rotation():
        d = get_data()
        return jsonify(rotation=d["rotation"], notes=d["rotation_notes"])

    @app.get("/api/locations")
    def locations():
        return jsonify(
            region="Sarawak",
            locations=SARAWAK_DIVISIONS,
            source=POWER_SOURCE,
            acknowledgement=nasa_power._saved.get("acknowledgement"),
        )

    @app.get("/api/climate")
    def climate():
        place, data = resolve_climate(request.args)
        if data is None:
            raise BadInput("Give a Sarawak 'location' code, or 'lat' and 'lon'.")
        monthly = [
            {"month": nasa_power.MONTH_NAMES[i], "temp_c": round(data["temp_c"][i], 2),
             "rain_mm": round(data["rain_mm_day"][i] * nasa_power.DAYS_IN_MONTH[i])}
            for i in range(12)
        ]
        return jsonify(location=place, source=POWER_SOURCE, period=data.get("period"), monthly=monthly,
                       rain_mm_year=sum(m["rain_mm"] for m in monthly))

    @app.get("/api/map/suitability")
    def map_suitability():
        src = request.args
        data = get_data()
        by_code = {c["code"]: c for c in data["crops"]}
        code = str(src.get("crop") or "").strip().upper()
        if code not in by_code:
            raise BadInput("Choose a crop: " + ", ".join(by_code) + ".")
        planted = parse_date(src.get("planted"))
        irrigation = parse_number(src.get("irrigation"), "irrigation") or 0.0
        crop = by_code[code]

        divisions = []
        for d in SARAWAK_DIVISIONS:
            clim = nasa_power.climate_for_location(d["code"])
            if clim is None:
                continue
            divisions.append({**d, **planner.climate_score(crop, clim, planted, irrigation)})

        point = None
        lat = parse_number(src.get("lat"), "lat")
        lon = parse_number(src.get("lon"), "lon")
        if lat is not None or lon is not None:
            place, clim = resolve_climate({"lat": lat, "lon": lon})
            point = {**place, **planner.climate_score(crop, clim, planted, irrigation)}

        return jsonify(
            crop={"code": crop["code"], "name": crop["name"], "local_name": crop["local_name"]},
            planted=planted.isoformat(),
            irrigation=irrigation,
            source=POWER_SOURCE,
            divisions=divisions,
            point=point,
        )

    @app.route("/api/rotation/plan", methods=["GET", "POST"])
    def rotation_plan():
        src = (request.get_json(silent=True) or {}) if request.method == "POST" else request.args
        data = get_data()
        codes = [c["code"] for c in data["crops"]]
        current = str(src.get("current") or "").strip().upper()
        if current not in codes:
            raise BadInput("Choose the crop you are growing now: " + ", ".join(codes) + ".")
        planted = parse_date(src.get("planted"))
        ph = parse_number(src.get("ph"), "ph")
        if ph is None:
            raise BadInput("Enter your soil pH to score the next crop.")
        irrigation = parse_number(src.get("irrigation"), "irrigation") or 0.0
        prep = parse_number(src.get("prep_days"), "prep_days")
        prep_days = planner.DEFAULT_PREP_DAYS if prep is None else int(round(prep))
        place, clim = resolve_climate(src)
        if clim is None:
            raise BadInput("Choose a location in Sarawak, or use your GPS location.")

        result = planner.plan(data, current, planted, clim, place, ph, irrigation, prep_days)
        return jsonify(
            input={"current": current, "planted": planted.isoformat(), "ph": ph, "irrigation": irrigation,
                   "prep_days": prep_days},
            climate={"source": POWER_SOURCE, "period": clim.get("period")},
            **result,
        )

    @app.route("/api/check", methods=["GET", "POST"])
    def check():
        if request.method == "POST":
            src = request.get_json(silent=True) or {}
        else:
            src = request.args
        ph = parse_number(src.get("ph"), "ph")
        temp = parse_number(src.get("temp"), "temp")
        water = parse_number(src.get("water"), "water")
        choice = str(src.get("crop") or "all").upper()

        all_crops = get_data()["crops"]
        if choice == "ALL":
            selected = all_crops
        else:
            selected = [c for c in all_crops if c["code"] == choice]
            if not selected:
                raise BadInput(f"Unknown crop {choice!r}. Use 'all' or one of: " + ", ".join(c["code"] for c in all_crops) + ".")

        place, clim = resolve_climate(src)
        crop_code = "all" if choice == "ALL" else choice
        if clim is None:
            results, counts = rules.assess_all(selected, ph, temp, water)
            return jsonify(input={"ph": ph, "temp": temp, "water": water, "crop": crop_code, "climate": None},
                           counts=counts, results=results)

        month = parse_number(src.get("month"), "month")
        if month is None or month != int(month):
            raise BadInput("Planting month must be a whole number from 1 (January) to 12 (December).")
        month = int(month)
        irrigation = parse_number(src.get("irrigation"), "irrigation") or 0.0

        def per_crop(crop):
            days, assumed = nasa_power.crop_season_days(crop)
            sea = nasa_power.season(clim, month, days)
            water_total = sea["rain_mm"] + irrigation
            return sea["temp_c"], water_total, {
                "source": POWER_SOURCE,
                "location": place["name"],
                "months": sea["months"],
                "days": days,
                "days_assumed": assumed,
                "temp_c": sea["temp_c"],
                "rain_mm": sea["rain_mm"],
                "irrigation_mm": irrigation,
                "water_mm": water_total,
            }

        results, counts = rules.assess_all(selected, ph, per_crop=per_crop)
        return jsonify(
            input={"ph": ph, "temp": None, "water": None, "crop": crop_code,
                   "climate": {"source": POWER_SOURCE, "period": clim.get("period"), "location": place,
                               "month": month, "month_name": nasa_power.MONTH_NAMES[month - 1],
                               "irrigation": irrigation}},
            counts=counts,
            results=results,
        )

    return app


app = create_app()
