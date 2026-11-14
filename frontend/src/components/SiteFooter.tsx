import { Wordmark } from "./BrandMark";
import { Container } from "./Container";
import { NAV_LINKS } from "./nav";

export function SiteFooter() {
  return (
    <footer className="border-t border-line bg-surface py-7">
      <Container className="flex flex-wrap items-center justify-between gap-x-7 gap-y-3.5">
        <a href="#top" className="font-display text-lg font-bold tracking-tight text-fg">
          <Wordmark />
        </a>
        <nav aria-label="Footer" className="flex flex-wrap gap-x-[18px] gap-y-1.5">
          {NAV_LINKS.map((l) => (
            <a key={l.href} href={l.href} className="text-[0.9rem] text-muted hover:text-fg">{l.label}</a>
          ))}
        </nav>
        <p className="text-[0.85rem] text-muted">© BUMI360. General guidance only.</p>
      </Container>
    </footer>
  );
}
