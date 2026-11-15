"use client";

import { useEffect, useRef, useState } from "react";
import { drawScene, SCENES } from "@/lib/hero-scenes";

const SHOW_MS = 8000;

/** The hero's moving background: three drawn scenes that slowly crossfade, with dots to pick one. */
export function HeroSky() {
  const boxRef = useRef<HTMLDivElement>(null);
  const canvases = useRef<(HTMLCanvasElement | null)[]>([]);
  const [active, setActive] = useState(0);
  const [ready, setReady] = useState(false);
  const [paused, setPaused] = useState(false);

  // Draw every scene at the hero's size, and again when the size really changes.
  useEffect(() => {
    const box = boxRef.current;
    if (!box) return;
    let last = { w: 0, h: 0 };
    let timer: ReturnType<typeof setTimeout> | undefined;
    const draw = () => {
      const w = Math.round(box.clientWidth);
      const h = Math.round(box.clientHeight);
      // Phone address bars change the height a little while scrolling; ignore that.
      if (w === last.w && Math.abs(h - last.h) < 80) return;
      last = { w, h };
      SCENES.forEach((s, i) => {
        const c = canvases.current[i];
        if (c) drawScene(c, s.id, w, h);
      });
      setReady(true);
    };
    draw();
    const ro = new ResizeObserver(() => {
      clearTimeout(timer);
      timer = setTimeout(draw, 150);
    });
    ro.observe(box);
    return () => {
      ro.disconnect();
      clearTimeout(timer);
    };
  }, []);

  // Change scene every few seconds while the hero is on screen. No movement for reduced motion.
  useEffect(() => {
    if (paused || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const box = boxRef.current;
    let visible = true;
    const io = new IntersectionObserver(([e]) => (visible = e.isIntersecting));
    if (box) io.observe(box);
    const id = setInterval(() => {
      if (visible && !document.hidden) setActive((a) => (a + 1) % SCENES.length);
    }, SHOW_MS);
    return () => {
      clearInterval(id);
      io.disconnect();
    };
  }, [paused]);

  return (
    <>
      <div ref={boxRef} className="absolute inset-0 overflow-hidden" aria-hidden="true">
        {SCENES.map((s, i) => (
          <canvas
            key={s.id}
            ref={(el) => {
              canvases.current[i] = el;
            }}
            className={`hero-scene absolute inset-0 h-full w-full ${ready && i === active ? "is-on" : ""}`}
          />
        ))}
        {/* Darker on the text side, so white text stays easy to read on every scene. */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(3,6,14,0)_90px,rgba(3,6,14,.45)_190px)] md:bg-[linear-gradient(90deg,rgba(3,6,14,.6),rgba(3,6,14,.08)_62%,rgba(3,6,14,0))]" />
        <div className="absolute inset-x-0 top-0 h-28 bg-[linear-gradient(rgba(3,6,14,.55),transparent)]" />
      </div>

      <div className="absolute bottom-4 right-4 z-10 flex items-center gap-1 md:bottom-6 md:right-8">
        {SCENES.map((s, i) => (
          <button
            key={s.id}
            type="button"
            onClick={() => {
              setActive(i);
              setPaused(true);
            }}
            aria-label={`Show background ${i + 1} of ${SCENES.length}: ${s.name}`}
            aria-pressed={i === active}
            className="group grid h-8 w-8 place-items-center rounded-full focus-visible:outline-white"
          >
            <span
              className={`block h-2 rounded-full transition-all duration-500 ${
                i === active ? "w-6 bg-white" : "w-2 bg-white/45 group-hover:bg-white/80"
              }`}
            />
          </button>
        ))}
      </div>
    </>
  );
}
