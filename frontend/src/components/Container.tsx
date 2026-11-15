export function Container({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`mx-auto w-full max-w-[1180px] px-4 md:px-8 ${className}`}>{children}</div>;
}

export function Eyebrow({ children }: { children: React.ReactNode }) {
  return (
    <p className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/[.04] px-3 py-1 text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-[#cfd8f3]">
      <span className="h-1.5 w-1.5 rounded-full bg-[#f2c46d] shadow-[0_0_10px_2px_rgba(242,196,109,.7)]" aria-hidden="true" />
      {children}
    </p>
  );
}

export function SectionTitle({ id, children }: { id?: string; children: React.ReactNode }) {
  return (
    <h2
      id={id}
      className="bg-[linear-gradient(100deg,#ffffff_30%,#b8c7f2)] bg-clip-text font-display text-[clamp(1.8rem,4vw,2.8rem)] font-bold leading-tight tracking-tight text-transparent"
    >
      {children}
    </h2>
  );
}

export function Panel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`rounded-[14px] border border-line bg-surface ${className}`}>{children}</div>;
}
