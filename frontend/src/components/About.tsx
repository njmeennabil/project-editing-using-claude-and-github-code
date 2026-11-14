import { Container, Eyebrow, SectionTitle } from "./Container";
import { StatusPill } from "./Status";

const RULES: [string, string, string, string][] = [
  ["Soil pH", "Within range", "–", "Outside range"],
  ["Temperature", "Within optimum", "Up to 2°C outside", "More than 2°C outside"],
  ["Water", "Within range", "Short by up to half, or excess", "Short by more than half"],
];

export function About() {
  const cell = "py-3 pr-3.5 text-left align-top border-b border-line";
  return (
    <section id="about" aria-labelledby="about-title" className="py-14 md:py-[72px]">
      <Container className="grid grid-cols-1 gap-8 lg:grid-cols-[1.4fr_1fr] lg:gap-12">
        <div className="min-w-0">
          <Eyebrow>About</Eyebrow>
          <SectionTitle id="about-title">How BUMI360 decides</SectionTitle>
          <p className="mb-5 mt-2.5 max-w-[62ch] text-muted">
            Each reading is compared with the crop&apos;s recommended range. The overall result follows the weakest reading.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-[0.92rem]">
              <thead>
                <tr>
                  <th className={`${cell} text-xs font-semibold text-muted`}>Reading</th>
                  <th className={cell}><StatusPill status="ok">Suitable</StatusPill></th>
                  <th className={cell}><StatusPill status="warn">With management</StatusPill></th>
                  <th className={cell}><StatusPill status="bad">Less suitable</StatusPill></th>
                </tr>
              </thead>
              <tbody>
                {RULES.map(([name, ok, warn, bad]) => (
                  <tr key={name}>
                    <th scope="row" className={`${cell} whitespace-nowrap font-semibold`}>{name}</th>
                    <td className={cell}>{ok}</td>
                    <td className={cell}>{warn}</td>
                    <td className={cell}>{bad}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 max-w-[65ch] text-sm text-muted">
            With NASA climate, temperature is the average over the crop&apos;s growing season and water is the season&apos;s
            rainfall plus any extra irrigation you enter. Water Spinach and Mustard Greens have no seasonal water figure in
            mm, so BUMI360 shows moisture advice and water does not change their result. Mustard Greens has no maturity
            figure, so a 30-day season is assumed.
          </p>
        </div>
        <div className="grid content-start gap-3.5">
          <AboutCard title="Climate data">
            Temperature and rainfall come from NASA POWER: 25-year monthly averages (2001–2025) for each Sarawak division or
            your GPS location. BUMI360 adds up the rain over each crop&apos;s own growing season, starting from your planting
            month. NASA data describes an area of about 50 km, so local conditions can differ. Data obtained from the NASA
            Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program.
          </AboutCard>
          <AboutCard title="Crop data">
            Crop requirements and fertiliser rates come from the BUMI360 crop database, with references including TNAU, Nepal
            guidelines and the Department of Agriculture Sarawak, as noted on each crop.
          </AboutCard>
          <AboutCard title="Coming next">
            Finer satellite rainfall (NASA GPM) and current soil moisture (NASA SMAP) for Sarawak.
          </AboutCard>
          <AboutCard title="Please note" strong>
            BUMI360 gives general guidance. Confirm planting decisions with a soil test and your local agriculture officer.
          </AboutCard>
        </div>
      </Container>
    </section>
  );
}

function AboutCard({ title, strong, children }: { title: string; strong?: boolean; children: React.ReactNode }) {
  return (
    <div className={`grid gap-2 rounded-[14px] bg-surface p-5 ${strong ? "border-[1.5px] border-fg" : "border border-line"}`}>
      <h3 className="font-display font-semibold">{title}</h3>
      <p className="text-[0.93rem] text-muted">{children}</p>
    </div>
  );
}
