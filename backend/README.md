# BUMI360 API (Python Flask)

Reads the crop database (`../database/tanaman.db`), translates it to English and runs the
suitability rules.

## Run locally

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/flask --app app run --port 5000
.venv/bin/python -m pytest tests
```

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/api/health` | `{"status": "ok", "crops": 5}` |
| GET | `/api/crops` | All crops with full growing guides |
| GET | `/api/crops/<code>` | One crop, e.g. `/api/crops/JAGUNG` |
| GET | `/api/rotation` | Rotation pairs and notes |
| GET | `/api/locations` | Sarawak's 12 divisions |
| GET | `/api/climate?location=KUCHING` | Monthly NASA POWER temperature and rainfall (or `?lat=&lon=`) |
| GET / POST | `/api/check` | Suitability. Either `ph`, `temp`, `water`, or `ph`, `location` (or `lat`/`lon`), `month`, `irrigation`. Optional `crop` (`all` or a code) |

Example:

```bash
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"ph": 5.8, "temp": 28, "water": 600, "crop": "all"}'
```

With NASA climate:

```bash
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"ph": 5.8, "location": "MIRI", "month": 3, "irrigation": 0, "crop": "JAGUNG"}'
```

For each crop, BUMI360 adds up NASA rainfall and averages NASA temperature over that crop's growing
season, starting on the 1st of the planting month. Extra irrigation is added to the rainfall.

The rules and their thresholds are in `rules.py`.

## NASA POWER climate data

- `locations.py`: Sarawak's 12 divisions and their coordinates.
- `nasa_power.py`: reads the NASA POWER Climatology API (no account needed) and works out each crop's season.
- `data/sarawak_climate.json`: saved data for the 12 divisions, so they work even if NASA is slow.
  Refresh it with `python3 scripts/update_climate.py`.
- GPS locations are fetched live from NASA and kept in memory.

Data obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the
NASA Earth Science/Applied Science Program.

## Settings

| Variable | Purpose |
|---|---|
| `ALLOWED_ORIGINS` | Websites allowed to call the API, e.g. `https://bumi360.vercel.app`. Default `*` |
| `BUMI_DB_PATH` | Optional path to another copy of `tanaman.db` |

## Deploy on Render

`render.yaml` at the repository root describes the service. In Render choose
**New + → Blueprint** and pick this repository.
