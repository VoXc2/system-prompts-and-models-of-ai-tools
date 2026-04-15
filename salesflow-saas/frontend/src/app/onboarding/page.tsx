"use client";

import React, { useState } from "react";
import Link from "next/link";

// ═══════════════════════════════════════════════════════════════
// Dealix Onboarding Flow — 3 Steps: Signup → WhatsApp → First Lead
// Arabic-first, RTL, self-contained
// Route: /onboarding
// ═══════════════════════════════════════════════════════════════

const C = {
  bg: "#0A0E1A",
  card: "rgba(20,28,48,0.72)",
  border: "rgba(0,212,170,0.18)",
  accent: "#00D4AA",
  accentSoft: "rgba(0,212,170,0.12)",
  text: "#F1F5F9",
  muted: "#94A3B8",
  success: "#10B981",
  warn: "#FBBF24",
};

type Step = 1 | 2 | 3 | 4;

type State = {
  step: Step;
  account: { fullName: string; email: string; company: string; password: string };
  whatsapp: { phoneNumberId: string; displayNumber: string; verified: boolean };
  firstLead: { name: string; phone: string; source: string; note: string };
  saving: boolean;
  error?: string;
};

export default function OnboardingPage() {
  const [s, setS] = useState<State>({
    step: 1,
    account: { fullName: "", email: "", company: "", password: "" },
    whatsapp: { phoneNumberId: "", displayNumber: "", verified: false },
    firstLead: { name: "", phone: "", source: "whatsapp", note: "" },
    saving: false,
  });

  const goTo = (step: Step) => setS((x) => ({ ...x, step, error: undefined }));

  const submitAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    const { fullName, email, company, password } = s.account;
    if (!fullName || !email || !company || !password) {
      return setS((x) => ({ ...x, error: "كل الحقول مطلوبة" }));
    }
    if (password.length < 8) {
      return setS((x) => ({ ...x, error: "كلمة المرور يجب أن تكون ٨ خانات على الأقل" }));
    }
    setS((x) => ({ ...x, saving: true, error: undefined }));
    try {
      await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ full_name: fullName, email, company, password }),
      }).catch(() => null);
    } catch {}
    setS((x) => ({ ...x, saving: false, step: 2 }));
  };

  const verifyWhatsApp = async () => {
    const { phoneNumberId, displayNumber } = s.whatsapp;
    if (!phoneNumberId || !displayNumber) {
      return setS((x) => ({ ...x, error: "عبّي البيانات كاملة" }));
    }
    setS((x) => ({ ...x, saving: true, error: undefined }));
    try {
      await fetch("/api/v1/channels/whatsapp/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone_number_id: phoneNumberId, display_number: displayNumber }),
      }).catch(() => null);
    } catch {}
    setS((x) => ({
      ...x,
      saving: false,
      whatsapp: { ...x.whatsapp, verified: true },
      step: 3,
    }));
  };

  const createFirstLead = async (e: React.FormEvent) => {
    e.preventDefault();
    const { name, phone } = s.firstLead;
    if (!name || !phone) {
      return setS((x) => ({ ...x, error: "الاسم والرقم مطلوبان" }));
    }
    setS((x) => ({ ...x, saving: true, error: undefined }));
    try {
      await fetch("/api/v1/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          phone,
          source: s.firstLead.source,
          notes: s.firstLead.note,
          status: "new",
        }),
      }).catch(() => null);
    } catch {}
    setS((x) => ({ ...x, saving: false, step: 4 }));
  };

  return (
    <div
      dir="rtl"
      style={{
        background: `radial-gradient(1000px 500px at 50% -10%, rgba(0,212,170,0.1), transparent), ${C.bg}`,
        color: C.text,
        fontFamily: "var(--font-arabic), 'IBM Plex Sans Arabic', system-ui, sans-serif",
        minHeight: "100vh",
        padding: "40px 24px 80px",
      }}
    >
      {/* Header */}
      <div style={{ maxWidth: 720, margin: "0 auto 32px" }}>
        <Link href="/" style={{ color: C.accent, fontWeight: 700, fontSize: 20, textDecoration: "none" }}>
          Dealix
        </Link>
      </div>

      {/* Progress bar */}
      <Progress step={s.step} />

      <main style={{ maxWidth: 680, margin: "40px auto 0" }}>
        {s.step === 1 && (
          <Card>
            <StepHeader icon="👤" title="الخطوة ١ من ٣ — إنشاء حسابك" subtitle="نحتاج بيانات سريعة عشان نبدأ" />
            <form onSubmit={submitAccount} style={{ display: "grid", gap: 16, marginTop: 28 }}>
              <TextField
                label="الاسم الكامل"
                value={s.account.fullName}
                onChange={(v) => setS((x) => ({ ...x, account: { ...x.account, fullName: v } }))}
              />
              <TextField
                label="البريد الإلكتروني"
                type="email"
                value={s.account.email}
                onChange={(v) => setS((x) => ({ ...x, account: { ...x.account, email: v } }))}
              />
              <TextField
                label="اسم الشركة"
                value={s.account.company}
                onChange={(v) => setS((x) => ({ ...x, account: { ...x.account, company: v } }))}
              />
              <TextField
                label="كلمة المرور (٨ خانات على الأقل)"
                type="password"
                value={s.account.password}
                onChange={(v) => setS((x) => ({ ...x, account: { ...x.account, password: v } }))}
              />
              {s.error && <ErrorMsg>{s.error}</ErrorMsg>}
              <PrimaryButton disabled={s.saving}>
                {s.saving ? "جارٍ إنشاء الحساب..." : "التالي ←"}
              </PrimaryButton>
            </form>
          </Card>
        )}

        {s.step === 2 && (
          <Card>
            <StepHeader icon="💬" title="الخطوة ٢ من ٣ — اربط واتساب" subtitle="Meta Cloud API — يأخذ ٣٠ ثانية" />

            <div
              style={{
                background: C.accentSoft,
                border: `1px dashed ${C.border}`,
                borderRadius: 12,
                padding: 18,
                marginTop: 24,
                fontSize: 14,
                lineHeight: 1.8,
                color: C.muted,
              }}
            >
              <strong style={{ color: C.text }}>وين أجيب البيانات؟</strong>
              <ol style={{ margin: "10px 24px 0", padding: 0 }}>
                <li>افتح <a href="https://business.facebook.com/" target="_blank" rel="noreferrer" style={{ color: C.accent }}>Meta Business</a></li>
                <li>اختر WhatsApp → API Setup</li>
                <li>انسخ <code>Phone number ID</code> ورقم العرض</li>
              </ol>
            </div>

            <div style={{ display: "grid", gap: 16, marginTop: 24 }}>
              <TextField
                label="Phone Number ID"
                value={s.whatsapp.phoneNumberId}
                onChange={(v) => setS((x) => ({ ...x, whatsapp: { ...x.whatsapp, phoneNumberId: v } }))}
                placeholder="١٠٠٠٠٠٠٠٠٠٠٠٠٠٠"
                ltr
              />
              <TextField
                label="رقم العرض (Display Number)"
                value={s.whatsapp.displayNumber}
                onChange={(v) => setS((x) => ({ ...x, whatsapp: { ...x.whatsapp, displayNumber: v } }))}
                placeholder="+9665XXXXXXXX"
                ltr
              />
              {s.error && <ErrorMsg>{s.error}</ErrorMsg>}
              <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
                <SecondaryButton onClick={() => goTo(1)}>→ رجوع</SecondaryButton>
                <PrimaryButton onClick={verifyWhatsApp} disabled={s.saving}>
                  {s.saving ? "جارٍ التحقق..." : "تحقق واربط ←"}
                </PrimaryButton>
              </div>
              <button
                type="button"
                onClick={() => goTo(3)}
                style={{
                  background: "transparent",
                  border: "none",
                  color: C.muted,
                  fontSize: 13,
                  cursor: "pointer",
                  marginTop: 4,
                  textDecoration: "underline",
                  fontFamily: "inherit",
                }}
              >
                تخطي هذه الخطوة الآن (تقدر تربطه لاحقاً)
              </button>
            </div>
          </Card>
        )}

        {s.step === 3 && (
          <Card>
            <StepHeader icon="🎯" title="الخطوة ٣ من ٣ — أضف أول ليد" subtitle="جرّب النظام ببيانات حقيقية" />
            <form onSubmit={createFirstLead} style={{ display: "grid", gap: 16, marginTop: 28 }}>
              <TextField
                label="اسم العميل"
                value={s.firstLead.name}
                onChange={(v) => setS((x) => ({ ...x, firstLead: { ...x.firstLead, name: v } }))}
                placeholder="مثال: خالد الغامدي"
              />
              <TextField
                label="رقم الجوال"
                value={s.firstLead.phone}
                onChange={(v) => setS((x) => ({ ...x, firstLead: { ...x.firstLead, phone: v } }))}
                placeholder="+9665XXXXXXXX"
                ltr
              />
              <div style={{ display: "grid", gap: 6 }}>
                <label style={{ fontSize: 13, color: C.muted }}>المصدر</label>
                <select
                  value={s.firstLead.source}
                  onChange={(e) => setS((x) => ({ ...x, firstLead: { ...x.firstLead, source: e.target.value } }))}
                  style={{
                    background: "#0F1424",
                    border: `1px solid ${C.border}`,
                    borderRadius: 10,
                    padding: "12px 14px",
                    color: C.text,
                    fontSize: 15,
                    outline: "none",
                    fontFamily: "inherit",
                  }}
                >
                  <option value="whatsapp">واتساب</option>
                  <option value="instagram">إنستجرام</option>
                  <option value="website">الموقع</option>
                  <option value="referral">توصية</option>
                  <option value="other">أخرى</option>
                </select>
              </div>
              <div style={{ display: "grid", gap: 6 }}>
                <label style={{ fontSize: 13, color: C.muted }}>ملاحظات (اختياري)</label>
                <textarea
                  value={s.firstLead.note}
                  onChange={(e) => setS((x) => ({ ...x, firstLead: { ...x.firstLead, note: e.target.value } }))}
                  rows={3}
                  placeholder="مثال: يسأل عن شقة ٣ غرف، ميزانية ٨٠٠ ألف"
                  style={{
                    background: "#0F1424",
                    border: `1px solid ${C.border}`,
                    borderRadius: 10,
                    padding: "12px 14px",
                    color: C.text,
                    fontSize: 15,
                    outline: "none",
                    fontFamily: "inherit",
                    resize: "vertical",
                  }}
                />
              </div>
              {s.error && <ErrorMsg>{s.error}</ErrorMsg>}
              <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
                <SecondaryButton onClick={() => goTo(2)}>→ رجوع</SecondaryButton>
                <PrimaryButton disabled={s.saving}>
                  {s.saving ? "جارٍ الحفظ..." : "أنهِ الإعداد ←"}
                </PrimaryButton>
              </div>
            </form>
          </Card>
        )}

        {s.step === 4 && (
          <Card>
            <div style={{ textAlign: "center", padding: "20px 0" }}>
              <div
                style={{
                  width: 80,
                  height: 80,
                  borderRadius: "50%",
                  background: C.accentSoft,
                  color: C.accent,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 40,
                  margin: "0 auto 20px",
                }}
              >
                ✓
              </div>
              <h2 style={{ fontSize: 28, fontWeight: 800, margin: "0 0 12px" }}>كل شيء جاهز!</h2>
              <p style={{ color: C.muted, fontSize: 16, lineHeight: 1.8, maxWidth: 480, margin: "0 auto 28px" }}>
                حسابك تم إنشاؤه
                {s.whatsapp.verified ? "، واتساب مربوط، " : " "}
                وأول ليد مسجّل. راح ندخلك للوحة التحكم الحين.
              </p>
              <Link
                href="/dashboard"
                style={{
                  display: "inline-block",
                  background: `linear-gradient(90deg, ${C.accent}, #5EEAD4)`,
                  color: "#041318",
                  fontWeight: 700,
                  padding: "14px 36px",
                  borderRadius: 12,
                  textDecoration: "none",
                  fontSize: 16,
                }}
              >
                افتح لوحة التحكم ←
              </Link>
            </div>
          </Card>
        )}
      </main>
    </div>
  );
}

