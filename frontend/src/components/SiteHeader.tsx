"use client";

import { useEffect, useState } from "react";
import { BrandMark, Wordmark } from "./BrandMark";
import { NAV_LINKS } from "./nav";


export function SiteHeader() {
  const [open, setOpen] = useState(false);
  // Over the dark hero: see-through at the very top, dark glass once scrolled. Past it: the normal bar.
  const [overHero, setOverHero] = useState(true);
  const [atTop, setAtTop] = useState(true);

  useEffect(() => {
    const hero = document.getElementById("hero");
    if (!hero) return;
    const check = () => {
      setOverHero(hero.getBoundingClientRect().bottom > 65);
      setAtTop(window.scrollY < 8);
    };
    check();
    window.addEventListener("scroll", check, { passive: true });
    window.addEventListener("resize", check);
    return () => {
      window.removeEventListener("scroll", check);
      window.removeEventListener("resize", check);
    };
  }, []);

  const clear = overHero && !open;

  return (
    <header
      className={`sticky top-0 z-50 border-b transition-colors duration-300 ${
        !clear
          ? "border-line bg-surface/90 text-fg backdrop-blur-md"
          : atTop
            ? "border-transparent bg-transparent text-white"
            : "border-white/10 bg-[rgba(5,8,18,.72)] text-white backdrop-blur-md"
      }`}
    >
      <div className="relative mx-auto flex h-16 max-w-[1180px] items-center justify-between gap-4 px-4 md:px-8">
        <a href="#top" className="flex items-center gap-2.5 font-display text-xl font-bold tracking-tight" aria-label="BUMI360 home">
          <BrandMark className="h-[30px] w-[30px]" />
          <Wordmark light={clear} />
        </a>

        <button
          type="button"
          className={`grid h-11 w-11 place-items-center rounded-[10px] border lg:hidden ${
            clear ? "border-white/30 bg-white/10" : "border-line bg-surface"
          }`}
          aria-expanded={open}
          aria-controls="site-nav"
          onClick={() => setOpen((o) => !o)}
        >
          <span className="sr-only">Menu</span>
          <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
          </svg>
        </button>

        <nav
          id="site-nav"
          aria-label="Main"
          className={`${open ? "flex" : "hidden"} absolute inset-x-0 top-full flex-col gap-0.5 border-b border-line bg-surface px-4 pb-3.5 pt-2 shadow-md lg:static lg:flex lg:flex-row lg:gap-1 lg:border-0 lg:bg-transparent lg:p-0 lg:shadow-none`}
        >
          {NAV_LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              className={`whitespace-nowrap rounded-lg px-3 py-3 text-base font-medium text-muted hover:bg-bg-alt hover:text-fg lg:py-2 lg:text-[0.95rem] ${
                clear ? "lg:text-white/85 lg:hover:bg-white/10 lg:hover:text-white" : ""
              }`}
            >
              {l.label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}
