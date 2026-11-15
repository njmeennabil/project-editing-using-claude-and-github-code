// One tab is shown at a time. The tab lives in the address (#check, #map…), so the
// back button, shared links and the hero cards all work.

export const TABS = [
  { id: "check", label: "Field check" },
  { id: "plan", label: "Next crop" },
  { id: "map", label: "Map" },
  { id: "crops", label: "Crop guide" },
  { id: "compare", label: "Compare" },
  { id: "rotation", label: "Rotation" },
  { id: "about", label: "About" },
] as const;

export type TabId = (typeof TABS)[number]["id"] | "home";

const IDS = new Set<string>(TABS.map((t) => t.id));

export function tabFromHash(hash: string): TabId {
  const id = hash.replace(/^#/, "");
  return IDS.has(id) ? (id as TabId) : "home";
}

/** Open a tab (adds a step to the browser history, like following a link). */
export function goToTab(id: TabId) {
  const hash = id === "home" ? "#top" : `#${id}`;
  if (window.location.hash === hash) window.scrollTo(0, 0);
  else window.location.hash = hash;
}

/**
 * Runs before the page is painted, so opening a link like /#map shows the map
 * straight away instead of flashing the home page first.
 */
export const TAB_BOOT_SCRIPT = `(function(){var h=location.hash.slice(1);var ids=${JSON.stringify(TABS.map((t) => t.id))};document.documentElement.dataset.tab=ids.indexOf(h)>-1?h:"home";})();`;
