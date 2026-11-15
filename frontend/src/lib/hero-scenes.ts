// Hero background scenes, drawn on a canvas. All artwork is drawn here in code:
// no photos, no satellite imagery and no outside images.

type Ctx = CanvasRenderingContext2D;

export const SCENES = [
  { id: "orbit", name: "Dawn orbit" },
  { id: "dusk", name: "Farm at dusk" },
  { id: "farmland", name: "Satellite over farmland" },
] as const;

export type SceneId = (typeof SCENES)[number]["id"];

/** On phones the satellite sits in the strip of sky between the header and the headline. */
const SKY_Y = 112;

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

/** Same numbers every time, so a scene looks the same on every visit and resize. */
function rng(seed: number) {
  let s = seed;
  return () => (s = (s * 16807) % 2147483647) / 2147483647;
}

function vgrad(x: Ctx, y0: number, y1: number, stops: [number, string][]) {
  const g = x.createLinearGradient(0, y0, 0, y1);
  stops.forEach(([o, c]) => g.addColorStop(o, c));
  return g;
}

function stars(x: Ctx, rnd: () => number, W: number, maxY: number, n: number, alpha = 1) {
  x.fillStyle = "#fff";
  for (let i = 0; i < n; i++) {
    const sx = rnd() * W;
    const sy = rnd() * maxY;
    const r = rnd() * 1.3 + 0.2;
    x.globalAlpha = alpha * (0.3 + rnd() * 0.7) * (1 - (sy / maxY) * 0.7);
    x.beginPath();
    x.arc(sx, sy, r, 0, Math.PI * 2);
    x.fill();
  }
  x.globalAlpha = 1;
}

/** A satellite: gold body, sensor box, dish and two blue solar wings. */
function satellite(x: Ctx, cx: number, cy: number, s: number, rot: number) {
  x.save();
  x.translate(cx, cy);
  x.rotate(rot);
  x.scale(s, s);
  for (const dir of [1, -1]) {
    x.save();
    x.translate(dir * 70, 0);
    x.fillStyle = "#2a3346";
    x.fillRect(dir > 0 ? 0 : -16, -6, 16, 12);
    for (let k = 0; k < 3; k++) {
      const px = dir > 0 ? 16 + k * 116 : -128 - k * 116;
      const g = x.createLinearGradient(px, -46, px + 112, 46);
      g.addColorStop(0, "#1b2a55");
      g.addColorStop(0.5, "#2f4a8c");
      g.addColorStop(1, "#14213f");
      x.fillStyle = g;
      x.fillRect(px, -46, 112, 92);
      x.strokeStyle = "rgba(190,205,255,.55)";
      x.lineWidth = 1.2;
      for (let gx = 0; gx <= 4; gx++) {
        x.beginPath();
        x.moveTo(px + gx * 28, -46);
        x.lineTo(px + gx * 28, 46);
        x.stroke();
      }
      for (let gy = 0; gy <= 3; gy++) {
        x.beginPath();
        x.moveTo(px, -46 + gy * 30.67);
        x.lineTo(px + 112, -46 + gy * 30.67);
        x.stroke();
      }
      x.strokeStyle = "rgba(220,225,240,.9)";
      x.lineWidth = 2;
      x.strokeRect(px, -46, 112, 92);
    }
    x.restore();
  }
  const g = x.createLinearGradient(-70, -60, 70, 60);
  g.addColorStop(0, "#f6d58a");
  g.addColorStop(0.35, "#b98a34");
  g.addColorStop(0.6, "#e9c46c");
  g.addColorStop(1, "#7a5520");
  x.fillStyle = g;
  x.fillRect(-70, -62, 140, 124);
  x.strokeStyle = "rgba(255,240,200,.6)";
  x.lineWidth = 1;
  for (let k = -60; k < 62; k += 14) {
    x.beginPath();
    x.moveTo(-70, k);
    x.lineTo(70, k + 8);
    x.stroke();
  }
  x.fillStyle = "#d9dce4";
  x.fillRect(-36, -92, 72, 30);
  x.fillStyle = "#eef0f5";
  x.beginPath();
  x.ellipse(0, 70, 34, 12, 0, 0, Math.PI * 2);
  x.fill();
  x.fillStyle = "#9aa1ad";
  x.fillRect(-4, 58, 8, 14);
  x.restore();
}

