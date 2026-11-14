"use client";

import { useRef } from "react";
import { maturity, num, phRange, range, waterText } from "@/lib/format";
import type { Crop, RotationItem } from "@/lib/types";
import { Container, Eyebrow, SectionTitle } from "./Container";

export function CropGuide({
  crops,
  rotation,
  selected,
  onSelect,
}: {
  crops: Crop[];
  rotation: RotationItem[];
  selected: string;
  onSelect: (code: string) => void;
}) {
  const stripRef = useRef<HTMLDivElement>(null);
  const crop = crops.find((c) => c.code === selected) ?? crops[0];

  function choose(code: string, focus = false) {
    onSelect(code);
    // Scroll the tab strip sideways only, never the page.
    const strip = stripRef.current;
    const tab = strip?.querySelector<HTMLButtonElement>(`[data-code="${code}"]`);
    if (strip && tab) {
      const left = tab.offsetLeft - strip.offsetLeft;
      const right = left + tab.offsetWidth;
      if (left < strip.scrollLeft) strip.scrollLeft = left;
      else if (right > strip.scrollLeft + strip.clientWidth) strip.scrollLeft = right - strip.clientWidth;
      if (focus) tab.focus({ preventScroll: true });
    }
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    e.preventDefault();
    const i = crops.findIndex((c) => c.code === crop.code);
    const next = crops[(i + (e.key === "ArrowRight" ? 1 : -1) + crops.length) % crops.length];
    choose(next.code, true);
  }

  return (
    <section id="crops" aria-labelledby="crops-title" className="border-y border-line bg-bg-alt py-14 md:py-[72px]">
      <Container>
        <div className="mb-7">
          <Eyebrow>Crop guide</Eyebrow>
          <SectionTitle id="crops-title">Growing guides</SectionTitle>
          <p className="mt-2.5 max-w-[62ch] text-muted">Soil, water, fertiliser and spacing for every crop in the BUMI360 database.</p>
        </div>

        <div ref={stripRef} role="tablist" aria-label="Choose a crop" onKeyDown={onKeyDown} className="mb-[18px] flex gap-2 overflow-x-auto pb-1.5">
          {crops.map((c) => {
            const active = c.code === crop.code;
            return (
              <button
                key={c.code}
                id={`tab-${c.code}`}
                data-code={c.code}
                type="button"
                role="tab"
                aria-selected={active}
                aria-controls="guide-panel"
                tabIndex={active ? 0 : -1}
                onClick={() => choose(c.code)}
                className={`grid min-h-12 flex-none rounded-xl border px-4 py-2.5 text-left ${active ? "border-fg bg-fg text-bg" : "border-line bg-surface text-fg"}`}
              >
                <span className="font-display font-semibold">{c.name}</span>
                <small className={`text-xs ${active ? "opacity-80" : "text-muted"}`}>{c.local_name}</small>
              </button>
            );
          })}
        </div>

        <article
          id="guide-panel"
          role="tabpanel"
          tabIndex={-1}
          aria-labelledby={`tab-${crop.code}`}
          className="grid gap-[26px] rounded-[14px] border border-line bg-surface p-6 md:p-8"
        >
          <GuideBody crop={crop} rotation={rotation} />
        </article>
      </Container>
    </section>
  );
}

function Block({ title, wide, children }: { title: string; wide?: boolean; children: React.ReactNode }) {
  return (
    <section className={`grid min-w-0 content-start gap-2.5 ${wide ? "md:col-span-2" : ""}`}>
      <h4 className="text-xs font-semibold uppercase tracking-[0.08em] text-muted">{title}</h4>
      {children}
    </section>
  );
}

function KeyValues({ rows }: { rows: [string, string][] }) {
  return (
    <dl className="grid gap-2">
      {rows.map(([k, v]) => (
        <div key={k} className="grid grid-cols-[minmax(110px,38%)_minmax(0,1fr)] gap-3 border-b border-line pb-2">
          <dt className="text-[0.9rem] text-muted">{k}</dt>
          <dd className="text-[0.95rem]">{v}</dd>
        </div>
      ))}
    </dl>
  );
}

const th = "py-2.5 pr-3.5 text-left align-top text-xs font-semibold text-muted border-b border-line";
const td = "py-2.5 pr-3.5 text-left align-top border-b border-line";

