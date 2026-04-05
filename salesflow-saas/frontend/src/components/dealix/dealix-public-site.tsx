"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { DealixCustomerJourneyLoop } from "@/components/dealix/dealix-customer-journey-loop";
import { DealixCompetitiveMoatStrip } from "@/components/dealix/dealix-competitive-moat-strip";
import { DealixSystemOverview } from "@/components/dealix/dealix-system-overview";
import { FeatureCardDiagram, HeroStatMiniDiagram } from "@/components/dealix/dealix-landing-diagrams";
import { CeoDirectContactCard } from "@/components/dealix/ceo-direct-contact-card";
import {
  ArrowLeft,
  BarChart3,
  Sparkles,
  Layers,
  Shield,
  Download,
  LayoutDashboard,
  Cpu,
  Globe2,
  Workflow,
  Clock,
  Coins,
  MousePointer2,
  Smartphone,
  Menu,
  X,
  TrendingUp,
} from "lucide-react";

const heroStats = [
  {
    value: "34+",
    title: "مسارات وكلاء",
    hint: "تغطية مسارات التشغيل والإشراف",
    icon: Workflow,
    mini: "agents" as const,
  },
  {
    value: "24/7",
    title: "تشغيل مستمر",
    hint: "قنوات ومتابعة دون انقطاع",
    icon: Clock,
    mini: "clock" as const,
  },
  {
    value: "SAR",
    title: "عملة محلية",
    hint: "تسعير وتقارير بالريال السعودي",
    icon: Coins,
    mini: "sar" as const,
  },
  {
    value: "360°",
    title: "دورة إيرادات",
    hint: "من التأهيل حتى التحصيل في طبقة واحدة",
    icon: TrendingUp,
    mini: "funnel" as const,
  },
] as const;

const heroContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.06 },
  },
};

const heroItem = {
  hidden: { opacity: 0, y: 18 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] as const },
  },
};

const features = [
  {
    title: "وكلاء متعددون + إشراف",
    desc: "طبقات من الاكتشاف إلى الإغلاق مع حوكمة وموافقات قبل الإرسال الحساس.",
    icon: Layers,
    diagram: "layers" as const,
  },
  {
    title: "قنوات حقيقية",
    desc: "واتساب، بريد، لينكد إن، صوت — مع تكامل CRM ومسارات دفع وعقود.",
    icon: Globe2,
    diagram: "channels" as const,
  },
  {
    title: "ذاكرة وتطوير ذاتي",
    desc: "سياق لكل عميل وصفقة؛ حلقات تحسين مستمرة قابلة للقياس.",
    icon: Cpu,
    diagram: "memory" as const,
  },
  {
    title: "جاهزية مؤسسية",
    desc: "عزل متعدد المستأجرين، تدقيق، وتقارير تنفيذية — وليس مجرد شات بوت.",
    icon: Shield,
    diagram: "shield" as const,
  },
];

/**
 * صفحة هبوط عامة — مستوى أعلى من landing عادي: حركة، تباين، مسارات واضحة.
 * (Lovable.dev أداة خارجية؛ التصميم هنا منفّذ بالكامل في Next.js.)
 */
const navLinkClass =
  "rounded-lg px-3 py-2.5 text-sm text-slate-300 transition-colors hover:bg-white/5 hover:text-white xl:px-0 xl:py-0 xl:hover:bg-transparent";