const FIELD_COLOURS = ["#6b8a3a", "#a49a4a", "#3f6b34", "#c2a65a", "#2f5530", "#8fae4c"];
const FARM_COLOURS = ["#5f8f3c", "#9c9d4f", "#3d7036", "#b8a35c", "#2e5c33", "#82a84e", "#6e7f3a"];

/** A: space at sunrise, the glowing edge of the Earth with farmland, a satellite beaming down. */
function orbit(x: Ctx, W: number, H: number) {
  const rnd = rng(7);
  const k = clamp(W / 1440, 0.4, 1.3);
  const narrow = W < 760;
  x.fillStyle = vgrad(x, 0, H, [[0, "#03050c"], [0.45, "#0a1530"], [0.62, "#1d2a52"], [0.72, "#5b3b5e"], [0.8, "#d0784a"]]);
  x.fillRect(0, 0, W, H);
  stars(x, rnd, W, H * 0.62, Math.round((420 * W) / 1440));

  const ex = W / 2;
  const er = Math.max(H * 1.62, W * 0.9);
  const ey = H * 0.73 + er;
  const glow = x.createRadialGradient(ex, ey, er * 0.98, ex, ey, er * 1.06);
  glow.addColorStop(0, "rgba(255,170,90,.9)");
  glow.addColorStop(0.35, "rgba(255,120,80,.45)");
  glow.addColorStop(0.7, "rgba(90,170,255,.25)");
  glow.addColorStop(1, "rgba(0,0,0,0)");
  x.fillStyle = glow;
  x.beginPath();
  x.arc(ex, ey, er * 1.06, 0, Math.PI * 2);
  x.fill();

  x.save();
  x.beginPath();
  x.arc(ex, ey, er, 0, Math.PI * 2);
  x.clip();
  x.fillStyle = vgrad(x, ey - er, H, [[0, "#2b3b2a"], [0.05, "#1f3a26"], [0.3, "#0d1d14"]]);
  x.fillRect(0, 0, W, H);
  const top = ey - er;
  const n = Math.round((380 * W) / 1440);
  for (let i = 0; i < n; i++) {
    const fx = rnd() * W;
    const fy = top + 6 + Math.pow(rnd(), 1.6) * (H - top);
    const w = (10 + rnd() * 40 * (1 + (fy - top) / 120)) * k;
    x.fillStyle = FIELD_COLOURS[Math.floor(rnd() * FIELD_COLOURS.length)];
    x.globalAlpha = 0.35 + rnd() * 0.4;
    x.fillRect(fx, fy, w, w * (0.18 + rnd() * 0.2));
  }
  x.globalAlpha = 1;
  x.restore();

  x.strokeStyle = "rgba(255,214,150,.9)";
  x.lineWidth = 2.5;
  x.beginPath();
  x.arc(ex, ey, er, Math.PI * 1.1, Math.PI * 1.9);
  x.stroke();

  const sx = narrow ? W * 0.72 : W * 0.8;
  const sy = narrow ? SKY_Y : H * 0.255;
  x.globalAlpha = 0.18;
  x.fillStyle = "#9fd0ff";
  x.beginPath();
  x.moveTo(sx - 20 * k, sy + 20 * k);
  x.lineTo(sx - 330 * k, H);
  x.lineTo(sx + 90 * k, H);
  x.closePath();
  x.fill();
  x.globalAlpha = 1;
  satellite(x, sx, sy, narrow ? 0.19 : 0.62 * k, -0.35);
}

