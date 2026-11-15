import { Container } from "./Container";
import { HeroSky } from "./HeroSky";

const glass =
  "rounded-[10px] border border-white/25 bg-[linear-gradient(160deg,rgba(255,255,255,.16),rgba(255,255,255,.04))] backdrop-blur-md";

function Arrow() {
  return (
    <svg viewBox="0 0 20 20" className="h-4 w-4 transition-transform group-hover:translate-x-0.5" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 10h12M11 5l5 5-5 5" />
    </svg>
  );
}

export function Hero({ cropCount }: { cropCount: number }) {
  const facts = [
    `${cropCount} crops with full guides`,
    "12 Sarawak divisions",
    "NASA GPM, SMAP and POWER data",
  ];
  return (
    <section
      id="hero"
      className="relative isolate -mt-[65px] overflow-hidden bg-[linear-gradient(#03050c,#0b1636_55%,#2a2246)] pb-20 pt-[168px] text-white md:pb-24 md:pt-40 lg:flex lg:min-h-[100svh] lg:items-center"
    >
      <HeroSky />
      <Container className="relative z-10">
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-white/80">NASA satellite data for Sarawak farms</p>
        <h1 className="max-w-[15ch] font-display text-[clamp(2.4rem,6.4vw,4.75rem)] font-bold leading-[1.02] tracking-tight [text-shadow:0_2px_30px_rgba(0,0,0,.35)]">
          Know what your land can grow.
        </h1>
        <p className="mt-5 max-w-[54ch] text-[1.08rem] leading-relaxed text-white/85">
          Enter your soil pH and choose where and when you plan to plant. BUMI360 checks each crop with NASA rainfall,
          soil moisture and temperature for Sarawak, then shows you how to grow it.
        </p>
        <ul className="mt-5 flex flex-wrap gap-x-5 gap-y-1.5 text-sm text-white/75" aria-label="At a glance">
          {facts.map((f) => (
            <li key={f} className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-white/70" aria-hidden="true" />
              {f}
            </li>
          ))}
        </ul>

        <div className="mt-9 grid gap-4 lg:grid-cols-[1.55fr_1fr]">
          <a href="#check" className={`group flex flex-col p-6 md:p-7 ${glass} hover:border-white/50`}>
            <h2 className="font-display text-[clamp(1.6rem,3vw,2.3rem)] font-bold leading-tight">Check your field</h2>
            <p className="mt-2 max-w-[46ch] text-white/80">
              Soil pH, location and planting month. Every crop scored for your field, with a fertiliser and care guide.
            </p>
            <span className="min-h-6 flex-1" aria-hidden="true" />
            <span className="inline-flex min-h-[48px] w-fit items-center gap-2 rounded-[6px] bg-[#f1efe9] px-5 font-semibold text-[#111] group-hover:bg-white">
              Check my field <Arrow />
            </span>
          </a>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
            <a href="#plan" className={`group block p-5 ${glass} bg-[rgba(10,14,24,.35)] hover:border-white/50`}>
              <h2 className="flex items-center justify-between gap-3 font-display text-xl font-bold">
                Plan your next crop <Arrow />
              </h2>
              <p className="mt-1.5 text-sm text-white/75">Top 3 crops for the season after your harvest, scored 0–100.</p>
            </a>
            <a href="#map" className={`group block p-5 ${glass} bg-[rgba(10,14,24,.35)] hover:border-white/50`}>
              <h2 className="flex items-center justify-between gap-3 font-display text-xl font-bold">
                Sarawak map <Arrow />
              </h2>
              <p className="mt-1.5 text-sm text-white/75">See crop scores, rainfall and soil moisture across Sarawak.</p>
            </a>
          </div>
        </div>
      </Container>
    </section>
  );
}
