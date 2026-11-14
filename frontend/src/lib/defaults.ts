import type { FieldInput } from "./types";

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
