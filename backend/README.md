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
| GET / POST | `/api/check` | Suitability for `ph`, `temp`, `water`, optional `crop` (`all` or a code) |

Example:

```bash
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"ph": 5.8, "temp": 28, "water": 600, "crop": "all"}'
```

The rules and their thresholds are in `rules.py`.

## Settings

| Variable | Purpose |
|---|---|
| `ALLOWED_ORIGINS` | Websites allowed to call the API, e.g. `https://bumi360.vercel.app`. Default `*` |
| `BUMI_DB_PATH` | Optional path to another copy of `tanaman.db` |

## Deploy on Render

`render.yaml` at the repository root describes the service. In Render choose
**New + → Blueprint** and pick this repository.
