export function BrandMark({ className = "" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 32 32" aria-hidden="true">
      <circle
        cx="16" cy="16" r="13" fill="none" stroke="currentColor" strokeWidth="2.6"
        strokeDasharray="66 16" strokeLinecap="round" transform="rotate(-60 16 16)"
      />
      <path d="M16 23c0-5.5 2.6-9 7-10-.9 5.3-3.4 8.2-7 10zm0 0c0-3.6-1.8-6.2-5.3-7 0 3.6 1.9 6.2 5.3 7z" fill="currentColor" />
    </svg>
  );
}

export function Wordmark({ light = false }: { light?: boolean }) {
  return (
    <span>
      BUMI<span className={`font-medium ${light ? "text-white/65" : "text-muted"}`}>360</span>
    </span>
  );
}
