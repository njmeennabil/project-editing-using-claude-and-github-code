"use client";

import { useEffect, useState } from "react";
import { ApiError, planNextCrop } from "@/lib/api";
import { DEFAULT_PLAN } from "@/lib/defaults";
import { num } from "@/lib/format";
import { locateMe, niceDate } from "@/lib/geo";
import type { Crop, MapPlace, Place, PlanInput, PlanOption, PlanResponse } from "@/lib/types";
import { Container, Eyebrow, Panel, SectionTitle } from "./Container";
import { FieldShell, NumberField, SelectField } from "./FieldCheck";

const STORAGE_KEY = "bumi360-plan-v1";

const VERDICT_STYLE: Record<string, { cls: string; sym: string }> = {
  "Highly recommended": { cls: "border-fg bg-fg text-bg", sym: "✓" },
  Recommended: { cls: "border-fg text-fg", sym: "✓" },
  "Possible with care": { cls: "border-fg text-fg", sym: "!" },
  "Not recommended": { cls: "border-dashed border-fg text-fg", sym: "✕" },
};

export function VerdictPill({ verdict }: { verdict: string }) {
  const v = VERDICT_STYLE[verdict] ?? VERDICT_STYLE["Possible with care"];
  return (
    <span className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border-[1.5px] px-2.5 py-1 text-[0.8rem] font-semibold ${v.cls}`}>
      <span aria-hidden="true" className="text-[0.8em] leading-none">{v.sym}</span>
      {verdict}
    </span>
  );
}

export function ScoreRing({ score, size = 92 }: { score: number; size?: number }) {
  const r = 40;
  const c = 2 * Math.PI * r;
  return (
    <div className="relative flex-none" style={{ width: size, height: size }}>
      <svg viewBox="0 0 100 100" width={size} height={size} aria-hidden="true">
        <circle cx="50" cy="50" r={r} fill="none" stroke="var(--track)" strokeWidth="10" />
        <circle
          cx="50" cy="50" r={r} fill="none" stroke="var(--fg)" strokeWidth="10" strokeLinecap="round"
          strokeDasharray={`${(c * score) / 100} ${c}`} transform="rotate(-90 50 50)"
        />
      </svg>
      <div className="absolute inset-0 grid place-items-center text-center leading-none">
        <span className="font-display text-[1.7rem] font-bold tabular-nums">{score}</span>
      </div>
      <span className="sr-only">Score {score} out of 100</span>
    </div>
  );
}

function Bar({ label, value, max }: { label: string; value: number; max: number }) {
  return (
    <div className="grid gap-1">
      <div className="flex justify-between text-[0.82rem] tabular-nums">
        <span className="text-muted">{label}</span>
        <span className="font-semibold">{value}/{max}</span>
      </div>
      <div className="h-2 rounded-full bg-track" aria-hidden="true">
        <div className="h-2 rounded-full bg-fg" style={{ width: `${(value / max) * 100}%` }} />
      </div>
    </div>
  );
}

function OptionCard({
  o,
  rank,
  after,
  place,
  onViewGuide,
}: {
  o: PlanOption;
  rank: number;
  after: string;
  place: string;
  onViewGuide: (code: string) => void;
}) {
  return (
    <article className="grid min-w-0 gap-5 rounded-[14px] border border-line bg-surface p-5 md:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] md:gap-7 md:p-6">
      <div className="grid min-w-0 content-start gap-4">
        <div className="flex min-w-0 items-start gap-4">
          <ScoreRing score={o.score} />
          <div className="grid min-w-0 gap-1.5">
            <span className="text-xs font-semibold uppercase tracking-[0.08em] text-muted">Option {rank}</span>
            <h4 className="font-display text-xl font-semibold leading-tight">
              {o.name} <span className="font-sans text-sm font-normal text-muted">{o.local_name}</span>
            </h4>
            <div className="flex flex-wrap"><VerdictPill verdict={o.verdict} /></div>
          </div>
        </div>
        <div className="grid gap-2.5">
          <Bar label="Climate fit" value={o.breakdown.climate} max={o.max.climate} />
          <Bar label="Rotation" value={o.breakdown.rotation} max={o.max.rotation} />
          <Bar label="Soil pH" value={o.breakdown.soil} max={o.max.soil} />
        </div>
      </div>

      <div className="grid min-w-0 content-start gap-3">
        <p className="rounded-[10px] border border-line bg-bg px-3 py-2 text-[0.82rem] leading-snug text-muted">
          <span className="font-semibold text-fg">NASA POWER</span> · {place} · {o.season.months} ({o.season.days} days
          {o.season.days_assumed ? ", assumed" : ""}): {num(o.season.temp_c)}°C average, {num(o.season.rain_mm)} mm rain
          {o.season.irrigation_mm ? ` + ${num(o.season.irrigation_mm)} mm irrigation` : ""}
        </p>
        <div className="grid gap-1 text-[0.92rem]">
          <p>
            <strong>Rotation after {after}: {o.rotation.rating}.</strong> {o.rotation.reason}
          </p>
          {!o.rotation.verified && (
            <p className="text-[0.78rem] text-muted">Rotation rating is a draft, awaiting expert review.</p>
          )}
        </div>
        <ul className="grid list-disc gap-1 pl-5 text-[0.88rem] text-muted">
          {o.notes.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
        <div className="border-t border-line pt-3">
          <button type="button" onClick={() => onViewGuide(o.code)} className="py-1 text-left text-[0.92rem] font-semibold hover:underline">
            View the {o.name.toLowerCase()} growing guide →
          </button>
        </div>
      </div>
    </article>
  );
}

export function NextCrop({
  crops,
  locations,
  initialPlan,
  onViewGuide,
  mapPlace = null,
  onPickOnMap,
}: {
  crops: Crop[];
  locations: Place[];
  initialPlan: PlanResponse | null;
  onViewGuide: (code: string) => void;
  mapPlace?: MapPlace | null;
  onPickOnMap?: () => void;
}) {
  const [form, setForm] = useState<PlanInput>(DEFAULT_PLAN);
  const [data, setData] = useState<PlanResponse | null>(initialPlan);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [gps, setGps] = useState<{ state: "idle" | "locating" | "error"; message?: string }>({ state: "idle" });

  // Bring back the last plan inputs (this browser only).
  useEffect(() => {
    let saved: PlanInput | null = null;
    try {
      const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (raw) saved = { ...DEFAULT_PLAN, ...raw };
    } catch {}
    if (!saved) return;
    const t = setTimeout(() => setForm(saved!), 0);
    return () => clearTimeout(t);
  }, []);

  // A place chosen on the map
  useEffect(() => {
    if (!mapPlace) return;
    const t = setTimeout(() => {
      setGps({ state: "idle" });
      setForm((f) => ({ ...f, location: mapPlace.location, lat: mapPlace.lat, lon: mapPlace.lon }));
      document.getElementById("plan")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 80);
    return () => clearTimeout(t);
  }, [mapPlace]);

  const waitingForGps = form.location === "GPS" && (!form.lat || !form.lon);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(form));
    } catch {}
    if (waitingForGps || !form.planted) return;
    const ctrl = new AbortController();
    const t = setTimeout(async () => {
      setLoading(true);
      try {
        setData(await planNextCrop(form, ctrl.signal, 70000));
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
    }, 350);
    return () => {
      clearTimeout(t);
      ctrl.abort();
    };
  }, [form, attempt, waitingForGps]);

  const set = (key: keyof PlanInput) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  function onLocationChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const value = e.target.value;
    if (value === "PICK") {
      onPickOnMap?.();
      return;
    }
    if (value !== "GPS") {
      setGps({ state: "idle" });
      setForm((f) => ({ ...f, location: value }));
      return;
    }
    setGps({ state: "locating" });
    locateMe(
      (lat, lon) => {
        setGps({ state: "idle" });
        setForm((f) => ({ ...f, location: "GPS", lat, lon }));
      },
      (message) => setGps({ state: "error", message }),
    );
  }

  const t = data?.timeline;
  const placeName = data?.location.name ?? "";

  return (
    <section id="plan" aria-labelledby="plan-title" className="border-t border-line py-14 md:py-[72px]">
      <Container>
        <div className="mb-7">
          <Eyebrow>Next crop</Eyebrow>
          <SectionTitle id="plan-title">What should you plant next?</SectionTitle>
          <p className="mt-2.5 max-w-[62ch] text-muted">
            Tell us what is growing now and when you planted it. BUMI360 works out when you will harvest, then scores
            every crop from 0 to 100 for the season after.
          </p>
        </div>

        <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[360px_minmax(0,1fr)] lg:gap-8">
          <Panel className="lg:sticky lg:top-[84px]">
            <form
              className="grid gap-[18px] p-[22px]"
              noValidate
              onSubmit={(e) => {
                e.preventDefault();
                setAttempt((a) => a + 1);
              }}
            >
              <h3 className="font-display text-lg font-semibold">Your current crop</h3>
              <div className="grid grid-cols-1 gap-4 sm:max-lg:grid-cols-2">
                <SelectField id="plan-current" label="Growing now" value={form.current} onChange={set("current")} hint="The crop in your field today">
                  {crops.map((c) => (
                    <option key={c.code} value={c.code}>{c.name} ({c.local_name})</option>
                  ))}
                </SelectField>
                <FieldShell id="plan-planted" label="Planting date" hint="The day you planted it">
                  <input
                    id="plan-planted"
                    type="date"
                    value={form.planted}
                    onChange={set("planted")}
                    min="2000-01-01"
                    max="2100-12-31"
                    className="min-h-12 w-full rounded-[10px] border border-line bg-bg px-3 text-base"
                  />
                </FieldShell>
                <SelectField
                  id="plan-location"
                  label="Location in Sarawak"
                  value={gps.state === "locating" ? "GPS" : form.location}
                  onChange={onLocationChange}
                  hint={
                    gps.state === "locating"
                      ? "Finding your location…"
                      : gps.state === "error"
                        ? gps.message!
                        : form.location === "GPS"
                          ? `Using your location: ${form.lat}, ${form.lon}`
                          : form.location === "MAP"
                            ? `Using the map point: ${form.lat}, ${form.lon}`
                            : "Division, GPS, or a point on the map"
                  }
                  hintAlert={gps.state === "error"}
                >
                  {locations.map((l) => (
                    <option key={l.code} value={l.code}>{l.name}</option>
                  ))}
                  <option value="GPS">Use my location (GPS)</option>
                      {form.location === "MAP" && <option value="MAP">Point chosen on map</option>}
                      <option value="PICK">Choose on map…</option>
                </SelectField>
                <NumberField id="plan-ph" label="Soil pH" unit="pH" hint="From a soil test, scale 0–14" step="0.1" value={form.ph} onChange={set("ph")} />
                <NumberField id="plan-prep" label="Days to prepare the land" unit="days" hint="Between harvest and next planting" step="1" value={form.prep_days} onChange={set("prep_days")} />
                <NumberField id="plan-irrigation" label="Extra irrigation" unit="mm" hint="Added to NASA rainfall for the next season" step="10" value={form.irrigation} onChange={set("irrigation")} />
              </div>
              <div className="flex flex-wrap gap-2.5">
                <button type="submit" className="min-h-[46px] flex-[1_1_180px] rounded-[10px] bg-fg px-5 font-semibold text-bg hover:opacity-90">
                  Score the next crop
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setForm(DEFAULT_PLAN);
                    setGps({ state: "idle" });
                  }}
                  className="min-h-[46px] rounded-[10px] border border-line px-5 font-semibold hover:bg-bg-alt"
                >
                  Reset to example
                </button>
              </div>
            </form>
          </Panel>

          <div className="grid min-w-0 gap-5" aria-live="polite" aria-busy={loading}>
            {error && (
              <div role="alert" className="flex flex-wrap items-center justify-between gap-3 rounded-[14px] border-[1.5px] border-dashed border-fg px-4 py-3 text-[0.92rem]">
                <span>{error}</span>
                <button type="button" onClick={() => setAttempt((a) => a + 1)} className="rounded-lg border border-line px-3 py-1.5 font-semibold hover:bg-bg-alt">
                  Try again
                </button>
              </div>
            )}

            {data && t ? (
              <div className={`grid gap-5 transition-opacity ${loading ? "opacity-60" : ""}`}>
                <ol className="grid grid-cols-1 gap-3 sm:grid-cols-3" aria-label="Timeline">
                  {[
                    { k: "Planted", v: niceDate(t.planted), s: t.current.name },
                    { k: "Expected harvest", v: niceDate(t.harvest), s: `~${t.growing_days} days${t.growing_days_assumed ? " (assumed)" : ""}` },
                    { k: "Next planting", v: niceDate(t.next_planting), s: `${t.prep_days} days to prepare the land` },
                  ].map((step, i) => (
                    <li key={step.k} className={`grid gap-0.5 rounded-[12px] border px-4 py-3 ${i === 2 ? "border-fg border-[1.5px]" : "border-line"} bg-surface`}>
                      <span className="text-xs font-semibold uppercase tracking-[0.07em] text-muted">{step.k}</span>
                      <span className="font-display text-lg font-semibold tabular-nums">{step.v}</span>
                      <span className="text-[0.82rem] text-muted">{step.s}</span>
                    </li>
                  ))}
                </ol>

                <h3 className="font-display text-[1.3rem] font-semibold">
                  Top 3 crops to plant after {t.current.name.toLowerCase()} in {placeName}
                  {loading && <span className="text-[0.9rem] font-normal text-muted"> · Updating…</span>}
                </h3>

                <div className="grid grid-cols-1 gap-4">
                  {data.recommendations.map((o, i) => (
                    <OptionCard key={o.code} o={o} rank={i + 1} after={t.current.name} place={placeName} onViewGuide={onViewGuide} />
                  ))}
                </div>

                {data.others.length > 0 && (
                  <div className="grid gap-2">
                    <h4 className="text-xs font-semibold uppercase tracking-[0.08em] text-muted">Other options</h4>
                    <ul className="grid gap-2">
                      {data.others.map((o) => (
                        <li key={o.code} className="flex flex-wrap items-center gap-x-4 gap-y-1.5 rounded-[12px] border border-line bg-surface px-4 py-3">
                          <span className="w-10 font-display text-xl font-bold tabular-nums">{o.score}</span>
                          <span className="font-semibold">{o.name}</span>
                          <VerdictPill verdict={o.verdict} />
                          <span className="basis-full text-[0.85rem] text-muted sm:basis-auto">
                            Rotation: {o.rotation.rating}. {o.rotation.reason}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <p className="text-[0.82rem] text-muted">
                  Scores are a guide, not a guarantee: climate fit 45 points (NASA POWER {data.climate.period?.match(/\d{4}\D+\d{4}/)?.[0].replace(/\D+/, "–") ?? ""} averages
                  for the next crop&apos;s own season), rotation 35, soil pH 20. A poor rotation is never shown as recommended.
                </p>
              </div>
            ) : (
              !error && <p className="text-muted">Scoring your next crop…</p>
            )}
          </div>
        </div>
      </Container>
    </section>
  );
}