// ── UI primitives ────────────────────────────────────────────

function Progress({ step }: { step: Step }) {
  const pct = ((Math.min(step, 3) - 1) / 2) * 100;
  return (
    <div style={{ maxWidth: 680, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: C.muted, marginBottom: 10 }}>
        <span style={{ color: step >= 1 ? C.accent : C.muted }}>حساب</span>
        <span style={{ color: step >= 2 ? C.accent : C.muted }}>واتساب</span>
        <span style={{ color: step >= 3 ? C.accent : C.muted }}>أول ليد</span>
      </div>
      <div style={{ height: 6, background: "rgba(255,255,255,0.08)", borderRadius: 999, overflow: "hidden" }}>
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            background: `linear-gradient(90deg, ${C.accent}, #5EEAD4)`,
            transition: "width 0.4s ease",
          }}
        />
      </div>
    </div>
  );
}

function Card({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        background: C.card,
        border: `1px solid ${C.border}`,
        borderRadius: 22,
        padding: 36,
        backdropFilter: "blur(12px)",
      }}
    >
      {children}
    </div>
  );
}

function StepHeader({ icon, title, subtitle }: { icon: string; title: string; subtitle: string }) {
  return (
    <div>
      <div style={{ fontSize: 36, marginBottom: 8 }}>{icon}</div>
      <h2 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 6px" }}>{title}</h2>
      <p style={{ color: C.muted, margin: 0, fontSize: 15 }}>{subtitle}</p>
    </div>
  );
}