/** B: dusk sky gradient over rows of crops, hills, a farm hut and palms. */
function dusk(x: Ctx, W: number, H: number) {
  const rnd = rng(11);
  const k = clamp(W / 1440, 0.45, 1.3);
  const narrow = W < 760;
  x.fillStyle = vgrad(x, 0, H, [[0, "#0b1230"], [0.35, "#2a2d5c"], [0.55, "#7a5277"], [0.66, "#d98a6a"], [0.7, "#f2b27c"]]);
  x.fillRect(0, 0, W, H);
  stars(x, rnd, W, H * 0.4, Math.round((220 * W) / 1440), 0.9);

  const sy = narrow ? SKY_Y : H * 0.125;
  x.strokeStyle = "rgba(255,255,255,.55)";
  x.lineWidth = 1.4;
  x.setLineDash([2, 7]);
  x.beginPath();
  x.moveTo(W * 0.5, sy + 10 * k);
  x.quadraticCurveTo(W * 0.76, sy - 45 * k, W * 1.02, sy + 40 * k);
  x.stroke();
  x.setLineDash([]);
  satellite(x, narrow ? W * 0.7 : W * 0.845, sy, narrow ? 0.16 : 0.26 * k, 0.12);

  const hy = H * 0.667;
  x.fillStyle = "#3c3155";
  x.beginPath();
  x.moveTo(0, hy);
  for (let px = 0; px <= W + 30; px += 30) x.lineTo(px, hy - (40 + Math.sin(px / 160) * 26 + Math.sin(px / 57) * 9) * k);
  x.lineTo(W, hy);
  x.closePath();
  x.fill();
  x.fillStyle = "#2a2340";
  x.beginPath();
  x.moveTo(0, hy);
  for (let px = 0; px <= W + 30; px += 30) x.lineTo(px, hy - (14 + Math.sin(px / 95 + 2) * 12) * k);
  x.lineTo(W, hy);
  x.closePath();
  x.fill();

  // Rows of crops running to a point on the horizon.
  const vx = W * 0.68;
  const spread = 120 * k;
  const rows = Math.ceil(W / spread) + 4;
  for (let i = -rows; i < rows; i++) {
    x.fillStyle = i % 2 ? "#1d2b1f" : "#28402a";
    x.beginPath();
    x.moveTo(vx + i * 6, hy);
    x.lineTo(vx + (i + 1) * 6, hy);
    x.lineTo(vx + (i + 1) * spread, H);
    x.lineTo(vx + i * spread, H);
    x.closePath();
    x.fill();
  }
  x.globalAlpha = 0.35;
  x.fillStyle = vgrad(x, hy, H, [[0, "#f2b27c"], [0.25, "rgba(242,178,124,0)"]]);
  x.fillRect(0, hy, W, H - hy);
  x.globalAlpha = 1;

  // Farm hut on stilts.
  x.fillStyle = "#0f1410";
  const hx = W * 0.868;
  const hb = hy - 15 * k;
  x.beginPath();
  x.moveTo(hx - 70 * k, hb);
  x.lineTo(hx, hb - 45 * k);
  x.lineTo(hx + 70 * k, hb);
  x.closePath();
  x.fill();
  x.fillRect(hx - 58 * k, hb - 1, 116 * k, 32 * k);
  x.fillRect(hx - 54 * k, hb + 30 * k, 6 * k, 22 * k);
  x.fillRect(hx + 48 * k, hb + 30 * k, 6 * k, 22 * k);

  const palm = (px: number, py: number, s: number) => {
    x.strokeStyle = "#0f1410";
    x.lineCap = "round";
    x.lineWidth = 5 * s;
    x.beginPath();
    x.moveTo(px, py);
    x.quadraticCurveTo(px + 12 * s, py - 90 * s, px + 4 * s, py - 170 * s);
    x.stroke();
    for (let j = 0; j < 7; j++) {
      const a = -Math.PI / 2 + (j - 3) * 0.5;
      x.lineWidth = 4 * s;
      x.beginPath();
      x.moveTo(px + 4 * s, py - 170 * s);
      x.quadraticCurveTo(
        px + 4 * s + Math.cos(a) * 50 * s,
        py - 190 * s + Math.sin(a) * 20 * s,
        px + 4 * s + Math.cos(a) * 85 * s,
        py - 150 * s + Math.abs(Math.sin(a)) * 10 * s,
      );
      x.stroke();
    }
  };
  palm(W * 0.944, hy, k);
  palm(W * 0.976, hy + 5 * k, 0.8 * k);
  palm(W * 0.757, hy, 0.7 * k);
}

