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
} as const;

export function isValidEmailFormat(value: string): boolean {
  const s = value.trim();
  if (!s) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
}
