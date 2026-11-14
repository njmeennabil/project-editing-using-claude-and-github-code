"use client";

import { useEffect, useState } from "react";
import { getSiteData } from "@/lib/api";
import type { CheckResponse, SiteData } from "@/lib/types";
import { Compare } from "./Compare";
import { Container, Eyebrow, SectionTitle } from "./Container";
import { CropGuide } from "./CropGuide";
import { FieldCheck } from "./FieldCheck";
import { Rotation } from "./Rotation";

/**
 * Everything that needs crop data. Uses the data prerendered on the server when
 * available; otherwise loads it from the Flask API in the browser and retries
 * while a sleeping server wakes up.
 */
export function BumiApp({ initialData, initialCheck }: { initialData: SiteData | null; initialCheck: CheckResponse | null }) {
  const [data, setData] = useState<SiteData | null>(initialData);
  const [failed, setFailed] = useState(false);
  const [retry, setRetry] = useState(0);
  const [selected, setSelected] = useState<string>(initialData?.crops[0]?.code ?? "");

  useEffect(() => {
    if (data) return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;
    let attempts = 0;
    const load = async () => {
      try {
        const site = await getSiteData(20000);
        if (cancelled) return;
        setData(site);
        setSelected((s) => s || site.crops[0]?.code || "");
      } catch {
        attempts += 1;
        if (cancelled) return;
        if (attempts < 8) timer = setTimeout(load, 5000);
        else setFailed(true);
      }
    };
    load();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [data, retry]);

  function viewGuide(code: string) {
    setSelected(code);
    document.getElementById("crops")?.scrollIntoView();
    document.getElementById("guide-panel")?.focus({ preventScroll: true });
  }

  if (!data) {
    return (
      <section id="check" aria-labelledby="check-title" className="py-14 md:py-[72px]">
        <Container>
          <Eyebrow>Field check</Eyebrow>
          <SectionTitle id="check-title">How suitable is your field?</SectionTitle>
          <div role="status" className="mt-7 grid max-w-xl gap-3 rounded-[14px] border-[1.5px] border-dashed border-fg p-5">
            {failed ? (
              <>
                <p className="font-semibold">Can&apos;t reach the BUMI360 server.</p>
                <p className="text-muted">Check your internet connection and try again.</p>
                <button
                  type="button"
                  onClick={() => {
                    setFailed(false);
                    setRetry((r) => r + 1);
                  }}
                  className="justify-self-start rounded-[10px] bg-fg px-5 py-2.5 font-semibold text-bg"
                >
                  Try again
                </button>
              </>
            ) : (
              <>
                <p className="font-semibold">Connecting to the BUMI360 server…</p>
                <p className="text-muted">If nobody has used it for a while, the server can take up to a minute to wake up.</p>
              </>
            )}
          </div>
        </Container>
      </section>
    );
  }

  return (
    <>
      <FieldCheck crops={data.crops} locations={data.locations} initialCheck={initialCheck} onViewGuide={viewGuide} />
      <CropGuide crops={data.crops} rotation={data.rotation} selected={selected} onSelect={setSelected} />
      <Compare crops={data.crops} />
      <Rotation rotation={data.rotation} notes={data.notes} />
    </>
  );
}
