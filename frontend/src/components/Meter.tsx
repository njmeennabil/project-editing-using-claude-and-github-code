import type { Meter as MeterData, Status } from "@/lib/types";
import { STATUS_COLOR } from "./Status";

export function Meter({ meter, status = "none" }: { meter: MeterData; status?: Status }) {
  const pct = (x: number) => Math.max(0, Math.min(100, ((x - meter.min) / (meter.max - meter.min)) * 100));
  const lo = pct(meter.low);
  const hi = pct(meter.high);
  return (
    <div className="relative h-2.5 rounded-[5px] bg-track" aria-hidden="true">
      <span className="absolute inset-y-0 rounded-[5px] bg-band" style={{ left: `${lo}%`, width: `${Math.max(hi - lo, 1)}%` }} />
      {meter.value != null && (
        <span
          className="absolute -top-1 -ml-0.5 h-[18px] w-1 rounded-sm shadow-[0_0_0_2px_var(--surface)]"
          style={{ left: `${pct(meter.value)}%`, background: STATUS_COLOR[status] }}
        />
      )}
    </div>
  );
}
