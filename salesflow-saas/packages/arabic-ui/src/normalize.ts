/**
 * Arabic text normalization — diacritics, hamza variants, alef-maksura, taa-marbuta.
 *
 * For search and comparison. Preserves original text for display.
 *
 * Examples:
 *   normalize("فَاتِحَة") === normalize("فاتحة")        // diacritics stripped
 *   normalize("أحمد") === normalize("احمد")              // hamza normalized
 *   normalize("رؤية") === normalize("روية")              // waw-hamza normalized
 *   normalize("سُنَّة") === normalize("سنة")              // shadda stripped
 */

// Arabic diacritics (fatha, kasra, damma, sukun, shadda, tanween, etc.)
const DIACRITICS = /[\u064B-\u0652\u0670\u0640]/g;

// Hamza variants
const ALEF_VARIANTS = /[\u0622\u0623\u0625\u0671]/g;  // آ, أ, إ, ٱ
const WAW_HAMZA = /\u0624/g;                           // ؤ
const YA_HAMZA = /\u0626/g;                            // ئ

// Taa marbuta
const TAA_MARBUTA = /\u0629/g;  // ة

// Alef maksura
const ALEF_MAKSURA = /\u0649/g;  // ى

// Extended Arabic characters
const TATWEEL = /\u0640/g;  // ـ (kashida)

export function normalize(text: string): string {
  if (!text) return "";
  return text
    .replace(DIACRITICS, "")
    .replace(ALEF_VARIANTS, "\u0627")     // → ا
    .replace(WAW_HAMZA, "\u0648")          // ؤ → و
    .replace(YA_HAMZA, "\u064A")           // ئ → ي
    .replace(TAA_MARBUTA, "\u0647")        // ة → ه
    .replace(ALEF_MAKSURA, "\u064A")       // ى → ي
    .replace(TATWEEL, "")
    .toLowerCase();
}

export function arabicMatch(haystack: string, needle: string): boolean {
  return normalize(haystack).includes(normalize(needle));
}

export function arabicCompare(a: string, b: string): number {
  return normalize(a).localeCompare(normalize(b), "ar", { sensitivity: "base" });
}
