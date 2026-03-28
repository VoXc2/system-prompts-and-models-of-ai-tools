"use client";

import Link from "next/link";
import {
  MessageSquare,
  Bot,
  FileText,
  RefreshCw,
  Users,
  BarChart3,
  Link2,
  UserPlus,
  Cpu,
  Handshake,
  Zap,
  ArrowLeft,
  CheckCircle2,
} from "lucide-react";

const features = [
  {
    icon: MessageSquare,
    title: "صندوق وارد موحد",
    desc: "كل محادثات واتساب في لوحة تحكم واحدة — تابع، رد، ونظم بدون ما تطلع من المنصة.",
  },
  {
    icon: Bot,
    title: "ردود ذكية بالذكاء الاصطناعي",
    desc: "ردود تلقائية باللهجة العربية المناسبة لعملائك، تفهم السياق وتجاوب بسرعة.",
  },
  {
    icon: FileText,
    title: "قوالب رسائل معتمدة",
    desc: "قوالب واتساب جاهزة ومعتمدة من Meta — ترحيب، متابعة، عروض، وتأكيد مواعيد.",
  },
  {
    icon: RefreshCw,
    title: "تسلسلات متابعة تلقائية",
    desc: "رتّب سلاسل متابعة تشتغل تلقائي — رسائل مجدولة حسب تفاعل العميل.",
  },
  {
    icon: Users,
    title: "تصنيف تلقائي للعملاء",
    desc: "الذكاء الاصطناعي يحلل المحادثات ويصنّف العملاء المحتملين حسب جديتهم واهتمامهم.",
  },
  {
    icon: BarChart3,
    title: "تقارير المحادثات",
    desc: "تحليلات شاملة — أوقات الرد، معدل التفاعل، وأداء كل عضو في الفريق.",
  },
];

const steps = [
  {
    num: "01",
    icon: Link2,
    title: "اربط رقم واتساب بزنس",
    desc: "وصّل رقمك الرسمي بالمنصة في دقائق عبر WhatsApp Business API.",
  },
  {
    num: "02",
    icon: UserPlus,
    title: "العملاء يتواصلون معك",
    desc: "عملاءك يرسلون رسائل عبر واتساب وكلها توصلك في مكان واحد.",
  },
  {
    num: "03",
    icon: Cpu,
    title: "الذكاء الاصطناعي يرد ويصنف",
    desc: "النظام يرد تلقائي، يفهم احتياج العميل، ويصنفه حسب مرحلة الشراء.",
  },
  {
    num: "04",
    icon: Handshake,
    title: "فريقك يتابع الصفقات الجاهزة",
    desc: "فريق المبيعات يستلم العملاء الجاهزين ويركز على إغلاق الصفقات.",
  },
];

const stats = [
  {
    value: "3x",
    prefix: "حتى",
    label: "أسرع في الرد على العملاء",
  },
  {
    value: "60%",
    prefix: "تقليل الوقت الضائع بنسبة تصل إلى",
    label: "",
  },
  {
    value: "40%",
    prefix: "زيادة معدل التحويل حتى",
    label: "",
  },
];

