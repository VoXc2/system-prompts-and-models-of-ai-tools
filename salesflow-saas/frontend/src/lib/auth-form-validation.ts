/** رسائل تحقق عربية — بديل لرسائل المتصفح الإنجليزية الافتراضية */

/** أقل طول لكلمة المرور في شاشة الدخول (واجهة فقط؛ الخادم يتحقق عند المصادقة) */
export const LOGIN_PASSWORD_MIN_LEN = 4;

export const authFormMsg = {
  emailRequired: "يرجى إدخال البريد الإلكتروني.",
  emailInvalid: "صيغة البريد الإلكتروني غير صحيحة.",
  passwordRequired: "يرجى إدخال كلمة المرور.",
  passwordShortLogin: "كلمة المرور يجب ألا تقل عن 4 أحرف.",
  companyRequired: "يرجى إدخال اسم الشركة.",
  fullNameRequired: "يرجى إدخال الاسم الكامل.",
  /** يطابق الـ API (schemas.py: Field(min_length=8)) */
  passwordShort: "كلمة المرور يجب ألا تقل عن 8 أحرف (مطلوب للتسجيل).",
  phoneRequired: "يرجى إدخال رقم الجوال السعودي.",
  phoneInvalid: "صيغة الجوال غير صحيحة (مثال: 05xxxxxxxx أو 9665xxxxxxxx).",
} as const;

export function isValidEmailFormat(value: string): boolean {
  const s = value.trim();
  if (!s) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
}

/** أرقام محلية سعودية: 05xxxxxxxx أو بدون صفر، أو تبدأ بـ 966 */
export function isValidSaMobile(value: string): boolean {
  const d = value.replace(/\s+/g, "").replace(/-/g, "");
  if (d.length < 9) return false;
  if (d.startsWith("966")) {
    const rest = d.slice(3);
    return rest.length === 9 && rest.startsWith("5");
  }
  if (d.startsWith("0") && d.length === 10 && d[1] === "5") return true;
  if (d.length === 9 && d.startsWith("5")) return true;
  return false;
}

/** تطبيع لحفظ موحّد 9665xxxxxxxx */
export function normalizeSaMobileDigits(value: string): string {
  const d = value.replace(/\D/g, "");
  if (d.startsWith("966")) return d;
  if (d.startsWith("0") && d.length >= 10) return "966" + d.slice(1);
  if (d.length === 9 && d.startsWith("5")) return "966" + d;
  return d;
}
