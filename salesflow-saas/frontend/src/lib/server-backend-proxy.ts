/**
 * Server-only fetch to FastAPI — يمكن إرفاق DEALIX_INTERNAL_API_TOKEN دون تسريبه للمتصفح.
 */

export function getServerBackendBaseUrl(): string {
  return (
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
    process.env.DEALIX_API_URL?.replace(/\/$/, "") ||
    "http://127.0.0.1:8000"
  );
}

export function backendProxyHeaders(): HeadersInit {
  const headers: Record<string, string> = { Accept: "application/json" };
  const token = process.env.DEALIX_INTERNAL_API_TOKEN?.trim();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}
