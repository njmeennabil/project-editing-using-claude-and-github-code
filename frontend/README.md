# BUMI360 frontend (Next.js + React + Tailwind)

The website farmers use. It gets all crop data and suitability results from the
BUMI360 Flask API in `../backend`.

## Run locally

Start the API first (see `../backend`), then:

```bash
cp .env.example .env.local     # set NEXT_PUBLIC_API_URL if the API is not on http://localhost:5000
npm install
npm run dev                    # http://localhost:3000
```

## Structure

| Path | Purpose |
|---|---|
| `src/app/page.tsx` | Home page; loads crop data from the API while prerendering |
| `src/app/layout.tsx` | Fonts, page title, theme colour |
| `src/app/globals.css` | Black-and-white colour tokens (light and dark) and Tailwind setup |
| `src/components/` | Header, hero, field check, crop guide, compare, rotation, about, footer |
| `src/lib/api.ts` | Calls to the Flask API |
| `src/lib/initial-data.ts` | Cached data for prerendering (refreshed hourly) |
| `src/lib/types.ts` | Shapes of the API responses |

The page is prerendered with data from the API and refreshed every hour. If the API is
asleep during a build or visit, the browser shows "Connecting…" and loads the data once
the API answers.

## Deploy on Vercel

1. Import the GitHub repository in Vercel.
2. Set **Root Directory** to `frontend`.
3. Add the environment variable `NEXT_PUBLIC_API_URL` with your Render API address.
4. Deploy.
