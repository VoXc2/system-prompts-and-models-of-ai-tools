/**
 * Only allow same-origin relative paths after login (blocks `//evil.com`, `https://…`, etc.).
 */
export function safeInternalNextPath(
  raw: string | null | undefined,
  fallback: string = "/dashboard"
): string {
  if (raw == null || typeof raw !== "string") return fallback;
  const t = raw.trim();
  if (!t.startsWith("/")) return fallback;
  if (t.startsWith("//")) return fallback;
  if (/[\s\\]/.test(t)) return fallback;
  if (t.includes("://")) return fallback;
  if (t.includes("@")) return fallback;
  return t;
}