export function DealixPublicSite() {
  const pathname = usePathname();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    setMobileNavOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!mobileNavOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [mobileNavOpen]);

  useEffect(() => {
    const onResize = () => {
      if (typeof window !== "undefined" && window.innerWidth >= 1280) {
        setMobileNavOpen(false);
      }
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 overflow-x-hidden">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(20,184,166,0.25),transparent)]" />
      <div className="pointer-events-none fixed top-0 right-0 h-[500px] w-[500px] rounded-full bg-teal-500/10 blur-[120px]" />
      <div className="pointer-events-none fixed bottom-0 left-0 h-[400px] w-[400px] rounded-full bg-cyan-500/10 blur-[100px]" />

      <header className="relative z-50 border-b border-white/5 bg-black/20 backdrop-blur-xl pointer-events-auto">
        <div className="mx-auto max-w-6xl px-4 py-3 sm:px-6 sm:py-4">
          <div className="flex min-h-[3.25rem] items-center justify-between gap-3">
            <Link
              href="/"
              className="flex min-w-0 flex-1 items-center gap-2.5 rounded-lg outline-none ring-offset-[#030712] focus-visible:ring-2 focus-visible:ring-teal-500/60 sm:gap-3 sm:flex-initial"
            >
              <div
                className="relative flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-slate-950/90 shadow-[inset_0_1px_0_rgba(255,255,255,.08),0_8px_28px_-10px_rgba(20,184,166,0.4)] sm:h-10 sm:w-10"
                aria-hidden
              >
                <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-teal-500/25 via-transparent to-emerald-600/15" />
                <BarChart3 className="relative h-[20px] w-[20px] text-teal-300 sm:h-[22px] sm:w-[22px]" strokeWidth={1.85} aria-hidden />
              </div>
              <div className="min-w-0 text-start">
                <p className="truncate text-base font-bold tracking-tight text-white sm:text-lg">Dealix</p>
                <p className="mt-0.5 line-clamp-2 text-[10px] font-semibold leading-snug text-teal-400/95 sm:text-xs sm:line-clamp-none">
                  <span className="hidden min-[380px]:inline">منصة لتشغيل المبيعات والإيرادات</span>
                  <span className="min-[380px]:hidden">منصة المبيعات</span>
                </p>
                <p className="mt-0.5 hidden text-[10px] leading-tight text-slate-500 min-[480px]:line-clamp-2 min-[480px]:block xl:line-clamp-none">
                  من التأهيل والمتابعة حتى العرض والتحصيل — للفرق B2B
                </p>
              </div>
            </Link>

            <nav
              className="hidden items-center gap-4 text-sm text-slate-400 xl:flex xl:gap-5 2xl:gap-7"
              aria-label="التنقل الرئيسي"
            >
              <a href="#product" className="shrink-0 whitespace-nowrap transition-colors hover:text-white">
                المنتج
              </a>
              <a href="#why" className="shrink-0 whitespace-nowrap transition-colors hover:text-white">
                لماذا Dealix
              </a>
              <Link href="/resources" className="shrink-0 whitespace-nowrap transition-colors hover:text-teal-300">
                التحميلات
              </Link>
              <Link href="/dealix-marketing/dashboard-guide" className="shrink-0 whitespace-nowrap transition-colors hover:text-teal-300">
                دليل لوحة التحكم
              </Link>
              <Link href="/marketers" className="shrink-0 whitespace-nowrap transition-colors hover:text-teal-300">
                المسوّقون
              </Link>
              <Link href="/help" className="shrink-0 whitespace-nowrap transition-colors hover:text-teal-300">
                الدعم
              </Link>
              <Link href="/strategy" className="shrink-0 whitespace-nowrap transition-colors hover:text-teal-300">
                الاستراتيجية
              </Link>
              <Link href="/explore" className="shrink-0 whitespace-nowrap font-semibold text-teal-300 transition-colors hover:text-teal-200">
                جولة اللوحة
              </Link>
              <a href="#ceo-contact" className="max-w-[10rem] shrink-0 text-end leading-snug transition-colors hover:text-amber-200/95 xl:max-w-none">
                تواصل مع المدير التنفيذي
              </a>
            </nav>

            <div className="flex shrink-0 items-center gap-2 sm:gap-3">
              <Link
                href="/explore"
                className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-teal-500/35 bg-teal-950/40 px-3 py-2 text-xs font-semibold text-teal-200 hover:border-teal-400/50 hover:bg-teal-900/50 sm:px-4 sm:text-sm"
              >
                استكشف اللوحة
              </Link>
              <Link
                href="/resources"
                className="hidden sm:inline-flex items-center gap-2 rounded-full border border-white/10 px-3 py-2 text-sm text-slate-300 hover:bg-white/5 sm:px-4"
              >
                <Download className="h-4 w-4 shrink-0" />
                <span className="hidden md:inline">موارد</span>
              </Link>
              <Link
                href="/login?next=/dashboard"
                prefetch={false}
                className="relative z-10 inline-flex items-center gap-1.5 rounded-full bg-teal-500 px-3 py-2 text-xs font-semibold text-slate-950 shadow-lg shadow-teal-500/30 transition hover:bg-teal-400 sm:gap-2 sm:px-5 sm:py-2.5 sm:text-sm"
              >
                <LayoutDashboard className="h-4 w-4 shrink-0" />
                <span className="hidden min-[400px]:inline">دخول المنصة</span>
                <span className="min-[400px]:hidden">دخول</span>
              </Link>
              <button
                type="button"
                className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-200 transition hover:bg-white/10 xl:hidden"
                aria-expanded={mobileNavOpen}
                aria-controls="dealix-public-mobile-nav"
                aria-label={mobileNavOpen ? "إغلاق القائمة" : "فتح القائمة"}
                onClick={() => setMobileNavOpen((o) => !o)}
              >
                {mobileNavOpen ? <X className="h-5 w-5" aria-hidden /> : <Menu className="h-5 w-5" aria-hidden />}
              </button>
            </div>
          </div>

          <nav
            id="dealix-public-mobile-nav"
            className={
              mobileNavOpen
                ? "mt-4 max-h-[min(70vh,32rem)] overflow-y-auto border-t border-white/10 pt-4 xl:hidden"
                : "hidden"
            }
            aria-label="التنقل — قائمة الجوال"
          >
            <div className="flex flex-col gap-0.5 pb-2">
              <a href="#product" className={navLinkClass} onClick={() => setMobileNavOpen(false)}>
                المنتج
              </a>
              <a href="#why" className={navLinkClass} onClick={() => setMobileNavOpen(false)}>
                لماذا Dealix
              </a>
              <Link href="/resources" className={navLinkClass} onClick={() => setMobileNavOpen(false)}>
                التحميلات
              </Link>
              <Link href="/dealix-marketing/dashboard-guide" className={navLinkClass} onClick={() => setMobileNavOpen(false)}>
                دليل لوحة التحكم
              </Link>
              <Link href="/marketers" className={navLinkClass} onClick={() => setMobileNavOpen(false)}>
                المسوّقون
              </Link>
              <Link href="/help" className={navLinkClass} onClick={() => setMobileNavOpen(false)}>
                الدعم
              </Link>
              <Link href="/strategy" className={navLinkClass} onClick={() => setMobileNavOpen(false)}>
                الاستراتيجية
              </Link>
              <Link href="/explore" className={navLinkClass} onClick={() => setMobileNavOpen(false)}>
                جولة في اللوحة (بدون تسجيل)
              </Link>
              <a href="#ceo-contact" className={navLinkClass} onClick={() => setMobileNavOpen(false)}>
                تواصل مع المدير التنفيذي
              </a>
            </div>
          </nav>
        </div>
      </header>

      <main className="relative z-10">
        <section className="mx-auto max-w-6xl px-6 pt-20 pb-24 md:pt-28 md:pb-32">
          <motion.div
            variants={heroContainer}
            initial="hidden"
            animate="show"
            className="mx-auto max-w-3xl text-center"
          >
            <motion.div variants={heroItem} className="mb-6 inline-flex items-center gap-2 rounded-full border border-teal-500/30 bg-teal-500/10 px-4 py-1.5 text-xs font-medium text-teal-200">
              <Sparkles className="h-3.5 w-3.5" />
              نظام تشغيل إيرادات B2B — سعودي المنطلق
            </motion.div>
            <motion.h1
              variants={heroItem}
              className="text-4xl font-extrabold leading-[1.15] tracking-tight md:text-6xl md:leading-[1.1]"
            >
              حوّل دورة المبيعات إلى{" "}
              <span className="bg-gradient-to-r from-teal-300 via-emerald-300 to-cyan-300 bg-clip-text text-transparent">
                آلة إيرادات
              </span>{" "}
              تعمل مع فريقك — لا ضدّه
            </motion.h1>
            <motion.div variants={heroItem} className="mt-6 space-y-5 text-center">
              <p className="text-lg font-semibold leading-relaxed text-slate-100 md:text-xl md:leading-snug">
                ليس «صفحة تسويق» — بل{" "}
                <span className="text-teal-300">تشغيل كامل لدورة الإيرادات</span>: من أول لمسة إلى
                التحصيل، مع وكلاء ذكاء،{" "}
                <span className="text-teal-200/95">موافقات قبل الإرسال الحسّاس</span>، وذاكرة لا
                تفقد سياق الصفقة.
              </p>
              <p className="mx-auto max-w-2xl text-base leading-relaxed text-slate-400 md:text-lg">
                منصّة واحدة تربط قنواتك وCRM وبياناتك؛ ترى أين تتسرب الصفقات، وتسرّع الإغلاق بقرارات
                مبنية على أرقام — مُهندسة للشركات B2B في السعودية (عملة ووقت وتشغيل محلي).
              </p>
              <ul
                className="m-0 flex list-none flex-wrap items-center justify-center gap-2 p-0 pt-1"
                aria-label="محاور المنصة"
              >
                {[
                  "توليد وتأهيل",
                  "متابعة متعددة القنوات",
                  "عروض وإغلاق",
                  "تحصيل وتحليلات",
                  "حوكمة وذاكرة",
                  "تكامل CRM",
                ].map((label, i) => (
                  <motion.li
                    key={label}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 + i * 0.05, duration: 0.35 }}
                    whileHover={{ scale: 1.04, borderColor: "rgba(45, 212, 191, 0.45)" }}
                    className="cursor-default rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs font-semibold text-teal-100/95 shadow-sm transition-colors hover:bg-teal-500/10"
                  >
                    {label}
                  </motion.li>
                ))}
              </ul>
            </motion.div>
            <motion.div
              variants={heroItem}
              className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row sm:flex-wrap"
            >
              <Link
                href="/explore"
                className="relative z-10 inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-2xl border-2 border-teal-400/50 bg-teal-950/50 px-8 py-4 text-base font-bold text-teal-100 shadow-lg shadow-teal-900/30 transition hover:scale-[1.02] hover:border-teal-300 hover:bg-teal-900/60"
              >
                جولة في اللوحة — بدون تسجيل
                <ArrowLeft className="h-5 w-5 rotate-180" />
              </Link>
              <Link
                href="/login?next=/dashboard"
                prefetch={false}
                className="relative z-10 inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-2xl bg-teal-500 px-8 py-4 text-base font-bold text-slate-950 shadow-xl shadow-teal-500/25 transition hover:scale-[1.02] hover:bg-teal-400"
              >
                تسجيل الدخول للوحة الحقيقية
                <ArrowLeft className="h-5 w-5 rotate-180" />
              </Link>
              <a
                href="/dealix-marketing/index.html"
                className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-2xl border border-white/15 bg-white/5 px-8 py-4 text-base font-semibold text-white backdrop-blur hover:bg-white/10"
              >
                <Download className="h-5 w-5" />
                فتح بوابة الملفات
              </a>
            </motion.div>
            <motion.div variants={heroItem} className="mt-16 w-full">
              <p className="mb-4 text-center text-xs font-semibold uppercase tracking-[0.2em] text-teal-500/80">
                لمحة سريعة
              </p>
              <div className="mx-auto grid max-w-4xl grid-cols-1 gap-4 sm:grid-cols-2 lg:max-w-none lg:grid-cols-4">
                {heroStats.map((item, i) => {
                  const StatIcon = item.icon;
                  return (
                    <motion.div
                      key={item.title}
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.12 + i * 0.07, duration: 0.45 }}
                      whileHover={{ y: -6, transition: { duration: 0.22 } }}
                      className="group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-white/[0.07] to-transparent p-5 text-center shadow-lg shadow-black/40 ring-1 ring-white/[0.06] transition-[border-color] duration-300 hover:border-teal-500/35"
                    >
                      <div
                        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-teal-400/40 to-transparent opacity-70"
                        aria-hidden
                      />
                      <div className="relative flex flex-col items-center gap-3">
                        <HeroStatMiniDiagram variant={item.mini} />
                        <div className="inline-flex rounded-xl border border-teal-500/20 bg-teal-950/30 p-2 text-teal-200">
                          <StatIcon className="h-4 w-4" strokeWidth={1.75} aria-hidden />
                        </div>
                        <p className="bg-gradient-to-b from-white to-slate-300 bg-clip-text text-2xl font-black tracking-tight text-transparent tabular-nums md:text-[1.75rem]">
                          {item.value}
                        </p>
                        <div className="space-y-1">
                          <p className="text-sm font-bold text-slate-50">{item.title}</p>
                          <p className="text-[12px] leading-relaxed text-slate-500">{item.hint}</p>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          </motion.div>
        </section>

        <section
          id="product"
          className="relative overflow-hidden border-t border-white/5 bg-[#050a14] py-24 md:py-32"
        >
          <div
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_90%_60%_at_50%_-10%,rgba(20,184,166,0.18),transparent_55%)]"
            aria-hidden
          />
          <div
            className="pointer-events-none absolute -left-1/4 top-1/3 h-[420px] w-[420px] rounded-full bg-teal-500/10 blur-[100px]"
            aria-hidden
          />
          <div
            className="pointer-events-none absolute -right-1/4 bottom-0 h-[380px] w-[380px] rounded-full bg-cyan-500/10 blur-[90px]"
            aria-hidden
          />
          <div
            className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:48px_48px] opacity-[0.35] [mask-image:radial-gradient(ellipse_at_center,black_30%,transparent_75%)]"
            aria-hidden
          />

          <div className="relative mx-auto max-w-6xl px-6">
            <div className="mb-16 text-center md:mb-20">
              <motion.div
                initial={{ opacity: 0, scale: 0.96 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                className="mb-5 inline-flex items-center gap-2 rounded-full border border-teal-500/35 bg-teal-500/10 px-4 py-1.5 text-xs font-bold uppercase tracking-[0.2em] text-teal-200 shadow-[0_0_40px_-8px_rgba(45,212,191,0.45)]"
              >
                <Sparkles className="h-3.5 w-3.5" aria-hidden />
                المنتج
              </motion.div>
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
                className="mx-auto max-w-3xl text-3xl font-black leading-[1.2] tracking-tight text-white md:text-5xl md:leading-[1.15]"
              >
                كل ما تحتاجه لتسريع{" "}
                <span className="bg-gradient-to-l from-teal-200 via-emerald-200 to-cyan-300 bg-clip-text text-transparent">
                  الإغلاق
                </span>
                <br className="hidden sm:block" />
                <span className="text-slate-400">— طبقة تشغيل لا تُقارن بصفحة هبوط عادية</span>
              </motion.h2>
              <motion.div
                initial={{ opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.08, duration: 0.45 }}
                className="mx-auto mt-6 flex w-full max-w-3xl flex-col items-center gap-5"
              >
                <div
                  className="flex w-full flex-col gap-3 sm:flex-row sm:items-stretch sm:justify-center sm:gap-4"
                  role="status"
                  aria-live="polite"
                >
                  <motion.div
                    whileHover={{ scale: 1.02, borderColor: "rgba(45, 212, 191, 0.45)" }}
                    whileTap={{ scale: 0.98 }}
                    transition={{ type: "spring", stiffness: 380, damping: 24 }}
                    className="flex flex-1 items-center gap-3 rounded-2xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-transparent px-4 py-3.5 text-start shadow-[inset_0_1px_0_rgba(255,255,255,0.06)] backdrop-blur-md sm:min-h-[4.5rem] sm:max-w-[20rem]"
                  >
                    <motion.span
                      className="inline-flex shrink-0 rounded-xl border border-teal-500/30 bg-teal-500/15 p-2 text-teal-300"
                      animate={{ y: [0, -3, 0] }}
                      transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
                      aria-hidden
                    >
                      <MousePointer2 className="hidden h-5 w-5 md:block" strokeWidth={1.75} />
                      <Smartphone className="h-5 w-5 md:hidden" strokeWidth={1.75} />
                    </motion.span>
                    <span className="text-sm font-semibold leading-snug text-slate-200">
                      <span className="hidden md:inline">
                        على الكمبيوتر: مرّر المؤشر فوق البطاقات — العمق والميلان يتفاعلان معك.
                      </span>
                      <span className="md:hidden">
                        على الجوال: المس البطاقة واتركها — نفس الإحساس بالعمق والحركة.
                      </span>
                    </span>
                  </motion.div>
                  <motion.div
                    whileHover={{ scale: 1.02, borderColor: "rgba(45, 212, 191, 0.45)" }}
                    whileTap={{ scale: 0.98 }}
                    transition={{ type: "spring", stiffness: 380, damping: 24 }}
                    className="flex flex-1 flex-col justify-center gap-1 rounded-2xl border border-white/10 bg-gradient-to-bl from-teal-500/[0.12] to-transparent px-4 py-3.5 text-center shadow-[0_0_36px_-16px_rgba(20,184,166,0.35)] backdrop-blur-md sm:min-h-[4.5rem] sm:max-w-[20rem]"
                  >
                    <span className="text-xs font-bold uppercase tracking-[0.18em] text-teal-300/95">
                      تلميح سريع
                    </span>
                    <span className="text-xs leading-relaxed text-slate-400 md:text-sm">
                      جرّب البطاقات الأربع — كل واحدة تمثّل طبقة تشغيل حقيقية، ليست زخرفة.
                    </span>
                  </motion.div>
                </div>
                <p className="max-w-2xl text-center text-sm leading-relaxed text-slate-500 md:text-[15px]">
                  طبقة واحدة تربط الوكلاء والقنوات والحوكمة وتكامل البيانات — منظومة مترابطة تعكس قوة
                  المنتج، على أي شاشة.
                </p>
              </motion.div>
            </div>

            <div className="mx-auto max-w-5xl [perspective:1400px]">
              <div
                className="grid grid-cols-1 gap-8 md:grid-cols-2 md:gap-10"
                style={{ transformStyle: "preserve-3d" }}
              >
                {features.map((f, i) => (
                  <motion.article
                    key={f.title}
                    initial={{ opacity: 0, y: 56, rotateX: 18 }}
                    whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
                    viewport={{ once: true, margin: "-60px" }}
                    transition={{
                      delay: i * 0.1,
                      duration: 0.55,
                      ease: [0.22, 1, 0.36, 1],
                    }}
                    whileHover={{
                      y: -14,
                      rotateX: -6,
                      rotateY: i % 2 === 0 ? 4 : -4,
                      transition: { duration: 0.38, ease: [0.22, 1, 0.36, 1] },
                    }}
                    style={{ transformStyle: "preserve-3d" }}
                    className="group relative rounded-[1.4rem] border border-white/[0.12] bg-gradient-to-br from-slate-950/80 via-slate-900/50 to-transparent p-8 shadow-[0_24px_60px_-28px_rgba(0,0,0,0.85)] ring-1 ring-white/[0.06] backdrop-blur-xl transition-shadow duration-500 hover:border-teal-400/30"
                  >
                    <div
                      className="pointer-events-none absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-teal-400/40 to-transparent opacity-70"
                      aria-hidden
                    />
                    <div className="relative flex flex-col gap-5">
                      <div
                        className="inline-flex h-14 w-14 items-center justify-center rounded-2xl border border-teal-500/25 bg-slate-950/60 text-teal-200 transition-transform duration-300 group-hover:-translate-y-0.5"
                        style={{ transform: "translateZ(24px)" }}
                      >
                        <f.icon className="h-7 w-7" strokeWidth={1.65} aria-hidden />
                      </div>
                      <div>
                        <h3 className="text-xl font-black tracking-tight text-white md:text-[1.35rem]">
                          {f.title}
                        </h3>
                        <p className="mt-3 text-sm leading-relaxed text-slate-400 md:text-[15px]">
                          {f.desc}
                        </p>
                      </div>
                      <FeatureCardDiagram variant={f.diagram} />
                    </div>
                  </motion.article>
                ))}
              </div>
            </div>

            <div
              className="pointer-events-none mx-auto mt-16 h-px max-w-md bg-gradient-to-r from-transparent via-teal-500/40 to-transparent"
              aria-hidden
            />
          </div>
        </section>

        <section id="why" className="py-20">
          <div className="mx-auto max-w-6xl px-6">
            <DealixSystemOverview />
          </div>
        </section>

        <section className="relative z-10 border-t border-white/5 py-16 md:py-20">
          <div className="mx-auto max-w-6xl px-6">
            <CeoDirectContactCard />
          </div>
        </section>

        <DealixCompetitiveMoatStrip />

        <DealixCustomerJourneyLoop />

        <footer className="border-t border-white/5 py-12 text-center text-sm text-slate-500">
          <p>© Dealix — منصة تشغيل المبيعات والإيرادات للشركات</p>
          <p className="mt-2 text-xs text-slate-600">
            وكلاء أذكاء، حوكمة، قنوات متعددة، وتكامل مع بياناتك.
          </p>
          <nav
            className="mt-6 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-slate-400"
            aria-label="روابط سريعة"
          >
            <Link href="/dealix-marketing/dashboard-guide" className="hover:text-teal-400 transition-colors">
              دليل لوحة التحكم والميزات
            </Link>
            <Link href="/resources" className="hover:text-teal-400 transition-colors">
              الموارد والتحميلات
            </Link>
            <Link href="/marketers" className="hover:text-teal-400 transition-colors">
              بوابة المسوّقين
            </Link>
            <Link href="/help" className="hover:text-teal-400 transition-colors">
              المساعدة
            </Link>
            <Link href="/explore" className="hover:text-teal-400 transition-colors">
              جولة اللوحة (مجاناً)
            </Link>
            <a href="#market-moat" className="hover:text-teal-400 transition-colors">
              التمييز أمام السوق
            </a>
            <a href="#customer-journey-loop" className="hover:text-teal-400 transition-colors">
              مسار العميل الكامل
            </a>
            <a href="#ceo-contact" className="hover:text-amber-300 transition-colors">
              المهندس سامي العسيري
            </a>
          </nav>
        </footer>
      </main>
    </div>
  );
}
