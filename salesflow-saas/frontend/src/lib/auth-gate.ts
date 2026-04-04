/**
 * Pure helpers for dashboard auth gating (middleware + unit tests).
 */

export const DEALIX_SESSION_COOKIE = "dealix_has_session";

/** Value stored by `syncSessionCookie(true)` — must match middleware check. */
export function dealixSessionCookieValueIsActive(value: string | undefined | null): boolean {
  return value === "1";
}

/**
 * Parse a raw `Cookie` header (e.g. from tests or proxies) for `dealix_has_session=1`.
 */
export function cookieHeaderHasDealixSession(header: string | null | undefined): boolean {
  if (!header) return false;
  const parts = header.split(";").map((p) => p.trim());
  for (const p of parts) {
    const eq = p.indexOf("=");
    if (eq === -1) continue;
    const name = p.slice(0, eq).trim();
    const val = p.slice(eq + 1).trim();
    if (name === DEALIX_SESSION_COOKIE && val === "1") return true;
  }
  return false;
}

export function buildLoginUrlWithNext(baseUrl: string, pathname: string): URL {
  const login = new URL("/login", baseUrl);
  login.searchParams.set("next", pathname);
  return login;
}
