import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gpm  # noqa: E402
import planner  # noqa: E402
import smap  # noqa: E402
from app import create_app  # noqa: E402

LATS = [round(5.126 - k * 0.0707, 4) for k in range(62)]       # north -> south like EASE-Grid rows
LONS = [round(109.466 + k * 0.0934, 4) for k in range(69)]


def fake_smap(now=0.30, usual=0.40, spread=0.05):
    grid = lambda v: [[v] * len(LONS) for _ in LATS]  # noqa: E731
    return {"grid": {"lat": LATS, "lon": LONS},
            "normals": {"period": "2016–2025", "surface": [grid(usual)] * 12, "rootzone": [grid(usual)] * 12,
                        "rootzone_std": [grid(spread)] * 12},
            "recent": {"start": "2026-11-04", "end": "2026-11-10", "days": 7, "surface": grid(now), "rootzone": grid(now)}}


@pytest.fixture(autouse=True)
def reset():
    yield
    smap.set_data(None)
    gpm.set_data(None)


def test_point_value_and_label():
    smap.set_data(fake_smap(now=0.30, usual=0.40, spread=0.05))
    v = smap.at(1.553, 110.359)
    assert v["rootzone_pct"] == 30.0 and v["usual_rootzone_pct"] == 40.0
    assert v["z"] == -2.0 and v["label"] == "much drier than usual"
    assert smap.at(7.0, 110.0) is None                 # outside the Sarawak block
    smap.set_data(fake_smap(now=0.41))
    assert smap.at(1.553, 110.359)["label"] == "about usual"


def test_soil_points_and_combination():
    usual = {"z": 0.0, "rootzone_pct": 40, "usual_rootzone_pct": 40, "label": "about usual"}
    dry = {"z": -3.0, "rootzone_pct": 30, "usual_rootzone_pct": 40, "label": "much drier than usual"}
    drier = {"z": -1.9, "rootzone_pct": 37, "usual_rootzone_pct": 40, "label": "drier than usual"}
    wet = {"z": 2.0, "rootzone_pct": 50, "usual_rootzone_pct": 40, "label": "much wetter than usual"}
    assert planner.soil_moisture_points(usual)[0] == 7.5
    assert planner.soil_moisture_points(dry)[0] == 0.0 and "Water the seedbed" in planner.soil_moisture_points(dry)[1]
    assert planner.soil_moisture_points(drier)[0] == pytest.approx(7.5 * (1 - 1.5 / 2.6))
    assert planner.soil_moisture_points(wet)[0] == pytest.approx(7.5 * 0.45)   # wet soil never drops below 45 %
    rain_ok = {"ratio": 1.0, "days": 60, "total_mm": 600, "normal_mm": 600}
    pts, notes = planner.conditions_points(rain_ok, usual)
    assert pts == 15 and len(notes) == 2
    assert planner.conditions_points(None, usual)[0] == 15       # soil only counts double
    assert planner.conditions_points(rain_ok, None)[0] == 15     # rain only, as before


def test_plan_and_check_include_soil_moisture():
    smap.set_data(fake_smap(now=0.30, usual=0.40, spread=0.05))
    c = create_app().test_client()
    d = c.post("/api/rotation/plan", json={"current": "JAGUNG", "planted": "2026-03-02", "location": "KUCHING", "ph": 6.2}).get_json()
    assert d["soil_moisture"]["label"] == "much drier than usual"
    assert any("Soil moisture this week" in n for n in d["recommendations"][0]["notes"])
    chk = c.post("/api/check", json={"ph": 6, "location": "KUCHING", "month": 3}).get_json()
    assert chk["input"]["climate"]["soil_moisture"]["rootzone_pct"] == 30.0


def test_soil_map():
    smap.set_data(fake_smap(now=0.30, usual=0.40, spread=0.05))
    d = create_app().test_client().get("/api/map/soil").get_json()
    assert d["available"] and len(d["z"]) == 62 and len(d["z"][0]) == 69 and d["z"][3][3] == -2.0
    smap.set_data(None)
    assert create_app().test_client().get("/api/map/soil").status_code == 404


def test_small_differences_count_as_usual():
    smap.set_data(fake_smap(now=0.385, usual=0.40, spread=0.005))     # 1.5 points below, z = -3
    v = smap.at(1.553, 110.359)
    assert v["z"] == 0.0 and v["label"] == "about usual"
    smap.set_data(fake_smap(now=0.37, usual=0.40, spread=0.005))      # 3 points below: drier, not "much"
    v = smap.at(1.553, 110.359)
    assert v["z"] == -3.0 and v["label"] == "drier than usual"
