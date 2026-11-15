import type { TabId } from "@/lib/tabs";

/** Small line icons for the menu and tab pages. */
const PATHS: Record<TabId, React.ReactNode> = {
  home: <path d="M4 11l8-7 8 7M6 9.5V20h12V9.5" />,
  check: (
    <>
      <path d="M12 20v-7" />
      <path d="M12 13c0-4 2.5-6.5 6.5-7-.5 4-3 6.5-6.5 7z" />
      <path d="M12 15c0-3-2-5-5.5-5.5.3 3.2 2.2 5.2 5.5 5.5z" />
      <path d="M5 20h14" />
    </>
  ),
  plan: (
    <>
      <rect x="4" y="5" width="16" height="15" rx="2" />
      <path d="M4 10h16M9 3v4M15 3v4" />
      <path d="M9.5 15l2 2 3.5-4" />
    </>
  ),
  map: (
    <>
      <path d="M9 4L3 6.5v13.5L9 17.5l6 2.5 6-2.5V4l-6 2.5z" />
      <path d="M9 4v13.5M15 6.5V20" />
    </>
  ),
  crops: (
    <>
      <path d="M5 4h11a3 3 0 013 3v13H8a3 3 0 01-3-3z" />
      <path d="M5 17a3 3 0 013-3h11" />
    </>
  ),
  compare: (
    <>
      <path d="M8 4v16M16 4v16" />
      <path d="M4 8h8M12 16h8" />
    </>
  ),
  rotation: (
    <>
      <path d="M20 12a8 8 0 01-13.7 5.6" />
      <path d="M4 12a8 8 0 0113.7-5.6" />
      <path d="M17.7 2.5v4h-4M6.3 21.5v-4h4" />
    </>
  ),
  about: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 11v5.5" />
      <circle cx="12" cy="7.8" r=".6" fill="currentColor" />
    </>
  ),
};

export function TabIcon({ id, className = "" }: { id: TabId; className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      {PATHS[id]}
    </svg>
  );
}
