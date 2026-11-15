import type { Status } from "@/lib/types";

// Status uses colour and a symbol, so it still reads for colour-blind visitors:
// green ✓ suitable, amber ! with management, red ✕ less suitable.
const SYMBOL: Record<Status, string> = { ok: "✓", warn: "!", bad: "✕", info: "i", none: "–" };

const PILL: Record<Status, string> = {
  ok: "border-ok bg-ok text-[#052e16]",
  warn: "border-warn bg-warn/10 text-warn",
  bad: "border-bad bg-bad/10 text-bad",
  info: "border-line text-muted",
  none: "border-line text-muted",
};

const ICON: Record<Status, string> = {
  ok: "border-ok bg-ok text-[#052e16]",
  warn: "border-warn bg-warn/15 text-warn",
  bad: "border-bad bg-bad/15 text-bad",
  info: "border-muted text-muted font-serif italic",
  none: "border-muted text-muted",
};

/** Colour for a status, for bars, meters and edges. */
export const STATUS_COLOR: Record<Status, string> = {
  ok: "var(--ok)",
  warn: "var(--warn)",
  bad: "var(--bad)",
  info: "var(--fg)",
  none: "var(--fg)",
};

export function StatusPill({ status, children }: { status: Status; children: React.ReactNode }) {
  return (
    <span className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border-[1.5px] px-2.5 py-1 text-[0.8rem] font-semibold ${PILL[status]}`}>
      <span aria-hidden="true" className="text-[0.8em] leading-none">{SYMBOL[status]}</span>
      {children}
    </span>
  );
}

export function StatusIcon({ status }: { status: Status }) {
  return (
    <span
      aria-hidden="true"
      className={`inline-grid h-[18px] w-[18px] flex-none place-items-center rounded-full border-[1.5px] text-[0.68rem] font-bold leading-none ${ICON[status]}`}
    >
      {SYMBOL[status]}
    </span>
  );
}
