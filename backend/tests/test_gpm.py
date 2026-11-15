import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gpm  # noqa: E402
import planner  # noqa: E402
from app import create_app  # noqa: E402

NAN = float("nan")


def fake_gpm(rain=5.0, recent_ratio=0.5):
    nlat, nlon = 43, 63
    grid = {"lon0": 109.55, "lat0": 0.85, "step": 0.1, "nlon": nlon, "nlat": nlat}
    month = [[rain] * nlon for _ in range(nlat)]
    month[0][0] = NAN  # a missing cell at the corner
    normal = [[600.0] * nlon for _ in range(nlat)]
    total = [[600.0 * recent_ratio] * nlon for _ in range(nlat)]
    return {"grid": grid, "normals": {"period": "2001–2024", "product": "test", "mm_per_day": [month] * 12},
            "recent": {"product": "test", "start": "2026-09-15", "end": "2026-11-13", "days": 60,
                       "total_mm": total, "normal_mm": normal}}


@pytest.fixture()
def client():
    gpm.set_data(fake_gpm())
    yield create_app().test_client()
    gpm.set_data(None)


def test_point_values_and_outside_grid():
    gpm.set_data(fake_gpm(rain=7.0))
    assert gpm.normals_at(1.553, 110.359) == [7.0] * 12
    assert gpm.normals_at(0.86, 109.56) == [7.0] * 12          # NaN corner cell is ignored
    assert gpm.normals_at(6.5, 110.0) is None                    # outside Sarawak box
    r = gpm.recent_at(1.553, 110.359)
    assert r["ratio"] == 0.5 and r["total_mm"] == 300 and r["normal_mm"] == 600
    gpm.set_data(None)
    assert gpm.normals_at(1.553, 110.359) is None


def test_merge_replaces_rain_but_keeps_temperature():
    gpm.set_data(fake_gpm(rain=7.0))
    power = {"temp_c": [27.0] * 12, "rain_mm_day": [10.0] * 12, "period": "2001–2025"}
    m = gpm.merge(power, 2.3, 111.8)
    assert m["rain_mm_day"] == [7.0] * 12 and m["temp_c"] == [27.0] * 12 and m["rain_mm_day_power"] == [10.0] * 12
    assert gpm.source_label(m) == "NASA GPM + POWER"
    assert gpm.merge(power, 7.0, 100.0)["rain_source"] == "NASA POWER"
    gpm.set_data(None)


def test_current_points():
    assert planner.current_points({"ratio": 1.0, "days": 60, "total_mm": 600, "normal_mm": 600})[0] == 15
    dry = planner.current_points({"ratio": 0.55, "days": 60, "total_mm": 330, "normal_mm": 600})
    assert dry[0] == pytest.approx(7.5) and "45% drier" in dry[1]
    wet = planner.current_points({"ratio": 2.0, "days": 60, "total_mm": 1200, "normal_mm": 600})
    assert wet[0] == 8.0 and "wetter" in wet[1]
    assert planner.current_points(None)[0] == planner.CURRENT_NO_DATA


def test_field_check_uses_gpm_rain(client):
    d = client.post("/api/check", json={"ph": 6, "location": "KUCHING", "month": 3, "crop": "JAGUNG"}).get_json()
    c = d["results"][0]["climate"]
    assert c["rain_mm"] == 5 * 65 and c["source"] == "NASA GPM + POWER"
    assert "GPM" in d["input"]["climate"]["period"]


def test_plan_has_recent_rain_part(client):
    d = client.post("/api/rotation/plan", json={"current": "JAGUNG", "planted": "2026-03-02", "location": "KUCHING", "ph": 6.2}).get_json()
    o = d["recommendations"][0]
    assert set(o["breakdown"]) == {"climate", "rotation", "soil", "current"}
    assert o["max"] == {"climate": 40, "rotation": 30, "soil": 15, "current": 15}
    assert o["score"] == sum(o["breakdown"].values())
    assert d["recent"]["ratio"] == 0.5 and "drier" in o["notes"][-1]


def test_map_rain_grid(client):
    d = client.get("/api/map/rain?crop=JAGUNG&planted=2026-03-01").get_json()
    assert d["available"] and len(d["season"]["total_mm"]) == 43 and len(d["season"]["total_mm"][0]) == 63
    assert d["season"]["total_mm"][5][5] == 5 * 65 and d["season"]["total_mm"][0][0] is None
    assert d["recent"]["ratio"][5][5] == 0.5


def test_map_rain_without_data():
    gpm.set_data(None)
    r = create_app().test_client().get("/api/map/rain?crop=JAGUNG&planted=2026-03-01")
    assert r.status_code == 404
