import Link from "next/link";
import {
  Building2,
  Heart,
  ShoppingCart,
  Globe,
  Briefcase,
  GraduationCap,
  Calendar,
  CheckCircle,
  ArrowLeft,
} from "lucide-react";

export const metadata = {
  title: "Dealix — حالات الاستخدام",
  description: "كيف Dealix يساعد كل قطاع يحوّل الاستفسارات لإيراد.",
};

const CALENDLY = "https://calendly.com/sami-assiri11/dealix-demo";

const useCases = [
  {
    icon: Briefcase,
    sector: "وكالات التسويق",
    pain: "عملاؤكم يصرفون على إعلانات والـ leads تضيع بعد الكلك",
    solution: "Dealix يصير خدمة جديدة تبيعونها: متابعة + حجز + تقارير",
    offer: "Agency Partner Pilot",
    color: "amber",
  },
  {
    icon: Building2,
    sector: "العقارات",
    pain: "60% من استفسارات الأسعار والمواقع ما تُتابع خلال ساعة",
    solution: "رد خلال 45 ثانية + فرز الجاد + حجز موعد معاينة",
    offer: "Speed-to-Lead Pilot — 499 ريال",
    color: "teal",
  },
  {
    icon: Heart,
    sector: "العيادات والمراكز",
    pain: "استفسارات واتساب كثيرة ما تتحول لمواعيد",
    solution: "فرز الاستفسارات + متابعة المتردد + حجز الموعد تلقائياً",
    offer: "Booking Follow-up Pilot — 499 ريال",
    color: "rose",
  },
  {
    icon: ShoppingCart,
    sector: "المتاجر الإلكترونية",
    pain: "محادثات واتساب/إنستغرام مهجورة بدون إغلاق",
    solution: "رد فوري على 'هل متوفر؟' و'كم التوصيل؟' + تحويل للشراء",
    offer: "Inquiry-to-Order Pilot — 499 ريال",
    color: "violet",
  },
  {
    icon: Globe,
    sector: "وكالات المواقع والبرمجة",
    pain: "المشروع ينتهي عند تسليم الموقع — لا recurring revenue",
    solution: "أضف Dealix كخدمة بعد الموقع: نماذج → متابعة → حجز → تقرير",
    offer: "Website-to-Lead Add-on",
    color: "cyan",
  },
  {
    icon: GraduationCap,
    sector: "خدمات B2B والتدريب",
    pain: "طلبات عروض وأسعار بدون متابعة منظمة",
    solution: "تنظيم المتابعة بعد العرض: تذكير + سؤال + حجز موعد مناقشة",
    offer: "Quote Follow-up Pilot — 499 ريال",
    color: "orange",
  },
];

const colorMap: Record<string, string> = {
  amber: "border-amber-500/20 bg-amber-500/5",
  teal: "border-teal-500/20 bg-teal-500/5",
  rose: "border-rose-500/20 bg-rose-500/5",
  violet: "border-violet-500/20 bg-violet-500/5",
  cyan: "border-cyan-500/20 bg-cyan-500/5",
  orange: "border-orange-500/20 bg-orange-500/5",
};

const iconColorMap: Record<string, string> = {
  amber: "text-amber-400",
  teal: "text-teal-400",
  rose: "text-rose-400",
  violet: "text-violet-400",
  cyan: "text-cyan-400",
  orange: "text-orange-400",
};

export default function UseCasesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      {/* Hero */}
      <section className="mx-auto max-w-4xl px-6 pb-12 pt-20 text-center">
        <h1 className="text-4xl font-extrabold leading-tight lg:text-5xl">
          كل قطاع عنده{" "}
          <span className="bg-gradient-to-l from-teal-400 to-emerald-500 bg-clip-text text-transparent">
            leads تضيع
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-300">
          Dealix يحوّل الاستفسارات من واتساب، الإيميل، النماذج، والحملات إلى متابعة وحجز وإيراد — لكل قطاع.
        </p>
      </section>

      {/* Use Cases Grid */}
      <section className="pb-20">
        <div className="mx-auto max-w-5xl px-6">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {useCases.map((uc) => (
              <div
                key={uc.sector}
                className={`flex flex-col rounded-2xl border p-6 ${colorMap[uc.color]}`}
              >
                <uc.icon className={`h-8 w-8 ${iconColorMap[uc.color]}`} />
                <h3 className="mt-4 text-lg font-bold">{uc.sector}</h3>
                <p className="mt-2 text-sm text-slate-400">
                  <strong className="text-red-400">الألم:</strong> {uc.pain}
                </p>
                <p className="mt-2 text-sm text-slate-400">
                  <strong className="text-emerald-400">الحل:</strong> {uc.solution}
                </p>
                <div className="mt-auto pt-4">
                  <span className="inline-block rounded-lg bg-white/10 px-3 py-1 text-xs font-medium text-slate-300">
                    {uc.offer}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-white/10 py-16">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <h2 className="text-2xl font-bold">
            قطاعك موجود؟ <span className="text-teal-400">جرّب Dealix</span>
          </h2>
          <p className="mt-4 text-slate-300">
            Pilot 7 أيام بـ 499 ريال. ضمان استرداد كامل.
          </p>
          <a
            href={CALENDLY}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-8 inline-flex items-center gap-2 rounded-xl bg-teal-500 px-8 py-3.5 text-base font-bold text-white transition hover:bg-teal-400"
          >
            <Calendar className="h-5 w-5" />
            احجز ديمو 10 دقائق
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-center gap-6 px-6 text-sm text-slate-500">
          <Link href="/" className="hover:text-teal-400">الرئيسية</Link>
          <Link href="/marketers" className="hover:text-teal-400">المسوّقين</Link>
          <Link href="/partners" className="hover:text-teal-400">الشراكات</Link>
          <Link href="/pricing" className="hover:text-teal-400">الباقات</Link>
          <Link href="/trust" className="hover:text-teal-400">الأمان</Link>
          <span>© {new Date().getFullYear()} Dealix</span>
        </div>
      </footer>
    </div>
  );
}
