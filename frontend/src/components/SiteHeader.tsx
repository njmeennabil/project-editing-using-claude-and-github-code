"use client";

import { useEffect, useRef, useState } from "react";
import { TABS } from "@/lib/tabs";
import { useTab } from "@/lib/use-tab";
import { BrandMark, Wordmark } from "./BrandMark";
import { TabIcon } from "./TabIcon";

export function SiteHeader() {
  const tab = useTab();
  const [open, setOpen] = useState(false);
  const [atTop, setAtTop] = useState(true);
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const check = () => setAtTop(window.scrollY < 8);
    check();
    window.addEventListener("scroll", check, { passive: true });
    return () => window.removeEventListener("scroll", check);
  }, []);

  // Close the menu with Escape or a tap outside it.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setOpen(false);
        buttonRef.current?.focus();
      }
    };
    const onDown = (e: PointerEvent) => {
      const t = e.target as Node;
      if (!menuRef.current?.contains(t) && !buttonRef.current?.contains(t)) setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onDown);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onDown);
    };
  }, [open]);

  // See-through only at the very top of the home page, over the hero.
  const clear = tab === "home" && atTop && !open;
  const current = TABS.find((t) => t.id === tab);

  return (
    <header
      className={`sticky top-0 z-50 border-b text-white transition-colors duration-300 ${
        clear ? "border-transparent bg-transparent" : "border-white/10 bg-[rgba(6,10,24,.78)] backdrop-blur-md"
      }`}
    >
      <div className="relative mx-auto flex h-16 max-w-[1180px] items-center justify-between gap-4 px-4 md:px-8">
        <a href="#top" className="flex items-center gap-2.5 font-display text-xl font-bold tracking-tight" aria-label="BUMI360 home">
          <BrandMark className="h-[30px] w-[30px]" />
          <Wordmark light />
        </a>

        <div className="flex items-center gap-3">
          {current && (
            <span className="hidden items-center gap-2 rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-sm font-medium text-white/85 sm:inline-flex">
              <TabIcon id={current.id} className="h-4 w-4" />
              {current.label}
            </span>
          )}
          <button
            ref={buttonRef}
            type="button"
            className={`grid h-11 w-11 place-items-center rounded-full border transition-colors ${
              open ? "border-white/50 bg-white/15" : "border-white/25 bg-white/5 hover:bg-white/10"
            }`}
            aria-expanded={open}
            aria-controls="site-menu"
            onClick={() => setOpen((o) => !o)}
          >
            <span className="sr-only">Menu</span>
            {open ? (
              <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden="true" fill="currentColor">
                <circle cx="12" cy="5" r="2" />
                <circle cx="12" cy="12" r="2" />
                <circle cx="12" cy="19" r="2" />
              </svg>
            )}
          </button>
        </div>

        {open && (
          <div
            ref={menuRef}
            id="site-menu"
            className="menu-pop absolute right-4 top-[calc(100%+8px)] w-[min(320px,calc(100vw-32px))] overflow-hidden rounded-[16px] border border-white/15 bg-[rgba(10,16,36,.94)] p-2 shadow-[0_20px_60px_rgba(0,0,0,.55)] backdrop-blur-xl md:right-8"
          >
            <nav aria-label="Main">
              <a
                href="#top"
                onClick={() => setOpen(false)}
                aria-current={tab === "home" ? "page" : undefined}
                className={`menu-item ${tab === "home" ? "is-on" : ""}`}
              >
                <TabIcon id="home" className="h-[18px] w-[18px]" />
                <span>Home</span>
              </a>
              <div className="mx-3 my-1.5 h-px bg-white/10" />
              {TABS.map((t, i) => (
                <a
                  key={t.id}
                  href={`#${t.id}`}
                  onClick={() => setOpen(false)}
                  aria-current={tab === t.id ? "page" : undefined}
                  className={`menu-item ${tab === t.id ? "is-on" : ""}`}
                >
                  <TabIcon id={t.id} className="h-[18px] w-[18px]" />
                  <span>{t.label}</span>
                  <span className="ml-auto font-mono text-[0.72rem] text-white/35">0{i + 1}</span>
                </a>
              ))}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
