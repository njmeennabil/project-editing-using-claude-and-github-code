"""Sarawak's 12 divisions, located at each division's main town.

Coordinates are approximate town centres. NASA POWER data covers a grid of
roughly 50 km, so this is precise enough to describe each division's climate.
"""

SARAWAK_DIVISIONS = [
    {"code": "KUCHING", "name": "Kuching", "lat": 1.553, "lon": 110.359},
    {"code": "SAMARAHAN", "name": "Samarahan", "lat": 1.459, "lon": 110.488},
    {"code": "SERIAN", "name": "Serian", "lat": 1.167, "lon": 110.567},
    {"code": "SRI_AMAN", "name": "Sri Aman", "lat": 1.237, "lon": 111.462},
    {"code": "BETONG", "name": "Betong", "lat": 1.404, "lon": 111.525},
    {"code": "SARIKEI", "name": "Sarikei", "lat": 2.127, "lon": 111.518},
    {"code": "SIBU", "name": "Sibu", "lat": 2.287, "lon": 111.830},
    {"code": "MUKAH", "name": "Mukah", "lat": 2.899, "lon": 112.091},
    {"code": "KAPIT", "name": "Kapit", "lat": 2.017, "lon": 112.933},
    {"code": "BINTULU", "name": "Bintulu", "lat": 3.170, "lon": 113.040},
    {"code": "MIRI", "name": "Miri", "lat": 4.399, "lon": 113.991},
    {"code": "LIMBANG", "name": "Limbang", "lat": 4.755, "lon": 115.009},
]

BY_CODE = {d["code"]: d for d in SARAWAK_DIVISIONS}
