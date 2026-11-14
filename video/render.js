// Render the BUMI360 promo to MP4: animation (bumi360-promo.html) + screen recording + voice-over.
// Needs Node.js, Playwright (Chromium) and ffmpeg. Run ./prepare.sh first to build assets/.
//   node render.js [output.mp4]
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const path = require("path");

const FPS = 30;
const SECONDS = 43;
const out = path.resolve(process.argv[2] || path.join(__dirname, "bumi360-promo.mp4"));
const assets = path.join(__dirname, "assets");

// The phone screen slides right by 900px from 36.5 s to 37.2 s (same easing as the HTML).
const phoneX =
  "st(0,clip((t-36.5)/0.7,0,1));1124+900*if(lt(ld(0),0.5),4*pow(ld(0),3),1-pow(-2*ld(0)+2,3)/2)";

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.join(__dirname, "bumi360-promo.html"));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);

  const ff = spawn("ffmpeg", [
    "-y", "-loglevel", "error",
    "-f", "lavfi", "-i", `color=c=white:s=1920x1080:r=${FPS}:d=${SECONDS}`,
    "-i", path.join(assets, "screen-track.mp4"),
    "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "png", "-i", "-",
    "-i", path.join(assets, "voiceover.m4a"),
    "-filter_complex",
    `[0:v][1:v]overlay=x='${phoneX}':y=84:eval=frame[base];[base][2:v]overlay=format=auto,format=yuv420p[v]`,
    "-map", "[v]", "-map", "3:a",
    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", String(FPS),
    "-c:a", "aac", "-b:a", "192k", "-t", String(SECONDS), "-movflags", "+faststart", out,
  ], { stdio: ["pipe", "inherit", "inherit"] });

  const total = FPS * SECONDS;
  for (let i = 0; i < total; i++) {
    await page.evaluate((t) => window.renderAt(t), i / FPS);
    const png = await page.screenshot({ type: "png", omitBackground: true });
    if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once("drain", r));
    if (i % 150 === 0) console.log(`frame ${i}/${total}`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  await browser.close();
  console.log("Saved", out);
})();
