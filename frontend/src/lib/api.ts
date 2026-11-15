// Calls to the BUMI360 Flask API. Used on the server (prerender) and in the browser.
import type { CheckResponse, Crop, FieldInput, MapRain, MapSoil, MapSuitability, Place, PlanInput, PlanResponse, RotationItem, SiteData } from "./types";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000").replace(/\/+$/, "");

/** The server answered, but with an error message (e.g. "'ph' must be a number"). */
export class ApiError extends Error {}

async function request<T>(path: string, init: RequestInit = {}, timeoutMs = 15000): Promise<T> {
  // Abort on timeout or when the caller aborts (works on older phone browsers too).
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  const outer = init.signal;
  const onAbort = () => ctrl.abort();
  if (outer) {
    if (outer.aborted) ctrl.abort();
    else outer.addEventListener("abort", onAbort, { once: true });
  }
  try {
    const res = await fetch(`${API_URL}${path}`, { ...init, signal: ctrl.signal });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new ApiError(body.error || `The server returned an error (${res.status}).`);
    return body as T;
  } finally {
    clearTimeout(timer);
    outer?.removeEventListener("abort", onAbort);
  }
}

export async function getSiteData(timeoutMs?: number): Promise<SiteData> {
  const [crops, rotation, places] = await Promise.all([
    request<{ crops: Crop[] }>("/api/crops", {}, timeoutMs),
    request<{ rotation: RotationItem[]; notes: string[] }>("/api/rotation", {}, timeoutMs),
    request<{ locations: Place[] }>("/api/locations", {}, timeoutMs),
  ]);
  return { crops: crops.crops, rotation: rotation.rotation, notes: rotation.notes, locations: places.locations };
}

/** GPS and map points are sent as coordinates; divisions by their code. */
export const usesCoordinates = (location: string) => location === "GPS" || location === "MAP";

/** What the API needs for each mode: NASA climate (place + month) or manual readings. */
export function checkPayload(input: FieldInput) {
  if (input.mode === "manual") {
    return { ph: input.ph, temp: input.temp, water: input.water, crop: input.crop };
  }
  const place = usesCoordinates(input.location)
    ? { lat: input.lat, lon: input.lon, point: input.location === "MAP" ? "map" : "gps" }
    : { location: input.location };
  return { ph: input.ph, crop: input.crop, month: input.month, irrigation: input.irrigation, ...place };
}

export function checkField(input: FieldInput, signal?: AbortSignal, timeoutMs?: number): Promise<CheckResponse> {
  return request<CheckResponse>(
    "/api/check",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(checkPayload(input)),
      signal,
    },
    timeoutMs,
  );
}

export function planNextCrop(input: PlanInput, signal?: AbortSignal, timeoutMs?: number): Promise<PlanResponse> {
  const place = usesCoordinates(input.location)
    ? { lat: input.lat, lon: input.lon, point: input.location === "MAP" ? "map" : "gps" }
    : { location: input.location };
  const body = {
    current: input.current,
    planted: input.planted,
    ph: input.ph,
    prep_days: input.prep_days,
    irrigation: input.irrigation,
    ...place,
  };
  return request<PlanResponse>(
    "/api/rotation/plan",
    { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), signal },
    timeoutMs,
  );
}

export function getMapSuitability(
  q: { crop: string; planted: string; irrigation?: string; lat?: string; lon?: string },
  signal?: AbortSignal,
): Promise<MapSuitability> {
  const params = new URLSearchParams({ crop: q.crop, planted: q.planted });
  if (q.irrigation) params.set("irrigation", q.irrigation);
  if (q.lat && q.lon) {
    params.set("lat", q.lat);
    params.set("lon", q.lon);
  }
  return request<MapSuitability>(`/api/map/suitability?${params}`, { signal }, 70000);
}

export function getMapRain(q: { crop: string; planted: string }, signal?: AbortSignal): Promise<MapRain> {
  const params = new URLSearchParams({ crop: q.crop, planted: q.planted });
  return request<MapRain>(`/api/map/rain?${params}`, { signal }, 70000);
}

export function getMapSoil(signal?: AbortSignal): Promise<MapSoil> {
  return request<MapSoil>("/api/map/soil", { signal }, 70000);
}
