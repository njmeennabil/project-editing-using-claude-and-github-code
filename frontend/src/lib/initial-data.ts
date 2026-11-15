import { cacheLife } from "next/cache";
import { checkField, getSiteData, planNextCrop } from "./api";
import { DEFAULT_INPUT, DEFAULT_PLAN } from "./defaults";
import type { CheckResponse, PlanResponse, SiteData } from "./types";

export interface InitialData extends SiteData {
  check: CheckResponse;
  plan: PlanResponse;
}

/**
 * Crop data and the example field check, fetched from Flask while the page is
 * prerendered and refreshed every hour. Returns null if the API can't be reached
 * (for example while a free Render server is asleep); the browser then loads it.
 */
export async function getInitialData(): Promise<InitialData | null> {
  "use cache";
  cacheLife("hours");
  try {
    const [site, check, plan] = await Promise.all([
      getSiteData(10000),
      checkField(DEFAULT_INPUT, undefined, 10000),
      planNextCrop(DEFAULT_PLAN, undefined, 10000),
    ]);
    return { ...site, check, plan };
  } catch {
    return null;
  }
}
