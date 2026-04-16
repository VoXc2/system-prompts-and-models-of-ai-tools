import { getApiBaseUrl } from "./api-base";

export type AuditableTarget = {
  id: string;
  label_ar: string;
  target: string;
  unit: string;
};

export type DesignPrinciple = {
  id: string;
  title_ar: string;
  summary: string;
};

export type SovereignModel = {
  name: string;
  operating_rule_ar: string;
  operating_rule_en: string;
  thesis_ar: string;
};

export type StrategyPlane = {
  id: string;
  name_ar: string;
  name_en: string;
  mission: string;
  capabilities: string[];
  building_blocks: string[];
  outcome: string;
};

export type BusinessTrack = {
  id: string;
  name_ar: string;
  scope: string[];
  automation_mode: string;
  primary_surfaces: string[];
};

export type ProgramClass = {
  id: string;
  label_ar: string;
  description: string;
};

export type ProgramLocks = {
  counts: {
    planes: number;
    business_tracks: number;
    agent_roles: number;
  };
  action_classes: ProgramClass[];
  approval_classes: ProgramClass[];
  reversibility_classes: ProgramClass[];
  sensitivity_levels: string[];
  metadata_trio: string[];
};

export type OperatingSurfaceStatus = "repo_anchor" | "build_next" | "target_required";

export type OperatingSurface = {
  id: string;
  name_ar: string;
  owner_track: string;
  status: OperatingSurfaceStatus;
  summary: string;
};

export type AutomationPolicy = {
  fully_automated: string[];
  approval_required: string[];
};

export type RoutingLane = {
  id: string;
  name_ar: string;
  purpose: string;
  models: string[];
  optimize_for: string[];
};

export type RoutingFabric = {
  lanes: RoutingLane[];
  scorecard: string[];
};

export type StrategySummary = {
  product: string;
  blueprint_version: string;
  positioning: string;
  vision: { tagline_ar: string; tagline_en: string };
  sovereign_model: SovereignModel;
  moat_pillars: string[];
  competitive_moat: Record<string, string>;
  auditable_targets: AuditableTarget[];
  planes: StrategyPlane[];
  business_tracks: BusinessTrack[];
  operating_surfaces: OperatingSurface[];
  program_locks: ProgramLocks;
  automation_policy: AutomationPolicy;
  routing_fabric: RoutingFabric;
  design_principles: DesignPrinciple[];
  phases: Array<{ id: number; name: string; horizon_days?: number; horizon_months?: string }>;
  execution_phases_detail: Array<{
    id: number;
    name_ar: string;
    window: string;
    deliverables: string[];
  }>;
  kpis: Array<{ axis: string; metric: string }>;
  readiness_definition: string[];
  doc_paths: Record<string, string>;
  repo_paths: Record<string, string>;
  market_frame?: string;
};

export async function fetchStrategySummary(signal?: AbortSignal): Promise<StrategySummary | null> {
  const base = getApiBaseUrl();
  try {
    const res = await fetch(`${base}/api/v1/strategy/summary`, {
      signal,
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) return null;
    return (await res.json()) as StrategySummary;
  } catch {
    return null;
  }
}
