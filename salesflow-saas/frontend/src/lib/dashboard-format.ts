/** تنسيق عملة للوحة التحكم — يُبقى متسقاً مع SAR. */
export function formatSar(value: number | string | undefined | null): string {
  if (value === undefined || value === null) return "—";
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) return "—";
  return new Intl.NumberFormat("ar-SA", {
    style: "currency",
    currency: "SAR",
    maximumFractionDigits: n >= 1000 ? 0 : 2,
  }).format(n);
}

export function stageLabelAr(stage: string): string {
  const map: Record<string, string> = {
    new: "جديد",
    negotiation: "تفاوض",
    proposal: "عرض سعر",
    closed_won: "مغلقة — فوز",
    closed_lost: "مغلقة — خسارة",
  };
  return map[stage] ?? stage;
}
