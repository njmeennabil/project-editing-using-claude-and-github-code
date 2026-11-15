import { Container, Eyebrow, SectionTitle } from "./Container";
import { StatusPill } from "./Status";
import { TabSection } from "./TabSection";

const RULES: [string, string, string, string][] = [
  ["Soil pH", "Within range", "–", "Outside range"],
  ["Temperature", "Within optimum", "Up to 2°C outside", "More than 2°C outside"],
  ["Water", "Within range", "Short by up to half, or excess", "Short by more than half"],
];

export function About() {
  const cell = "py-3 pr-3.5 text-left align-top border-b border-line";
  return (
    <TabSection id="about">
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
            Rainfall comes from NASA GPM IMERG V07 at about 10 km: monthly normals for 2001–2024 (IMERG Final) and the last
            60 days (IMERG Late), updated every week. Temperature comes from NASA POWER 25-year averages (2001–2025). BUMI360
            adds up each crop&apos;s own growing season from your planting date. GPM IMERG data provided by NASA Goddard Earth
            Sciences Data and Information Services Center (GES DISC); temperature data from the NASA Langley Research Center
            (LaRC) POWER Project, funded through the NASA Earth Science/Applied Science Program.
          </AboutCard>
          <AboutCard title="Soil moisture">
            This week&apos;s soil moisture comes from NASA SMAP Level 4 (about 9 km): satellite measurements combined with a land
            model, so forest areas have values too. BUMI360 compares the root zone (top 1 m) with what is usual for the month
            (2016–2025). It runs about 4–5 days behind. Data provided by the NASA National Snow and Ice Data Center
            Distributed Active Archive Center (NSIDC DAAC).
          </AboutCard>
          <AboutCard title="Explore the data in NASA Giovanni">
            Open{" "}
            <a href="https://giovanni.gsfc.nasa.gov/giovanni/" target="_blank" rel="noopener" className="font-semibold text-fg underline">
              NASA Giovanni
            </a>
            , choose <em>Time Averaged Map</em>, search for <em>GPM_3IMERGM</em> (IMERG monthly precipitation), and set the
            region to <em>109.5, 0.8, 115.8, 5.1</em> (Sarawak) to see the same rainfall data BUMI360 uses.
          </AboutCard>
          <AboutCard title="Next-crop score">
            Each crop gets up to 40 points for climate (temperature and rainfall over its own season after your harvest), 30
            for rotation after your current crop, 15 for soil pH and 15 for current conditions (the last 60 days of rain and this week&apos;s soil moisture, each
            against what is usual).
            Most rotation ratings are drafts from general agronomy and are awaiting expert review.
          </AboutCard>
          <AboutCard title="Crop data">
            Crop requirements and fertiliser rates come from the BUMI360 crop database, with references including TNAU, Nepal
            guidelines and the Department of Agriculture Sarawak, as noted on each crop.
          </AboutCard>
          <AboutCard title="Map data">
            Map background © OpenStreetMap contributors (and © CARTO when enabled). Division boundaries from geoBoundaries
            (citypopulation.de, CC BY 3.0), with Sarawak&apos;s districts merged into its 12 divisions by BUMI360.
          </AboutCard>
          <AboutCard title="Coming next">
            Seasonal rainfall forecasts, and confirmed rotation ratings from agricultural experts.
          </AboutCard>
          <AboutCard title="Please note" strong>
            BUMI360 gives general guidance. Confirm planting decisions with a soil test and your local agriculture officer.
          </AboutCard>
        </div>
      </Container>
    </TabSection>
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
