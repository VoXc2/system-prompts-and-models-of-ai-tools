"use client";

/** مخططات SVG ثابتة — بديل الإضاءة الزخرفية: توضح طبقات المنتج بصرياً. */

export function HeroStatMiniDiagram({ variant }: { variant: "agents" | "clock" | "sar" | "funnel" }) {
  const common = "h-14 w-full max-w-[9rem] mx-auto text-teal-400/90";
  if (variant === "agents") {
    return (
      <svg viewBox="0 0 120 56" className={common} aria-hidden>
        <path d="M8 44 L8 12 L32 12 L32 28 L56 28 L56 44" fill="none" stroke="currentColor" strokeWidth="2" />
        <circle cx="8" cy="12" r="4" fill="currentColor" opacity="0.35" />
        <circle cx="32" cy="12" r="4" fill="currentColor" opacity="0.55" />
        <circle cx="56" cy="28" r="4" fill="currentColor" opacity="0.75" />
        <circle cx="32" cy="44" r="4" fill="currentColor" />
        <text x="64" y="20" fill="#64748b" fontSize="8">
          وكلاء + إشراف
        </text>
      </svg>
    );
  }
  if (variant === "clock") {
    return (
      <svg viewBox="0 0 120 56" className={common} aria-hidden>
        <circle cx="28" cy="28" r="22" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.4" />
        <path d="M28 28 L28 14 M28 28 L40 36" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <circle cx="85" cy="28" r="3" fill="currentColor" opacity="0.5" />
        <circle cx="95" cy="18" r="3" fill="currentColor" opacity="0.35" />
        <circle cx="95" cy="38" r="3" fill="currentColor" opacity="0.35" />
        <text x="58" y="52" fill="#64748b" fontSize="7">
          قنوات مستمرة
        </text>
      </svg>
    );
  }
  if (variant === "sar") {
    return (
      <svg viewBox="0 0 120 56" className={common} aria-hidden>
        <rect x="8" y="32" width="16" height="20" rx="2" fill="currentColor" opacity="0.35" />
        <rect x="32" y="22" width="16" height="30" rx="2" fill="currentColor" opacity="0.55" />
        <rect x="56" y="12" width="16" height="40" rx="2" fill="currentColor" opacity="0.75" />
        <rect x="80" y="18" width="16" height="34" rx="2" fill="currentColor" />
        <text x="8" y="10" className="fill-slate-500 text-[8px] font-sans">
          تقارير بالريال
        </text>
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 120 56" className={common} aria-hidden>
      <path d="M10 48 L30 20 L50 32 L70 14 L90 28 L110 18" fill="none" stroke="currentColor" strokeWidth="2" />
      <circle cx="30" cy="20" r="3" fill="currentColor" />
      <circle cx="50" cy="32" r="3" fill="currentColor" opacity="0.8" />
      <circle cx="70" cy="14" r="3" fill="currentColor" opacity="0.6" />
      <circle cx="90" cy="28" r="3" fill="currentColor" opacity="0.45" />
      <text x="8" y="10" fill="#64748b" fontSize="7">
        مسار الصفقة
      </text>
    </svg>
  );
}

export function FeatureCardDiagram({ variant }: { variant: "layers" | "channels" | "memory" | "shield" }) {
  const box = "h-24 w-full rounded-lg border border-teal-500/20 bg-slate-950/40 p-2";
  if (variant === "layers") {
    return (
      <div className={box} aria-hidden>
        <svg viewBox="0 0 200 72" className="h-full w-full text-teal-400/80">
          <rect x="10" y="8" width="180" height="14" rx="3" fill="currentColor" opacity="0.15" />
          <rect x="20" y="28" width="160" height="14" rx="3" fill="currentColor" opacity="0.28" />
          <rect x="30" y="48" width="140" height="14" rx="3" fill="currentColor" opacity="0.42" />
          <text x="100" y="68" textAnchor="middle" fill="#64748b" fontSize="9">
            طبقات: اكتشاف → إغلاق
          </text>
        </svg>
      </div>
    );
  }
  if (variant === "channels") {
    return (
      <div className={box} aria-hidden>
        <svg viewBox="0 0 200 72" className="h-full w-full text-cyan-400/80">
          <circle cx="40" cy="36" r="14" fill="none" stroke="currentColor" strokeWidth="1.5" />
          <circle cx="100" cy="36" r="14" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.7" />
          <circle cx="160" cy="36" r="14" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.45" />
          <path d="M54 36 H86 M114 36 H146" stroke="currentColor" strokeWidth="1" opacity="0.5" />
          <text x="100" y="68" textAnchor="middle" fill="#64748b" fontSize="9">
            واتساب · بريد · CRM
          </text>
        </svg>
      </div>
    );
  }
  if (variant === "memory") {
    return (
      <div className={box} aria-hidden>
        <svg viewBox="0 0 200 72" className="h-full w-full text-emerald-400/80">
          <ellipse cx="100" cy="32" rx="70" ry="22" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
          <circle cx="70" cy="32" r="6" fill="currentColor" opacity="0.5" />
          <circle cx="100" cy="32" r="6" fill="currentColor" opacity="0.75" />
          <circle cx="130" cy="32" r="6" fill="currentColor" />
          <path d="M76 32 H94 M106 32 H124" stroke="currentColor" strokeWidth="1" opacity="0.4" />
          <text x="100" y="68" textAnchor="middle" fill="#64748b" fontSize="9">
            سياق لكل عميل
          </text>
        </svg>
      </div>
    );
  }
  return (
    <div className={box} aria-hidden>
      <svg viewBox="0 0 200 72" className="h-full w-full text-teal-400/80">
        <rect x="40" y="16" width="120" height="36" rx="4" fill="none" stroke="currentColor" strokeWidth="1.5" />
        <path d="M55 34 L70 44 L95 24 L120 40 L145 28" fill="none" stroke="currentColor" strokeWidth="2" />
        <text x="100" y="68" textAnchor="middle" fill="#64748b" fontSize="9">
          عزل · تدقيق · تقارير
        </text>
      </svg>
    </div>
  );
}
