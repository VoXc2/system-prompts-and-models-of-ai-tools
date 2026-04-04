import Link from "next/link";
import {
  ArrowLeft,
  Headphones,
  MessageCircle,
  Building2,
  Handshake,
  Shield,
  ChevronDown,
} from "lucide-react";
import type { Metadata } from "next";
import { CeoDirectContactCard } from "@/components/dealix/ceo-direct-contact-card";

export const metadata: Metadata = {
  title: "الدعم والأسئلة الشائعة — Dealix",
  description:
    "إجابات استراتيجية عن المنتج، الشراكة، الإحالات، والمواد التسويقية — Dealix السعودية.",
};

const PHONE_DISPLAY = "05 977 885 39";
const WA_LINK = "https://wa.me/966597788539";

const faqBlocks: { title: string; icon: typeof Building2; items: { q: string; a: string }[] }[] = [
  {
    title: "المنتج والتمييز",
    icon: Building2,
    items: [
      {
        q: "ما الذي يميّز Dealix عن «بوت واتساب» أو أداة تأهيل منفصلة؟",
        a: "Dealix منصّة تشغيل إيرادات كاملة: طبقات وكلاء، حوكمة قبل الإرسال الحساس، ذاكرة لكل صفقة، وتكامل مع CRM ومسارات دفع — وليس مجرد رد آلي على رسالة واحدة.",
      },
      {
        q: "هل نحتاج Salesforce من اليوم الأول؟",
        a: "لا يُفترض كشرط للبدء؛ التصميم يدعم مسار CRM قوياً عند توفره. يُحدّد نطاق التكامل أثناء الـ POC حسب نضج بياناتكم.",
      },
      {
        q: "كيف تُدار القنوات المتعددة دون تضارب في الهوية؟",
        a: "سياسات موحّدة للقوالب، موافقات قبل المحتوى الحساس، وسجل تدقيق — بحيث تبقى الرسائل متسقة عبر واتساب وبريد ولينكدإن ضمن حدودكم التنظيمية.",
      },
    ],
  },
  {
    title: "الشراكة والمسوّقون",
    icon: Handshake,
    items: [
      {
        q: "كيف أبدأ كمسوّق شريك؟",
        a: "ادخل بوابة المسوّقين على الموقع، راجع المواد العامة والهيكل، ثم نسّق مع فريق Dealix لتفعيل الحساب وربط الإحالات قبل أول اجتماع إغلاق مع عميل أو مستثمر.",
      },
      {
        q: "كيف تُثبت إحالة مستثمر أو عميل؟",
        a: "يُفضّل تسجيل الإحالة كتابياً (بريد أو واتساب رسمي) مع اسم الجهة وتاريخ أول تعريف — تُقارن لاحقاً مع سجل الإغلاق وفق اتفاقية الشريك.",
      },
      {
        q: "أين أجد قوالب واتساب والعروض القطاعية؟",
        a: "من مركز الموارد وبوابة التسويق الثابتة: حزمة ZIP، عروض HTML للطباعة، وملفات Markdown للقطاعات — كلها من نفس النطاق دون خادم منفصل.",
      },
    ],
  },
  {
    title: "الاستثمار والمواد العامة",
    icon: Shield,
    items: [
      {
        q: "ما الذي يمكن مشاركته مع مستثمر مؤهل؟",
        a: "العرض الاستثماري والملف التعريفي المتاحان علناً على الموقع؛ الأرقام التفصيلية والالتزامات القانونية تبقى ضمن جدول عمل ومستندات رسمية.",
      },
      {
        q: "هل العروض القطاعية ضمان أداء؟",
        a: "العروض تشرح نموذج قيمة ومسارات تشغيل؛ أي أرقام نمو أو ROI في العروض تُفهم كأمثلة مرجعية ما لم تُربط صراحة بعقد أو POC مُوثَّق.",
      },
    ],
  },
  {
    title: "التشغيل والخصوصية",
    icon: Headphones,
    items: [
      {
        q: "كيف تُعالج البيانات الحساسة؟",
        a: "عزل منطقي متعدد المستأجرين، مسارات موافقة، وتقليل البيانات في الرسائل — مع التزامكم بسياسات العملاء في القطاعات المنظمة (صحة، مالية، إلخ).",
      },
      {
        q: "ما أوقات الرد على الاستفسارات التشغيلية؟",
        a: "نسعى لرد أولي خلال ساعات العمل (الأحد–الخميس) عبر القنوات الرسمية؛ للطوارئ التجارية يُنصح بذكر «عاجل» في رسالة واتساب مع سياق مختصر.",
      },
    ],
  },
];

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-teal-950 text-slate-100">
      <div className="mx-auto max-w-3xl px-6 py-12 md:py-16">
        <Link
          href="/"
          className="mb-8 inline-flex items-center gap-2 text-sm text-teal-400 hover:text-teal-300"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden />
          الصفحة الرئيسية
        </Link>

        <header className="space-y-4 text-center md:text-right">
          <p className="text-sm font-semibold text-teal-400">Dealix · GTM &amp; شراكة</p>
          <h1 className="text-3xl font-bold tracking-tight md:text-4xl">الدعم والأسئلة الشائعة</h1>
          <p className="text-slate-400 leading-relaxed">
            إجابات موجزة لقرارات الشراء والشراكة — وليست بديلاً عن العقد أو خطة العمل المخصصة.
          </p>
        </header>

        <div className="mt-10">
          <CeoDirectContactCard />
        </div>

        <div className="mt-10 rounded-2xl border border-teal-500/30 bg-gradient-to-br from-teal-950/60 to-slate-900/80 p-6 shadow-[0_0_48px_-20px_rgba(20,184,166,0.35)]">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-teal-300/90">
                هاتف وواتساب (السعودية)
              </p>
              <a
                href="tel:+966597788539"
                className="mt-2 block text-2xl font-black tracking-tight text-white hover:text-teal-200 md:text-3xl"
              >
                {PHONE_DISPLAY}
              </a>
              <p className="mt-2 text-sm text-slate-400">
                للاستفسارات التشغيلية، تفعيل الشراكة، أو طلب مواد إضافية.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <a
                href={WA_LINK}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-xl bg-teal-500 px-5 py-3 text-sm font-bold text-slate-950 shadow-lg shadow-teal-900/40 transition hover:bg-teal-400"
              >
                <MessageCircle className="h-4 w-4" aria-hidden />
                فتح واتساب
              </a>
              <Link
                href="/resources"
                className="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white hover:bg-white/10"
              >
                مركز الموارد
              </Link>
              <Link
                href="/marketers"
                className="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white hover:bg-white/10"
              >
                بوابة المسوّقين
              </Link>
            </div>
          </div>
        </div>

        <div className="mt-14 space-y-12">
          {faqBlocks.map((block) => (
            <section key={block.title} className="space-y-4">
              <div className="flex items-center gap-3 border-b border-white/10 pb-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-500/15 text-teal-300">
                  <block.icon className="h-5 w-5" aria-hidden />
                </span>
                <h2 className="text-xl font-bold text-white">{block.title}</h2>
              </div>
              <div className="space-y-3">
                {block.items.map((item) => (
                  <details
                    key={item.q}
                    className="group rounded-2xl border border-white/10 bg-white/[0.04] transition hover:border-teal-500/25"
                  >
                    <summary className="flex cursor-pointer list-none items-start justify-between gap-3 px-5 py-4 text-start font-semibold text-slate-100 [&::-webkit-details-marker]:hidden">
                      <span className="flex-1 leading-snug">{item.q}</span>
                      <ChevronDown className="mt-0.5 h-5 w-5 shrink-0 text-teal-400/80 transition group-open:rotate-180" />
                    </summary>
                    <div className="border-t border-white/5 px-5 pb-5 pt-0 text-sm leading-relaxed text-slate-400">
                      {item.a}
                    </div>
                  </details>
                ))}
              </div>
            </section>
          ))}
        </div>

        <p className="mt-14 text-center text-xs text-slate-500">
          © Dealix — آخر تحديث للصفحة مرجعي؛ تُراجع الشروط والعقود الرسمية عند الالتزام المالي.
        </p>
      </div>
    </div>
  );
}
