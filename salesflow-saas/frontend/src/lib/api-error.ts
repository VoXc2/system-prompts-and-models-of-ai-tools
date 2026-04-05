/** يستخرج رسالة خطأ مقروءة من استجابات FastAPI (نص، أو مصفوفة أخطاء تحقق). */
export function parseApiErrorDetail(payload: unknown): string {
  if (!payload || typeof payload !== "object") return "";
  const d = payload as { detail?: unknown };
  if (typeof d.detail === "string") return d.detail;
  if (Array.isArray(d.detail)) {
    return d.detail
      .map((item) => {
        if (item && typeof item === "object" && "msg" in item) {
          return String((item as { msg?: string }).msg ?? "");
        }
        return typeof item === "string" ? item : "";
      })
      .filter(Boolean)
      .join(" ");
  }
  return "";
}
