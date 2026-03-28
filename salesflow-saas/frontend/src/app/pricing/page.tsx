"use client";

import { useState } from "react";
import Link from "next/link";

const tiers = [
  {
    name: "أساسي",
    nameEn: "Starter",
    monthlyPrice: 299,
    popular: false,
    cta: "ابدأ الآن",
    features: [
      "3 مستخدمين",
      "500 عميل محتمل",
      "واتساب بزنس API",
      "متابعة تلقائية أساسية",
      "تقارير أساسية",
      "دعم بالإيميل",
    ],
  },
  {
    name: "احترافي",
    nameEn: "Pro",
    monthlyPrice: 699,
    popular: true,
    cta: "ابدأ الآن",
    features: [
      "10 مستخدمين",
      "5,000 عميل محتمل",
      "واتساب + إيميل",
      "ذكاء اصطناعي متقدم",
      "تسلسلات بيعية تلقائية",
      "تقارير متقدمة + لوحة تحكم",
      "Voice AI (100 مكالمة)",
      "دعم أولوية",
    ],
  },
  {
    name: "مؤسسي",
    nameEn: "Enterprise",
    monthlyPrice: null,
    popular: false,
    cta: "تواصل معنا",
    features: [
      "مستخدمين غير محدود",
      "عملاء غير محدود",
      "كل مميزات الاحترافي",
      "Voice AI غير محدود",
      "API كامل",
      "مدير حساب مخصص",
      "تدريب الفريق",
      "SLA مخصص",
      "تكامل مخصص",
    ],
  },
];

const faqs = [
  {
    q: "هل يمكنني تغيير الباقة في أي وقت؟",
    a: "نعم، يمكنك الترقية أو تخفيض باقتك في أي وقت. سيتم احتساب الفرق بشكل تناسبي في فاتورتك القادمة.",
  },
  {
    q: "هل يوجد فترة تجريبية مجانية؟",
    a: "نعم، نوفر فترة تجريبية مجانية لمدة 14 يوم لجميع الباقات بدون الحاجة لبطاقة ائتمانية.",
  },
  {
    q: "كيف يتم التعامل مع بياناتي؟",
    a: "بياناتك محمية بأعلى معايير الأمان. نستخدم تشفير SSL ونلتزم بمعايير حماية البيانات المحلية والدولية. خوادمنا موجودة في المملكة العربية السعودية.",
  },
  {
    q: "ما هي طرق الدفع المتاحة؟",
    a: "نقبل بطاقات الائتمان (فيزا، ماستركارد، مدى)، التحويل البنكي، وأيضاً الدفع عبر Apple Pay. الفواتير تصدر شهرياً أو سنوياً حسب اختيارك.",
  },
  {
    q: "كيف يمكنني التواصل مع الدعم الفني؟",
    a: "فريق الدعم متاح عبر الإيميل لباقة أساسي، ودعم أولوية عبر الواتساب والهاتف لباقة احترافي ومؤسسي. وقت الاستجابة أقل من 4 ساعات للباقات المدفوعة.",
  },
];

function CheckIcon() {
  return (
    <svg
      className="h-5 w-5 shrink-0 text-[#0FAF9A]"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={2.5}
      stroke="currentColor"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
    </svg>
  );
}

