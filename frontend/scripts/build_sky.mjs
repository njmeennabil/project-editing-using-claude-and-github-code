// Builds the night-sky drawings behind each tab (public/sky/*.svg).
// Run from frontend/: node scripts/build_sky.mjs
import { writeFileSync } from "node:fs";

let seed = 5;
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const INK = "rgba(170,200,255,.42)";
const svg = (inner, w = 1440, h = 900, extra = "") =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}"${extra}>${inner}</svg>\n`;

const files = {};

// A 600×600 tile of small stars, repeated across every tab.
let stars = "";
for (let i = 0; i < 70; i++) {
  stars += `<circle cx="${(rnd() * 600).toFixed(1)}" cy="${(rnd() * 600).toFixed(1)}" r="${(rnd() * 0.9 + 0.25).toFixed(2)}" fill="#fff" opacity="${(0.2 + rnd() * 0.6).toFixed(2)}"/>`;
}
files["stars.svg"] = svg(stars, 600, 600);

// Field check: rows of crops running to the horizon (bottom of the tab).
{
  let s = "";
  const vx = 1080, hy = 640;
  for (let i = -14; i <= 14; i++) s += `<line x1="${vx + i * 4}" y1="${hy}" x2="${vx + i * 150}" y2="900" stroke="${INK}" stroke-width="1.4" opacity=".55"/>`;
  s += `<path d="M0 ${hy} Q 360 ${hy - 40} 720 ${hy - 10} T 1440 ${hy - 20}" fill="none" stroke="${INK}" stroke-width="1.6" opacity=".7"/>`;
  files["check.svg"] = svg(s);
}

// Next crop: dotted orbits around a planet, with a small satellite.
files["plan.svg"] = svg(
  `<g fill="none" stroke="${INK}" stroke-width="1.4" stroke-dasharray="3 8" opacity=".8"><ellipse cx="1180" cy="210" rx="420" ry="120" transform="rotate(-12 1180 210)"/><ellipse cx="1180" cy="210" rx="300" ry="80" transform="rotate(-12 1180 210)"/></g>` +
    `<circle cx="1180" cy="210" r="34" fill="none" stroke="${INK}" stroke-width="1.6" opacity=".8"/>` +
    `<g transform="translate(800 250) rotate(-12)" fill="${INK}" opacity=".9"><rect x="-6" y="-5" width="12" height="10"/><rect x="-30" y="-3" width="22" height="6"/><rect x="8" y="-3" width="22" height="6"/></g>`,
);

// Map: curved lines of latitude and longitude across the whole tab.
{
  let s = "";
  for (let i = 0; i < 11; i++) s += `<path d="M ${-100 + i * 165} 0 Q ${-40 + i * 165} 450 ${-100 + i * 165} 900" fill="none" stroke="${INK}" stroke-width="1" opacity=".45" vector-effect="non-scaling-stroke"/>`;
  for (let j = 0; j < 7; j++) s += `<path d="M 0 ${60 + j * 130} Q 720 ${20 + j * 130} 1440 ${60 + j * 130}" fill="none" stroke="${INK}" stroke-width="1" opacity=".45" vector-effect="non-scaling-stroke"/>`;
  files["map.svg"] = svg(s, 1440, 900, ' preserveAspectRatio="none"');
}

// Crop guide: leaves.
{
  const leaf = (x, y, r, k) =>
    `<g transform="translate(${x} ${y}) rotate(${r}) scale(${k})" fill="none" stroke="${INK}" stroke-width="1.6"><path d="M0 0 C 40 -60 120 -70 170 -40 C 120 -10 50 10 0 0 Z"/><path d="M0 0 C 60 -25 110 -35 170 -40"/></g>`;
  files["crops.svg"] = svg(`<g opacity=".8">${leaf(1240, 160, -30, 1.4)}${leaf(1300, 260, 10, 1)}${leaf(1180, 300, -70, 0.8)}${leaf(60, 820, -40, 1.2)}${leaf(120, 880, -5, 0.9)}</g>`);
}

// Compare: a constellation.
{
  const pts = [[1040, 120], [1150, 190], [1260, 150], [1330, 260], [1210, 320], [1110, 280]];
  let s = '<g opacity=".85">';
  for (let i = 0; i < pts.length - 1; i++) s += `<line x1="${pts[i][0]}" y1="${pts[i][1]}" x2="${pts[i + 1][0]}" y2="${pts[i + 1][1]}" stroke="${INK}" stroke-width="1.2"/>`;
  pts.forEach((p) => (s += `<circle cx="${p[0]}" cy="${p[1]}" r="4" fill="${INK}"/>`));
  files["compare.svg"] = svg(s + "</g>");
}

// Rotation: a cycle of arrows.
{
  let s = `<g fill="none" stroke="${INK}" stroke-width="1.6" opacity=".75"><circle cx="1220" cy="230" r="170" stroke-dasharray="190 77"/><circle cx="1220" cy="230" r="120" opacity=".5"/></g>`;
  for (let k = 0; k < 4; k++) {
    const a = (k * Math.PI) / 2 - 0.35, x = 1220 + 170 * Math.cos(a), y = 230 + 170 * Math.sin(a);
    s += `<path d="M -9 -7 L 4 0 L -9 7" fill="none" stroke="${INK}" stroke-width="2" opacity=".9" transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${((a * 180) / Math.PI + 90).toFixed(1)})"/>`;
  }
  files["rotation.svg"] = svg(s);
}

// About: a satellite (top) over the glowing edge of the Earth (bottom).
files["about.svg"] = svg(
  `<g transform="translate(1180 190) rotate(-20)" fill="${INK}" opacity=".95"><rect x="-14" y="-12" width="28" height="24"/><rect x="-80" y="-9" width="60" height="18"/><rect x="20" y="-9" width="60" height="18"/></g>` +
    `<path d="M 1180 210 L 1040 900 L 1320 900 Z" fill="${INK}" opacity=".12"/>`,
);
files["earth.svg"] = svg(
  `<defs><radialGradient id="g" cx="50%" cy="100%" r="80%"><stop offset="0" stop-color="#1c3b2a"/><stop offset=".6" stop-color="#0d2018"/></radialGradient></defs>` +
    `<circle cx="720" cy="2400" r="1640" fill="none" stroke="rgba(120,180,255,.10)" stroke-width="70"/><circle cx="720" cy="2400" r="1615" fill="none" stroke="rgba(120,180,255,.18)" stroke-width="22"/>` +
    `<circle cx="720" cy="2400" r="1600" fill="url(#g)"/>` +
    `<circle cx="720" cy="2400" r="1600" fill="none" stroke="rgba(255,190,120,.7)" stroke-width="3"/>`,
);

for (const [name, body] of Object.entries(files)) writeFileSync(new URL(`../public/sky/${name}`, import.meta.url), body);
console.log("Wrote", Object.keys(files).join(", "));
