"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DealixAuthBrandMark } from "@/components/dealix-auth-brand-mark";
import { useAuth } from "@/contexts/auth-context";
import { setParentRef } from "@/lib/marketer-team";
import {
  authFormMsg,
  isValidEmailFormat,
  isValidSaMobile,
  normalizeSaMobileDigits,
} from "@/lib/auth-form-validation";

type RegisterFieldKey = "company" | "fullName" | "email" | "password" | "phone";

export default function RegisterPage() {
  const { register } = useAuth();
  const [nextParam, setNextParam] = useState<string | null>(null);
  const [refParam, setRefParam] = useState<string | null>(null);
  const [companyName, setCompanyName] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<RegisterFieldKey, string>>>({});
  const [pending, setPending] = useState(false);

  function clearFieldError(key: RegisterFieldKey) {
    setFieldErrors((prev) => {
      if (!prev[key]) return prev;
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }

  function validateRegister(): boolean {
    const errs: Partial<Record<RegisterFieldKey, string>> = {};
    if (!companyName.trim()) errs.company = authFormMsg.companyRequired;
    if (!fullName.trim()) errs.fullName = authFormMsg.fullNameRequired;
    const em = email.trim();
    if (!em) errs.email = authFormMsg.emailRequired;
    else if (!isValidEmailFormat(em)) errs.email = authFormMsg.emailInvalid;
    if (!password) errs.password = authFormMsg.passwordRequired;
    else if (password.length < 8) errs.password = authFormMsg.passwordShort;
    const ph = phone.trim();
    if (!ph) errs.phone = authFormMsg.phoneRequired;
    else if (!isValidSaMobile(ph)) errs.phone = authFormMsg.phoneInvalid;
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  }

  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    setNextParam(p.get("next"));
    setRefParam(p.get("ref"));
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!validateRegister()) return;
    setPending(true);
    try {
      const phoneNorm = normalizeSaMobileDigits(phone.trim());
      await register(
        {
          company_name: companyName.trim(),
          full_name: fullName.trim(),
          email: email.trim(),
          password,
          phone: phoneNorm,
        },
        nextParam
      );
      if (refParam) {
        try {
          setParentRef(refParam);
        } catch {
          /* ignore */
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "فشل التسجيل");
    } finally {
      setPending(false);
    }
  }

  const loginHref = nextParam ? `/login?next=${encodeURIComponent(nextParam)}` : "/login";

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden p-6">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(20,184,166,0.12),transparent)]"
        aria-hidden
      />
      <div className="relative w-full max-w-md space-y-8">
        <div className="space-y-3 text-center">
          <DealixAuthBrandMark />
          <h1 className="text-2xl font-black tracking-tight">إنشاء حساب شركة</h1>
          <p className="text-sm leading-relaxed text-muted-foreground">
            مستأجر جديد + مالك (owner) تلقائياً. الجوال مطلوب للتواصل والتحقق لاحقاً.
          </p>
          {refParam && (
            <div className="rounded-xl border border-teal-500/30 bg-teal-950/40 px-4 py-3 text-sm text-teal-100">
              أنت تُسجّل ضمن فريق مسوّق: رمز الدعوة{" "}
              <span className="font-mono font-bold text-white">{refParam}</span> — بعد الإتمام يُربط
              حسابك بالهرم عند تفعيل الخادم.
            </div>
          )}
        </div>

        <form
          noValidate
          onSubmit={onSubmit}
          className="space-y-4 rounded-2xl border border-border/60 bg-card/40 p-8 shadow-2xl shadow-black/25 backdrop-blur-md"
        >
          {error && (
            <div className="text-sm text-destructive bg-destructive/10 border border-destructive/30 rounded-lg px-3 py-2">
              {error}
            </div>
          )}
          <div className="space-y-2 text-right">
            <label htmlFor="company" className="text-sm font-medium">
              اسم الشركة
            </label>
            <input
              id="company"
              type="text"
              value={companyName}
              onChange={(e) => {
                setCompanyName(e.target.value);
                clearFieldError("company");
              }}
              aria-invalid={fieldErrors.company ? true : undefined}
              aria-describedby={fieldErrors.company ? "company-error" : undefined}
              className={`w-full rounded-xl border bg-secondary/40 px-4 py-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                fieldErrors.company ? "border-destructive/60" : "border-border"
              }`}
            />
            {fieldErrors.company && (
              <p id="company-error" className="text-xs text-destructive" role="alert">
                {fieldErrors.company}
              </p>
            )}
          </div>
          <div className="space-y-2 text-right">
            <label htmlFor="fullName" className="text-sm font-medium">
              الاسم الكامل
            </label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => {
                setFullName(e.target.value);
                clearFieldError("fullName");
              }}
              aria-invalid={fieldErrors.fullName ? true : undefined}
              aria-describedby={fieldErrors.fullName ? "fullName-error" : undefined}
              className={`w-full rounded-xl border bg-secondary/40 px-4 py-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                fieldErrors.fullName ? "border-destructive/60" : "border-border"
              }`}
            />
            {fieldErrors.fullName && (
              <p id="fullName-error" className="text-xs text-destructive" role="alert">
                {fieldErrors.fullName}
              </p>
            )}
          </div>
          <div className="space-y-2 text-right">
            <label htmlFor="email" className="text-sm font-medium">
              البريد الإلكتروني
            </label>
            <input
              id="email"
              type="email"
              inputMode="email"
              autoComplete="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                clearFieldError("email");
              }}
              aria-invalid={fieldErrors.email ? true : undefined}
              aria-describedby={fieldErrors.email ? "reg-email-error" : undefined}
              className={`w-full rounded-xl border bg-secondary/40 px-4 py-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                fieldErrors.email ? "border-destructive/60" : "border-border"
              }`}
            />
            {fieldErrors.email && (
              <p id="reg-email-error" className="text-xs text-destructive" role="alert">
                {fieldErrors.email}
              </p>
            )}
          </div>
          <div className="space-y-2 text-right">
            <label htmlFor="phone" className="text-sm font-medium">
              الجوال <span className="text-destructive">*</span>
            </label>
            <input
              id="phone"
              type="tel"
              inputMode="tel"
              autoComplete="tel"
              placeholder="05xxxxxxxx أو 9665xxxxxxxx"
              value={phone}
              onChange={(e) => {
                setPhone(e.target.value);
                clearFieldError("phone");
              }}
              aria-invalid={fieldErrors.phone ? true : undefined}
              aria-describedby={fieldErrors.phone ? "reg-phone-error" : undefined}
              className={`w-full rounded-xl border bg-secondary/40 px-4 py-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                fieldErrors.phone ? "border-destructive/60" : "border-border"
              }`}
            />
            {fieldErrors.phone && (
              <p id="reg-phone-error" className="text-xs text-destructive" role="alert">
                {fieldErrors.phone}
              </p>
            )}
          </div>
          <div className="space-y-2 text-right">
            <label htmlFor="password" className="text-sm font-medium">
              كلمة المرور
            </label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                clearFieldError("password");
              }}
              aria-invalid={fieldErrors.password ? true : undefined}
              aria-describedby={fieldErrors.password ? "reg-password-error" : undefined}
              className={`w-full rounded-xl border bg-secondary/40 px-4 py-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                fieldErrors.password ? "border-destructive/60" : "border-border"
              }`}
            />
            {fieldErrors.password && (
              <p id="reg-password-error" className="text-xs text-destructive" role="alert">
                {fieldErrors.password}
              </p>
            )}
          </div>
          <button
            type="submit"
            disabled={pending}
            className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-bold text-sm hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            {pending ? "جاري الإنشاء…" : "تسجيل والدخول"}
          </button>
          <p className="text-center text-sm text-muted-foreground">
            لديك حساب؟{" "}
            <Link href={loginHref} className="text-primary font-semibold hover:underline">
              تسجيل الدخول
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
