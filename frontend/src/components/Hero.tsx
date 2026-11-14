import { Container } from "./Container";

export function Hero({ cropCount }: { cropCount: number }) {
  const facts = [
    { n: String(cropCount), label: "crops with full guides" },
    { n: "3", label: "field readings: pH, °C, mm" },
    { n: "0", label: "sign-ups needed" },
  ];
  return (
    <section className="border-b border-line bg-[radial-gradient(ellipse_60%_80%_at_100%_0%,color-mix(in_srgb,var(--fg)_7%,transparent),transparent_70%)] py-12 md:py-16">
      <Container className="grid grid-cols-1 items-end gap-8 lg:grid-cols-[1.5fr_1fr]">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.1em]">Crop planning for Malaysian farms</p>
          <h1 className="max-w-[16ch] font-display text-[clamp(2rem,5.2vw,3.4rem)] font-bold leading-[1.05] tracking-tight">
            Know what your land can grow before you plant.
          </h1>
          <p className="mt-4 max-w-[58ch] text-[1.08rem] text-muted">
            Enter your soil pH, average temperature and the water your field gets in a season. BUMI360 checks each crop
            against its needs and shows you the fertiliser, spacing and care it requires.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <a href="#check" className="inline-flex min-h-[46px] items-center rounded-[10px] bg-fg px-5 font-semibold text-bg hover:opacity-90">
              Check my field
            </a>
            <a href="#crops" className="inline-flex min-h-[46px] items-center rounded-[10px] border border-line px-5 font-semibold hover:bg-bg-alt">
              Browse crops
            </a>
          </div>
        </div>
        <ul className="grid grid-cols-3 gap-3 lg:grid-cols-1" aria-label="At a glance">
          {facts.map((f) => (
            <li key={f.label} className="flex flex-col gap-0.5 rounded-r-[10px] border-l-[3px] border-fg bg-surface px-4 py-3.5 lg:flex-row lg:items-baseline lg:gap-3.5">
              <span className="font-display text-[1.8rem] font-bold leading-none tabular-nums">{f.n}</span>
              <span className="text-sm leading-snug text-muted">{f.label}</span>
            </li>
          ))}
        </ul>
      </Container>
    </section>
  );
}
