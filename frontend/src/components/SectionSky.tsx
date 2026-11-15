// The night sky behind a tab: stars, a soft coloured glow and a line drawing
// for that tab (drawings are in public/sky, made by scripts/build_sky.mjs).

type Motif = "check" | "plan" | "map" | "crops" | "compare" | "rotation" | "about";

const GLOW: Record<Motif, string> = {
  check: "rgba(60,140,110,.30)",
  plan: "rgba(120,90,200,.32)",
  map: "rgba(60,110,220,.30)",
  crops: "rgba(70,150,80,.28)",
  compare: "rgba(150,100,200,.24)",
  rotation: "rgba(220,140,90,.24)",
  about: "rgba(240,150,90,.26)",
};

const PLACE: Record<Motif, "top" | "bottom" | "full"> = {
  check: "bottom",
  plan: "top",
  map: "full",
  crops: "top",
  compare: "top",
  rotation: "top",
  about: "top",
};

export function SectionSky({ motif }: { motif: Motif }) {
  return (
    <div
      className="sky"
      aria-hidden="true"
      style={{
        background: `radial-gradient(60% 70% at 85% 8%, ${GLOW[motif]}, transparent 70%), radial-gradient(50% 40% at 0% 100%, rgba(40,70,160,.18), transparent 70%), linear-gradient(#060a18, #081028)`,
      }}
    >
      <div className="sky-stars" />
      {motif === "about" && <div className="sky-bottom" style={{ backgroundImage: "url(/sky/earth.svg)" }} />}
      <div className={`sky-${PLACE[motif]}`} style={{ backgroundImage: `url(/sky/${motif}.svg)` }} />
    </div>
  );
}
