/** حالة «نظام المسوّق» — ربط محلي مع الخادم (معرّف الشريك، الرمز، الخطوات). */

export const MARKETER_OS_STORAGE_KEY = "dealix_marketer_os_v1";

export type MarketerOsSteps = {
  registered: boolean;
  profileSaved: boolean;
  activated: boolean;
  firstDeal: boolean;
};

export type MarketerOsState = {
  affiliateId: string | null;
  referralCode: string | null;
  email: string | null;
  status: string | null;
  totalDealsClosed: number;
  totalCommissionEarned: number;
  currentMonthDeals: number;
  steps: MarketerOsSteps;
  lastSyncedAt: string | null;
};

const defaultSteps: MarketerOsSteps = {
  registered: false,
  profileSaved: false,
  activated: false,
  firstDeal: false,
};

export const defaultMarketerOsState: MarketerOsState = {
  affiliateId: null,
  referralCode: null,
  email: null,
  status: null,
  totalDealsClosed: 0,
  totalCommissionEarned: 0,
  currentMonthDeals: 0,
  steps: { ...defaultSteps },
  lastSyncedAt: null,
};

export function loadMarketerOsState(): MarketerOsState {
  if (typeof window === "undefined") return { ...defaultMarketerOsState, steps: { ...defaultSteps } };
  try {
    const raw = localStorage.getItem(MARKETER_OS_STORAGE_KEY);
    if (!raw) return { ...defaultMarketerOsState, steps: { ...defaultSteps } };
    const p = JSON.parse(raw) as Partial<MarketerOsState>;
    return {
      ...defaultMarketerOsState,
      ...p,
      steps: { ...defaultSteps, ...p.steps },
    };
  } catch {
    return { ...defaultMarketerOsState, steps: { ...defaultSteps } };
  }
}

export function saveMarketerOsState(next: MarketerOsState): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(MARKETER_OS_STORAGE_KEY, JSON.stringify(next));
}

export function patchMarketerOsState(partial: Partial<MarketerOsState>): MarketerOsState {
  const cur = loadMarketerOsState();
  const merged: MarketerOsState = {
    ...cur,
    ...partial,
    steps: { ...cur.steps, ...partial.steps },
  };
  saveMarketerOsState(merged);
  return merged;
}

export function clearMarketerOsState(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(MARKETER_OS_STORAGE_KEY);
}
