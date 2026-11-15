import { About } from "@/components/About";
import { BumiApp } from "@/components/BumiApp";
import { Hero } from "@/components/Hero";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { getInitialData } from "@/lib/initial-data";

export default async function Home() {
  const initial = await getInitialData();
  const site = initial
    ? { crops: initial.crops, rotation: initial.rotation, notes: initial.notes, locations: initial.locations }
    : null;

  return (
    <div id="top">
      <a
        href="#check"
        className="absolute -top-16 left-4 z-[100] rounded-lg bg-fg px-3.5 py-2 text-bg focus:top-2"
      >
        Skip to the field check
      </a>
      <SiteHeader />
      <main>
        <Hero cropCount={initial?.crops.length ?? 5} />
        <BumiApp initialData={site} initialCheck={initial?.check ?? null} initialPlan={initial?.plan ?? null} />
        <About />
      </main>
      <SiteFooter />
    </div>
  );
}