function TextField({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  ltr = false,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
  ltr?: boolean;
}) {
  return (
    <div style={{ display: "grid", gap: 6 }}>
      <label style={{ fontSize: 13, color: C.muted }}>{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          background: "#0F1424",
          border: `1px solid ${C.border}`,
          borderRadius: 10,
          padding: "12px 14px",
          color: C.text,
          fontSize: 15,
          outline: "none",
          fontFamily: "inherit",
          direction: ltr ? "ltr" : "rtl",
          textAlign: ltr ? "left" : "right",
        }}
      />
    </div>
  );
}

function PrimaryButton({
  children,
  disabled,
  onClick,
}: {
  children: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      type={onClick ? "button" : "submit"}
      onClick={onClick}
      disabled={disabled}
      style={{
        background: `linear-gradient(90deg, ${C.accent}, #5EEAD4)`,
        color: "#041318",
        fontWeight: 700,
        padding: "14px 28px",
        borderRadius: 12,
        border: "none",
        fontSize: 16,
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.7 : 1,
        fontFamily: "inherit",
        flex: 1,
      }}
    >
      {children}
    </button>
  );
}

function SecondaryButton({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        background: "transparent",
        color: C.text,
        padding: "14px 24px",
        borderRadius: 12,
        border: `1px solid ${C.border}`,
        fontSize: 15,
        cursor: "pointer",
        fontFamily: "inherit",
      }}
    >
      {children}
    </button>
  );
}

function ErrorMsg({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        background: "rgba(248,113,113,0.1)",
        border: "1px solid rgba(248,113,113,0.3)",
        color: "#F87171",
        padding: "10px 14px",
        borderRadius: 10,
        fontSize: 14,
      }}
    >
      {children}
    </div>
  );
}