export default function WhatsAppCRMPage() {
  return (
    <div dir="rtl" className="min-h-screen bg-[#F8FAFC] text-[#0F172A]">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-[#0B3B66]/95 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link
            href="/"
            className="flex items-center gap-2 text-white hover:text-[#0FAF9A] transition-colors"
          >
            <ArrowLeft className="w-5 h-5 rotate-180" />
            <span className="font-semibold">Dealix</span>
          </Link>
          <Link
            href="/book-demo"
            className="bg-[#0FAF9A] hover:bg-[#0FAF9A]/90 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            ابدأ تجربتك المجانية
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-bl from-[#0B3B66] via-[#0B3B66] to-[#0F172A] text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 right-20 w-72 h-72 bg-[#0FAF9A] rounded-full blur-3xl" />
          <div className="absolute bottom-10 left-10 w-96 h-96 bg-[#C89B3C] rounded-full blur-3xl" />
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32 text-center">
          <div className="inline-flex items-center gap-2 bg-[#0FAF9A]/15 border border-[#0FAF9A]/30 rounded-full px-4 py-1.5 mb-8">
            <MessageSquare className="w-4 h-4 text-[#0FAF9A]" />
            <span className="text-sm text-[#0FAF9A] font-medium">
              WhatsApp Business API + CRM
            </span>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight mb-6">
            واتساب CRM —{" "}
            <span className="text-[#0FAF9A]">حوّل محادثاتك لصفقات</span>
          </h1>
          <p className="text-lg sm:text-xl text-white/80 max-w-3xl mx-auto mb-10 leading-relaxed">
            اربط واتساب بزنس API مع خط أنابيب المبيعات الكامل. كل رسالة تتحول
            لفرصة، كل محادثة تنتقل لمرحلة البيع المناسبة — تلقائي وبالذكاء
            الاصطناعي.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/book-demo"
              className="bg-[#0FAF9A] hover:bg-[#0FAF9A]/90 text-white px-8 py-3.5 rounded-xl text-lg font-semibold transition-colors shadow-lg shadow-[#0FAF9A]/25"
            >
              ابدأ تجربتك المجانية
            </Link>
            <Link
              href="/pricing"
              className="border border-white/25 hover:bg-white/10 text-white px-8 py-3.5 rounded-xl text-lg font-medium transition-colors"
            >
              اطّلع على الأسعار
            </Link>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-[#0B3B66] mb-4">
            كل ما تحتاجه لإدارة واتساب باحترافية
          </h2>
          <p className="text-lg text-[#0F172A]/60 max-w-2xl mx-auto">
            أدوات متكاملة تحوّل واتساب من مجرد تطبيق محادثة لمنصة مبيعات ذكية.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <div
              key={i}
              className="bg-white rounded-2xl p-6 border border-[#0B3B66]/10 hover:border-[#0FAF9A]/40 hover:shadow-lg hover:shadow-[#0FAF9A]/5 transition-all duration-300 group"
            >
              <div className="w-12 h-12 bg-[#0FAF9A]/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-[#0FAF9A]/20 transition-colors">
                <f.icon className="w-6 h-6 text-[#0FAF9A]" />
              </div>
              <h3 className="text-xl font-bold text-[#0B3B66] mb-2">
                {f.title}
              </h3>
              <p className="text-[#0F172A]/60 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-[#0B3B66] text-white py-20 sm:py-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              كيف يشتغل؟
            </h2>
            <p className="text-lg text-white/70 max-w-2xl mx-auto">
              أربع خطوات بسيطة تربط واتساب بزنس بنظام مبيعاتك الكامل.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, i) => (
              <div key={i} className="relative text-center">
                <div className="w-16 h-16 bg-[#0FAF9A]/15 border border-[#0FAF9A]/30 rounded-2xl flex items-center justify-center mx-auto mb-5">
                  <step.icon className="w-7 h-7 text-[#0FAF9A]" />
                </div>
                <span className="inline-block text-sm font-bold text-[#C89B3C] mb-2">
                  خطوة {step.num}
                </span>
                <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                <p className="text-white/60 leading-relaxed text-sm">
                  {step.desc}
                </p>
                {i < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-8 -left-4 w-8 text-[#0FAF9A]/40">
                    <ArrowLeft className="w-6 h-6" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 sm:py-28 bg-gradient-to-b from-[#F8FAFC] to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-[#0B3B66] mb-4">
              نتائج متوقعة وواقعية
            </h2>
            <p className="text-[#0F172A]/60 max-w-2xl mx-auto">
              تقديرات مبنية على بيانات أداء أنظمة CRM المتكاملة مع واتساب في
              السوق السعودي.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-2xl p-8 border border-[#0B3B66]/10 text-center shadow-sm">
              <div className="text-sm font-medium text-[#0F172A]/50 mb-3">
                حتى
              </div>
              <div className="text-5xl sm:text-6xl font-bold text-[#0FAF9A] mb-3">
                3x
              </div>
              <p className="text-[#0B3B66] font-semibold text-lg">
                أسرع في الرد على العملاء
              </p>
            </div>
            <div className="bg-white rounded-2xl p-8 border border-[#0B3B66]/10 text-center shadow-sm">
              <div className="text-sm font-medium text-[#0F172A]/50 mb-3">
                تقليل الوقت الضائع بنسبة تصل إلى
              </div>
              <div className="text-5xl sm:text-6xl font-bold text-[#F97316] mb-3">
                60%
              </div>
              <p className="text-[#0B3B66] font-semibold text-lg">
                وقت أقل في المهام التكرارية
              </p>
            </div>
            <div className="bg-white rounded-2xl p-8 border border-[#0B3B66]/10 text-center shadow-sm">
              <div className="text-sm font-medium text-[#0F172A]/50 mb-3">
                زيادة معدل التحويل حتى
              </div>
              <div className="text-5xl sm:text-6xl font-bold text-[#C89B3C] mb-3">
                40%
              </div>
              <p className="text-[#0B3B66] font-semibold text-lg">
                عملاء محتملين يتحولون لصفقات
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-bl from-[#0B3B66] to-[#0F172A] text-white py-20 sm:py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 bg-[#C89B3C]/15 border border-[#C89B3C]/30 rounded-full px-4 py-1.5 mb-8">
            <Zap className="w-4 h-4 text-[#C89B3C]" />
            <span className="text-sm text-[#C89B3C] font-medium">
              14 يوم تجربة مجانية
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-6 leading-tight">
            جاهز تحوّل واتساب لأقوى قناة مبيعات؟
          </h2>
          <p className="text-lg text-white/70 max-w-2xl mx-auto mb-10 leading-relaxed">
            سجّل الحين وابدأ تستقبل عملاءك، ترد عليهم بالذكاء الاصطناعي،
            وتتابع صفقاتك — كلها من مكان واحد.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
            <Link
              href="/book-demo"
              className="bg-[#0FAF9A] hover:bg-[#0FAF9A]/90 text-white px-10 py-4 rounded-xl text-lg font-bold transition-colors shadow-lg shadow-[#0FAF9A]/25"
            >
              ابدأ تجربتك المجانية
            </Link>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-white/50">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-[#0FAF9A]" />
              بدون بطاقة ائتمان
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-[#0FAF9A]" />
              إعداد في دقائق
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-[#0FAF9A]" />
              دعم فني بالعربي
            </span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0F172A] text-white/40 py-8 text-center text-sm">
        <div className="max-w-7xl mx-auto px-4">
          <p>&copy; 2026 Dealix. جميع الحقوق محفوظة.</p>
        </div>
      </footer>
    </div>
  );
}
