"use client";

import { useEffect, useState } from "react";
import { ApiError, checkField } from "@/lib/api";
import { DEFAULT_INPUT, MONTHS } from "@/lib/defaults";
import { num } from "@/lib/format";
import type { CheckResponse, ClimateMode, Crop, FieldInput, MapPlace, Place } from "@/lib/types";
import { Container, Eyebrow, Panel, SectionTitle } from "./Container";
import { ResultCard } from "./ResultCard";
import { StatusPill } from "./Status";

const STORAGE_KEY = "bumi360-field-v2";
const LABEL = { ok: "suitable", warn: "suitable with management", bad: "less suitable" } as const;

function readSaved(): FieldInput | null {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    return saved ? { ...DEFAULT_INPUT, ...saved } : null;
  } catch {
    return null;
  }
}

function years(period: string | null | undefined) {
  const m = period?.match(/(\d{4})\D+(\d{4})/);
  return m ? `${m[1]}–${m[2]} average` : "long-term average";
}

export function FieldCheck({
  crops,
  locations,
  initialCheck,
  onViewGuide,
  mapPlace = null,
  onPickOnMap,
}: {
  crops: Crop[];
  locations: Place[];
  initialCheck: CheckResponse | null;
  onViewGuide: (code: string) => void;
  mapPlace?: MapPlace | null;
  onPickOnMap?: () => void;
}) {
  const [form, setForm] = useState<FieldInput>(DEFAULT_INPUT);
  const [restored, setRestored] = useState(false);
  const [data, setData] = useState<CheckResponse | null>(initialCheck);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [gps, setGps] = useState<{ state: "idle" | "locating" | "error"; message?: string }>({ state: "idle" });

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

  // A place chosen on the map
  useEffect(() => {
    if (!mapPlace) return;
    const t = setTimeout(() => {
      setGps({ state: "idle" });
      setForm((f) => ({ ...f, mode: "nasa", location: mapPlace.location, lat: mapPlace.lat, lon: mapPlace.lon }));
      document.getElementById("check")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 80);
    return () => clearTimeout(t);
  }, [mapPlace]);

  const waitingForGps = form.mode === "nasa" && form.location === "GPS" && (!form.lat || !form.lon);

  // Ask the Flask API whenever the readings change (short pause so typing stays smooth).
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(form));
    } catch {}
    if (waitingForGps) return;
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
  }, [form, attempt, waitingForGps]);

  const set = (key: keyof FieldInput) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  function setMode(mode: ClimateMode) {
    setForm((f) => ({ ...f, mode }));
  }

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
    if (!("geolocation" in navigator)) {
      setGps({ state: "error", message: "This browser can't share your location. Choose a division instead." });
      return;
    }
    setGps({ state: "locating" });
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGps({ state: "idle" });
        setForm((f) => ({
          ...f,
          location: "GPS",
          lat: pos.coords.latitude.toFixed(4),
          lon: pos.coords.longitude.toFixed(4),
        }));
      },
      (err) => {
        setGps({
          state: "error",
          message:
            err.code === err.PERMISSION_DENIED
              ? "Location access was not allowed. Choose a division instead, or allow location in your browser settings."
              : "Your location could not be found. Choose a division instead.",
        });
      },
      { enableHighAccuracy: false, timeout: 15000, maximumAge: 600000 },
    );
  }

  const climate = data?.input.climate;
  const conds = data
    ? climate
      ? [
          data.input.ph == null ? "pH not entered" : `pH ${data.input.ph.toFixed(1)}`,
          climate.location.name,
          `planting in ${MONTHS[climate.month - 1]}`,
          climate.irrigation ? `+${num(climate.irrigation)} mm irrigation` : null,
          `${climate.source} climate, ${years(climate.period)}`,
        ]
          .filter(Boolean)
          .join(" · ")
      : [
          data.input.ph == null ? "pH not entered" : `pH ${data.input.ph.toFixed(1)}`,
          data.input.temp == null ? "temperature not entered" : `${num(data.input.temp)}°C`,
          data.input.water == null ? "water not entered" : `${num(data.input.water)} mm per season`,
        ].join(" · ")
    : "";

  const total = data?.results.length ?? 0;
  const single = data && data.input.crop !== "all" ? data.results[0] : null;
  const locationValue = gps.state === "locating" ? "GPS" : form.location;

  return (
    <section id="check" aria-labelledby="check-title" className="py-14 md:py-[72px]">
      <Container>
        <div className="mb-7">
          <Eyebrow>Field check</Eyebrow>
          <SectionTitle id="check-title">How suitable is your field?</SectionTitle>
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
              <h3 className="font-display text-lg font-semibold">Your field</h3>

              <fieldset className="grid gap-1.5">
                <legend className="mb-1.5 text-[0.92rem] font-semibold">Temperature and water</legend>
                <div role="radiogroup" aria-label="Temperature and water" className="grid grid-cols-2 rounded-[10px] border border-line bg-bg p-1">
                  {([
                    ["nasa", "NASA climate"],
                    ["manual", "Enter manually"],
                  ] as const).map(([value, label]) => (
                    <button
                      key={value}
                      type="button"
                      role="radio"
                      aria-checked={form.mode === value}
                      onClick={() => setMode(value)}
                      className={`min-h-10 rounded-[7px] px-2 text-[0.9rem] font-semibold ${form.mode === value ? "bg-fg text-bg" : "text-muted hover:text-fg"}`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
                <span className="text-[0.8rem] text-muted">
                  {form.mode === "nasa"
                    ? "Uses NASA POWER climate averages (built from satellite and weather observations), worked out for each crop's growing season."
                    : "Type in your own temperature and water readings."}
                </span>
              </fieldset>

              <div className="grid grid-cols-1 gap-4 sm:max-lg:grid-cols-2">
                <NumberField id="ph" label="Soil pH" unit="pH" hint="From a soil test, scale 0–14" step="0.1" value={form.ph} onChange={set("ph")} />

                {form.mode === "nasa" ? (
                  <>
                    <SelectField id="location" label="Location in Sarawak" value={locationValue} onChange={onLocationChange}
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
                    <SelectField id="month" label="Planting month" value={form.month} onChange={set("month")} hint="The season starts on the 1st of this month">
                      {MONTHS.map((m, i) => (
                        <option key={m} value={String(i + 1)}>{m}</option>
                      ))}
                    </SelectField>
                    <NumberField id="irrigation" label="Extra irrigation" unit="mm" hint="Added to NASA rainfall for each crop's season" step="10" value={form.irrigation} onChange={set("irrigation")} />
                  </>
                ) : (
                  <>
                    <NumberField id="temp" label="Average temperature" unit="°C" hint="Typical day and night average" step="0.5" value={form.temp} onChange={set("temp")} />
                    <NumberField id="water" label="Water available per season" unit="mm" hint="Rainfall plus irrigation" step="10" value={form.water} onChange={set("water")} />
                  </>
                )}

                <SelectField id="crop" label="Crop" value={form.crop} onChange={set("crop")} hint="Pick one crop or compare all">
                  <option value="all">All crops (compare)</option>
                  {crops.map((c) => (
                    <option key={c.code} value={c.code}>{c.name} ({c.local_name})</option>
                  ))}
                </SelectField>
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
                    setGps({ state: "idle" });
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

export function FieldShell({ id, label, hint, hintAlert, children }: {
  id: string;
  label: string;
  hint: string;
  hintAlert?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="grid min-w-0 content-start gap-1.5">
      <label htmlFor={id} className="text-[0.92rem] font-semibold">{label}</label>
      {children}
      <span role={hintAlert ? "alert" : undefined} className={`text-[0.8rem] ${hintAlert ? "font-semibold text-fg" : "text-muted"}`}>
        {hint}
      </span>
    </div>
  );
}

export function SelectField(props: {
  id: string;
  label: string;
  hint: string;
  hintAlert?: boolean;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  children: React.ReactNode;
}) {
  return (
    <FieldShell id={props.id} label={props.label} hint={props.hint} hintAlert={props.hintAlert}>
      <select
        id={props.id}
        value={props.value}
        onChange={props.onChange}
        className="min-h-12 w-full rounded-[10px] border border-line bg-bg px-3 text-base"
      >
        {props.children}
      </select>
    </FieldShell>
  );
}

export function NumberField(props: {
  id: string;
  label: string;
  unit: string;
  hint: string;
  step: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <FieldShell id={props.id} label={props.label} hint={props.hint}>
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
    </FieldShell>
  );
}
