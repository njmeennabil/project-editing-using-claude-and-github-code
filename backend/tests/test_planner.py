import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import nasa_power  # noqa: E402
import planner  # noqa: E402
from app import create_app  # noqa: E402

FLAT = {"temp_c": [27.0] * 12, "rain_mm_day": [10.0] * 12}


@pytest.fixture()
def client():
    return create_app().test_client()


def plan(client, **body):
    base = {"current": "JAGUNG", "planted": "2026-03-02", "location": "KUCHING", "ph": 6.2}
    return client.post("/api/rotation/plan", json={**base, **body})


def test_season_from_exact_date_crosses_year():
    s = nasa_power.season_from_date(FLAT, date(2026, 12, 20), 30)
    assert s["months"] == "Dec–Jan" and s["rain_mm"] == 300 and s["end"] == "2027-01-18"


def test_timeline_uses_maturity_and_prep_days(client):
    t = plan(client).get_json()["timeline"]
    assert t["harvest"] == "2026-05-06"        # 2 Mar + 65 days
    assert t["next_planting"] == "2026-05-20"  # + 14 days
    t = plan(client, prep_days=0).get_json()["timeline"]
    assert t["next_planting"] == "2026-05-06"


def test_three_recommendations_and_breakdown_adds_up(client):
    d = plan(client).get_json()
    assert len(d["recommendations"]) == 3 and len(d["others"]) == 2
    for o in d["recommendations"] + d["others"]:
        assert o["score"] == sum(o["breakdown"].values())
        assert 0 <= o["score"] <= 100
    scores = [o["score"] for o in d["recommendations"] + d["others"]]
    assert scores == sorted(scores, reverse=True)


def test_after_maize_a_legume_comes_first_and_maize_is_not_recommended(client):
    d = plan(client).get_json()
    assert d["recommendations"][0]["code"] in ("SOYA", "KACANG_TANAH")
    maize = next(o for o in d["recommendations"] + d["others"] if o["code"] == "JAGUNG")
    assert maize["rotation"]["rating"] == "Poor"
    assert maize["verdict"] in ("Possible with care", "Not recommended")


def test_after_peanut_maize_ranks_first(client):
    d = plan(client, current="KACANG_TANAH", planted="2026-01-10").get_json()
    top = d["recommendations"][0]
    assert top["code"] == "JAGUNG" and top["rotation"]["verified"] is True


def test_irrigation_and_ph_change_the_score(client):
    dry = plan(client, location="MIRI", planted="2026-01-01").get_json()
    wet = plan(client, location="MIRI", planted="2026-01-01", irrigation=400).get_json()
    soy = lambda d: next(o for o in d["recommendations"] + d["others"] if o["code"] == "SOYA")  # noqa: E731
    assert soy(wet)["season"]["water_mm"] == soy(dry)["season"]["water_mm"] + 400
    acid = plan(client, ph=4.2).get_json()
    assert soy(acid)["breakdown"]["soil"] == 0


def test_points_rules():
    crop = {"temp_min_c": 26, "temp_max_c": 30, "water_min_mm": 500, "water_max_mm": 1000,
            "soil": {"ph_min": 6.0, "ph_max": 7.5, "ph_danger_below": 4.5}}
    assert planner.temp_points(crop, 28)[0] == 22.5
    assert planner.temp_points(crop, 25)[0] == 18.0        # 1 °C below
    assert planner.water_points(crop, 250)[0] == 11.25     # half the minimum
    assert planner.water_points(crop, 3000)[0] == 22.5 * 0.4
    assert planner.soil_points(crop, 5.5)[0] == 15.0
    assert planner.soil_points(crop, 4.0)[0] == 0.0
    assert planner.verdict(90) == "Highly recommended"
    assert planner.verdict(90, "lemah") == "Possible with care"


def test_gps_location(client, monkeypatch):
    monkeypatch.setattr(nasa_power, "fetch_climatology", lambda lat, lon, timeout=20: {**FLAT, "period": "t", "model": "t"})
    nasa_power._live_cache.clear()
    d = plan(client, location=None, lat=2.3, lon=111.8).get_json()
    assert d["location"]["code"] == "GPS"


@pytest.mark.parametrize("body,needle", [
    ({"current": "RICE"}, "crop you are growing"),
    ({"planted": "02/03/2026"}, "Planting date"),
    ({"planted": "2026-02-30"}, "Planting date"),
    ({"ph": None}, "soil pH"),
    ({"location": None}, "location"),
    ({"prep_days": 400}, "harvest and next planting"),
])
def test_bad_input(client, body, needle):
    r = plan(client, **body)
    assert r.status_code == 400 and needle in r.get_json()["error"], r.get_json()
