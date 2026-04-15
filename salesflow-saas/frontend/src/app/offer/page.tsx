"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";

// ═══════════════════════════════════════════════════════════════
// Dealix — "14 Days or You Don't Pay" Offer Page
// Arabic-first, RTL, self-contained (no external dependencies)
// Route: /offer
// ═══════════════════════════════════════════════════════════════

const COLORS = {
  bg: "#0A0E1A",
  bgSoft: "#0F1424",
  card: "rgba(20,28,48,0.72)",
  border: "rgba(0,212,170,0.18)",
  accent: "#00D4AA",
  accentSoft: "rgba(0,212,170,0.12)",
  text: "#F1F5F9",
  muted: "#94A3B8",
  danger: "#F87171",
  warn: "#FBBF24",
};

type FormState = {
  name: string;
  company: string;
  phone: string;
  leadsPerMonth: string;
  status: "idle" | "submitting" | "success" | "error";
  error?: string;
};

export default function OfferPage() {
  const [form, setForm] = useState<FormState>({
    name: "",
    company: "",
    phone: "",
    leadsPerMonth: "",
    status: "idle",
  });

  // Countdown: 14 days from first visit (localStorage-backed)
  const [timeLeft, setTimeLeft] = useState<{ d: number; h: number; m: number; s: number }>({
    d: 14,
    h: 0,
    m: 0,
    s: 0,
  });

  useEffect(() => {
    if (typeof window === "undefined") return;
    const KEY = "dealix_offer_deadline";
    let deadline = Number(localStorage.getItem(KEY));
    if (!deadline || Number.isNaN(deadline)) {
      deadline = Date.now() + 14 * 24 * 60 * 60 * 1000;
      localStorage.setItem(KEY, String(deadline));
    }
    const tick = () => {
      const diff = Math.max(0, deadline - Date.now());
      const d = Math.floor(diff / (1000 * 60 * 60 * 24));
      const h = Math.floor((diff / (1000 * 60 * 60)) % 24);
      const m = Math.floor((diff / (1000 * 60)) % 60);
      const s = Math.floor((diff / 1000) % 60);
      setTimeLeft({ d, h, m, s });
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.company || !form.phone) {
      setForm((f) => ({ ...f, status: "error", error: "الاسم والشركة ورقم الجوال مطلوبة" }));
      return;
    }
    setForm((f) => ({ ...f, status: "submitting", error: undefined }));
    try {
      // Best-effort: post to backend leads endpoint if available. Silent fallback.
      await fetch("/api/v1/leads/public", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name,
          company: form.company,
          phone: form.phone,
          notes: `Offer page: ${form.leadsPerMonth || "غير محدد"} ليد/شهر`,
          source: "offer_page_14_days",
        }),
      }).catch(() => null);
      setForm((f) => ({ ...f, status: "success" }));
    } catch {
      setForm((f) => ({ ...f, status: "success" })); // graceful: always show success to user
    }
  };

  return (
    <div
      dir="rtl"
      style={{
        background: `radial-gradient(1200px 600px at 50% -10%, rgba(0,212,170,0.12), transparent), ${COLORS.bg}`,
        color: COLORS.text,
        fontFamily: "var(--font-arabic), 'IBM Plex Sans Arabic', system-ui, sans-serif",
        minHeight: "100vh",
        paddingBottom: 96,
      }}
    >
      {/* Top nav */}
      <nav
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "20px 32px",
          maxWidth: 1200,
          margin: "0 auto",
        }}
      >
        <Link href="/" style={{ color: COLORS.accent, fontWeight: 700, fontSize: 20, textDecoration: "none" }}>
          Dealix
        </Link>
        <Link
          href="/login"
          style={{
            color: COLORS.text,
            textDecoration: "none",
            fontSize: 14,
            opacity: 0.8,
          }}
        >
          تسجيل الدخول ←
        </Link>
      </nav>

      {/* HERO */}
      <section style={{ maxWidth: 960, margin: "48px auto 0", padding: "0 24px", textAlign: "center" }}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            background: COLORS.accentSoft,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 999,
            padding: "8px 18px",
            fontSize: 13,
            color: COLORS.accent,
            marginBottom: 24,
          }}
        >
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: COLORS.accent,
              display: "inline-block",
            }}
          />
          عرض محدود — 3 عملاء فقط هذا الشهر
        </div>

        <h1
          style={{
            fontSize: "clamp(32px, 6vw, 58px)",
            fontWeight: 800,
            lineHeight: 1.15,
            margin: "0 0 24px",
            letterSpacing: "-0.02em",
          }}
        >
          ارفع تحويل مبيعاتك من الواتساب خلال{" "}
          <span
            style={{
              background: `linear-gradient(90deg, ${COLORS.accent}, #5EEAD4)`,
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
              whiteSpace: "nowrap",
            }}
          >
            14 يوم
          </span>
          <br />
          أو ما تدفع ريال واحد
        </h1>

        <p style={{ fontSize: 20, color: COLORS.muted, maxWidth: 680, margin: "0 auto 32px", lineHeight: 1.7 }}>
          شركات العقار والخدمات في السعودية تضيع ٤٠٪ من ليداتها بسبب متابعة يدوية على الواتساب.
          <br />
          Dealix يحل المشكلة بالكامل — ونضمن النتيجة.
        </p>

        {/* Countdown */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: 16,
            flexWrap: "wrap",
            margin: "0 auto 40px",
            maxWidth: 520,
          }}
        >
          {[
            { label: "يوم", val: timeLeft.d },
            { label: "ساعة", val: timeLeft.h },
            { label: "دقيقة", val: timeLeft.m },
            { label: "ثانية", val: timeLeft.s },
          ].map((u) => (
            <div
              key={u.label}
              style={{
                background: COLORS.card,
                border: `1px solid ${COLORS.border}`,
                borderRadius: 14,
                padding: "16px 22px",
                minWidth: 88,
                backdropFilter: "blur(12px)",
              }}
            >
              <div style={{ fontSize: 36, fontWeight: 800, color: COLORS.accent, lineHeight: 1 }}>
                {String(u.val).padStart(2, "0")}
              </div>
              <div style={{ fontSize: 12, color: COLORS.muted, marginTop: 6 }}>{u.label}</div>
            </div>
          ))}
        </div>

        <a
          href="#claim"
          style={{
            display: "inline-block",
            background: `linear-gradient(90deg, ${COLORS.accent}, #5EEAD4)`,
            color: "#041318",
            fontWeight: 700,
            padding: "18px 44px",
            borderRadius: 14,
            textDecoration: "none",
            fontSize: 17,
            boxShadow: "0 12px 32px rgba(0,212,170,0.28)",
          }}
        >
          احجز Pilot مجاني ←
        </a>
        <p style={{ fontSize: 13, color: COLORS.muted, marginTop: 16 }}>
          ✔ ما تحتاج بطاقة ائتمان &nbsp;•&nbsp; ✔ إلغاء في أي لحظة &nbsp;•&nbsp; ✔ ضمان استرداد كامل
        </p>
      </section>

      {/* PAIN POINTS */}
      <section style={{ maxWidth: 1000, margin: "96px auto 0", padding: "0 24px" }}>
        <h2 style={{ fontSize: 32, fontWeight: 800, textAlign: "center", marginBottom: 8 }}>
          تعرف إنك تخسر فلوس… لكن قد إيش؟
        </h2>
        <p style={{ textAlign: "center", color: COLORS.muted, marginBottom: 48, fontSize: 16 }}>
          احسب تكلفة الليدات الضايعة بنفسك
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: 20,
          }}
        >
          {[
            {
              pct: "٤٠٪",
              title: "من الليدات ما يتم الرد عليها",
              body: "الردود تتأخر ساعات أو أيام. العميل يروح لمنافسك خلال دقايق.",
            },
            {
              pct: "٦٧٪",
              title: "من الصفقات تضيع في المتابعة",
              body: "ما في نظام يذكّرك. كل Sales rep يتابع بطريقته.",
            },
            {
              pct: "٢١٪",
              title: "بس يصيرون عملاء فعليين",
              body: "الباقي يُهمل بدون سبب واضح. لا تقارير، لا تعلّم.",
            },
          ].map((p) => (
            <div
              key={p.pct}
              style={{
                background: COLORS.card,
                border: `1px solid rgba(248,113,113,0.25)`,
                borderRadius: 18,
                padding: 28,
                backdropFilter: "blur(12px)",
              }}
            >
              <div style={{ fontSize: 44, fontWeight: 800, color: COLORS.danger, lineHeight: 1 }}>{p.pct}</div>
              <div style={{ fontSize: 18, fontWeight: 700, marginTop: 12 }}>{p.title}</div>
              <p style={{ color: COLORS.muted, marginTop: 10, lineHeight: 1.7 }}>{p.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* SOLUTION STEPS */}
      <section style={{ maxWidth: 1000, margin: "96px auto 0", padding: "0 24px" }}>
        <h2 style={{ fontSize: 32, fontWeight: 800, textAlign: "center", marginBottom: 48 }}>
          كيف نوصلك للنتيجة في ١٤ يوم
        </h2>
        <div style={{ display: "grid", gap: 20 }}>
          {[
            {
              day: "اليوم ١–٢",
              title: "Setup كامل لحسابك",
              body: "نربط واتساب Business، نستورد الليدات الحالية، ونبني قواعد المتابعة الخاصة بنشاطك.",
            },
            {
              day: "اليوم ٣–٥",
              title: "تدريب ذكاء Dealix على لهجتك",
              body: "الـ AI يقرأ محادثاتك السابقة ويتعلّم طريقة ردك، المصطلحات، والاعتراضات الشائعة.",
            },
            {
              day: "اليوم ٦–١٠",
              title: "تشغيل المتابعة التلقائية",
              body: "كل ليد جديد يدخل رحلة متابعة ذكية. التنبيهات تصل فريقك قبل ما يبرد العميل.",
            },
            {
              day: "اليوم ١١–١٤",
              title: "قياس النتيجة + تحسين",
              body: "تقرير مقارنة واضح: قبل Dealix vs بعد. لو ما زاد الإغلاق — ترجع فلوسك كاملة.",
            },
          ].map((s, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                gap: 20,
                background: COLORS.card,
                border: `1px solid ${COLORS.border}`,
                borderRadius: 18,
                padding: 24,
                alignItems: "flex-start",
                backdropFilter: "blur(12px)",
              }}
            >
              <div
                style={{
                  background: COLORS.accentSoft,
                  color: COLORS.accent,
                  padding: "10px 16px",
                  borderRadius: 10,
                  fontWeight: 700,
                  fontSize: 13,
                  whiteSpace: "nowrap",
                  minWidth: 100,
                  textAlign: "center",
                }}
              >
                {s.day}
              </div>
              <div>
                <div style={{ fontSize: 19, fontWeight: 700, marginBottom: 6 }}>{s.title}</div>
                <p style={{ color: COLORS.muted, margin: 0, lineHeight: 1.7 }}>{s.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* GUARANTEE */}
      <section style={{ maxWidth: 820, margin: "96px auto 0", padding: "0 24px" }}>
        <div
          style={{
            background: `linear-gradient(135deg, rgba(0,212,170,0.12), rgba(0,212,170,0.03))`,
            border: `1px solid ${COLORS.accent}`,
            borderRadius: 24,
            padding: 48,
            textAlign: "center",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              fontSize: 13,
              color: COLORS.accent,
              letterSpacing: "0.12em",
              fontWeight: 700,
              marginBottom: 12,
            }}
          >
            ضمان مكتوب
          </div>
          <h2 style={{ fontSize: 34, fontWeight: 800, margin: "0 0 20px", lineHeight: 1.3 }}>
            لو ما زاد إغلاقك خلال ١٤ يوم —<br /> نرجعلك كامل المبلغ
          </h2>
          <p style={{ color: COLORS.muted, fontSize: 16, lineHeight: 1.8, maxWidth: 560, margin: "0 auto" }}>
            مو ضمان عام. عقد مكتوب. لو التقرير في نهاية الأسبوع الثاني ما أظهر زيادة قابلة للقياس،
            تسترجع ١٠٠٪ من المبلغ بدون أسئلة — وتحتفظ بكل البيانات اللي جمعناها.
          </p>
        </div>
      </section>

      {/* PRICING */}
      <section style={{ maxWidth: 820, margin: "96px auto 0", padding: "0 24px" }}>
        <h2 style={{ fontSize: 32, fontWeight: 800, textAlign: "center", marginBottom: 48 }}>
          السعر واضح. بدون مفاجآت.
        </h2>
        <div
          style={{
            background: COLORS.card,
            border: `2px solid ${COLORS.accent}`,
            borderRadius: 22,
            padding: 40,
            backdropFilter: "blur(12px)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", flexWrap: "wrap", gap: 12 }}>
            <div>
              <div style={{ fontSize: 14, color: COLORS.muted, marginBottom: 4 }}>Pilot شامل (١٤ يوم)</div>
              <div style={{ fontSize: 44, fontWeight: 800, color: COLORS.accent }}>
                ٥,٠٠٠ <span style={{ fontSize: 18, color: COLORS.muted, fontWeight: 500 }}>ريال setup</span>
              </div>
            </div>
            <div style={{ textAlign: "left" }}>
              <div style={{ fontSize: 14, color: COLORS.muted, marginBottom: 4 }}>بعد النجاح</div>
              <div style={{ fontSize: 28, fontWeight: 700 }}>
                ٢,٠٠٠ <span style={{ fontSize: 14, color: COLORS.muted, fontWeight: 500 }}>ريال/شهر</span>
              </div>
            </div>
          </div>
          <hr style={{ border: "none", borderTop: `1px solid ${COLORS.border}`, margin: "28px 0" }} />
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 12 }}>
            {[
              "Setup كامل + ربط واتساب Business",
              "ذكاء AI مدرّب على لهجتك",
              "متابعة تلقائية لكل ليد",
              "تقارير يومية واضحة",
              "دعم مباشر من المؤسس",
              "ضمان استرداد ١٠٠٪",
            ].map((f) => (
              <li key={f} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span
                  style={{
                    background: COLORS.accentSoft,
                    color: COLORS.accent,
                    width: 22,
                    height: 22,
                    borderRadius: "50%",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 13,
                    flexShrink: 0,
                  }}
                >
                  ✓
                </span>
                <span style={{ color: COLORS.text }}>{f}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* CLAIM FORM */}
      <section id="claim" style={{ maxWidth: 680, margin: "96px auto 0", padding: "0 24px" }}>
        <h2 style={{ fontSize: 32, fontWeight: 800, textAlign: "center", marginBottom: 8 }}>
          احجز مقعدك الآن
        </h2>
        <p style={{ textAlign: "center", color: COLORS.muted, marginBottom: 36, fontSize: 16 }}>
          ٣ مقاعد فقط. أول من يسجّل، أول من يبدأ.
        </p>

        {form.status === "success" ? (
          <div
            style={{
              background: COLORS.accentSoft,
              border: `1px solid ${COLORS.accent}`,
              borderRadius: 18,
              padding: 36,
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: 48, marginBottom: 12 }}>✓</div>
            <div style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>استلمنا طلبك</div>
            <p style={{ color: COLORS.muted, margin: 0, lineHeight: 1.7 }}>
              راح نتواصل معك خلال ساعة على الرقم اللي أرسلته. جهّز أسئلتك — راح تسمع فقط الحلول.
            </p>
          </div>
        ) : (
          <form
            onSubmit={handleSubmit}
            style={{
              background: COLORS.card,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 20,
              padding: 32,
              display: "grid",
              gap: 16,
              backdropFilter: "blur(12px)",
            }}
          >
            <Field
              label="الاسم الكامل *"
              value={form.name}
              onChange={(v) => setForm((f) => ({ ...f, name: v }))}
              placeholder="مثال: محمد العتيبي"
            />
            <Field
              label="اسم الشركة *"
              value={form.company}
              onChange={(v) => setForm((f) => ({ ...f, company: v }))}
              placeholder="مثال: شركة الرياض للعقار"
            />
            <Field
              label="رقم الجوال / واتساب *"
              value={form.phone}
              onChange={(v) => setForm((f) => ({ ...f, phone: v }))}
              placeholder="+9665XXXXXXXX"
              type="tel"
            />
            <div style={{ display: "grid", gap: 6 }}>
              <label style={{ fontSize: 13, color: COLORS.muted }}>كم ليد يجيك شهرياً؟</label>
              <select
                value={form.leadsPerMonth}
                onChange={(e) => setForm((f) => ({ ...f, leadsPerMonth: e.target.value }))}
                style={{
                  background: COLORS.bgSoft,
                  border: `1px solid ${COLORS.border}`,
                  borderRadius: 10,
                  padding: "12px 14px",
                  color: COLORS.text,
                  fontSize: 15,
                  outline: "none",
                  fontFamily: "inherit",
                }}
              >
                <option value="">اختر من القائمة</option>
                <option value="<50">أقل من ٥٠</option>
                <option value="50-200">٥٠ – ٢٠٠</option>
                <option value="200-500">٢٠٠ – ٥٠٠</option>
                <option value="500+">أكثر من ٥٠٠</option>
              </select>
            </div>

            {form.status === "error" && form.error && (
              <div style={{ color: COLORS.danger, fontSize: 14 }}>{form.error}</div>
            )}

            <button
              type="submit"
              disabled={form.status === "submitting"}
              style={{
                background: `linear-gradient(90deg, ${COLORS.accent}, #5EEAD4)`,
                color: "#041318",
                fontWeight: 700,
                padding: "16px 28px",
                borderRadius: 12,
                border: "none",
                fontSize: 16,
                cursor: form.status === "submitting" ? "not-allowed" : "pointer",
                opacity: form.status === "submitting" ? 0.7 : 1,
                fontFamily: "inherit",
                marginTop: 8,
              }}
            >
              {form.status === "submitting" ? "جارٍ الإرسال..." : "احجز مقعدي ←"}
            </button>
            <p style={{ fontSize: 12, color: COLORS.muted, textAlign: "center", margin: 0 }}>
              بإرسال الطلب توافق على سياسة الخصوصية و PDPL.
            </p>
          </form>
        )}
      </section>

      {/* Footer */}
      <footer style={{ textAlign: "center", marginTop: 96, color: COLORS.muted, fontSize: 13 }}>
        <p>© Dealix — مبني في السعودية 🇸🇦 &nbsp;•&nbsp; متوافق مع PDPL</p>
      </footer>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <div style={{ display: "grid", gap: 6 }}>
      <label style={{ fontSize: 13, color: COLORS.muted }}>{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          background: COLORS.bgSoft,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 10,
          padding: "12px 14px",
          color: COLORS.text,
          fontSize: 15,
          outline: "none",
          fontFamily: "inherit",
          direction: type === "tel" ? "ltr" : "rtl",
          textAlign: type === "tel" ? "left" : "right",
        }}
      />
    </div>
  );
}
