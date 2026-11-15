import type { FieldInput, PlanInput } from "./types";

export const DEFAULT_INPUT: FieldInput = {
  mode: "nasa",
  ph: "5.8",
  crop: "all",
  temp: "28",
  water: "600",
  location: "KUCHING",
  lat: "",
  lon: "",
  month: "3",
  irrigation: "0",
};

export const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export const DEFAULT_PLAN: PlanInput = {
  current: "JAGUNG",
  planted: "2026-03-02",
  location: "KUCHING",
  lat: "",
  lon: "",
  ph: "5.8",
  prep_days: "14",
  irrigation: "0",
};
