import { num } from "@/lib/format";
import type { RotationItem } from "@/lib/types";
import { Container, Eyebrow, SectionTitle } from "./Container";

export function Rotation({ rotation, notes }: { rotation: RotationItem[]; notes: string[] }) {
  return (
    <section id="rotation" aria-labelledby="rotation-title" className="border-y border-line bg-bg-alt py-14 md:py-[72px]">
      <Container>
        <div className="mb-7">
          <Eyebrow>Crop rotation</Eyebrow>
          <SectionTitle id="rotation-title">Plant legumes first</SectionTitle>
          <p className="mt-2.5 max-w-[62ch] text-muted">
            Soybean and peanut fix nitrogen from the air. The crop that follows them starts with richer soil.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-3.5 md:grid-cols-2">
          {rotation.map((r) => (
            <article key={`${r.before}-${r.after}`} className="grid gap-2.5 rounded-[14px] border border-line bg-surface p-5">
              <div className="flex flex-wrap items-center gap-3 font-display text-lg font-semibold">
                <span>{r.before}</span>
                <span aria-label="then" className="text-xl">→</span>
                <span>{r.after}</span>
                {r.yield_gain_pct ? (
                  <span className="rounded-full bg-fg px-2 py-0.5 font-sans text-[0.8rem] font-bold text-bg">+{num(r.yield_gain_pct)}% yield</span>
                ) : null}
              </div>
              <p className="text-[0.88rem] text-muted">{r.note}</p>
            </article>
          ))}
        </div>
        <ul className="mt-6 grid list-disc gap-1.5 pl-5 text-muted">
          {notes.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      </Container>
    </section>
  );
}
