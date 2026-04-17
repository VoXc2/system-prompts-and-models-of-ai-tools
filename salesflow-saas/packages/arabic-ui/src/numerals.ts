/**
 * Numeral formatting — Western (0-9), Arabic-Indic (٠-٩), Eastern Arabic-Indic.
 *
 * Locale-aware currency formatting for MENA.
 */

export type NumeralSystem = "western" | "arabic-indic" | "eastern-arabic-indic";

const WESTERN_DIGITS = "0123456789";
const ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩";
const EASTERN_ARABIC_INDIC_DIGITS = "۰۱۲۳۴۵۶۷۸۹";

export function convertDigits(text: string, to: NumeralSystem): string {
  const target =
    to === "arabic-indic" ? ARABIC_INDIC_DIGITS :
    to === "eastern-arabic-indic" ? EASTERN_ARABIC_INDIC_DIGITS :
    WESTERN_DIGITS;

  return text.replace(/[\d\u0660-\u0669\u06F0-\u06F9]/g, (ch) => {
    const code = ch.charCodeAt(0);
    let idx: number;
    if (code >= 0x30 && code <= 0x39) idx = code - 0x30;
    else if (code >= 0x0660 && code <= 0x0669) idx = code - 0x0660;
    else if (code >= 0x06F0 && code <= 0x06F9) idx = code - 0x06F0;
    else return ch;
    return target[idx];
  });
}

export function formatCurrency(
  value: number,
  currency: "SAR" | "AED" | "EGP" | "USD" | "JOD" | "KWD" = "SAR",
  locale: "ar-SA" | "ar-AE" | "ar-EG" | "en-US" = "ar-SA",
  numerals: NumeralSystem = "western"
): string {
  const formatted = new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
  }).format(value);

  return convertDigits(formatted, numerals);
}

export function formatNumber(
  value: number,
  locale: string = "ar-SA",
  numerals: NumeralSystem = "western"
): string {
  const formatted = new Intl.NumberFormat(locale).format(value);
  return convertDigits(formatted, numerals);
}
