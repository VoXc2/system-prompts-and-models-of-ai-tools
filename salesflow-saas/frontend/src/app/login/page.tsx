"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ShieldCheck } from "lucide-react";
import { DealixAuthBrandMark } from "@/components/dealix-auth-brand-mark";
import { useAuth } from "@/contexts/auth-context";
import {
  LOGIN_PASSWORD_MIN_LEN,
  authFormMsg,
  isValidEmailFormat,
} from "@/lib/auth-form-validation";

export default function LoginPage() {
  const { login } = useAuth();
  const [nextParam, setNextParam] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    setNextParam(p.get("next"));
  }, []);

  function validate(): boolean {
    setEmailError(null);
    setPasswordError(null);
    let ok = true;
    const em = email.trim();
    if (!em) {
      setEmailError(authFormMsg.emailRequired);
      ok = false;
    } else if (!isValidEmailFormat(em)) {
      setEmailError(authFormMsg.emailInvalid);
      ok = false;
    }
    if (!password) {
      setPasswordError(authFormMsg.passwordRequired);
      ok = false;
    } else if (password.length < LOGIN_PASSWORD_MIN_LEN) {
      setPasswordError(authFormMsg.passwordShortLogin);
      ok = false;
    }
    return ok;
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!validate()) return;
    setPending(true);
    try {
      await login(email.trim(), password, nextParam);
    } catch (err) {
      setError(err instanceof Error ? err.message : "فشل تسجيل الدخول");
    } finally {
      setPending(false);
    }
  }

  const registerHref = nextParam
    ? `/register?next=${encodeURIComponent(nextParam)}`
    : "/register";

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden p-6">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(20,184,166,0.12),transparent)]"
        aria-hidden
      />
      <div className="relative w-full max-w-md space-y-8">
        <div className="space-y-3 text-center">
          <DealixAuthBrandMark />
          <div>
            <h1 className="text-2xl font-black tracking-tight">تسجيل الدخول</h1>
            <p className="mt-1 text-sm font-semibold text-muted-foreground">Dealix</p>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              أدخل بريدك وكلمة المرور للوصول إلى لوحة التشغيل.
            </p>
          </div>
        </div>

        <form
          noValidate
          onSubmit={onSubmit}
          className="space-y-5 rounded-2xl border border-border/60 bg-card/40 p-8 shadow-2xl shadow-black/25 backdrop-blur-md"
        >
          {error && (
            <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </div>
          )}
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
                if (emailError) setEmailError(null);
              }}
              aria-invalid={emailError ? true : undefined}
              aria-describedby={emailError ? "email-error" : undefined}
              className={`w-full rounded-xl border bg-secondary/40 px-4 py-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                emailError ? "border-destructive/60" : "border-border"
              }`}
            />
            {emailError && (
              <p id="email-error" className="text-xs text-destructive" role="alert">
                {emailError}
              </p>
            )}
          </div>
          <div className="space-y-2 text-right">
            <label htmlFor="password" className="text-sm font-medium">
              كلمة المرور
            </label>
            <p id="password-hint" className="text-xs text-muted-foreground">
              4 أحرف على الأقل.
            </p>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (passwordError) setPasswordError(null);
              }}
              aria-invalid={passwordError ? true : undefined}
              aria-describedby={
                passwordError ? "password-error password-hint" : "password-hint"
              }
              className={`w-full rounded-xl border bg-secondary/40 px-4 py-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                passwordError ? "border-destructive/60" : "border-border"
              }`}
            />
            {passwordError && (
              <p id="password-error" className="text-xs text-destructive" role="alert">
                {passwordError}
              </p>
            )}
          </div>
          <button
            type="submit"
            disabled={pending}
            className="w-full rounded-xl bg-primary py-3 text-sm font-bold text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {pending ? "جاري الدخول…" : "دخول"}
          </button>
          <p className="text-center text-sm text-muted-foreground">
            ليس لديك حساب؟{" "}
            <Link href={registerHref} className="font-semibold text-primary hover:underline">
              إنشاء شركة جديدة
            </Link>
          </p>
          <p className="text-center text-sm">
            <Link href="/explore" className="font-medium text-teal-400 hover:text-teal-300 hover:underline">
              استكشف شكل اللوحة أولاً — بدون تسجيل
            </Link>
          </p>
          <div className="flex items-start justify-center gap-2 rounded-xl border border-border/40 bg-secondary/20 px-3 py-2.5 text-center">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary/80" aria-hidden />
            <p className="text-[13px] leading-relaxed text-muted-foreground">
              جلسة مؤمّنة لحساب شركتك. لا تشارك كلمة المرور مع أي طرف.
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
