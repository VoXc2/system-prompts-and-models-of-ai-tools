import {
  Stethoscope, Calendar, MessageSquare, Users, BarChart3,
  CheckCircle2, ArrowLeft, Phone, Clock, Shield, Bot, Heart
} from "lucide-react";

const benefits = [
  { icon: Calendar, title: "حجز مواعيد تلقائي", desc: "المريض يحجز من الواتساب أو الموقع، والنظام ينظم الجدول تلقائياً" },
  { icon: MessageSquare, title: "تذكير بالمواعيد", desc: "رسائل تذكير تلقائية قبل الموعد بيوم وساعة. تقلل عدم الحضور" },
  { icon: Users, title: "متابعة ما بعد الزيارة", desc: "رسائل متابعة ذكية بعد الزيارة: استبيان رضا، تذكير بموعد المراجعة" },
  { icon: Bot, title: "رد تلقائي ذكي", desc: "يرد على الاستفسارات الشائعة: ساعات العمل، الأسعار، الموقع، التأمينات" },
  { icon: BarChart3, title: "تقارير الأداء", desc: "عدد المرضى الجدد، نسبة الحضور، الإيرادات الشهرية، أداء كل طبيب" },
  { icon: Shield, title: "خصوصية المرضى", desc: "تشفير كامل، صلاحيات محددة، سجل تدقيق لكل عملية وصول" },
];

const pipeline = ["استفسار جديد", "تم التواصل", "موعد محجوز", "تمت الزيارة", "متابعة ما بعد"];

const results = [
  { metric: "تقليل عدم الحضور", value: "حتى 60%", desc: "بتذكيرات الواتساب التلقائية" },
  { metric: "زيادة حجوزات المواعيد", value: "حتى 40%", desc: "بالرد السريع والحجز التلقائي" },
  { metric: "توفير وقت الاستقبال", value: "ساعتين/يوم", desc: "بأتمتة الردود المتكررة" },
];

export default function HealthcarePage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 h-16 flex justify-between items-center">
          <a href="/" className="flex items-center gap-2">
            <img src="/logo.svg" alt="Dealix" className="h-9 w-9" />
            <span className="text-xl font-bold text-primary">Dealix</span>
          </a>
          <a href="/book-demo" className="bg-accent hover:bg-accent-600 text-white px-5 py-2 rounded-lg text-sm font-medium transition">
            احجز عرض
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-gradient-to-br from-primary via-primary-700 to-dark pt-32 pb-20 px-4 text-white">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center gap-2 mb-4">
            <Stethoscope className="w-6 h-6 text-secondary" />
            <span className="text-secondary font-medium text-sm">قطاع العيادات والصحة</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-6 leading-tight">
            نظم عيادتك وزد حجوزاتك
            <br />
            <span className="text-secondary">بذكاء وبدون فوضى</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl leading-relaxed">
            من الاستفسار الأول إلى متابعة ما بعد الزيارة — Dealix ينظم كل شي ويتأكد ما يضيع عليك مريض واحد.
          </p>
          <a href="/book-demo" className="inline-flex items-center gap-2 bg-accent hover:bg-accent-600 text-white px-8 py-4 rounded-xl text-lg font-bold transition shadow-2xl">
            احجز عرض مجاني لعيادتك
            <ArrowLeft className="w-5 h-5" />
          </a>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-14">كل اللي تحتاجه عيادتك</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {benefits.map((b, i) => (
              <div key={i} className="bg-white border border-gray-100 rounded-2xl p-6 hover:shadow-lg transition">
                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4">
                  <b.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-bold text-lg mb-2">{b.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{b.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline Visual */}
      <section className="py-16 bg-light px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-10">رحلة المريض في Dealix</h2>
          <div className="flex items-center justify-between gap-2 overflow-x-auto pb-4">
            {pipeline.map((stage, i) => (
              <div key={i} className="flex items-center gap-2 flex-shrink-0">
                <div className="bg-primary text-white rounded-xl px-5 py-3 text-sm font-medium text-center min-w-[120px]">
                  {stage}
                </div>
                {i < pipeline.length - 1 && <ArrowLeft className="w-5 h-5 text-gray-300 flex-shrink-0" />}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Expected Results */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">نتائج متوقعة</h2>
          <p className="text-gray-500 text-center mb-12">بناءً على أفضل الممارسات في أتمتة العيادات</p>
          <div className="grid md:grid-cols-3 gap-8">
            {results.map((r, i) => (
              <div key={i} className="text-center bg-primary/5 rounded-2xl p-8">
                <div className="text-4xl font-bold font-mono text-primary mb-2">{r.value}</div>
                <div className="font-bold text-lg mb-1">{r.metric}</div>
                <div className="text-gray-500 text-sm">{r.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-primary text-white px-4">
        <div className="max-w-3xl mx-auto text-center">
          <Heart className="w-12 h-12 mx-auto mb-4 text-secondary" />
          <h2 className="text-3xl font-bold mb-4">جاهز تنظم عيادتك؟</h2>
          <p className="text-gray-300 mb-8">احجز عرض توضيحي مجاني واكتشف كيف Dealix يساعد عيادتك</p>
          <a href="/book-demo" className="inline-block bg-accent hover:bg-accent-600 text-white px-8 py-4 rounded-xl text-lg font-bold transition shadow-2xl">
            احجز عرض مجاني
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-dark text-gray-400 py-8 px-4 text-center text-sm">
        <a href="/" className="text-white hover:text-secondary transition">&larr; العودة للرئيسية</a>
        <p className="mt-4">&copy; 2025 Dealix. جميع الحقوق محفوظة</p>
      </footer>
    </div>
  );
}
