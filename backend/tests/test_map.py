import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import nasa_power  # noqa: E402
from app import create_app  # noqa: E402

FLAT = {"temp_c": [27.0] * 12, "rain_mm_day": [10.0] * 12, "period": "t", "model": "t"}


@pytest.fixture()
def client():
    return create_app().test_client()


def test_all_twelve_divisions_scored(client):
    d = client.get("/api/map/suitability?crop=JAGUNG&planted=2026-03-01").get_json()
    assert d["crop"]["name"] == "Maize" and len(d["divisions"]) == 12
    for div in d["divisions"]:
        assert 0 <= div["score"] <= 100
        assert div["score"] in range(div["temp_points"] + div["water_points"] - 1, div["temp_points"] + div["water_points"] + 2)
    by = {x["code"]: x for x in d["divisions"]}
    # Miri is drier in March: maize scores lower there than in Kuching
    assert by["MIRI"]["score"] < by["KUCHING"]["score"]
    assert d["point"] is None


def test_irrigation_raises_dry_division(client):
    dry = client.get("/api/map/suitability?crop=JAGUNG&planted=2026-03-01").get_json()
    wet = client.get("/api/map/suitability?crop=JAGUNG&planted=2026-03-01&irrigation=200").get_json()
    miri = lambda d: next(x for x in d["divisions"] if x["code"] == "MIRI")  # noqa: E731
    assert miri(wet)["score"] > miri(dry)["score"]


def test_map_point(client, monkeypatch):
    monkeypatch.setattr(nasa_power, "fetch_climatology", lambda lat, lon, timeout=20: FLAT)
    nasa_power._live_cache.clear()
    d = client.get("/api/map/suitability?crop=SOYA&planted=2026-05-20&lat=2.0&lon=112.0").get_json()
    assert d["point"]["code"] == "GPS" and d["point"]["season"]["rain_mm"] == 10 * 115


@pytest.mark.parametrize("q,needle", [
    ("crop=RICE&planted=2026-03-01", "Choose a crop"),
    ("crop=JAGUNG&planted=yesterday", "Planting date"),
    ("crop=JAGUNG&planted=2026-03-01&lat=2.0", "both"),
])
def test_bad_input(client, q, needle):
    r = client.get(f"/api/map/suitability?{q}")
    assert r.status_code == 400 and needle in r.get_json()["error"]