function GuideBody({ crop: c, rotation }: { crop: Crop; rotation: RotationItem[] }) {
  const s = c.soil;
  const soil: [string, string][] = [["Texture", s.texture], ["Drainage", s.drainage]];
  if (s.ph_danger_below != null) soil.push(["Avoid", `pH below ${num(s.ph_danger_below)}`]);
  if (s.note) soil.push(["Note", s.note]);

  const water: [string, string][] = [["Critical stages", c.critical_water_stages.length ? c.critical_water_stages.join(", ") : "No data"]];
  if (c.water_note) water.push(["Note", c.water_note]);
  water.push(["Key nutrient", c.key_nutrient], ["Nitrogen need", c.nitrogen_need]);

  const rot = rotation.filter((r) => r.before === c.name || r.after === c.name);

  const stats = [
    { label: "Soil pH", value: phRange(c) },
    { label: "Temperature", value: `${range(c.temp_min_c, c.temp_max_c)}°C` },
    { label: "Water / season", value: waterText(c), note: c.water_target_mm ? `~${num(c.water_target_mm)} mm for high yield` : null },
    { label: "Maturity", value: maturity(c), note: c.maturity_note },
  ];

  return (
    <>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm text-muted">
            <i>{c.scientific_name}</i> · {c.local_name}
          </p>
          <h3 className="font-display text-[clamp(1.6rem,3vw,2.1rem)] font-bold">{c.name}</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {[c.type, c.fixes_nitrogen ? "Fixes nitrogen" : null, c.source ? `Source: ${c.source}` : null]
            .filter(Boolean)
            .map((b) => (
              <span key={b} className="rounded-full border border-line bg-bg-alt px-2.5 py-1 text-[0.8rem] font-semibold text-muted">
                {b}
              </span>
            ))}
        </div>
      </div>

      <dl className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {stats.map((st) => (
          <div key={st.label} className="min-w-0 rounded-xl border border-line bg-bg px-4 py-3.5">
            <dt className="text-xs font-semibold uppercase tracking-[0.07em] text-muted">{st.label}</dt>
            <dd className="mt-1 font-display text-xl font-semibold leading-tight tabular-nums">
              {st.value}
              {st.note && <small className="mt-1 block font-sans text-[0.8rem] font-normal text-muted">{st.note}</small>}
            </dd>
          </div>
        ))}
      </dl>

      <div className="grid grid-cols-1 gap-[26px] md:grid-cols-2 md:gap-x-10 md:gap-y-7">
        <Block title="Soil"><KeyValues rows={soil} /></Block>
        <Block title="Water and nutrients"><KeyValues rows={water} /></Block>

        {c.npk.length > 0 && (
          <Block title="NPK dose (kg/ha)">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-[0.92rem] tabular-nums">
                <thead>
                  <tr><th className={th}>Source</th><th className={th}>When</th><th className={th}>N</th><th className={th}>P₂O₅</th><th className={th}>K₂O</th></tr>
                </thead>
                <tbody>
                  {c.npk.map((b, i) => (
                    <tr key={i}>
                      <td className={td}>{b.source}</td>
                      <td className={td}>
                        {b.condition}
                        {b.note && <span className="block text-[0.85rem] text-muted">{b.note}</span>}
                      </td>
                      <td className={`${td} whitespace-nowrap`}>{range(b.n_min, b.n_max)}</td>
                      <td className={`${td} whitespace-nowrap`}>{range(b.p2o5_min, b.p2o5_max)}</td>
                      <td className={`${td} whitespace-nowrap`}>{range(b.k2o_min, b.k2o_max)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Block>
        )}

        {c.fertiliser_programme.length > 0 && (
          <Block title="Fertiliser programme">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-[0.92rem] tabular-nums">
                <thead><tr><th className={th}>Product</th><th className={th}>Rate</th><th className={th}>When</th></tr></thead>
                <tbody>
                  {c.fertiliser_programme.map((p, i) => (
                    <tr key={i}>
                      <td className={td}>
                        {p.product}
                        {p.note && <span className="block text-[0.85rem] text-muted">{p.note}</span>}
                      </td>
                      <td className={`${td} whitespace-nowrap`}>{range(p.rate_min, p.rate_max)} {p.unit}</td>
                      <td className={td}>{p.timing}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Block>
        )}

        {c.special_nutrients.length > 0 && (
          <Block title="Special nutrients">
            <ul className="grid list-disc gap-1.5 pl-5 text-[0.95rem]">
              {c.special_nutrients.map((n) => (
                <li key={n.nutrient}>
                  <strong>{n.nutrient}</strong>: {n.role}
                  {n.product && `. ${n.product}${n.rate_min_kg_ha != null ? ` ${range(n.rate_min_kg_ha, n.rate_max_kg_ha)} kg/ha` : ""}`}
                  {n.timing && `, ${n.timing.toLowerCase()}`}.
                </li>
              ))}
            </ul>
          </Block>
        )}

        {c.spacing.length > 0 && (
          <Block title="Plant spacing">
            <ul className="grid list-disc gap-1.5 pl-5 text-[0.95rem]">
              {c.spacing.map((j, i) => {
                const row = range(j.row_min_cm, j.row_max_cm);
                const plant = range(j.plant_min_cm, j.plant_max_cm);
                const text =
                  row !== "–" && plant !== "–"
                    ? `${row} × ${plant} cm (between rows × within row)`
                    : row !== "–"
                      ? `${row} cm between rows`
                      : `${plant} cm between plants`;
                return (
                  <li key={i}>
                    {j.variety && <strong>{j.variety}: </strong>}
                    {text}
                  </li>
                );
              })}
            </ul>
          </Block>
        )}

        {c.practices.length > 0 && (
          <Block title="Good practice" wide>
            <ul className="grid gap-2">
              {c.practices.map((p, i) => (
                <li key={i} className="flex items-baseline gap-2.5 text-[0.95rem]">
                  <span className="min-w-[82px] flex-none rounded-md border border-line px-1.5 text-center text-xs font-semibold text-muted">{p.category}</span>
                  <span>{p.text}</span>
                </li>
              ))}
            </ul>
          </Block>
        )}

        {rot.length > 0 && (
          <Block title="Rotation" wide>
            <ul className="grid list-disc gap-1.5 pl-5 text-[0.95rem]">
              {rot.map((r, i) => (
                <li key={i}>
                  <strong>{r.before} → {r.after}</strong>
                  {r.yield_gain_pct ? ` (+${num(r.yield_gain_pct)}% yield)` : ""}. {r.note}
                </li>
              ))}
            </ul>
          </Block>
        )}
      </div>
    </>
  );
}
