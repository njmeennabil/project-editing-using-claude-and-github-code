import { Wordmark } from "./BrandMark";
import { Container } from "./Container";
import { TABS } from "@/lib/tabs";

export function SiteFooter() {
  return (
    <footer className="border-t border-white/10 bg-[linear-gradient(#060a18,#03050c)] py-8">
      <Container className="flex flex-wrap items-center justify-between gap-x-7 gap-y-3.5">
        <a href="#top" className="font-display text-lg font-bold tracking-tight text-fg">
          <Wordmark light />
        </a>
        <nav aria-label="Footer" className="flex flex-wrap gap-x-[18px] gap-y-1.5">
          {TABS.map((t) => (
            <a key={t.id} href={`#${t.id}`} className="text-[0.9rem] text-muted hover:text-fg">{t.label}</a>
          ))}
        </nav>
        <p className="text-[0.85rem] text-muted">© BUMI360. General guidance only.</p>
      </Container>
    </footer>
  );
}
