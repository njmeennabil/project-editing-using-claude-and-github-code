"""BUMI360 API (Flask).

Endpoints
    GET  /api/health                 Service status
    GET  /api/crops                  All crops with full growing guides
    GET  /api/crops/<code>           One crop by its database code, e.g. /api/crops/JAGUNG (maize)
    GET  /api/rotation               Crop rotation pairs and notes
    GET  /api/check?ph=&temp=&water=&crop=
    POST /api/check  {"ph": 5.8, "temp": 28, "water": 600, "crop": "all"}

Run locally:
    pip install -r requirements-dev.txt
    flask --app app run --port 5000
"""
import os
import sys
from functools import lru_cache
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "database"))

from crop_data import DEFAULT_DB, load_data  # noqa: E402

import rules  # noqa: E402

LIMITS = {"ph": (0.0, 14.0), "temp": (-10.0, 60.0), "water": (0.0, 20000.0)}
NAMES = {"ph": "Soil pH", "temp": "Average temperature", "water": "Water per season"}


class BadInput(Exception):
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


def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False
    app.json.ensure_ascii = False

    origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    @app.errorhandler(BadInput)
    def bad_input(e):
        return jsonify(error=str(e)), 400

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

        results, counts = rules.assess_all(selected, ph, temp, water)
        return jsonify(
            input={"ph": ph, "temp": temp, "water": water, "crop": "all" if choice == "ALL" else choice},
            counts=counts,
            results=results,
        )

    return app


app = create_app()