/** C: a satellite close up over a green patchwork of farms, clouds and a blue atmosphere. */
function farmland(x: Ctx, W: number, H: number) {
  const rnd = rng(23);
  const k = clamp(W / 1440, 0.4, 1.3);
  const narrow = W < 760;
  x.fillStyle = vgrad(x, 0, H, [[0, "#02040a"], [0.2, "#061024"], [0.42, "#0f2a52"]]);
  x.fillRect(0, 0, W, H);
  stars(x, rnd, W, H * 0.3, Math.round((260 * W) / 1440));

  const ex = W * 0.38;
  const er = Math.max(H * 1.72, W * 1.1);
  const ey = H * 0.33 + er;
  const top = ey - er;
  const at = x.createRadialGradient(ex, ey, er * 0.99, ex, ey, er * 1.07);
  at.addColorStop(0, "rgba(120,200,255,.95)");
  at.addColorStop(0.4, "rgba(60,130,230,.45)");
  at.addColorStop(1, "rgba(0,0,0,0)");
  x.fillStyle = at;
  x.beginPath();
  x.arc(ex, ey, er * 1.07, 0, Math.PI * 2);
  x.fill();

  x.save();
  x.beginPath();
  x.arc(ex, ey, er, 0, Math.PI * 2);
  x.clip();
  x.fillStyle = vgrad(x, top, H, [[0, "#1f4f7a"], [0.12, "#2a5f3f"], [0.4, "#1f4a2c"]]);
  x.fillRect(0, 0, W, H);
  const depth = H - top;
  const n = Math.round((1400 * W * depth) / (1440 * 600));
  for (let i = 0; i < n; i++) {
    const fx = rnd() * W;
    const fy = top + 30 * k + rnd() * depth;
    const d = (fy - top) / depth;
    const w = (6 + rnd() * 34 * (0.4 + d * 2)) * k;
    x.fillStyle = FARM_COLOURS[Math.floor(rnd() * FARM_COLOURS.length)];
    x.globalAlpha = 0.45 + rnd() * 0.45;
    x.save();
    x.translate(fx, fy);
    x.rotate((rnd() - 0.5) * 0.3);
    x.fillRect(0, 0, w, w * (0.35 + rnd() * 0.4));
    x.restore();
  }
  x.globalAlpha = 1;
  const clouds = Math.round((40 * W * depth) / (1440 * 600));
  for (let i = 0; i < clouds; i++) {
    const cx = rnd() * W;
    const cy = top + 20 * k + rnd() * depth;
    const r = (40 + rnd() * 140) * k;
    const cg = x.createRadialGradient(cx, cy, 0, cx, cy, r);
    cg.addColorStop(0, "rgba(255,255,255,.75)");
    cg.addColorStop(1, "rgba(255,255,255,0)");
    x.fillStyle = cg;
    x.beginPath();
    x.ellipse(cx, cy, r * 1.8, r * 0.6, -0.1, 0, Math.PI * 2);
    x.fill();
  }
  x.fillStyle = vgrad(x, top, top + 220 * k, [[0, "rgba(120,190,255,.45)"], [1, "rgba(120,190,255,0)"]]);
  x.fillRect(0, 0, W, H);
  x.restore();

  x.fillStyle = "rgba(2,6,14,.35)";
  x.fillRect(0, 0, W, H);
  satellite(x, narrow ? W * 0.72 : W * 0.845, narrow ? SKY_Y : H * 0.24, narrow ? 0.19 : 0.72 * k, -0.42);
}

const DRAW: Record<SceneId, (x: Ctx, W: number, H: number) => void> = { orbit, dusk, farmland };

/** Draws a scene to fill the canvas at its CSS size, sharp on high-density screens. */
export function drawScene(canvas: HTMLCanvasElement, id: SceneId, W: number, H: number) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.round(W * dpr);
  canvas.height = Math.round(H * dpr);
  const x = canvas.getContext("2d");
  if (!x) return;
  x.setTransform(dpr, 0, 0, dpr, 0, 0);
  DRAW[id](x, W, H);
}
