"use client";

/**
 * نظرة على منظومة Dealix — مخطط ثابت يغني عن الفيديو إلى حين إنتاج وسائط لاحقاً.
 */
export function DealixSystemOverview() {
  return (
    <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-slate-900/90 to-[#050a14] p-6 shadow-2xl md:p-10">
      <div className="mb-8 text-center">
        <h2 className="text-2xl font-black tracking-tight text-white md:text-3xl">لماذا Dealix — المنظومة كاملة</h2>
        <p className="mx-auto mt-3 max-w-2xl text-sm leading-relaxed text-slate-400 md:text-base">
          من أول لمسة تسويقية إلى التحصيل: طبقة واحدة تربط القنوات، الوكلاء، الحوكمة، وذاكرة الصفقة — ليس مجرد قمع
          إيرادات معزول.
        </p>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-teal-500/15 bg-black/30 p-4 md:p-6">
        <svg
          viewBox="0 0 720 200"
          className="mx-auto h-auto w-full min-w-[560px] text-teal-300"
          role="img"
          aria-labelledby="sys-overview-title"
        >
          <title id="sys-overview-title">مسار Dealix من التأهيل إلى التحصيل</title>
          <defs>
            <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgb(45 212 191)" stopOpacity="0.35" />
              <stop offset="100%" stopColor="rgb(52 211 153)" stopOpacity="0.9" />
            </linearGradient>
          </defs>

          {/* stages */}
          {[
            { x: 20, label: "تأهيل", sub: "Leads" },
            { x: 140, label: "متابعة", sub: "قنوات" },
            { x: 260, label: "عرض", sub: "CRM" },
            { x: 380, label: "إغلاق", sub: "موافقات" },
            { x: 500, label: "تحصيل", sub: "SAR" },
            { x: 620, label: "تحليل", sub: "KPI" },
          ].map((s, i) => (
            <g key={s.label}>
              <rect
                x={s.x}
                y="56"
                width="88"
                height="72"
                rx="10"
                fill="rgb(15 23 42)"
                stroke="url(#g1)"
                strokeWidth="1.5"
                opacity={0.5 + i * 0.08}
              />
              <text x={s.x + 44} y="88" textAnchor="middle" fill="#f8fafc" fontSize="11" fontWeight="700">
                {s.label}
              </text>
              <text x={s.x + 44} y="108" textAnchor="middle" fill="#64748b" fontSize="9">
                {s.sub}
              </text>
            </g>
          ))}

          {/* arrows */}
          {[108, 228, 348, 468, 588].map((x) => (
            <path
              key={x}
              d={`M${x} 92 L${x + 24} 92`}
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              opacity="0.45"
            />
          ))}

          {/* agents row */}
          <text x="360" y="28" textAnchor="middle" fill="#99f6e4" fontSize="12" fontWeight="700">
            وكلاء + حوكمة عبر كامل الدورة
          </text>
          <rect x="200" y="148" width="320" height="36" rx="8" fill="rgb(6 78 59 / 0.35)" stroke="currentColor" strokeWidth="1" opacity="0.6" />
          <text x="360" y="170" textAnchor="middle" fill="#cbd5e1" fontSize="10">
            PDPL · سجلات · عزل مستأجرين · تكاملات مفتوحة
          </text>
        </svg>
      </div>

      <ul className="mt-6 grid gap-3 text-sm text-slate-400 sm:grid-cols-3">
        <li className="rounded-xl border border-white/5 bg-white/[0.03] px-4 py-3 text-center">
          <span className="font-semibold text-teal-200">قبل الإرسال الحساس</span>
          <br />
          موافقات وسياسات
        </li>
        <li className="rounded-xl border border-white/5 bg-white/[0.03] px-4 py-3 text-center">
          <span className="font-semibold text-teal-200">ذاكرة الصفقة</span>
          <br />
          لا فقدان سياق
        </li>
        <li className="rounded-xl border border-white/5 bg-white/[0.03] px-4 py-3 text-center">
          <span className="font-semibold text-teal-200">سياق سعودي</span>
          <br />
          عملة ووقت وزاتكا جاهزة للمسار
        </li>
      </ul>
    </section>
  );
}
