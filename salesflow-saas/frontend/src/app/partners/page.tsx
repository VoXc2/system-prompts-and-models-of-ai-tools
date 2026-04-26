import Link from "next/link";
import {
  Users,
  Briefcase,
  Zap,
  Shield,
  CheckCircle,
  Calendar,
  DollarSign,
  ArrowLeft,
  Building2,
  Handshake,
} from "lucide-react";

export const metadata = {
  title: "Dealix — شراكة الوكالات والشركاء",
  description:
    "كن شريك Dealix. أضف خدمة متابعة وتحويل leads لعملائك واربح من أول اشتراك مدفوع.",
};

const CALENDLY = "https://calendly.com/sami-assiri11/dealix-demo";

const partnerModels = [
  {
    icon: Users,
    name: "شريك إحالة",
    desc: "عرّفنا على شركة مناسبة. Dealix يتولى الديمو والتشغيل. تستحق عمولتك بعد الدفع المؤكد.",
    earn: "10-20% من أول فاتورة",
    color: "emerald",
  },
  {
    icon: Briefcase,
    name: "شريك بيع / وكالة",
    desc: "بيع Dealix ضمن خدماتك التسويقية. احتفظ بهامش خدمتك وDealix يشغّل طبقة المتابعة والحجز.",
    earn: "20% MRR + 50% setup fee",
    color: "amber",
  },
  {
    icon: Handshake,
    name: "تبادل خدمات",
    desc: "ساعد بالمحتوى أو الإحالات أو الوصول لعملاء. Dealix يدعمك بتجربة وتشغيل مشترك لمدة 30 يوم.",
    earn: "pilot مجاني + co-selling",
    color: "blue",
  },
  {
    icon: Building2,
    name: "شريك تنفيذ",
    desc: "أنت تساعد بالـ setup والتكامل. Dealix يوفّر المنتج والـ playbook. العميل يدفع باقة مشتركة.",
    earn: "implementation fee",
    color: "purple",
  },
];

export default function PartnersPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      {/* Hero */}
      <section className="mx-auto max-w-4xl px-6 pb-16 pt-20 text-center">
        <span className="inline-block rounded-full bg-emerald-500/10 px-4 py-1.5 text-sm font-medium text-emerald-400 ring-1 ring-emerald-500/20">
          برنامج الشراكات
        </span>
        <h1 className="mt-6 text-4xl font-extrabold leading-tight lg:text-5xl">
          اربح من{" "}
          <span className="bg-gradient-to-l from-emerald-400 to-teal-500 bg-clip-text text-transparent">
            أول اشتراك مدفوع
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-slate-300">
          أنت تجيب العملاء. Dealix يشغّل طبقة المتابعة والحجز والتقارير. اربح من
          أول اشتراك مدفوع مؤهل يأتي عن طريقك.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <a
            href={CALENDLY}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-8 py-3.5 text-base font-bold text-white transition hover:bg-emerald-400"
          >
            <Calendar className="h-5 w-5" />
            احجز مكالمة شراكة
          </a>
          <Link
            href="/marketers"
            className="inline-flex items-center gap-2 rounded-xl border border-white/20 px-8 py-3.5 text-base font-medium transition hover:bg-white/10"
          >
            صفحة المسوّقين
          </Link>
        </div>
      </section>

      {/* Partner Models */}
      <section className="border-y border-white/10 bg-slate-900/50 py-16">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="text-center text-2xl font-bold">4 نماذج شراكة</h2>
          <div className="mt-10 grid gap-6 sm:grid-cols-2">
            {partnerModels.map((m) => (
              <div
                key={m.name}
                className="rounded-2xl border border-white/10 bg-white/5 p-6"
              >
                <m.icon className="h-8 w-8 text-emerald-400" />
                <h3 className="mt-4 text-lg font-semibold">{m.name}</h3>
                <p className="mt-2 text-sm text-slate-400">{m.desc}</p>
                <div className="mt-4 inline-block rounded-lg bg-emerald-500/10 px-3 py-1 text-sm font-medium text-emerald-400">
                  {m.earn}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="text-2xl font-bold">كيف تبدأ</h2>
          <div className="mt-8 grid gap-6 sm:grid-cols-3">
            {[
              { step: "١", title: "اختر عميل", desc: "عميل واحد عندك يعاني من ضياع leads" },
              { step: "٢", title: "نسوي pilot", desc: "7 أيام مجاناً لأول عميل — نثبت القيمة" },
              { step: "٣", title: "نكمّل ونربح", desc: "لو اشتغل → خدمة شهرية. أنت العلاقة، أنا التشغيل" },
            ].map((s) => (
              <div key={s.step} className="rounded-xl border border-white/10 bg-white/5 p-6">
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500 text-lg font-bold text-white">
                  {s.step}
                </div>
                <h3 className="mt-4 font-semibold">{s.title}</h3>
                <p className="mt-2 text-sm text-slate-400">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Revenue Calculator */}
      <section className="border-y border-white/10 bg-slate-900/50 py-16">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <DollarSign className="mx-auto h-10 w-10 text-amber-400" />
          <h2 className="mt-4 text-2xl font-bold">كم تقدر تربح كشريك؟</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-3xl font-extrabold text-amber-400">14,880</div>
              <div className="mt-1 text-sm text-slate-400">ريال/سنة من عميل واحد</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-3xl font-extrabold text-amber-400">74,400</div>
              <div className="mt-1 text-sm text-slate-400">ريال/سنة من 5 عملاء</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-3xl font-extrabold text-amber-400">223,800</div>
              <div className="mt-1 text-sm text-slate-400">ريال/سنة كشريك نشط</div>
            </div>
          </div>
        </div>
      </section>

      {/* Founder Direct */}
      <section className="py-10">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <p className="text-lg text-slate-300">أي سؤال؟ تواصل مع المؤسس مباشرة:</p>
          <a href="tel:+966597788539" className="mt-3 inline-block text-2xl font-bold text-amber-400 hover:text-amber-300" dir="ltr">0597788539</a>
          <p className="mt-1 text-sm text-slate-500">سامي العسيري — مؤسس Dealix</p>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-white/10 py-20">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <h2 className="text-3xl font-extrabold">
            ابدأ بعميل واحد — <span className="text-emerald-400">مجاناً</span>
          </h2>
          <p className="mt-4 text-lg text-slate-300">
            أول عميل عندك = pilot 7 أيام مجاناً. لو اشتغل تبدأ تحصّل. لو ما اشتغل لا التزام.
          </p>
          <a
            href={CALENDLY}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-8 inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-8 py-4 text-lg font-bold text-white transition hover:bg-emerald-400"
          >
            <Handshake className="h-5 w-5" />
            كن شريك Dealix
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-center gap-6 px-6 text-sm text-slate-500">
          <Link href="/" className="hover:text-teal-400">الرئيسية</Link>
          <Link href="/marketers" className="hover:text-teal-400">المسوّقين</Link>
          <Link href="/pricing" className="hover:text-teal-400">الباقات</Link>
          <Link href="/use-cases" className="hover:text-teal-400">حالات الاستخدام</Link>
          <Link href="/trust" className="hover:text-teal-400">الأمان</Link>
          <Link href="/privacy" className="hover:text-teal-400">الخصوصية</Link>
          <span>© {new Date().getFullYear()} Dealix</span>
        </div>
      </footer>
    </div>
  );
}
