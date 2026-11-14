import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import create_app  # noqa: E402


@pytest.fixture()
def client():
    return create_app().test_client()


def by_code(results):
    return {r["code"]: r for r in results}


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok", "crops": 5}


def test_crops_are_english(client):
    crops = client.get("/api/crops").get_json()["crops"]
    assert [c["name"] for c in crops] == ["Maize", "Soybean", "Peanut", "Water Spinach", "Mustard Greens"]
    maize = client.get("/api/crops/jagung").get_json()
    assert maize["soil"]["texture"] == "Loam or sandy loam"


def test_unknown_crop_404(client):
    assert client.get("/api/crops/NOPE").status_code == 404


def test_example_field(client):
    data = client.get("/api/check?ph=5.8&temp=28&water=600").get_json()
    res = by_code(data["results"])
    assert data["counts"] == {"ok": 4, "warn": 0, "bad": 1, "none": 0}
    assert res["SOYA"]["status"] == "bad"
    assert res["SOYA"]["checks"][0]["title"] == "Too acidic"
    assert data["results"][-1]["code"] == "SOYA"  # least suitable last


def test_post_single_crop(client):
    data = client.post("/api/check", json={"ph": 6.5, "temp": 28, "water": 700, "crop": "SOYA"}).get_json()
    assert len(data["results"]) == 1
    assert data["results"][0]["status"] == "ok"
    assert "700 mm" in data["results"][0]["checks"][2]["message"]


def test_aluminium_danger(client):
    soy = client.get("/api/check?ph=4.2&temp=28&water=600&crop=soya").get_json()["results"][0]
    assert soy["checks"][0]["title"] == "Danger"


def test_temperature_margins(client):
    maize = lambda t: client.get(f"/api/check?ph=6&temp={t}&water=600&crop=JAGUNG").get_json()["results"][0]  # noqa: E731
    assert maize(35)["status"] == "warn"   # 2°C above 33
    assert maize(35.5)["status"] == "bad"
    assert maize(18)["status"] == "ok"


def test_water_rules(client):
    maize = lambda w: client.get(f"/api/check?ph=6&temp=28&water={w}&crop=JAGUNG").get_json()["results"][0]  # noqa: E731
    assert maize(300)["status"] == "warn"   # 200 short of 500 (40%)
    assert maize(200)["status"] == "bad"    # 300 short (60%)
    assert maize(900)["checks"][2]["title"] == "Excess water"
    spinach = client.get("/api/check?ph=6&temp=28&water=50&crop=KANGKUNG").get_json()["results"][0]
    assert spinach["checks"][2]["status"] == "info" and spinach["status"] == "ok"


def test_missing_and_invalid_input(client):
    data = client.get("/api/check?temp=28&water=600").get_json()
    assert data["counts"]["none"] == 5
    r = client.get("/api/check?ph=abc")
    assert r.status_code == 400 and "number" in r.get_json()["error"]
    assert client.get("/api/check?ph=15").status_code == 400
    assert client.get("/api/check?ph=6&crop=RICE").status_code == 400


def test_cors_header(client):
    r = client.get("/api/health", headers={"Origin": "https://bumi360.vercel.app"})
    assert r.headers.get("Access-Control-Allow-Origin") in ("*", "https://bumi360.vercel.app")
