import Link from "next/link";
import { MarketerOsPanel } from "@/components/marketers/marketer-os-panel";
import {
  MessageCircle,
  Download,
  FileText,
  CheckSquare,
  Presentation,
  ArrowLeft,
  ExternalLink,
  Compass,
  Briefcase,
  Sparkles,
  Users,
  Landmark,
  LayoutDashboard,
  Clapperboard,
} from "lucide-react";

const links = [
  {
    title: "دليل لوحة التحكم (للشركات)",
    href: "/dealix-marketing/dashboard-guide",
    desc: "شرح التبويبات: القيادة، الوكلاء، المالية، العروض، والسكربتات — لاستخدامك مع العميل.",
    icon: LayoutDashboard,
  },
  {
    title: "العرض الاستثماري الكامل (عام — PDF)",
    href: "/investors",
    desc: "نفس الوثيقة للمستثمرين المؤهلين: ملخص، فرصة، مخاطر، خارطة طريق. رابط قصير للمشاركة.",
    icon: Landmark,
  },
  {
    title: "الخطة الاستراتيجية والمنافسة",
    href: "/strategy",
    desc: "لماذا Dealix، مراحل التنفيذ، وتحميل الوثيقة الكاملة.",
    icon: Compass,
  },
  {
    title: "مركز الموارد (كل الروابط)",
    href: "/resources",
    desc: "ZIP، العروض، والملفات التسويقية.",
    icon: Download,
  },
  {
    title: "فهرس الملفات الثابتة",
    href: "/dealix-marketing/index.html",
    desc: "نسخة HTML كاملة من بوابة الأصول.",
    icon: FileText,
  },
  {
    title: "قوالب واتساب (نسخ ولصق)",
    href: "/dealix-marketing/marketers/whatsapp-playbook-ar.txt",
    desc: "رسائل جاهزة — عدّل الاسم والرابط فقط.",
    icon: MessageCircle,
  },
  {
    title: "قائمة تحقق الدخول",
    href: "/dealix-marketing/marketers/entry-checklist-ar.txt",
    desc: "تأكد أنك غطيت الخطوات قبل التواصل مع العملاء.",
    icon: CheckSquare,
  },
  {
    title: "العروض القطاعية (11 وثيقة)",
    href: "/dealix-presentations/00-dealix-company-master-ar.html",
    desc: "ابدأ من ملف الشركة ثم اختر رقم القطاع.",
    icon: Presentation,
    external: false,
  },
  {
    title: "هيكل العمولة (Markdown)",
    href: "/dealix-marketing/arsenal",
    desc: "Silver / Gold / Platinum — راجع العقد الرسمي للأرقام النهائية.",
    icon: FileText,
  },
  {
    title: "سكربتات فيديو للمسوّق (VO + ترويج)",
    href: "/dealix-marketing/Dealix_Video_Scripts_Master_AR.md",
    desc: "V1 وV2 مخصصة لمسار الشريك وحديث العميل عن اللوحة — ضمن حزمة السبعة مقاطع.",
    icon: Clapperboard,
  },
];

