"use client";

import { useEffect, useState } from "react";
import { getSiteData } from "@/lib/api";
import type { CheckResponse, MapPlace, PlanResponse, SiteData } from "@/lib/types";
import { Compare } from "./Compare";
import { Container, Eyebrow, SectionTitle } from "./Container";
import { CropGuide } from "./CropGuide";
import { FieldCheck } from "./FieldCheck";
import { NextCrop } from "./NextCrop";
import { Rotation } from "./Rotation";
import { goToTab } from "@/lib/tabs";
import { TabSection } from "./TabSection";
import { type MapTarget, SarawakMap } from "./SarawakMap";

/**
 * Everything that needs crop data. Uses the data prerendered on the server when
 * available; otherwise loads it from the Flask API in the browser and retries
 * while a sleeping server wakes up.
 */
export function BumiApp({
  initialData,
  initialCheck,
  initialPlan,
}: {
  initialData: SiteData | null;
  initialCheck: CheckResponse | null;
  initialPlan: PlanResponse | null;
}) {
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

  const [mapTarget, setMapTarget] = useState<MapTarget | null>(null);
  const [checkPlace, setCheckPlace] = useState<MapPlace | null>(null);
  const [planPlace, setPlanPlace] = useState<MapPlace | null>(null);

  function pickOnMap(target: MapTarget) {
    setMapTarget(target);
    // Let the dropdown close first (phones), then open the map tab.
    (document.activeElement as HTMLElement | null)?.blur();
    setTimeout(() => goToTab("map"), 80);
  }

  function useMapPlace(target: MapTarget, place: Omit<MapPlace, "nonce">) {
    const withNonce = { ...place, nonce: Date.now() };
    if (target === "check") setCheckPlace(withNonce);
    else setPlanPlace(withNonce);
    setMapTarget(null);
    goToTab(target);
  }

  function viewGuide(code: string) {
    setSelected(code);
    goToTab("crops");
    setTimeout(() => document.getElementById("guide-panel")?.focus({ preventScroll: true }), 50);
  }

  if (!data) {
    return (
      <TabSection id="check">
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
      </TabSection>
    );
  }

  return (
    <>
      <FieldCheck
        crops={data.crops}
        locations={data.locations}
        initialCheck={initialCheck}
        onViewGuide={viewGuide}
        mapPlace={checkPlace}
        onPickOnMap={() => pickOnMap("check")}
      />
      <NextCrop
        crops={data.crops}
        locations={data.locations}
        initialPlan={initialPlan}
        onViewGuide={viewGuide}
        mapPlace={planPlace}
        onPickOnMap={() => pickOnMap("plan")}
      />
      <SarawakMap crops={data.crops} locations={data.locations} target={mapTarget} onUse={useMapPlace} />
      <CropGuide crops={data.crops} rotation={data.rotation} selected={selected} onSelect={setSelected} />
      <Compare crops={data.crops} />
      <Rotation rotation={data.rotation} notes={data.notes} />
    </>
  );
}
