/**
 * Direction detection and RTL utilities.
 */

// Strong RTL character range check (per Unicode Bidirectional Algorithm)
const STRONG_RTL = /[\u0590-\u083F\u08A0-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]/;
const STRONG_LTR = /[A-Za-z\u00C0-\u024F\u1E00-\u1EFF]/;

export type Direction = "ltr" | "rtl";

/**
 * Detect dominant direction of a string.
 * Returns "rtl" if first strong character is Arabic/Hebrew/etc, else "ltr".
 */
export function detectDirection(text: string): Direction {
  if (!text) return "ltr";
  for (const ch of text) {
    if (STRONG_RTL.test(ch)) return "rtl";
    if (STRONG_LTR.test(ch)) return "ltr";
  }
  return "ltr";
}

export function hasArabic(text: string): boolean {
  return STRONG_RTL.test(text);
}

export function isRTL(locale: string): boolean {
  return /^(ar|he|fa|ur|ps|sd|ckb)(\b|-)/.test(locale);
}

/**
 * Wrap mixed-direction content to prevent bidi reordering issues.
 * Usage: `الطلب ${isolate("ORD-2026-001234")} جاهز`
 */
export function isolate(text: string): string {
  return `\u2068${text}\u2069`;
}
