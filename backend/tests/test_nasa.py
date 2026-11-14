import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import nasa_power  # noqa: E402
from app import create_app  # noqa: E402

FLAT = {"temp_c": [26.0] * 12, "rain_mm_day": [10.0] * 12, "period": "test", "model": "test"}


@pytest.fixture()
def client():
    return create_app().test_client()


def test_season_sums_days_across_months():
    s = nasa_power.season(FLAT, 3, 65)
    assert s == {"temp_c": 26.0, "rain_mm": 650, "months": "Mar–May"}
    # Wraps over the new year
    assert nasa_power.season(FLAT, 12, 40)["months"] == "Dec–Jan"
    assert nasa_power.season(FLAT, 2, 28)["months"] == "Feb"


def test_crop_season_days():
    assert nasa_power.crop_season_days({"maturity_min_days": 60, "maturity_max_days": 70}) == (65, False)
    assert nasa_power.crop_season_days({"maturity_min_days": None, "maturity_max_days": None}) == (30, True)


def test_saved_sarawak_divisions_cover_all_12(client):
    locs = client.get("/api/locations").get_json()["locations"]
    assert len(locs) == 12
    for loc in locs:
        assert nasa_power.climate_for_location(loc["code"]) is not None, loc["code"]


def test_climate_endpoint(client):
    d = client.get("/api/climate?location=kuching").get_json()
    assert d["location"]["name"] == "Kuching"
    assert len(d["monthly"]) == 12 and d["rain_mm_year"] > 1000


def test_check_with_location_uses_each_crop_season(client):
    d = client.post("/api/check", json={"ph": 6.2, "location": "KUCHING", "month": 3, "crop": "all"}).get_json()
    by = {r["code"]: r for r in d["results"]}
    assert by["JAGUNG"]["climate"]["months"] == "Mar–May"        # 65 days
    assert by["KACANG_TANAH"]["climate"]["months"] == "Mar–Jul"  # 150 days
    assert by["SAWI"]["climate"]["days_assumed"] is True
    assert d["input"]["climate"]["month_name"] == "Mar"


def test_irrigation_is_added_to_rain(client):
    base = client.post("/api/check", json={"ph": 6.2, "location": "MIRI", "month": 3, "crop": "JAGUNG"}).get_json()
    more = client.post("/api/check", json={"ph": 6.2, "location": "MIRI", "month": 3, "crop": "JAGUNG", "irrigation": 200}).get_json()
    rain = base["results"][0]["climate"]["rain_mm"]
    assert more["results"][0]["climate"]["water_mm"] == rain + 200
    assert base["results"][0]["checks"][2]["title"] == "Not enough"
    assert more["results"][0]["checks"][2]["title"] == "Sufficient"


def test_gps_point_fetches_live_and_caches(client, monkeypatch):
    calls = []

    def fake_fetch(lat, lon, timeout=20):
        calls.append((lat, lon))
        return FLAT

    monkeypatch.setattr(nasa_power, "fetch_climatology", fake_fetch)
    nasa_power._live_cache.clear()
    for _ in range(2):
        d = client.post("/api/check", json={"ph": 6.2, "lat": 2.5, "lon": 112.5, "month": 1, "crop": "JAGUNG"}).get_json()
    assert d["input"]["climate"]["location"]["code"] == "GPS"
    assert d["results"][0]["climate"]["rain_mm"] == 650
    assert len(calls) == 1  # second request served from cache


def test_nasa_down_gives_502(client, monkeypatch):
    def broken(lat, lon, timeout=20):
        raise nasa_power.ClimateUnavailable("NASA POWER is not responding right now.")

    monkeypatch.setattr(nasa_power, "fetch_climatology", broken)
    nasa_power._live_cache.clear()
    r = client.post("/api/check", json={"ph": 6, "lat": 3.3, "lon": 113.3, "month": 1})
    assert r.status_code == 502 and "NASA" in r.get_json()["error"]


@pytest.mark.parametrize("body,needle", [
    ({"ph": 6, "location": "MIRI"}, "Planting month"),
    ({"ph": 6, "location": "MIRI", "month": 13}, "Planting month"),
    ({"ph": 6, "location": "ATLANTIS", "month": 1}, "Unknown location"),
    ({"ph": 6, "lat": 2.5, "month": 1}, "both"),
    ({"ph": 6, "location": "MIRI", "month": 1, "irrigation": -5}, "Extra irrigation"),
])
def test_bad_climate_input(client, body, needle):
    r = client.post("/api/check", json=body)
    assert r.status_code == 400 and needle in r.get_json()["error"]