export default function MarketersPage() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <p className="text-sm font-semibold text-teal-400">Dealix Partner GTM</p>
      <h1 className="mt-2 text-3xl font-bold tracking-tight">بوابة المسوّقين</h1>
      <p className="mt-3 leading-relaxed text-slate-400">
        مسار واحد: موارد جاهزة، عروض قوية، ثم مسار الصفقات والعمولات، وحسابك البنكي للتسوية.
        أدوات عرض الاستثمار <strong className="text-slate-200">عامة</strong> وتُشارك مع أي طرف مؤهل — لا حاجة لصلاحيات داخلية.
        انسخ قوالب الواتساب وعدّل{" "}
        <code className="rounded bg-white/10 px-1.5 py-0.5 text-teal-200">{`{الاسم}`}</code> و
        <code className="rounded bg-white/10 px-1.5 py-0.5 text-teal-200">رابط موقعك</code>.
      </p>

      <div className="mt-8">
        <MarketerOsPanel />
      </div>

      <div className="mt-6 rounded-2xl border border-amber-500/35 bg-gradient-to-br from-amber-950/50 to-slate-900/80 p-5">
        <p className="text-sm font-bold text-amber-200">مكافأة إحالة مستثمر</p>
        <p className="mt-2 text-sm leading-relaxed text-slate-300">
          أي مسوّق يحيل مستثمراً يُغلق استثماره مع Dealix يستحق{" "}
          <strong className="text-amber-100">مكافأة نقدية مباشرة كبيرة</strong> — تُحدَّد في اتفاقية الشريك
          المعتمدة (راجع أيضاً{" "}
          <Link href="/dealix-marketing/arsenal" className="text-teal-400 underline-offset-2 hover:text-teal-300">
            هيكل العمولة
          </Link>
          ). سجّل إحالتك عبر فريق Dealix قبل العرض النهائي لضمان الربط.
        </p>
      </div>

      <div className="mt-8 grid gap-3 md:grid-cols-3">
        <Link
          href="/marketers/team"
          className="flex flex-col gap-1 rounded-2xl border border-teal-400/40 bg-gradient-to-br from-teal-900/40 to-slate-900/60 p-5 transition hover:border-teal-300/60 hover:from-teal-900/60"
        >
          <span className="flex items-center gap-2 text-sm font-bold text-teal-100">
            <Users className="h-4 w-4" aria-hidden />
            المدراء والفريق
          </span>
          <span className="text-xs leading-relaxed text-slate-400">
            دعوة حتى 10 مسوّقين، رمز تسجيل، وصفقات هرمية تحتك.
          </span>
        </Link>
        <Link
          href="/marketers/deals"
          className="flex flex-col gap-1 rounded-2xl border border-teal-500/35 bg-teal-950/50 p-5 transition hover:border-teal-400/60 hover:bg-teal-950/70"
        >
          <span className="flex items-center gap-2 text-sm font-bold text-teal-200">
            <Sparkles className="h-4 w-4" aria-hidden />
            الصفقات والعمولات
          </span>
          <span className="text-xs leading-relaxed text-slate-400">
            مراحل الدورة، الشفافية في الدخل، وربط لوحة التحكم.
          </span>
        </Link>
        <Link
          href="/marketers/account"
          className="flex flex-col gap-1 rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-teal-500/40 hover:bg-white/10 md:col-span-1"
        >
          <span className="flex items-center gap-2 text-sm font-bold text-white">
            <Briefcase className="h-4 w-4 text-teal-400" aria-hidden />
            حسابي وهويتي
          </span>
          <span className="text-xs leading-relaxed text-slate-400">
            بيانات التواصل والآيبان — محفوظة محلياً للمعاينة حتى ربط الخادم.
          </span>
        </Link>
      </div>

      <div className="mt-10 space-y-3">
        {links.map((item) => (
          <a
            key={item.href}
            href={item.href}
            className="flex gap-4 rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-teal-500/40 hover:bg-white/10"
          >
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-teal-500/20 text-teal-300">
              <item.icon className="h-6 w-6" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 font-semibold text-white">
                {item.title}
                <ExternalLink className="h-3.5 w-3.5 shrink-0 opacity-50" aria-hidden />
              </div>
              <p className="mt-1 text-sm text-slate-400">{item.desc}</p>
              <p className="mt-2 truncate font-mono text-xs text-teal-500/80">{item.href}</p>
            </div>
          </a>
        ))}
      </div>

      <div className="mt-12 rounded-2xl border border-teal-500/30 bg-teal-950/40 p-6">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-teal-200">
          <MessageCircle className="h-5 w-5" aria-hidden />
          تلميح واتساب سريع
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-slate-300">
          احفظ رسالة واحدة كقالب في واتساب (الأجهزة المدعومة) أو استخدم ملاحظات سريعة. لا ترسل
          لعملاء نهائيين دون تنسيق مع فريق Dealix وحسب سياسة الاستخدام.
        </p>
      </div>

      <div className="mt-10 flex flex-wrap gap-4">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-teal-400 hover:text-teal-300"
        >
          <ArrowLeft className="h-4 w-4 rotate-180" aria-hidden />
          الصفحة الرئيسية
        </Link>
        <Link href="/resources" className="text-sm text-teal-400 hover:text-teal-300">
          الموارد
        </Link>
        <Link href="/dashboard" className="text-sm text-teal-400 hover:text-teal-300">
          المنصة
        </Link>
      </div>
    </div>
  );
}
