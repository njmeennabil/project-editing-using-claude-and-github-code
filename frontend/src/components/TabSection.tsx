import { TABS } from "@/lib/tabs";
import { Container } from "./Container";
import { SectionSky } from "./SectionSky";
import { TabIcon } from "./TabIcon";

type Id = (typeof TABS)[number]["id"];

/** One tab of the site: its night-sky background, its content, and links to the tabs either side. */
export function TabSection({ id, children }: { id: Id; children: React.ReactNode }) {
  const i = TABS.findIndex((t) => t.id === id);
  const prev = TABS[i - 1];
  const next = TABS[i + 1];
  return (
    <section id={id} aria-labelledby={`${id}-title`} className="tab-panel relative isolate overflow-hidden pb-10 pt-12 md:pb-14 md:pt-16">
      <SectionSky motif={id} />
      {children}
      <Container>
        <nav aria-label="More tabs" className="mt-14 grid grid-cols-2 gap-3 border-t border-white/10 pt-6">
          {prev ? (
            <a href={`#${prev.id}`} className="pager group">
              <span className="text-xs text-muted">← Previous</span>
              <span className="flex items-center gap-2 font-display font-semibold">
                <TabIcon id={prev.id} className="h-4 w-4 text-white/70" />
                {prev.label}
              </span>
            </a>
          ) : (
            <a href="#top" className="pager group">
              <span className="text-xs text-muted">← Back</span>
              <span className="flex items-center gap-2 font-display font-semibold">
                <TabIcon id="home" className="h-4 w-4 text-white/70" />
                Home
              </span>
            </a>
          )}
          {next ? (
            <a href={`#${next.id}`} className="pager group items-end text-right">
              <span className="text-xs text-muted">Next →</span>
              <span className="flex items-center gap-2 font-display font-semibold">
                {next.label}
                <TabIcon id={next.id} className="h-4 w-4 text-white/70" />
              </span>
            </a>
          ) : (
            <a href="#top" className="pager group items-end text-right">
              <span className="text-xs text-muted">Back to →</span>
              <span className="flex items-center gap-2 font-display font-semibold">
                Home
                <TabIcon id="home" className="h-4 w-4 text-white/70" />
              </span>
            </a>
          )}
        </nav>
      </Container>
    </section>
  );
}
