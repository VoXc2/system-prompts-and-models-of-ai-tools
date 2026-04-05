"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  MessageCircle,
  UserPlus,
  Link2,
  Cpu,
  LineChart,
  Rocket,
  ArrowLeft,
  Sparkles,
} from "lucide-react";

const STEPS = [
  {
    n: "١",
    title: "تواصل وتعريف",
    desc: "اجتماع أو رسالة أو طلب عرض: نحدّد قطاعكم، نضع التوقعات، ونوضّح الفرق بين «أتمتة بسيطة» ونظام تشغيل إيرادات كامل.",
    icon: MessageCircle,
  },
  {
    n: "٢",
    title: "إنشاء الحساب",
    desc: "تسجيل شركة + مالك (مستأجر جديد) مع جوال وبريد؛ تجربة منظّمة دون التزام مالي قبل الاتفاق — ثم ربط فريقكم تدريجياً.",
    icon: UserPlus,
  },
  {
    n: "٣",
    title: "التأهيل والربط",
    desc: "ربط قنوات (واتساب، بريد، CRM)، سياسات الحوكمة، وصلاحيات الفريق — حتى تدخل الصفقات والبيانات في طبقة واحدة.",
    icon: Link2,
  },
  {
    n: "٤",
    title: "تفعيل الوكلاء والمسارات",
    desc: "تشغيل وكلاء ذكاء لمسارات التأهيل والإغلاق والدعم، مع موافقات قبل الإرسال الحساس وذاكرة لا تُفقد.",
    icon: Cpu,
  },
  {
    n: "٥",
    title: "تشغيل يومي وتحصيل",
    desc: "متابعة صفقات، عروض، تحصيل بالريال، وتقارير تنفيذية — ترون أين تتسرب الصفقات وتسرّعون الإغلاق.",
    icon: LineChart,
  },
  {
    n: "٦",
    title: "شركة على منصة مبيعات شاملة",
    desc: "نفس المنظومة تصبح مركز إيرادات: تحليلات، تحسين مستمر، وتكاملات — وليس أداة معزولة عن بياناتكم.",
    icon: Rocket,
  },
] as const;

export function DealixCustomerJourneyLoop() {
  return (
    <section
      id="customer-journey-loop"
      className="relative scroll-mt-24 border-t border-white/5 bg-gradient-to-b from-[#030712] via-[#050a14] to-[#030712] py-20 md:py-28"
    >
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_70%_40%_at_50%_0%,rgba(20,184,166,0.12),transparent_60%)]"
        aria-hidden
      />

      <div className="relative mx-auto max-w-6xl px-6">
        <div className="mb-14 text-center md:mb-16">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-4 inline-flex items-center gap-2 rounded-full border border-teal-500/30 bg-teal-500/10 px-4 py-1.5 text-xs font-bold uppercase tracking-[0.2em] text-teal-200"
          >
            <Sparkles className="h-3.5 w-3.5" aria-hidden />
            من أول تواصل إلى منصة مبيعات شاملة
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.05 }}
            className="text-2xl font-black tracking-tight text-white md:text-4xl md:leading-snug"
          >
            اللوب الكامل لرحلتكم مع{" "}
            <span className="bg-gradient-to-l from-teal-300 to-cyan-300 bg-clip-text text-transparent">Dealix</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-slate-400 md:text-base"
          >
            هكذا يمشي العميل عندنا: من لمسة أولى واضحة، إلى حساب منظّم، ثم ربط وتفعيل، حتى تصبح شركتكم تعمل على منصة
            مبيعات وإيرادات متكاملة — لا مجرد «اشتراك في أداة».
          </motion.p>
        </div>

        <div className="relative">
          <div
            className="pointer-events-none absolute right-[calc(50%-1px)] top-0 hidden h-full w-0.5 bg-gradient-to-b from-teal-500/50 via-teal-500/20 to-transparent md:right-8 md:block lg:right-12"
            aria-hidden
          />

          <ol className="relative space-y-0">
            {STEPS.map((step, i) => {
              const Icon = step.icon;
              const isLast = i === STEPS.length - 1;
              return (
                <motion.li
                  key={step.n}
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-40px" }}
                  transition={{ delay: i * 0.06, duration: 0.45 }}
                  className={`relative flex flex-col gap-4 pb-12 md:flex-row md:items-start md:gap-8 md:pb-14 ${
                    !isLast ? "" : "pb-0"
                  }`}
                >
                  <div className="flex shrink-0 items-center gap-3 md:w-40 md:flex-col md:items-end md:gap-2 lg:w-48">
                    <span className="flex h-12 w-12 items-center justify-center rounded-2xl border border-teal-500/40 bg-teal-950/80 text-lg font-black text-teal-200 shadow-lg shadow-teal-900/30 md:h-14 md:w-14 md:text-xl">
                      {step.n}
                    </span>
                    <span className="hidden text-xs font-bold uppercase tracking-wider text-teal-500/90 md:block">
                      مرحلة
                    </span>
                  </div>

                  <div className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/[0.03] p-5 shadow-lg shadow-black/20 backdrop-blur-sm md:p-6">
                    <div className="mb-3 flex items-center gap-3">
                      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-500/15 text-teal-300">
                        <Icon className="h-5 w-5" strokeWidth={1.75} aria-hidden />
                      </span>
                      <h3 className="text-lg font-bold text-white md:text-xl">{step.title}</h3>
                    </div>
                    <p className="text-sm leading-relaxed text-slate-400 md:text-[15px]">{step.desc}</p>
                  </div>
                </motion.li>
              );
            })}
          </ol>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12 flex flex-col items-center justify-center gap-4 border-t border-white/10 pt-10 sm:flex-row sm:flex-wrap sm:gap-3"
        >
          <p className="w-full text-center text-sm text-slate-500 sm:w-auto">جاهز لرؤية الشكل داخل المنصة؟</p>
          <Link
            href="/explore"
            className="inline-flex items-center gap-2 rounded-full border border-teal-500/40 bg-teal-950/50 px-6 py-3 text-sm font-bold text-teal-100 transition hover:border-teal-400 hover:bg-teal-900/60"
          >
            جولة في اللوحة (مجاناً)
            <ArrowLeft className="h-4 w-4 rotate-180" aria-hidden />
          </Link>
          <Link
            href="/register?next=%2Fdashboard"
            className="inline-flex items-center gap-2 rounded-full bg-teal-500 px-6 py-3 text-sm font-bold text-slate-950 shadow-lg shadow-teal-900/40 transition hover:bg-teal-400"
          >
            إنشاء حساب شركة
            <ArrowLeft className="h-4 w-4 rotate-180" aria-hidden />
          </Link>
          <Link
            href="/login?next=%2Fdashboard"
            className="text-sm font-semibold text-slate-400 underline-offset-4 hover:text-teal-300 hover:underline"
          >
            لدي حساب بالفعل
          </Link>
        </motion.div>
      </div>
    </section>
  );
}
