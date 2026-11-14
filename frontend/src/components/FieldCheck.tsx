"use client";

import { useEffect, useState } from "react";
import { ApiError, checkField } from "@/lib/api";
import { DEFAULT_INPUT } from "@/lib/defaults";
import { num } from "@/lib/format";
import type { CheckResponse, Crop, FieldInput } from "@/lib/types";
import { Container, Eyebrow, Panel, SectionTitle } from "./Container";
import { ResultCard } from "./ResultCard";
import { StatusPill } from "./Status";

const STORAGE_KEY = "bumi360-field-v1";
const LABEL = { ok: "suitable", warn: "suitable with management", bad: "less suitable" } as const;

function readSaved(): FieldInput | null {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    return saved ? { ...DEFAULT_INPUT, ...saved } : null;
  } catch {
    return null;
  }
}

export function FieldCheck({
  crops,
  initialCheck,
  onViewGuide,
}: {
  crops: Crop[];
  initialCheck: CheckResponse | null;
  onViewGuide: (code: string) => void;
}) {
  const [form, setForm] = useState<FieldInput>(DEFAULT_INPUT);
  const [restored, setRestored] = useState(false);
  const [data, setData] = useState<CheckResponse | null>(initialCheck);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  // Bring back the farmer's last readings (this browser only).
  useEffect(() => {
    const saved = readSaved();
    if (!saved) return;
    const t = setTimeout(() => {
      setForm(saved);
      setRestored(true);
    }, 0);
    return () => clearTimeout(t);
  }, []);

  // Ask the Flask API whenever the readings change (short pause so typing stays smooth).
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(form));
    } catch {}
    const ctrl = new AbortController();
    const t = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await checkField(form, ctrl.signal, 70000);
        setData(res);
        setError(null);
      } catch (e) {
        if (ctrl.signal.aborted) return;
        setError(
          e instanceof ApiError
            ? e.message
            : "Can't reach the BUMI360 server. If nobody has used it for a while, it can take up to a minute to wake up.",
        );
      } finally {
        if (!ctrl.signal.aborted) setLoading(false);
      }
    }, 300);
    return () => {
      clearTimeout(t);
      ctrl.abort();
    };
  }, [form, attempt]);

  const set = (key: keyof FieldInput) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const conds = data
    ? [
        data.input.ph == null ? "pH not entered" : `pH ${data.input.ph.toFixed(1)}`,
        data.input.temp == null ? "temperature not entered" : `${num(data.input.temp)}°C`,
        data.input.water == null ? "water not entered" : `${num(data.input.water)} mm per season`,
      ].join(" · ")
    : "";

  const total = data?.results.length ?? 0;
  const single = data && data.input.crop !== "all" ? data.results[0] : null;

  return (
    <section id="check" aria-labelledby="check-title" className="py-14 md:py-[72px]">
      <Container>
        <div className="mb-7">
          <Eyebrow>Field check</Eyebrow>
          <SectionTitle id="check-title">How suitable is your field?</SectionTitle>
        </div>

        <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[340px_minmax(0,1fr)] lg:gap-8">
          <Panel className="lg:sticky lg:top-[84px]">
            <form
              className="grid gap-[18px] p-[22px]"
              noValidate
              onSubmit={(e) => {
                e.preventDefault();
                setAttempt((a) => a + 1);
              }}
            >
              <h3 className="font-display text-lg font-semibold">Your field</h3>
              <div className="grid grid-cols-1 gap-4 sm:max-lg:grid-cols-2">
                <NumberField id="ph" label="Soil pH" unit="pH" hint="From a soil test, scale 0–14" step="0.1" value={form.ph} onChange={set("ph")} />
                <NumberField id="temp" label="Average temperature" unit="°C" hint="Typical day and night average" step="0.5" value={form.temp} onChange={set("temp")} />
                <NumberField id="water" label="Water available per season" unit="mm" hint="Rainfall plus irrigation" step="10" value={form.water} onChange={set("water")} />
                <div className="grid min-w-0 gap-1.5">
                  <label htmlFor="crop" className="text-[0.92rem] font-semibold">Crop</label>
                  <select
                    id="crop"
                    value={form.crop}
                    onChange={set("crop")}
                    className="min-h-12 w-full rounded-[10px] border border-line bg-bg px-3 text-base"
                  >
                    <option value="all">All crops (compare)</option>
                    {crops.map((c) => (
                      <option key={c.code} value={c.code}>
                        {c.name} ({c.local_name})
                      </option>
                    ))}
                  </select>
                  <span className="text-[0.8rem] text-muted">Pick one crop or compare all</span>
                </div>
              </div>
              <div className="flex flex-wrap gap-2.5">
                <button type="submit" className="min-h-[46px] flex-[1_1_180px] rounded-[10px] bg-fg px-5 font-semibold text-bg hover:opacity-90">
                  Check suitability
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setForm(DEFAULT_INPUT);
                    setRestored(false);
                  }}
                  className="min-h-[46px] rounded-[10px] border border-line px-5 font-semibold hover:bg-bg-alt"
                >
                  Reset to example
                </button>
              </div>
              <p className="text-[0.82rem] text-muted">
                {restored ? "Your last readings have been restored." : "These are example values. Replace them with your own field readings."}
              </p>
            </form>
          </Panel>

          <div className="grid min-w-0 gap-4" aria-live="polite" aria-busy={loading}>
            {error && (
              <div role="alert" className="flex flex-wrap items-center justify-between gap-3 rounded-[14px] border-[1.5px] border-dashed border-fg px-4 py-3 text-[0.92rem]">
                <span>{error}</span>
                <button type="button" onClick={() => setAttempt((a) => a + 1)} className="rounded-lg border border-line px-3 py-1.5 font-semibold hover:bg-bg-alt">
                  Try again
                </button>
              </div>
            )}

            {data ? (
              <>
                <div className={`grid gap-2 transition-opacity ${loading ? "opacity-60" : ""}`}>
                  <h3 className="font-display text-[1.3rem] font-semibold">
                    {single
                      ? `${single.name}: ${single.label.toLowerCase()}`
                      : data.counts.none
                        ? "Complete the form for a full result"
                        : `${data.counts.ok} of ${total} crops suit your field as it is`}
                  </h3>
                  <p className="text-[0.92rem] tabular-nums text-muted">
                    {conds}
                    {loading && " · Updating…"}
                  </p>
                  {!single && (
                    <div className="flex flex-wrap gap-2">
                      {(["ok", "warn", "bad"] as const)
                        .filter((s) => data.counts[s])
                        .map((s) => (
                          <StatusPill key={s} status={s}>
                            {data.counts[s]} {LABEL[s]}
                          </StatusPill>
                        ))}
                    </div>
                  )}
                </div>
                <div className={`grid gap-3.5 ${data.results.length > 1 ? "xl:grid-cols-2" : ""}`}>
                  {data.results.map((r) => (
                    <ResultCard key={r.code} result={r} onViewGuide={onViewGuide} />
                  ))}
                </div>
              </>
            ) : (
              !error && <p className="text-muted">Checking your field…</p>
            )}
          </div>
        </div>
      </Container>
    </section>
  );
}

function NumberField(props: {
  id: string;
  label: string;
  unit: string;
  hint: string;
  step: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <div className="grid min-w-0 gap-1.5">
      <label htmlFor={props.id} className="text-[0.92rem] font-semibold">{props.label}</label>
      <div className="flex min-h-12 overflow-hidden rounded-[10px] border border-line bg-bg focus-within:outline-2 focus-within:outline-offset-1 focus-within:outline-fg">
        <input
          id={props.id}
          type="number"
          inputMode="decimal"
          step={props.step}
          value={props.value}
          onChange={props.onChange}
          className="min-w-0 flex-1 bg-transparent px-3.5 text-[1.1rem] font-semibold tabular-nums outline-none"
        />
        <span className="grid place-items-center border-l border-line px-3.5 text-sm text-muted">{props.unit}</span>
      </div>
      <span className="text-[0.8rem] text-muted">{props.hint}</span>
    </div>
  );
}
