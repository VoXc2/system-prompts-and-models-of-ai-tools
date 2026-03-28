import { Phone, Mail, Clock, CheckCircle2, ArrowLeft } from "lucide-react";

export default function BookDemoPage() {
  return (
    <div className="min-h-screen bg-light text-gray-900">
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 h-16 flex justify-between items-center">
          <a href="/" className="flex items-center gap-2">
            <img src="/logo.svg" alt="Dealix" className="h-9 w-9" />
            <span className="text-xl font-bold text-primary">Dealix</span>
          </a>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-4 pt-28 pb-20">
        <div className="grid md:grid-cols-2 gap-12">
          {/* Left - Info */}
          <div>
            <h1 className="text-4xl font-bold mb-4">احجز عرض توضيحي مجاني</h1>
            <p className="text-gray-500 text-lg mb-8 leading-relaxed">
              في 20 دقيقة نعرّفك على النظام، نفهم احتياجك، ونوريك كيف Dealix يناسب شركتك.
            </p>

            <div className="space-y-6">
              {[
                { icon: CheckCircle2, text: "عرض مباشر مخصص لقطاعك (عيادات / عقارات / غيرها)" },
                { icon: CheckCircle2, text: "نفهم تحدياتك ونقترح الحل المناسب" },
                { icon: CheckCircle2, text: "إجابة على كل أسئلتك بدون التزام" },
                { icon: CheckCircle2, text: "نساعدك تبدأ التجربة المجانية فوراً" },
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-3">
                  <item.icon className="w-5 h-5 text-secondary mt-0.5 flex-shrink-0" />
                  <p className="text-gray-700">{item.text}</p>
                </div>
              ))}
            </div>

            <div className="mt-10 p-6 bg-white rounded-2xl border border-gray-100">
              <h3 className="font-bold mb-4">أو تواصل مباشرة</h3>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-center gap-2"><Phone className="w-4 h-4 text-primary" /> واتساب بزنس</div>
                <div className="flex items-center gap-2"><Mail className="w-4 h-4 text-primary" /> sales@dealix.sa</div>
                <div className="flex items-center gap-2"><Clock className="w-4 h-4 text-primary" /> الأحد - الخميس، 9 ص - 6 م</div>
              </div>
            </div>
          </div>

          {/* Right - Form */}
          <div className="bg-white rounded-2xl border border-gray-100 p-8 shadow-sm">
            <h2 className="text-xl font-bold mb-6">معلوماتك</h2>
            <form className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الاسم الكامل</label>
                <input type="text" className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary" placeholder="محمد عبدالله" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">رقم الجوال</label>
                <input type="tel" dir="ltr" className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary" placeholder="+966 5XX XXX XXXX" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">البريد الإلكتروني</label>
                <input type="email" dir="ltr" className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary" placeholder="you@company.com" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">اسم الشركة</label>
                <input type="text" className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary" placeholder="اسم شركتك أو عيادتك" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">القطاع</label>
                <select className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary bg-white">
                  <option value="">اختر القطاع</option>
                  <option value="healthcare">عيادات / صحة</option>
                  <option value="real_estate">عقارات</option>
                  <option value="construction">مقاولات</option>
                  <option value="beauty">صالونات / تجميل</option>
                  <option value="education">تعليم / تدريب</option>
                  <option value="other">قطاع آخر</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">حجم الفريق</label>
                <select className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary bg-white">
                  <option value="">اختر الحجم</option>
                  <option value="1-5">1 - 5 أشخاص</option>
                  <option value="6-15">6 - 15 شخص</option>
                  <option value="16-50">16 - 50 شخص</option>
                  <option value="50+">أكثر من 50</option>
                </select>
              </div>
              <button type="submit" className="w-full bg-accent hover:bg-accent-600 text-white py-4 rounded-xl font-bold text-lg transition shadow-lg shadow-accent/25 flex items-center justify-center gap-2">
                احجز العرض الآن
                <ArrowLeft className="w-5 h-5" />
              </button>
              <p className="text-xs text-gray-400 text-center">
                بالضغط على الزر، أنت توافق على <a href="/legal/privacy" className="underline">سياسة الخصوصية</a> و<a href="/legal/terms" className="underline">الشروط والأحكام</a>
              </p>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
