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

export interface CropResult {
  code: string;
  name: string;
  local_name: string;
  scientific_name: string;
  status: OverallStatus;
  label: string;
  checks: Check[];
}

export interface CheckResponse {
  input: { ph: number | null; temp: number | null; water: number | null; crop: string };
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
}

export interface FieldInput {
  ph: string;
  temp: string;
  water: string;
  crop: string;
}
