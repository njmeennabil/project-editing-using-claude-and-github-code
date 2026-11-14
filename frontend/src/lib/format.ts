import type { Crop } from "./types";

export function num(n: number | null | undefined): string {
  if (n == null) return "–";
  return String(Math.round(n * 100) / 100);
}

export function range(lo: number | null, hi: number | null): string {
  if (lo == null && hi == null) return "–";
  if (lo == null) return `≤ ${num(hi)}`;
  if (hi == null) return `≥ ${num(lo)}`;
  return lo === hi ? num(lo) : `${num(lo)}–${num(hi)}`;
}

export const phRange = (c: Crop) => `${c.soil.ph_min.toFixed(1)}–${c.soil.ph_max.toFixed(1)}`;

export function maturity(c: Crop): string {
  if (c.maturity_min_days == null) return "No data";
  return c.maturity_min_days === c.maturity_max_days
    ? `~${c.maturity_min_days} days`
    : `${range(c.maturity_min_days, c.maturity_max_days)} days`;
}

export const waterText = (c: Crop) => (c.water_min_mm == null ? "Keep moist" : `${range(c.water_min_mm, c.water_max_mm)} mm`);
