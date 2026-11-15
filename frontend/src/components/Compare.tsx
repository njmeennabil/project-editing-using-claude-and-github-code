import { maturity, phRange, range, waterText } from "@/lib/format";
import type { Crop } from "@/lib/types";
import { Container, Eyebrow, SectionTitle } from "./Container";
import { TabSection } from "./TabSection";

export function Compare({ crops }: { crops: Crop[] }) {
  const head = ["Crop", "Type", "Soil pH", "Temp (°C)", "Water / season", "Key nutrient", "Nitrogen", "Maturity"];
  const cell = "px-4 py-3.5 text-left align-top border-b border-line";
  return (
    <TabSection id="compare">
      <Container>
        <div className="mb-7">
          <Eyebrow>Compare</Eyebrow>
          <SectionTitle id="compare-title">Crops side by side</SectionTitle>
        </div>
        <div className="overflow-x-auto rounded-[14px] border border-line bg-surface">
          <table className="w-full min-w-[760px] border-collapse text-[0.92rem] tabular-nums">
            <thead className="bg-bg-alt">
              <tr>
                {head.map((h) => (
                  <th key={h} scope="col" className={`${cell} text-xs font-semibold text-muted`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {crops.map((c) => (
                <tr key={c.code} className="[&:last-child>*]:border-b-0">
                  <th scope="row" className={`${cell} whitespace-nowrap font-semibold`}>
                    {c.name}
                    <small className="block font-normal text-muted">{c.local_name}</small>
                  </th>
                  <td className={cell}>{c.type}</td>
                  <td className={`${cell} whitespace-nowrap`}>{phRange(c)}</td>
                  <td className={`${cell} whitespace-nowrap`}>{range(c.temp_min_c, c.temp_max_c)}</td>
                  <td className={`${cell} whitespace-nowrap`}>{waterText(c)}</td>
                  <td className={cell}>{c.key_nutrient}</td>
                  <td className={cell}>{c.nitrogen_need}</td>
                  <td className={`${cell} whitespace-nowrap`}>{maturity(c)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Container>
    </TabSection>
  );
}
