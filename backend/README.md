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
| GET / POST | `/api/rotation/plan` | Next-crop planner: `current` (crop code), `planted` (YYYY-MM-DD), `location` (or `lat`/`lon`), `ph`, optional `prep_days` (default 14) and `irrigation`. Scores all 5 crops 0–100 and returns the top 3 |
| GET | `/api/map/rain?crop=&planted=` | NASA GPM rainfall grid for the map: expected rain over the crop's season, and the last 60 days against normal |
| GET | `/api/map/soil` | NASA SMAP root-zone soil moisture this week, compared with the usual for the month |
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

## Next-crop planner (`planner.py`)

1. Expected harvest = planting date + the current crop's maturity days; next planting = harvest + `prep_days`.
2. Each crop is scored for its own season starting on that date (NASA POWER, day by day):

| Part | Points | Rule |
|---|---|---|
| Climate fit | 40 | Temperature 20 (−4 per °C outside the best range) + water 20 (shortfall in proportion; excess down to 40%; 16 for crops with no mm figure) |
| Rotation | 30 | `penilaian_giliran` table: Excellent 30 · Good 22 · Fair 14 · Poor 4 |
| Soil pH | 15 | −7.5 per pH unit outside the range; 0 below a danger level |
| Current conditions | 15 | Half from the last 60 days of GPM rain ÷ normal (full from 0.8 to 1.3), half from this week's SMAP root-zone soil moisture against the usual for the month (full within ±0.4 standard deviations). If one is missing, the other counts for all 15 |

A Poor rotation caps the verdict at "Possible with care". Most rotation ratings are drafts
(`disahkan = 0` in the database) awaiting expert review.

## NASA GPM rainfall (`gpm.py`)

`data/gpm_sarawak.json` holds a 0.1° (~10 km) grid over Sarawak: monthly rainfall normals for 2001–2024
(IMERG Final, `GPM_3IMERGM`) and the last 60 days (IMERG Late, `GPM_3IMERGDL`). Wherever this grid covers a
place, its rainfall replaces NASA POWER rainfall (temperature stays from POWER). A place uses the mean of the
3 × 3 cells around it.

The file is built by `scripts/update_gpm.py` in GitHub Actions (`.github/workflows/gpm.yml`) every Monday,
using the `EARTHDATA_TOKEN` repository secret. Only the Sarawak box of each NASA file is downloaded (OPeNDAP).
A check over July–September 2025 found IMERG Late within about ±7% of IMERG Final at Sarawak's towns.

**The Earthdata token expires after 60 days.** When the weekly run fails with "NASA refused access", generate
a new token at urs.earthdata.nasa.gov and replace the `EARTHDATA_TOKEN` secret.

GPM IMERG data provided by NASA Goddard Earth Sciences Data and Information Services Center (GES DISC).

## NASA SMAP soil moisture (`smap.py`)

`data/smap_sarawak.json` holds SMAP Level 4 (`SPL4SMGP` v008, 9 km) surface (0–5 cm) and root-zone
(0–100 cm) soil moisture for the Sarawak block of the EASE-Grid 2.0 (rows 739–800, columns 3100–3168):
monthly normals and spread for 2016–2025 (four sample days a month at 14:00 Sarawak time) and the mean of
the last 7 days. Built by `scripts/update_smap.py` in the same weekly workflow, with the same token.
SMAP Level 4 data provided by the NASA National Snow and Ice Data Center DAAC (NSIDC DAAC).
