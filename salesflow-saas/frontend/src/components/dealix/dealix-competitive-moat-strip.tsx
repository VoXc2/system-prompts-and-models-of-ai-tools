"use client";

import Link from "next/link";
import { Globe2, MessageCircle, Scale, Wallet } from "lucide-react";

/**
 * موضع Dealix مقارنةً بأدوات إيرادات أمريكية مرجعية (Gong / Outreach / Salesforce+).
 * يركّز على ما لا يقدّمه المنافس الأجنبي بنفس الجودة المحلية — وليس ادّعاء تفوق مطلق.
 */
export function DealixCompetitiveMoatStrip() {
  const rows = [
    {
      icon: Globe2,
      title: "سياق سعودي أولاً",
      body: "ريال، ساعات عمل الأحد–الخميس، PDPL، زاتكا/فوترة ضمن الرحلة — وليس قالب US-only.",
    },
    {
      icon: MessageCircle,
      title: "واتساب كقناة تشغيل",
      body: "قوالب، تسليم، موافقات قبل الإرسال الحساس — مقارنةً ببريد/مكالمات فقط في منصات الغرب.",
    },
    {
      icon: Wallet,
      title: "نظام إيرادات وليس «أداة مكالمات»",
      body: "صفقة، تحصيل، عمولات، مسوّقون — طبقة واحدة تُقاس على الإغلاق لا على النشاط فقط.",
    },
    {
      icon: Scale,
      title: "حوكمة وامتثال قابل للتدقيق",
      body: "عزل مستأجرين، سجلات، أدوار — مسار واضح نحو ضوابط مؤسسية عندما ينضج ICP.",
    },
  ];

  return (
    <section
      id="market-moat"
      className="relative border-y border-white/10 bg-gradient-to-b from-slate-950/90 via-slate-900/40 to-slate-950/90 py-16 md:py-20"
      aria-labelledby="market-moat-heading"
    >
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-400/90">مقارنة معيارية</p>
          <h2 id="market-moat-heading" className="mt-3 text-2xl font-black tracking-tight text-white md:text-3xl">
            لماذا ليس «نسخة عربية» من Gong أو Outreach؟
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-slate-400 md:text-[15px]">
            الأدوات المرجعية قوية في سوقها — لكنها لم تُبنَ لـ B2B السعودي، ولا لعملة محلية، ولا لقناة واتساب كعمود فقري، ولا
            لمسار امتثال PDPL ضمن نفس لوحة التشغيل.
          </p>
        </div>
        <div className="mt-12 grid gap-5 sm:grid-cols-2">
          {rows.map((row) => (
            <article
              key={row.title}
              className="rounded-2xl border border-white/[0.08] bg-slate-950/50 p-6 text-right shadow-[0_20px_50px_-28px_rgba(0,0,0,0.75)] backdrop-blur-md"
            >
              <div className="flex items-start gap-4">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-teal-500/25 bg-teal-500/10 text-teal-200">
                  <row.icon className="h-5 w-5" aria-hidden />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">{row.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-400">{row.body}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
        <p className="mt-10 text-center text-xs text-slate-500">
          للخطة التفصيلية والمراحل:{" "}
          <Link href="/strategy" className="text-teal-400 underline-offset-4 hover:text-teal-300 hover:underline">
            صفحة الاستراتيجية
          </Link>
          {" · "}
          <Link href="/explore" className="text-teal-400 underline-offset-4 hover:text-teal-300 hover:underline">
            جولة اللوحة
          </Link>
        </p>
      </div>
    </section>
  );
}
