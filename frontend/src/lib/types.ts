// Shapes returned by the BUMI360 Flask API (backend/app.py).

export type Status = "ok" | "warn" | "bad" | "info" | "none";
export type OverallStatus = Exclude<Status, "info">;

export interface Meter {
  min: number;
  max: number;
  low: number;
  high: number;
  value: number | null;
}

export interface Check {
  factor: "ph" | "temp" | "water";
  name: string;
  range_text: string;
  your_value_text: string | null;
  meter: Meter | null;
  status: Status;
  title: string | null;
  message: string;
}

export interface ClimateInfo {
  source: string;
  location: string;
  months: string;
  days: number;
  days_assumed: boolean;
  temp_c: number;
  rain_mm: number;
  irrigation_mm: number;
  water_mm: number;
}

export interface Place {
  code: string;
  name: string;
  lat: number;
  lon: number;
}

export interface CropResult {
  climate?: ClimateInfo;
  code: string;
  name: string;
  local_name: string;
  scientific_name: string;
  status: OverallStatus;
  label: string;
  checks: Check[];
}

export interface CheckResponse {
  input: {
    ph: number | null;
    temp: number | null;
    water: number | null;
    crop: string;
    climate: {
      source: string;
      period: string | null;
      location: Place;
      month: number;
      month_name: string;
      irrigation: number;
      soil_moisture?: SoilMoisture | null;
    } | null;
  };
  counts: Record<OverallStatus, number>;
  results: CropResult[];
}

export interface Crop {
  id: number;
  code: string;
  name: string;
  local_name: string;
  scientific_name: string;
  type: string;
  fixes_nitrogen: boolean;
  key_nutrient: string;
  nitrogen_need: string;
  temp_min_c: number;
  temp_max_c: number;
  water_min_mm: number | null;
  water_max_mm: number | null;
  water_target_mm: number | null;
  water_note: string | null;
  maturity_min_days: number | null;
  maturity_max_days: number | null;
  maturity_note: string | null;
  source: string | null;
  soil: {
    texture: string;
    drainage: string;
    ph_min: number;
    ph_max: number;
    ph_danger_below: number | null;
    note: string | null;
  };
  critical_water_stages: string[];
  npk: {
    source: string;
    condition: string | null;
    n_min: number | null;
    n_max: number | null;
    p2o5_min: number | null;
    p2o5_max: number | null;
    k2o_min: number | null;
    k2o_max: number | null;
    note: string | null;
  }[];
  fertiliser_programme: {
    product: string;
    rate_min: number | null;
    rate_max: number | null;
    unit: string;
    timing: string | null;
    note: string | null;
  }[];
  special_nutrients: {
    nutrient: string;
    role: string;
    product: string | null;
    rate_min_kg_ha: number | null;
    rate_max_kg_ha: number | null;
    timing: string | null;
  }[];
  practices: { category: string; text: string }[];
  spacing: {
    variety: string | null;
    row_min_cm: number | null;
    row_max_cm: number | null;
    plant_min_cm: number | null;
    plant_max_cm: number | null;
  }[];
}

export interface RotationItem {
  before: string;
  after: string;
  yield_gain_pct: number | null;
  note: string;
}

export interface SiteData {
  crops: Crop[];
  rotation: RotationItem[];
  notes: string[];
  locations: Place[];
}

/** "nasa": temperature and rainfall from NASA POWER for a place and planting month. */
export type ClimateMode = "nasa" | "manual";

export interface FieldInput {
  mode: ClimateMode;
  ph: string;
  crop: string;
  // manual mode
  temp: string;
  water: string;
  // NASA mode
  location: string; // division code, "GPS", or "MAP" (point tapped on the map)
  lat: string;
  lon: string;
  month: string; // "1"–"12"
  irrigation: string;
}

// ---------- Next-crop planner (/api/rotation/plan) ----------
export interface PlanInput {
  current: string;
  planted: string; // YYYY-MM-DD
  location: string; // division code, "GPS" or "MAP"
  lat: string;
  lon: string;
  ph: string;
  prep_days: string;
  irrigation: string;
}

export interface PlanOption {
  code: string;
  name: string;
  local_name: string;
  score: number;
  verdict: string;
  breakdown: { climate: number; rotation: number; soil: number; current?: number };
  max: { climate: number; rotation: number; soil: number; current?: number };
  rotation: { rating: string; reason: string; verified: boolean; source: string };
  season: {
    temp_c: number;
    rain_mm: number;
    months: string;
    start: string;
    end: string;
    days: number;
    days_assumed: boolean;
    irrigation_mm: number;
    water_mm: number;
  };
  notes: string[];
}

export interface PlanResponse {
  input: { current: string; planted: string; ph: number; irrigation: number; prep_days: number };
  climate: { source: string; period: string | null };
  location: Place;
  recent: RecentRain | null;
  soil_moisture?: SoilMoisture | null;
  timeline: {
    current: { code: string; name: string; local_name: string };
    planted: string;
    growing_days: number;
    growing_days_assumed: boolean;
    harvest: string;
    prep_days: number;
    next_planting: string;
  };
  recommendations: PlanOption[];
  others: PlanOption[];
}

// ---------- Map (/api/map/suitability) ----------
export interface MapScore {
  score: number;
  verdict: string;
  temp_points: number;
  water_points: number;
  season: PlanOption["season"];
  notes: string[];
}

export interface MapSuitability {
  crop: { code: string; name: string; local_name: string };
  planted: string;
  irrigation: number;
  source: string;
  divisions: (Place & MapScore)[];
  point: (Place & MapScore) | null;
}

/** A place chosen on the map, handed to the Field check or Next crop form. */
export interface MapPlace {
  location: string; // division code, or "MAP" for a tapped point
  lat: string;
  lon: string;
  name: string;
  nonce: number;
}

export interface RecentRain {
  start: string;
  end: string;
  days: number;
  total_mm: number;
  normal_mm: number;
  ratio: number;
}

export interface MapRain {
  available: boolean;
  grid: { lon0: number; lat0: number; step: number; nlon: number; nlat: number };
  crop: { code: string; name: string };
  season: { planted: string; days: number; months: string; total_mm: (number | null)[][]; min: number | null; max: number | null };
  recent: { start: string; end: string; days: number; ratio: (number | null)[][] } | null;
  normals_period: string;
  source: string;
}

export interface SoilMoisture {
  start: string;
  end: string;
  days: number;
  rootzone_pct: number;
  surface_pct: number | null;
  usual_rootzone_pct: number | null;
  z: number | null;
  label: string;
  normals_period: string;
}

export interface MapSoil {
  available: boolean;
  grid: { lat: number[]; lon: number[] };
  start: string;
  end: string;
  rootzone: (number | null)[][];
  z: (number | null)[][];
  normals_period: string;
  source: string;
}
