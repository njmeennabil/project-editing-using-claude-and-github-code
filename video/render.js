// Render the BUMI360 promo to MP4: animation (bumi360-promo.html) + screen recording + audio.
// Needs Node.js, Playwright (Chromium) and ffmpeg.
//   node render.js            43-s version with the full voice-over   (run ./prepare.sh first)
//   node render.js --cut30    30-s version with sound effects        (run make30.py first)
// An output path can be given as the last argument.
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const FPS = 30;
const assets = path.join(__dirname, "assets");
const cut30 = process.argv.includes("--cut30");
const outArg = process.argv.slice(2).find((a) => !a.startsWith("--"));

const cfg = cut30 ? JSON.parse(fs.readFileSync(path.join(assets, "cut30.json"), "utf8")) : null;
const SECONDS = cut30 ? cfg.duration : 43;
const [slideA, slideB] = cut30 ? cfg.slide : [36.5, 37.2];
const screen = path.join(assets, cut30 ? "screen-track-30.mp4" : "screen-track.mp4");
const audio = path.join(assets, cut30 ? "audio-30.m4a" : "voiceover.m4a");
const out = path.resolve(outArg || path.join(__dirname, cut30 ? "bumi360-promo-30s.mp4" : "bumi360-promo.mp4"));

// The phone screen slides right by 900px at the end (same easing as the HTML).
const phoneX = `st(0,clip((t-${slideA})/${(slideB - slideA).toFixed(4)},0,1));` +
  "1124+900*if(lt(ld(0),0.5),4*pow(ld(0),3),1-pow(-2*ld(0)+2,3)/2)";

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.join(__dirname, "bumi360-promo.html"));
  await page.evaluate(() => document.fonts.ready);
  if (cut30) await page.evaluate((c) => { window.CUT = c; }, cfg);
  await page.waitForTimeout(800);

  const ff = spawn("ffmpeg", [
    "-y", "-loglevel", "error",
    "-f", "lavfi", "-i", `color=c=white:s=1920x1080:r=${FPS}:d=${SECONDS}`,
    "-i", screen,
    "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "png", "-i", "-",
    "-i", audio,
    "-filter_complex",
    `[0:v][1:v]overlay=x='${phoneX}':y=84:eval=frame[base];[base][2:v]overlay=format=auto,format=yuv420p[v]`,
    "-map", "[v]", "-map", "3:a",
    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", String(FPS),
    "-c:a", "aac", "-b:a", "192k", "-t", String(SECONDS), "-movflags", "+faststart", out,
  ], { stdio: ["pipe", "inherit", "inherit"] });

  const total = Math.round(FPS * SECONDS);
  for (let i = 0; i < total; i++) {
    const t = i / FPS;
    await page.evaluate(([t, c]) => (c ? window.renderCut(t) : window.renderAt(t)), [t, cut30]);
    const png = await page.screenshot({ type: "png", omitBackground: true });
    if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once("drain", r));
    if (i % 150 === 0) console.log(`frame ${i}/${total}`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  await browser.close();
  console.log("Saved", out);
})();
