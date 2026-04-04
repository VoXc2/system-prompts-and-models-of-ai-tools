/**
 * التواصل المباشر مع الرئيس التنفيذي — يُضبط من البيئة.
 * - NEXT_PUBLIC_CEO_BOOKING_URL: رابط حجز Google Calendar (Appointment schedule) أو أي صفحة حجز رسمية.
 * - NEXT_PUBLIC_CEO_WHATSAPP: رقم واتساب بصيغة 9665xxxxxxxx بدون +.
 */

export const CEO_NAME_AR = "المهندس سامي العسيري";
export const CEO_TITLE_AR = "الرئيس التنفيذي — Dealix";

export function getCeoBookingUrl(): string {
  return (process.env.NEXT_PUBLIC_CEO_BOOKING_URL || "").trim();
}

export function getCeoWhatsappE164(): string {
  const v = (process.env.NEXT_PUBLIC_CEO_WHATSAPP || "966597788539").replace(/\D/g, "");
  return v.length >= 9 ? v : "966597788539";
}

export function getCeoWhatsappLink(prefill?: string): string {
  const base = `https://wa.me/${getCeoWhatsappE164()}`;
  const msg =
    prefill ||
    `مرحباً، أرغب بالتواصل مع ${CEO_NAME_AR} (${CEO_TITLE_AR}) بخصوص Dealix.`;
  return `${base}?text=${encodeURIComponent(msg)}`;
}

/** إذا لم يُضبط رابط الحجز، نوجّه لطلب موعد عبر واتساب. */
export function getCeoBookingOrScheduleViaWaLink(): string {
  const url = getCeoBookingUrl();
  if (url.length > 0) return url;
  return getCeoWhatsappLink(
    "مرحباً، أرغب بحجز موعد أو مكالمة (Google Meet) مع المهندس سامي العسيري — الرئيس التنفيذي لـ Dealix."
  );
}
