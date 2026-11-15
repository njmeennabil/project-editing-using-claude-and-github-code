"use client";

import { useEffect, useRef } from "react";
import { useTab } from "@/lib/use-tab";

/** Shows the chosen tab (CSS reads html[data-tab]) and starts each tab at the top. */
export function TabSync() {
  const tab = useTab();
  const first = useRef(true);
  useEffect(() => {
    document.documentElement.dataset.tab = tab;
    if (first.current) {
      first.current = false;
      if (tab === "home") return;
    }
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [tab]);
  return null;
}
