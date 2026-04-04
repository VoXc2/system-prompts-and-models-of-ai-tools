/** تخزين محلي للمعاينة — يُستبدل بربط الخادم لاحقاً */

export const STORAGE_INVITE = "dealix_marketer_invite_v1";
export const STORAGE_TEAM = "dealix_marketer_team_v1";
export const STORAGE_PARENT = "dealix_marketer_parent_ref_v1";

export type TeamMember = {
  id: string;
  name: string;
  joinedAt: string;
  source: "simulated" | "signup";
};

export type TeamState = {
  members: TeamMember[];
};

export function generateInviteCode(): string {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let s = "";
  for (let i = 0; i < 8; i++) s += chars[Math.floor(Math.random() * chars.length)];
  return s;
}

export function loadTeamState(): TeamState {
  if (typeof window === "undefined") return { members: [] };
  try {
    const raw = localStorage.getItem(STORAGE_TEAM);
    if (!raw) return { members: [] };
    const p = JSON.parse(raw) as TeamState;
    if (!p.members || !Array.isArray(p.members)) return { members: [] };
    return p;
  } catch {
    return { members: [] };
  }
}

export function saveTeamState(state: TeamState): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_TEAM, JSON.stringify(state));
}

export function getOrCreateInviteCode(): string {
  if (typeof window === "undefined") return "";
  let c = localStorage.getItem(STORAGE_INVITE);
  if (!c) {
    c = generateInviteCode();
    localStorage.setItem(STORAGE_INVITE, c);
  }
  return c;
}

export function getParentRef(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(STORAGE_PARENT);
}

export function setParentRef(ref: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_PARENT, ref);
}
