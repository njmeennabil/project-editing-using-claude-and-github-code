// Colours for the Sarawak map layers, and the matching legend.
// Score: verdict colours. Rain: light to deep blue. Recent rain and soil moisture:
// brown (drier) – grey (normal) – blue (wetter).

export type Rgb = [number, number, number];
export type Ramp = [number, Rgb][];

export const RAIN_RAMP: Ramp = [
  [0, [190, 228, 255]],
  [0.5, [80, 160, 255]],
  [1, [37, 70, 235]],
];

export const DRY_WET_RAMP: Ramp = [
  [0, [205, 120, 40]],
  [0.5, [200, 205, 215]],
  [1, [50, 130, 255]],
];

function mix(a: number, b: number, k: number) {
  return Math.round(a + (b - a) * k);
}

export function rampAt(ramp: Ramp, t: number): Rgb {
  const x = Math.max(0, Math.min(1, t));
  for (let i = 1; i < ramp.length; i++) {
    const [t0, c0] = ramp[i - 1];
    const [t1, c1] = ramp[i];
    if (x <= t1) {
      const k = (x - t0) / (t1 - t0 || 1);
      return [mix(c0[0], c1[0], k), mix(c0[1], c1[1], k), mix(c0[2], c1[2], k)];
    }
  }
  return ramp[ramp.length - 1][1];
}

/** CSS gradient for a legend bar. */
export function rampCss(ramp: Ramp) {
  return `linear-gradient(90deg, ${ramp.map(([t, c]) => `rgb(${c.join(",")}) ${t * 100}%`).join(", ")})`;
}

/** Pixel colour and opacity (0–255) for a grid value scaled to 0–1. */
export function sequential(t: number): [Rgb, number] {
  return [rampAt(RAIN_RAMP, t), Math.round(70 + t * 170)];
}

/** Diverging: stronger the further from normal (0.5). */
export function diverging(t: number): [Rgb, number] {
  return [rampAt(DRY_WET_RAMP, t), Math.round(40 + Math.abs(t - 0.5) * 2 * 200)];
}

/** Verdict bands, the same as Next crop: 80+, 60+, 40+, below 40. */
export const SCORE_BANDS = [
  { min: 80, label: "80–100", name: "Highly recommended", color: "#22c55e", opacity: 0.5 },
  { min: 60, label: "60–79", name: "Recommended", color: "#86efac", opacity: 0.38 },
  { min: 40, label: "40–59", name: "Possible with care", color: "#fbbf24", opacity: 0.42 },
  { min: 0, label: "0–39", name: "Not recommended", color: "#f87171", opacity: 0.48 },
] as const;

export function scoreBand(score: number) {
  return SCORE_BANDS.find((b) => score >= b.min) ?? SCORE_BANDS[SCORE_BANDS.length - 1];
}
