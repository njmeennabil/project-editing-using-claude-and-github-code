"use client";

import { useSyncExternalStore } from "react";
import { type TabId, tabFromHash } from "./tabs";

function subscribe(cb: () => void) {
  window.addEventListener("hashchange", cb);
  return () => window.removeEventListener("hashchange", cb);
}

export function useTab(): TabId {
  return useSyncExternalStore(
    subscribe,
    () => tabFromHash(window.location.hash),
    () => "home",
  );
}