export default function PricingPage() {
  const [isYearly, setIsYearly] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  function getPrice(monthlyPrice: number | null): string {
    if (monthlyPrice === null) return "تواصل معنا";
    if (isYearly) {
      const yearly = Math.round(monthlyPrice * 12 * 0.8);
      return `${yearly.toLocaleString("ar-SA")} ر.س/سنة`;
    }
    return `${monthlyPrice} ر.س/شهر`;
  }

  function getSavings(monthlyPrice: number | null): string | null {
    if (!isYearly || monthlyPrice === null) return null;
    const saved = Math.round(monthlyPrice * 12 * 0.2);
    return `وفّر ${saved.toLocaleString("ar-SA")} ر.س سنوياً`;
  }

  return (
    <div dir="rtl" className="min-h-screen bg-[#F8FAFC]">
      {/* Header */}
      <header className="bg-[#0B3B66] text-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <nav className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold tracking-tight">
              Dealix
            </Link>
            <div className="flex items-center gap-6">
              <Link href="/" className="text-sm text-white/80 hover:text-white transition-colors">
                الرئيسية
              </Link>
              <Link
                href="/book-demo"
                className="rounded-lg bg-[#0FAF9A] px-5 py-2 text-sm font-semibold text-white hover:bg-[#0FAF9A]/90 transition-colors"
              >
                احجز عرض تجريبي
              </Link>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="bg-[#0B3B66] pb-20 pt-16 text-center text-white">
        <h1 className="text-4xl font-extrabold sm:text-5xl">خطط أسعار بسيطة وشفافة</h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-white/70">
          اختر الباقة المناسبة لحجم أعمالك. جميع الباقات تشمل تجربة مجانية 14 يوم.
        </p>

        {/* Toggle */}
        <div className="mt-10 flex items-center justify-center gap-4">
          <span className={`text-sm font-medium ${!isYearly ? "text-white" : "text-white/50"}`}>
            شهري
          </span>
          <button
            onClick={() => setIsYearly(!isYearly)}
            className={`relative inline-flex h-7 w-14 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
              isYearly ? "bg-[#0FAF9A]" : "bg-white/30"
            }`}
            role="switch"
            aria-checked={isYearly}
            aria-label="تبديل بين الدفع الشهري والسنوي"
          >
            <span
              className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out ${
                isYearly ? "-translate-x-7" : "translate-x-0"
              }`}
            />
          </button>
          <span className={`text-sm font-medium ${isYearly ? "text-white" : "text-white/50"}`}>
            سنوي
          </span>
          {isYearly && (
            <span className="rounded-full bg-[#C89B3C] px-3 py-1 text-xs font-bold text-[#0F172A]">
              خصم 20%
            </span>
          )}
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="-mt-12 px-4 pb-20 sm:px-6 lg:px-8">
        <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-3">
          {tiers.map((tier) => (
            <div
              key={tier.nameEn}
              className={`relative flex flex-col rounded-2xl bg-white p-8 shadow-lg ring-1 ${
                tier.popular
                  ? "ring-2 ring-[#0FAF9A] scale-105 z-10"
                  : "ring-gray-200"
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="rounded-full bg-[#F97316] px-4 py-1.5 text-xs font-bold text-white shadow-md">
                    الأكثر شعبية
                  </span>
                </div>
              )}

              <div className="mb-6 text-center">
                <h3 className="text-xl font-bold text-[#0F172A]">{tier.name}</h3>
                <p className="mt-1 text-sm text-gray-500">{tier.nameEn}</p>
                <div className="mt-4">
                  <span className="text-3xl font-extrabold text-[#0B3B66]">
                    {getPrice(tier.monthlyPrice)}
                  </span>
                </div>
                {getSavings(tier.monthlyPrice) && (
                  <p className="mt-1 text-sm font-medium text-[#0FAF9A]">
                    {getSavings(tier.monthlyPrice)}
                  </p>
                )}
              </div>

              <ul className="mb-8 flex-1 space-y-3">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3 text-sm text-[#0F172A]">
                    <CheckIcon />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <Link
                href={tier.monthlyPrice === null ? "/book-demo" : "/book-demo"}
                className={`block w-full rounded-xl py-3 text-center text-sm font-bold transition-colors ${
                  tier.popular
                    ? "bg-[#0FAF9A] text-white hover:bg-[#0FAF9A]/90"
                    : "bg-[#0B3B66] text-white hover:bg-[#0B3B66]/90"
                }`}
              >
                {tier.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Free Trial Banner */}
      <section className="bg-gradient-to-l from-[#0B3B66] to-[#0FAF9A] py-16">
        <div className="mx-auto max-w-4xl px-4 text-center text-white sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold sm:text-4xl">تجربة مجانية 14 يوم</h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-white/80">
            ابدأ تجربتك المجانية اليوم بدون الحاجة لبطاقة ائتمانية. استكشف جميع المميزات واكتشف كيف يمكن لـ Dealix تحويل مبيعاتك.
          </p>
          <Link
            href="/book-demo"
            className="mt-8 inline-block rounded-xl bg-[#C89B3C] px-8 py-4 text-lg font-bold text-[#0F172A] shadow-lg hover:bg-[#C89B3C]/90 transition-colors"
          >
            ابدأ تجربتك المجانية
          </Link>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <h2 className="mb-12 text-center text-3xl font-extrabold text-[#0F172A]">
            الأسئلة الشائعة
          </h2>
          <div className="space-y-4">
            {faqs.map((faq, idx) => (
              <div
                key={idx}
                className="overflow-hidden rounded-xl border border-gray-200 bg-white"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="flex w-full items-center justify-between px-6 py-5 text-right"
                >
                  <span className="text-base font-semibold text-[#0F172A]">{faq.q}</span>
                  <svg
                    className={`h-5 w-5 shrink-0 text-[#0B3B66] transition-transform duration-200 ${
                      openFaq === idx ? "rotate-180" : ""
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2}
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                  </svg>
                </button>
                {openFaq === idx && (
                  <div className="border-t border-gray-100 px-6 py-4">
                    <p className="text-sm leading-relaxed text-gray-600">{faq.a}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="bg-[#0F172A] py-16">
        <div className="mx-auto max-w-4xl px-4 text-center text-white sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold">جاهز لتحويل مبيعاتك؟</h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-white/60">
            احجز عرض تجريبي مجاني مع فريقنا واكتشف كيف يمكن لـ Dealix مضاعفة إيراداتك.
          </p>
          <Link
            href="/book-demo"
            className="mt-8 inline-block rounded-xl bg-[#F97316] px-8 py-4 text-lg font-bold text-white shadow-lg hover:bg-[#F97316]/90 transition-colors"
          >
            احجز عرض تجريبي مجاني
          </Link>
          <p className="mt-4 text-sm text-white/40">
            بدون التزام. إلغاء في أي وقت.
          </p>
        </div>
      </section>
    </div>
  );
}
