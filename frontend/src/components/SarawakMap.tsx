"use client";

import "leaflet/dist/leaflet.css";
import type * as Leaflet from "leaflet";
import { useEffect, useRef, useState } from "react";
import { ApiError, getMapRain, getMapSoil, getMapSuitability } from "@/lib/api";
import { DEFAULT_PLAN } from "@/lib/defaults";
import { num } from "@/lib/format";
import type { Crop, MapRain, MapScore, MapSoil, MapSuitability, Place } from "@/lib/types";
import { Container, Eyebrow, SectionTitle } from "./Container";
import { FieldShell, SelectField } from "./FieldCheck";
import { ScoreRing, VerdictPill } from "./NextCrop";

export type MapTarget = "check" | "plan";
type Layer = "score" | "rain" | "recent" | "soil";

type GeoFeature = { geometry: { type: string; coordinates: number[][][] | number[][][][] } };

interface GridSpec {
  values: (number | null)[][];
  nrows: number;
  ncols: number;
  northFirst: boolean; // row 0 is the northern edge
  lo: number;
  hi: number;
  south: number;
  north: number;
  west: number;
  east: number;
}

/** Draw a data grid as a smooth greyscale picture, clipped to Sarawak. Darker = more water. */
function gridImage(spec: GridSpec, fg: string, features: GeoFeature[]) {
  const small = document.createElement("canvas");
  small.width = spec.ncols;
  small.height = spec.nrows;
  const sc = small.getContext("2d")!;
  const img = sc.createImageData(spec.ncols, spec.nrows);
  const [r, gg, b] = (fg.match(/[0-9a-f]{2}/gi) ?? ["0a", "0a", "0a"]).map((h) => parseInt(h, 16));
  for (let j = 0; j < spec.nrows; j++) {
    for (let i = 0; i < spec.ncols; i++) {
      const v = spec.values[j]?.[i];
      if (v == null) continue;
      const row = spec.northFirst ? j : spec.nrows - 1 - j;
      const k = (row * spec.ncols + i) * 4;
      const t = Math.max(0, Math.min(1, (v - spec.lo) / (spec.hi - spec.lo || 1)));
      img.data[k] = r;
      img.data[k + 1] = gg;
      img.data[k + 2] = b;
      img.data[k + 3] = Math.round(30 + t * 200);
    }
  }
  sc.putImageData(img, 0, 0);
  const scale = 10;
  const big = document.createElement("canvas");
  big.width = spec.ncols * scale;
  big.height = spec.nrows * scale;
  const bc = big.getContext("2d")!;
  const px = (lon: number) => ((lon - spec.west) / (spec.east - spec.west)) * big.width;
  const py = (lat: number) => ((spec.north - lat) / (spec.north - spec.south)) * big.height;
  bc.beginPath();
  for (const f of features) {
    const polys = (f.geometry.type === "Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates) as number[][][][];
    for (const poly of polys) {
      for (const ring of poly) {
        ring.forEach(([lon, lat], n) => (n === 0 ? bc.moveTo(px(lon), py(lat)) : bc.lineTo(px(lon), py(lat))));
        bc.closePath();
      }
    }
  }
  bc.clip("evenodd");
  bc.imageSmoothingEnabled = true;
  bc.drawImage(small, 0, 0, big.width, big.height);
  return {
    url: big.toDataURL("image/png"),
    bounds: [[spec.south, spec.west], [spec.north, spec.east]] as [[number, number], [number, number]],
  };
}

function rainSpec(rain: MapRain, layer: "rain" | "recent"): GridSpec {
  const g = rain.grid;
  const west = g.lon0 - g.step / 2, south = g.lat0 - g.step / 2;
  return {
    values: layer === "rain" ? rain.season.total_mm : rain.recent?.ratio ?? [],
    nrows: g.nlat,
    ncols: g.nlon,
    northFirst: false,
    lo: layer === "rain" ? rain.season.min ?? 0 : 0.3,
    hi: layer === "rain" ? rain.season.max ?? 1 : 1.7,
    south,
    north: south + g.nlat * g.step,
    west,
    east: west + g.nlon * g.step,
  };
}

function soilSpec(soil: MapSoil): GridSpec {
  const { lat, lon } = soil.grid;
  const dLat = Math.abs(lat[0] - lat[1]) / 2, dLon = Math.abs(lon[1] - lon[0]) / 2;
  return {
    values: soil.z,
    nrows: lat.length,
    ncols: lon.length,
    northFirst: true,
    lo: -2,
    hi: 2,
    south: lat[lat.length - 1] - dLat,
    north: lat[0] + dLat,
    west: lon[0] - dLon,
    east: lon[lon.length - 1] + dLon,
  };
}

const CARTO_KEY = process.env.NEXT_PUBLIC_CARTO_KEY || "";
const SARAWAK: [[number, number], [number, number]] = [[0.85, 109.55], [5.05, 115.7]];
const BOUNDARY_CREDIT =
  'Boundaries: <a href="https://www.geoboundaries.org/" target="_blank" rel="noopener">geoBoundaries</a> (CC BY 3.0)';

function tiles(dark: boolean) {
  if (CARTO_KEY) {
    return {
      url: `https://{s}.basemaps.cartocdn.com/${dark ? "dark_all" : "light_all"}/{z}/{x}/{y}{r}.png?key=${encodeURIComponent(CARTO_KEY)}`,
      className: "",
      attribution:
        '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors, © <a href="https://carto.com/attribution/" target="_blank" rel="noopener">CARTO</a>',
      subdomains: "abcd",
    };
  }
  // Fallback while no CARTO key is set: OpenStreetMap tiles shown in greyscale.
  return {
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    className: "bw-tiles",
    attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
    subdomains: "abc",
  };
}

function verdictClass(score: number) {
  return score >= 80 ? "hr" : score >= 60 ? "r" : score >= 40 ? "p" : "n";
}

function pinHtml(code: string, name: string, score: number | null, selected: boolean) {
  const cls = score == null ? "none" : verdictClass(score);
  return `<div class="bumi-pin ${cls}${selected ? " sel" : ""}" data-code="${code}"><b>${score ?? "–"}</b><span>${name}</span></div>`;
}

export function SarawakMap({
  crops,
  locations,
  target,
  onUse,
}: {
  crops: Crop[];
  locations: Place[];
  target: MapTarget | null;
  onUse: (target: MapTarget, place: { location: string; lat: string; lon: string; name: string }) => void;
}) {
  const box = useRef<HTMLDivElement>(null);
  const L = useRef<typeof Leaflet | null>(null);
  const map = useRef<Leaflet.Map | null>(null);
  const tileLayer = useRef<Leaflet.TileLayer | null>(null);
  const shapes = useRef<Leaflet.GeoJSON | null>(null);
  const pins = useRef<Map<string, Leaflet.Marker>>(new Map());
  const pointPin = useRef<Leaflet.CircleMarker | null>(null);
  const rainLayer = useRef<Leaflet.ImageOverlay | null>(null);
  const features = useRef<GeoFeature[]>([]);

  const [ready, setReady] = useState(false);
  const [crop, setCrop] = useState("JAGUNG");
  const [planted, setPlanted] = useState(DEFAULT_PLAN.planted);
  const [point, setPoint] = useState<{ lat: string; lon: string } | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [data, setData] = useState<MapSuitability | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [layer, setLayer] = useState<Layer>("score");
  const [rain, setRain] = useState<MapRain | null>(null);
  const [rainError, setRainError] = useState<string | null>(null);
  const [soil, setSoil] = useState<MapSoil | null>(null);

  // Create the map once (Leaflet needs the browser, so it is loaded here).
  useEffect(() => {
    let cancelled = false;
    let media: MediaQueryList | null = null;
    let onTheme: (() => void) | null = null;
    (async () => {
      const lib = (await import("leaflet")).default;
      if (cancelled || !box.current || map.current) return;
      L.current = lib;
      const m = lib.map(box.current, {
        scrollWheelZoom: false,
        minZoom: 6,
        maxZoom: 15,
        maxBounds: [[-1.0, 107.5], [7.0, 118.0]],
        attributionControl: true,
      });
      map.current = m;
      m.attributionControl.setPrefix(false);
      m.fitBounds(SARAWAK, { padding: [10, 10] });
      // Zoomed out, badges show only the score; names appear from zoom 8.
      const zoomClass = () => box.current?.classList.toggle("zoom-low", m.getZoom() < 8);
      zoomClass();
      m.on("zoomend", zoomClass);
      m.on("focus click", () => m.scrollWheelZoom.enable());
      m.on("blur", () => m.scrollWheelZoom.disable());
      m.on("click", (e: Leaflet.LeafletMouseEvent) => {
        setPoint({ lat: e.latlng.lat.toFixed(4), lon: e.latlng.lng.toFixed(4) });
        setSelected("POINT");
      });

      media = window.matchMedia("(prefers-color-scheme: dark)");
      const isDark = () => document.documentElement.dataset.theme === "dark" || (document.documentElement.dataset.theme !== "light" && !!media?.matches);
      const addTiles = () => {
        tileLayer.current?.remove();
        const t = tiles(isDark());
        tileLayer.current = lib
          .tileLayer(t.url, { attribution: `${t.attribution} · ${BOUNDARY_CREDIT}`, className: t.className, subdomains: t.subdomains, maxZoom: 19 })
          .addTo(m);
      };
      addTiles();
      onTheme = addTiles;
      media.addEventListener("change", onTheme);

      const res = await fetch("/data/sarawak-divisions.geojson");
      const geo = await res.json();
      if (cancelled) return;
      features.current = geo.features;
      shapes.current = lib
        .geoJSON(geo, {
          // Outlines only: taps go through to the map so any exact spot can be chosen.
          interactive: false,
          style: () => ({ color: "#0a0a0a", weight: 1.2, fillOpacity: 0, opacity: 0.7 }),
        })
        .addTo(m);

      locations.forEach((d) => {
        const mk = lib
          .marker([d.lat, d.lon], {
            icon: lib.divIcon({ className: "bumi-pin-wrap", html: pinHtml(d.code, d.name, null, false), iconSize: [0, 0] }),
            keyboard: true,
            title: d.name,
          })
          .on("click", (e: Leaflet.LeafletMouseEvent) => {
            lib.DomEvent.stopPropagation(e);
            setSelected(d.code);
          })
          .addTo(m);
        pins.current.set(d.code, mk);
      });
      setReady(true);
    })();
    return () => {
      cancelled = true;
      if (media && onTheme) media.removeEventListener("change", onTheme);
      map.current?.remove();
      map.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- the map is created once; divisions never change
  }, []);

  // Fetch scores when the crop, date or tapped point changes.
  useEffect(() => {
    if (!planted) return;
    const ctrl = new AbortController();
    const t = setTimeout(async () => {
      setLoading(true);
      try {
        setData(await getMapSuitability({ crop, planted, lat: point?.lat, lon: point?.lon }, ctrl.signal));
        setError(null);
      } catch (e) {
        if (ctrl.signal.aborted) return;
        setError(e instanceof ApiError ? e.message : "Can't reach the BUMI360 server. It may be waking up; try again in a minute.");
      } finally {
        if (!ctrl.signal.aborted) setLoading(false);
      }
    }, 300);
    return () => {
      clearTimeout(t);
      ctrl.abort();
    };
  }, [crop, planted, point]);

  // GPM rainfall grid for the shading layers.
  useEffect(() => {
    if (layer === "score" || !planted) return;
    const ctrl = new AbortController();
    const t = setTimeout(async () => {
      try {
        if (layer === "soil") setSoil(await getMapSoil(ctrl.signal));
        else setRain(await getMapRain({ crop, planted }, ctrl.signal));
        setRainError(null);
      } catch (e) {
        if (ctrl.signal.aborted) return;
        setRainError(e instanceof ApiError ? e.message : "This shading could not be loaded.");
      }
    }, 300);
    return () => {
      clearTimeout(t);
      ctrl.abort();
    };
  }, [layer, crop, planted]);

  // Draw or remove the rainfall shading.
  useEffect(() => {
    const lib = L.current;
    const m = map.current;
    if (!ready || !lib || !m) return;
    rainLayer.current?.remove();
    rainLayer.current = null;
    if (layer === "score") return;
    let spec: GridSpec | null = null;
    if (layer === "soil") spec = soil ? soilSpec(soil) : null;
    else if (rain && (layer === "rain" || rain.recent)) spec = rainSpec(rain, layer);
    if (!spec) return;
    const fg = getComputedStyle(document.documentElement).getPropertyValue("--fg").trim() || "#0a0a0a";
    const pic = gridImage(spec, fg, features.current);
    rainLayer.current = lib.imageOverlay(pic.url, pic.bounds, { opacity: 0.85, interactive: false }).addTo(m);
  }, [ready, layer, rain, soil]);

  // Paint scores and the selection onto the map.
  useEffect(() => {
    const lib = L.current;
    if (!ready || !lib) return;
    const fg = getComputedStyle(document.documentElement).getPropertyValue("--fg").trim() || "#0a0a0a";
    const scores = new Map((data?.divisions ?? []).map((d) => [d.code, d.score]));
    shapes.current?.setStyle((f) => {
      const s = scores.get(f?.properties.code);
      const sel = f?.properties.code === selected;
      const fill = layer !== "score" || s == null ? 0 : (s / 100) * 0.28;
      return { color: fg, weight: sel ? 3 : 1.2, opacity: sel ? 1 : 0.7, fillColor: fg, fillOpacity: fill };
    });
    locations.forEach((d) => {
      const pin = pins.current.get(d.code);
      pin?.setIcon(
        lib.divIcon({ className: "bumi-pin-wrap", html: pinHtml(d.code, d.name, scores.get(d.code) ?? null, d.code === selected), iconSize: [0, 0] }),
      );
      pin?.setZIndexOffset(d.code === selected ? 1000 : 0);
    });
    const m = map.current;
    pointPin.current?.remove();
    pointPin.current = null;
    if (point && m) {
      pointPin.current = lib
        .circleMarker([Number(point.lat), Number(point.lon)], { radius: 9, color: fg, weight: 3, fillColor: fg, fillOpacity: selected === "POINT" ? 1 : 0.4 })
        .addTo(m);
    }
  }, [ready, data, selected, point, locations, layer]);

  const info: (Place & MapScore) | null =
    selected === "POINT" ? data?.point ?? null : data?.divisions.find((d) => d.code === selected) ?? null;
  const ranked = [...(data?.divisions ?? [])].sort((a, b) => b.score - a.score);

  function use(where: MapTarget) {
    if (!info) return;
    const isPoint = selected === "POINT";
    onUse(where, {
      location: isPoint ? "MAP" : info.code,
      lat: String(isPoint ? point?.lat ?? info.lat : info.lat),
      lon: String(isPoint ? point?.lon ?? info.lon : info.lon),
      name: isPoint ? `Map point (${point?.lat}, ${point?.lon})` : info.name,
    });
  }

  const buttons: { where: MapTarget; label: string }[] = [
    { where: "check", label: "Use in Field check" },
    { where: "plan", label: "Use in Next crop" },
  ];
  if (target === "plan") buttons.reverse();

  return (
    <section id="map" aria-labelledby="map-title" className="border-t border-line py-14 md:py-[72px]">
      <Container>
        <div className="mb-7">
          <Eyebrow>Map</Eyebrow>
          <SectionTitle id="map-title">Where does it grow best in Sarawak?</SectionTitle>
          <p className="mt-2.5 max-w-[62ch] text-muted">
            Pick a crop and a planting date to see its climate score in every division. Tap a division&apos;s score badge for
            details, or tap anywhere on the map to check that exact spot.
          </p>
          {target && (
            <p role="status" className="mt-3 inline-block rounded-[10px] border-[1.5px] border-fg px-3 py-2 text-[0.9rem] font-semibold">
              Tap your farm on the map, then press “{target === "check" ? "Use in Field check" : "Use in Next crop"}”.
            </p>
          )}
        </div>

        <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:max-w-[720px]">
          <SelectField id="map-crop" label="Crop" value={crop} onChange={(e) => setCrop(e.target.value)} hint="Score this crop">
            {crops.map((c) => (
              <option key={c.code} value={c.code}>{c.name} ({c.local_name})</option>
            ))}
          </SelectField>
          <FieldShell id="map-planted" label="Planting date" hint="The season starts on this day">
            <input
              id="map-planted"
              type="date"
              value={planted}
              onChange={(e) => setPlanted(e.target.value)}
              min="2000-01-01"
              max="2100-12-31"
              className="min-h-12 w-full rounded-[10px] border border-line bg-bg px-3 text-base"
            />
          </FieldShell>
        </div>

        <div className="mb-4 grid gap-1.5">
          <span className="text-[0.92rem] font-semibold" id="map-layer-label">Shading</span>
          <div role="radiogroup" aria-labelledby="map-layer-label" className="grid max-w-[720px] grid-cols-2 rounded-[10px] border border-line bg-bg p-1 sm:grid-cols-4">
            {([
              ["score", "Climate score"],
              ["rain", "Expected rain"],
              ["recent", "Last 60 days"],
              ["soil", "Soil moisture"],
            ] as const).map(([value, label]) => (
              <button
                key={value}
                type="button"
                role="radio"
                aria-checked={layer === value}
                onClick={() => setLayer(value)}
                className={`min-h-10 rounded-[7px] px-2 text-[0.88rem] font-semibold ${layer === value ? "bg-fg text-bg" : "text-muted hover:text-fg"}`}
              >
                {label}
              </button>
            ))}
          </div>
          <span className="text-[0.8rem] text-muted">
            {layer === "score"
              ? "Darker divisions have a higher climate score for this crop and date."
              : layer === "rain"
                ? rain
                  ? `NASA GPM: normal rain over the ${rain.crop.name.toLowerCase()} season (${rain.season.months}, ${rain.season.days} days) from ${rain.normals_period}, about 10 km detail. Lighter ≈ ${num(rain.season.min ?? 0)} mm, darker ≈ ${num(rain.season.max ?? 0)} mm.`
                  : "Loading NASA GPM rainfall…"
                : layer === "recent"
                  ? rain?.recent
                    ? `NASA GPM: rain from ${rain.recent.start} to ${rain.recent.end} compared with normal. Lighter = drier than normal, darker = wetter.`
                    : "Loading NASA GPM rainfall…"
                  : soil
                    ? `NASA SMAP: root-zone soil moisture ${soil.start} to ${soil.end} compared with the usual for this month (${soil.normals_period}), about 9 km. Lighter = drier than usual, darker = wetter.`
                    : "Loading NASA SMAP soil moisture…"}
            {rainError && layer !== "score" ? ` ${rainError}` : ""}
          </span>
        </div>

        <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
          <div className="bumi-map relative isolate min-w-0 overflow-hidden rounded-[14px] border border-line">
            <div ref={box} className="h-[58vh] max-h-[640px] min-h-[380px] w-full" role="application" aria-label="Map of Sarawak divisions" />
            {loading && (
              <span className="absolute left-3 top-3 z-[500] rounded-full border border-line bg-surface px-3 py-1 text-[0.8rem] font-semibold">
                Updating…
              </span>
            )}
          </div>

          <div className="grid min-w-0 gap-4" aria-live="polite">
            {error && (
              <div role="alert" className="rounded-[14px] border-[1.5px] border-dashed border-fg px-4 py-3 text-[0.92rem]">{error}</div>
            )}

            {info ? (
              <article className="grid gap-4 rounded-[14px] border border-line bg-surface p-5">
                <div className="flex items-start gap-4">
                  <ScoreRing score={info.score} size={84} />
                  <div className="grid min-w-0 gap-1.5">
                    <span className="text-xs font-semibold uppercase tracking-[0.08em] text-muted">
                      {selected === "POINT" ? "Your map point" : "Division"}
                    </span>
                    <h3 className="font-display text-xl font-semibold leading-tight">
                      {selected === "POINT" ? `${point?.lat}, ${point?.lon}` : info.name}
                    </h3>
                    <div className="flex flex-wrap"><VerdictPill verdict={info.verdict} /></div>
                  </div>
                </div>
                <p className="rounded-[10px] border border-line bg-bg px-3 py-2 text-[0.82rem] leading-snug text-muted">
                  <span className="font-semibold text-fg">{data?.source ?? "NASA"}</span> · {data?.crop.name} · {info.season.months} ({info.season.days} days
                  {info.season.days_assumed ? ", assumed" : ""}): {num(info.season.temp_c)}°C average, {num(info.season.rain_mm)} mm rain
                </p>
                <ul className="grid list-disc gap-1 pl-5 text-[0.88rem] text-muted">
                  {info.notes.map((n) => <li key={n}>{n}</li>)}
                </ul>
                <div className="grid gap-2">
                  {buttons.map((b, i) => (
                    <button
                      key={b.where}
                      type="button"
                      onClick={() => use(b.where)}
                      className={`min-h-[46px] rounded-[10px] px-4 font-semibold ${i === 0 ? "bg-fg text-bg hover:opacity-90" : "border border-line hover:bg-bg-alt"}`}
                    >
                      {b.label}
                    </button>
                  ))}
                </div>
              </article>
            ) : (
              <p className="rounded-[14px] border border-line bg-surface p-5 text-muted">
                Tap a score badge, or anywhere on the map, to see the details here.
              </p>
            )}

            {ranked.length > 0 && (
              <div className="grid gap-2">
                <h4 className="text-xs font-semibold uppercase tracking-[0.08em] text-muted">
                  {data?.crop.name}: climate score by division
                </h4>
                <ol className="grid grid-cols-2 gap-x-4 gap-y-1 text-[0.9rem] tabular-nums">
                  {ranked.map((d) => (
                    <li key={d.code}>
                      <button type="button" onClick={() => setSelected(d.code)} className={`flex w-full justify-between gap-2 py-0.5 text-left hover:underline ${d.code === selected ? "font-bold" : ""}`}>
                        <span>{d.name}</span>
                        <span>{d.score}</span>
                      </button>
                    </li>
                  ))}
                </ol>
              </div>
            )}
            <p className="text-[0.78rem] text-muted">
              Climate score only (temperature 50 + water 50) at each division&apos;s main town: temperature from NASA POWER,
              rainfall from NASA GPM (about 10 km). Your soil pH, rotation and recent rain are scored in Next crop.
            </p>
          </div>
        </div>
      </Container>
    </section>
  );
}
