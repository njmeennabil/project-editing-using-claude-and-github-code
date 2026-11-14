import type { CropResult } from "@/lib/types";
import { Meter } from "./Meter";
import { StatusIcon, StatusPill } from "./Status";

export function ResultCard({ result, onViewGuide }: { result: CropResult; onViewGuide: (code: string) => void }) {
  return (
    <article className="grid min-w-0 gap-3.5 rounded-[14px] border border-line bg-surface px-5 py-[18px]">
      <div className="flex flex-wrap items-start justify-between gap-2.5">
        <div>
          <h4 className="font-display text-xl font-semibold">{result.name}</h4>
          <p className="mt-0.5 text-sm text-muted">
            {result.local_name} · <i>{result.scientific_name}</i>
          </p>
        </div>
        <StatusPill status={result.status}>{result.label}</StatusPill>
      </div>

      <ul className="grid gap-3.5">
        {result.checks.map((c) => (
          <li key={c.factor} className="grid gap-1.5">
            <div className="flex flex-wrap justify-between gap-2.5 text-sm tabular-nums">
              <span className="inline-flex items-center gap-2 font-semibold">
                <StatusIcon status={c.status} />
                {c.name}
              </span>
              <span className="text-muted">
                {c.range_text}
                {c.your_value_text ? ` · ${c.your_value_text}` : ""}
              </span>
            </div>
            {c.meter && <Meter meter={c.meter} />}
            <p className="text-[0.9rem]">
              {c.title && <strong className="font-bold">{c.title}. </strong>}
              {c.message}
            </p>
          </li>
        ))}
      </ul>

      <div className="border-t border-line pt-3">
        <button type="button" onClick={() => onViewGuide(result.code)} className="py-1 text-[0.92rem] font-semibold hover:underline">
          View the {result.name.toLowerCase()} growing guide →
        </button>
      </div>
    </article>
  );
}
