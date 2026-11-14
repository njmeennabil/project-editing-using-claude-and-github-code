import type { Status } from "@/lib/types";

// Black-and-white status: shown by shape and symbol, never by colour alone.
const SYMBOL: Record<Status, string> = { ok: "✓", warn: "!", bad: "✕", info: "i", none: "–" };

export function StatusPill({ status, children }: { status: Status; children: React.ReactNode }) {
  const style =
    status === "ok"
      ? "border-fg bg-fg text-bg"
      : status === "warn"
        ? "border-fg text-fg"
        : status === "bad"
          ? "border-dashed border-fg text-fg"
          : "border-line text-muted";
  return (
    <span className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border-[1.5px] px-2.5 py-1 text-[0.8rem] font-semibold ${style}`}>
      <span aria-hidden="true" className="text-[0.8em] leading-none">{SYMBOL[status]}</span>
      {children}
    </span>
  );
}

export function StatusIcon({ status }: { status: Status }) {
  const style =
    status === "ok"
      ? "border-fg bg-fg text-bg"
      : status === "bad"
        ? "border-dashed border-fg text-fg"
        : status === "warn"
          ? "border-fg text-fg"
          : "border-muted text-muted";
  return (
    <span
      aria-hidden="true"
      className={`inline-grid h-[18px] w-[18px] flex-none place-items-center rounded-full border-[1.5px] text-[0.68rem] font-bold leading-none ${style} ${status === "info" ? "font-serif italic" : ""}`}
    >
      {SYMBOL[status]}
    </span>
  );
}
