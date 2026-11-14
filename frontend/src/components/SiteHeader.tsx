"use client";

import { useState } from "react";
import { BrandMark, Wordmark } from "./BrandMark";
import { NAV_LINKS } from "./nav";


export function SiteHeader() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-surface/90 backdrop-blur-md">
      <div className="relative mx-auto flex h-16 max-w-[1180px] items-center justify-between gap-4 px-4 md:px-8">
        <a href="#top" className="flex items-center gap-2.5 font-display text-xl font-bold tracking-tight text-fg" aria-label="BUMI360 home">
          <BrandMark className="h-[30px] w-[30px]" />
          <Wordmark />
        </a>

        <button
          type="button"
          className="grid h-11 w-11 place-items-center rounded-[10px] border border-line bg-surface md:hidden"
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
          className={`${open ? "flex" : "hidden"} absolute inset-x-0 top-full flex-col gap-0.5 border-b border-line bg-surface px-4 pb-3.5 pt-2 shadow-md md:static md:flex md:flex-row md:gap-1 md:border-0 md:bg-transparent md:p-0 md:shadow-none`}
        >
          {NAV_LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              className="rounded-lg px-3 py-3 text-base font-medium text-muted hover:bg-bg-alt hover:text-fg md:py-2 md:text-[0.95rem]"
            >
              {l.label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}
