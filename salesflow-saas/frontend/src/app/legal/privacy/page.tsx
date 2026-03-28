export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 h-16 flex justify-between items-center">
          <a href="/" className="flex items-center gap-2">
            <img src="/logo.svg" alt="Dealix" className="h-9 w-9" />
            <span className="text-xl font-bold text-primary">Dealix</span>
          </a>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-4 pt-28 pb-20">
        <h1 className="text-4xl font-bold mb-2">سياسة الخصوصية</h1>
        <p className="text-gray-400 text-sm mb-8">آخر تحديث: يناير 2025</p>

        <div className="prose prose-gray max-w-none space-y-8 text-gray-700 leading-relaxed">
          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">1. من نحن</h2>
            <p>
              Dealix (&ldquo;نحن&rdquo;، &ldquo;الشركة&rdquo;) هي منصة تقنية لإدارة المبيعات والإيرادات مقرها المملكة العربية السعودية.
              نلتزم بحماية خصوصية بياناتك الشخصية وفقاً لنظام حماية البيانات الشخصية (PDPL) الصادر عن الهيئة السعودية للبيانات والذكاء الاصطناعي (SDAIA).
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">2. البيانات التي نجمعها</h2>
            <p>نجمع الأنواع التالية من البيانات:</p>
            <ul className="list-disc pr-6 space-y-2 mt-2">
              <li><strong>بيانات الحساب:</strong> الاسم، البريد الإلكتروني، رقم الجوال، اسم الشركة، القطاع</li>
              <li><strong>بيانات الاستخدام:</strong> سجلات الدخول، الصفحات المزارة، الإجراءات المتخذة داخل المنصة</li>
              <li><strong>بيانات العملاء المحتملين:</strong> معلومات العملاء التي تدخلها في النظام (أسماء، أرقام، ملاحظات)</li>
              <li><strong>بيانات المحادثات:</strong> رسائل الواتساب والإيميل المرسلة والمستقبلة عبر المنصة</li>
              <li><strong>بيانات تقنية:</strong> عنوان IP، نوع المتصفح، نظام التشغيل</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">3. كيف نستخدم بياناتك</h2>
            <ul className="list-disc pr-6 space-y-2">
              <li>تقديم خدمات المنصة وتشغيلها</li>
              <li>تحسين تجربة المستخدم وتطوير المنتج</li>
              <li>إرسال إشعارات الخدمة والتحديثات</li>
              <li>الامتثال للمتطلبات القانونية والتنظيمية</li>
              <li>حماية أمن المنصة ومنع الاستخدام غير المشروع</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">4. الأساس القانوني للمعالجة</h2>
            <p>
              نعالج بياناتك بناءً على: (أ) موافقتك الصريحة، (ب) ضرورة تنفيذ العقد بيننا،
              (ج) التزاماتنا القانونية، أو (د) مصالحنا المشروعة في تحسين خدماتنا.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">5. مشاركة البيانات</h2>
            <p>لا نبيع بياناتك الشخصية. قد نشاركها مع:</p>
            <ul className="list-disc pr-6 space-y-2 mt-2">
              <li><strong>مزودي الخدمات:</strong> شركات الاستضافة، معالجة الدفع، خدمات الرسائل (مع التزامهم بالسرية)</li>
              <li><strong>الجهات التنظيمية:</strong> عند الطلب بموجب أمر قضائي أو التزام قانوني</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">6. حماية البيانات</h2>
            <p>
              نطبق إجراءات أمنية تشمل: تشفير البيانات أثناء النقل والتخزين (TLS/AES-256)،
              صلاحيات وصول محددة لكل مستخدم، سجلات تدقيق كاملة، ونسخ احتياطية دورية.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">7. حقوقك</h2>
            <p>بموجب نظام PDPL، لك الحق في:</p>
            <ul className="list-disc pr-6 space-y-2 mt-2">
              <li>الاطلاع على بياناتك الشخصية المخزنة لدينا</li>
              <li>طلب تصحيح أو تحديث بياناتك</li>
              <li>طلب حذف بياناتك (مع مراعاة الالتزامات القانونية)</li>
              <li>سحب موافقتك على المعالجة في أي وقت</li>
              <li>تقديم شكوى للهيئة السعودية للبيانات والذكاء الاصطناعي</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">8. الاحتفاظ بالبيانات</h2>
            <p>
              نحتفظ ببياناتك طوال مدة اشتراكك النشط وبعد الإلغاء لمدة لا تتجاوز 90 يوماً،
              ما لم يتطلب القانون فترة أطول.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">9. الذكاء الاصطناعي</h2>
            <p>
              نستخدم تقنيات الذكاء الاصطناعي لتحسين خدماتنا (مثل: الرد التلقائي، تأهيل العملاء، تحليل المحادثات).
              قرارات الذكاء الاصطناعي تخضع لمراجعة بشرية، ولك الحق في طلب تفسير أي قرار آلي يؤثر عليك.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">10. تسجيل المكالمات</h2>
            <p>
              إذا كنت تستخدم خاصية المساعد الصوتي، فإن المكالمات تُسجل وتُحفظ كنصوص لأغراض تحسين الخدمة.
              يتم إبلاغ المتصل في بداية المكالمة بأن المحادثة مسجلة.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">11. التواصل معنا</h2>
            <p>
              لأي استفسارات تتعلق بالخصوصية أو لممارسة حقوقك:
            </p>
            <ul className="list-none space-y-1 mt-2">
              <li>البريد: privacy@dealix.sa</li>
              <li>الموقع: dealix.sa/legal/privacy</li>
            </ul>
          </section>
        </div>
      </main>

      <footer className="bg-dark text-gray-400 py-8 px-4 text-center text-sm">
        <a href="/" className="text-white hover:text-secondary transition">&larr; العودة للرئيسية</a>
        <span className="mx-4">|</span>
        <a href="/legal/terms" className="text-white hover:text-secondary transition">الشروط والأحكام</a>
        <p className="mt-4">&copy; 2025 Dealix. جميع الحقوق محفوظة</p>
      </footer>
    </div>
  );
}
