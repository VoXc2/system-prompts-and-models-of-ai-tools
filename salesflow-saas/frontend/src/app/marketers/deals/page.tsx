import Link from "next/link";
import {
  ArrowLeft,
  Briefcase,
  CircleDollarSign,
  GitBranch,
  LayoutDashboard,
  Presentation,
  Users,
} from "lucide-react";

const stages = [
  { title: "اكتشاف وتأهيل", desc: "تحديد احتياج العميل وملاءمة Dealix لقطاعه." },
  { title: "عرض ووضوح", desc: "العروض القطاعية والمواد الجاهزة تسرّع الثقة." },
  { title: "إغلاق وتشغيل", desc: "التسجيل في المنصة، ربط القنوات، ومتابعة الصفقات." },
  { title: "عمولة وتسوية", desc: "طبقات Silver / Gold / Platinum — راجع العقد والملف الرسمي." },
];

export default function MarketerDealsPage() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Link
        href="/marketers"
        className="mb-6 inline-flex items-center gap-2 text-sm text-teal-400 hover:text-teal-300"
      >
        <ArrowLeft className="h-4 w-4 rotate-180" aria-hidden />
        العودة للبوابة
      </Link>

      <h1 className="text-2xl font-bold tracking-tight text-white">مسار الصفقات والعمولات</h1>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">
        من أول تواصل إلى تحويل العمولة: استخدم المواد أدناه مع العملاء، ثم نفّذ التشغيل من لوحة
        التحكم بعد تسجيل الدخول.
      </p>

      <ol className="mt-8 space-y-4">
        {stages.map((s, i) => (
          <li
            key={s.title}
            className="flex gap-4 rounded-2xl border border-white/10 bg-white/5 p-4"
          >
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-teal-500/20 text-sm font-black text-teal-200">
              {i + 1}
            </span>
            <div>
              <h2 className="font-semibold text-white">{s.title}</h2>
              <p className="mt-1 text-sm text-slate-400">{s.desc}</p>
            </div>
          </li>
        ))}
      </ol>

      <div className="mt-10 space-y-3 rounded-2xl border border-teal-500/25 bg-teal-950/40 p-6">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-teal-200">
          <CircleDollarSign className="h-5 w-5" aria-hidden />
          ضمان الشفافية في الدخل
        </h2>
        <p className="text-sm leading-relaxed text-slate-300">
          مستويات العمولة والشروط مذكورة في{" "}
          <a
            href="/dealix-marketing/arsenal"
            className="font-semibold text-teal-400 underline-offset-2 hover:underline"
          >
            ملف التسويق والعمولة
          </a>{" "}
          والعقد الرسمي هو المرجع للأرقام النهائية. بعد التسجيل كشريك، تُربط صفقاتك بحسابك في
          المنصة.
        </p>
      </div>

      <div className="mt-8 grid gap-3 sm:grid-cols-2">
        <Link
          href="/marketers/team"
          className="flex items-center gap-3 rounded-2xl border border-teal-500/30 bg-teal-950/40 p-4 text-sm font-semibold text-white transition hover:border-teal-400/50"
        >
          <Users className="h-5 w-5 shrink-0 text-teal-400" aria-hidden />
          فريقي والدعوات (هرمي)
        </Link>
        <Link
          href="/dealix-presentations/00-dealix-company-master-ar.html"
          className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm font-semibold text-white transition hover:border-teal-500/40"
        >
          <Presentation className="h-5 w-5 shrink-0 text-teal-400" aria-hidden />
          عروض HTML القطاعية
        </Link>
        <Link
          href="/resources"
          className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm font-semibold text-white transition hover:border-teal-500/40"
        >
          <GitBranch className="h-5 w-5 shrink-0 text-teal-400" aria-hidden />
          مركز الموارد (ZIP)
        </Link>
        <Link
          href="/dashboard"
          className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm font-semibold text-white transition hover:border-teal-500/40"
        >
          <LayoutDashboard className="h-5 w-5 shrink-0 text-teal-400" aria-hidden />
          لوحة التحكم — الصفقات الحية
        </Link>
        <Link
          href="/marketers/account"
          className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm font-semibold text-white transition hover:border-teal-500/40"
        >
          <Briefcase className="h-5 w-5 shrink-0 text-teal-400" aria-hidden />
          بيانات الحساب البنكي
        </Link>
      </div>
    </div>
  );
}
