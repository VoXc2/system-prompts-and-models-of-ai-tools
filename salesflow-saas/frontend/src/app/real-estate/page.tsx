import {
  Home, MapPin, MessageSquare, Users, BarChart3,
  CheckCircle2, ArrowLeft, Phone, Building2, Bot, TrendingUp
} from "lucide-react";

const districts = [
  "النرجس", "الياسمين", "حطين", "العارض", "الملقا", "الربيع",
  "العقيق", "الصحافة", "النخيل", "الورود", "المروج", "الغدير",
  "الملك فهد", "العليا", "السليمانية", "المحمدية", "الرائد", "النفل",
  "قرطبة", "الحمراء",
];

const benefits = [
  { icon: Users, title: "إدارة عملاء ذكية", desc: "كل عميل مربوط بتفضيلاته: ميزانية، حي مفضل، نوع عقار. المطابقة تلقائية" },
  { icon: MessageSquare, title: "متابعة واتساب تلقائية", desc: "رسائل متابعة ذكية بعد الجولة، تذكير بالعروض الجديدة، وتحديثات الأسعار" },
  { icon: MapPin, title: "عرض عقارات بالواتساب", desc: "أرسل كتالوج عقارات مصور مباشرة للعميل عبر الواتساب" },
  { icon: Bot, title: "وكيل مبيعات ذكي", desc: "يرد على الاستفسارات، يؤهل العميل (ميزانية + جدية)، ويحول الجاد لك" },
  { icon: BarChart3, title: "تقارير أداء الوسطاء", desc: "كم عرض عرض كل وسيط؟ كم صفقة أغلق؟ كم عمولة حقق؟" },
  { icon: TrendingUp, title: "تحليل السوق", desc: "تتبع اتجاهات الأسعار، أكثر الأحياء طلباً، متوسط أيام البيع" },
];

const pipeline = ["استفسار جديد", "تم التواصل", "جولة عقارية", "عرض سعر", "تفاوض", "تم الإغلاق"];

export default function RealEstatePage() {
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
      <section className="bg-gradient-to-br from-secondary-700 via-secondary to-primary pt-32 pb-20 px-4 text-white">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center gap-2 mb-4">
            <Home className="w-6 h-6 text-white/80" />
            <span className="text-white/80 font-medium text-sm">قطاع العقارات — الرياض</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-6 leading-tight">
            نظّم صفقاتك العقارية
            <br />
            <span className="text-accent">وأغلق أسرع</span>
          </h1>
          <p className="text-xl text-white/80 mb-8 max-w-2xl leading-relaxed">
            من الاستفسار الأول إلى توقيع العقد — Dealix ينظم عملاءك، يتابعهم تلقائياً، ويساعدك تغلق أسرع بـ 3 مرات.
          </p>
          <a href="/book-demo" className="inline-flex items-center gap-2 bg-accent hover:bg-accent-600 text-white px-8 py-4 rounded-xl text-lg font-bold transition shadow-2xl">
            احجز عرض مجاني لمكتبك
            <ArrowLeft className="w-5 h-5" />
          </a>
        </div>
      </section>

      {/* Riyadh Districts */}
      <section className="py-12 bg-light px-4">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-xl font-bold mb-6">نغطي أحياء الرياض الأكثر طلباً</h2>
          <div className="flex flex-wrap justify-center gap-2">
            {districts.map((d, i) => (
              <span key={i} className="bg-white border border-gray-200 rounded-full px-4 py-1.5 text-sm text-gray-600">
                {d}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-14">كل اللي يحتاجه مكتبك العقاري</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {benefits.map((b, i) => (
              <div key={i} className="bg-white border border-gray-100 rounded-2xl p-6 hover:shadow-lg transition">
                <div className="w-12 h-12 bg-secondary/10 rounded-xl flex items-center justify-center mb-4">
                  <b.icon className="w-6 h-6 text-secondary" />
                </div>
                <h3 className="font-bold text-lg mb-2">{b.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{b.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline */}
      <section className="py-16 bg-light px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-10">رحلة العميل العقاري في Dealix</h2>
          <div className="flex items-center justify-between gap-2 overflow-x-auto pb-4">
            {pipeline.map((stage, i) => (
              <div key={i} className="flex items-center gap-2 flex-shrink-0">
                <div className="bg-secondary text-white rounded-xl px-4 py-3 text-sm font-medium text-center min-w-[100px]">
                  {stage}
                </div>
                {i < pipeline.length - 1 && <ArrowLeft className="w-5 h-5 text-gray-300 flex-shrink-0" />}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-secondary text-white px-4">
        <div className="max-w-3xl mx-auto text-center">
          <Building2 className="w-12 h-12 mx-auto mb-4 text-white/80" />
          <h2 className="text-3xl font-bold mb-4">جاهز تنظم مكتبك العقاري؟</h2>
          <p className="text-white/80 mb-8">احجز عرض توضيحي واكتشف كيف Dealix يزيد إغلاقاتك</p>
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
