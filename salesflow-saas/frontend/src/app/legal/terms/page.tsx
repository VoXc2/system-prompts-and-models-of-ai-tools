export default function TermsPage() {
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
        <h1 className="text-4xl font-bold mb-2">الشروط والأحكام</h1>
        <p className="text-gray-400 text-sm mb-8">آخر تحديث: يناير 2025</p>

        <div className="prose prose-gray max-w-none space-y-8 text-gray-700 leading-relaxed">
          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">1. تعريفات</h2>
            <ul className="list-disc pr-6 space-y-2">
              <li><strong>&ldquo;المنصة&rdquo;</strong> تعني منصة Dealix لإدارة المبيعات والإيرادات بما فيها التطبيق والموقع و API</li>
              <li><strong>&ldquo;المشترك&rdquo;</strong> تعني الشخص أو الشركة التي تسجل في المنصة</li>
              <li><strong>&ldquo;المستخدم&rdquo;</strong> تعني أي شخص يستخدم المنصة تحت حساب المشترك</li>
              <li><strong>&ldquo;الخدمة&rdquo;</strong> تعني جميع المميزات والوظائف المتاحة عبر المنصة</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">2. قبول الشروط</h2>
            <p>
              باستخدامك للمنصة أو تسجيلك فيها، فإنك توافق على هذه الشروط والأحكام.
              إذا كنت تستخدم المنصة نيابة عن شركة، فإنك تقر بأنك مخول بإلزام الشركة بهذه الشروط.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">3. الحساب والتسجيل</h2>
            <ul className="list-disc pr-6 space-y-2">
              <li>يجب أن تكون المعلومات المقدمة دقيقة وكاملة</li>
              <li>أنت مسؤول عن الحفاظ على سرية بيانات الدخول</li>
              <li>يجب إبلاغنا فوراً عند اكتشاف أي استخدام غير مصرح به</li>
              <li>نحتفظ بحق إيقاف أو إلغاء أي حساب ينتهك هذه الشروط</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">4. الاشتراك والدفع</h2>
            <ul className="list-disc pr-6 space-y-2">
              <li>الاشتراك شهري أو سنوي حسب الخطة المختارة</li>
              <li>الأسعار بالريال السعودي وتشمل ضريبة القيمة المضافة (15%)</li>
              <li>يتجدد الاشتراك تلقائياً ما لم يتم الإلغاء قبل نهاية الدورة</li>
              <li>لا يتم استرداد المبالغ المدفوعة عن الفترة الحالية عند الإلغاء</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">5. التجربة المجانية</h2>
            <p>
              نوفر تجربة مجانية لمدة 14 يوماً بكامل المميزات. لا تحتاج بطاقة ائتمان للتسجيل.
              بعد انتهاء التجربة، يتم تعليق الحساب حتى اختيار خطة مدفوعة.
              بياناتك تبقى محفوظة لمدة 30 يوماً بعد انتهاء التجربة.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">6. الاستخدام المقبول</h2>
            <p>يُحظر استخدام المنصة في:</p>
            <ul className="list-disc pr-6 space-y-2 mt-2">
              <li>إرسال رسائل مزعجة (spam) أو غير مرغوب فيها</li>
              <li>انتحال هوية شخص أو جهة أخرى</li>
              <li>جمع بيانات شخصية بدون موافقة أصحابها</li>
              <li>أي نشاط يخالف أنظمة المملكة العربية السعودية</li>
              <li>محاولة اختراق أو التلاعب بأنظمة المنصة</li>
              <li>استخدام المنصة في أنشطة غسيل الأموال أو الاحتيال</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">7. الذكاء الاصطناعي</h2>
            <ul className="list-disc pr-6 space-y-2">
              <li>مخرجات الذكاء الاصطناعي استشارية وليست بديلاً عن الحكم البشري</li>
              <li>أنت مسؤول عن مراجعة واعتماد أي رسالة يولدها النظام قبل إرسالها أو بعده</li>
              <li>لا نضمن دقة أو ملاءمة مخرجات الذكاء الاصطناعي في جميع الحالات</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">8. مستوى الخدمة</h2>
            <p>
              نسعى لتوفير المنصة بنسبة تشغيل 99.5% شهرياً. الصيانة المجدولة يتم الإعلان عنها مسبقاً.
              لا نتحمل مسؤولية الانقطاعات الناتجة عن: خدمات طرف ثالث، كوارث طبيعية، أو أسباب خارجة عن سيطرتنا.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">9. الملكية الفكرية</h2>
            <p>
              المنصة وجميع محتوياتها (كود، تصميم، شعارات، نصوص) مملوكة لـ Dealix.
              بياناتك التي تدخلها في المنصة تبقى ملكاً لك.
              نمنحك ترخيصاً محدوداً وغير قابل للتحويل لاستخدام المنصة خلال فترة اشتراكك.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">10. تحديد المسؤولية</h2>
            <p>
              في أقصى حد يسمح به النظام، لا تتجاوز مسؤوليتنا إجمالي المبالغ المدفوعة منك
              خلال الـ 12 شهراً السابقة للمطالبة. لا نتحمل مسؤولية الأضرار غير المباشرة أو التبعية.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">11. الإلغاء</h2>
            <ul className="list-disc pr-6 space-y-2">
              <li>يمكنك إلغاء اشتراكك في أي وقت من إعدادات حسابك</li>
              <li>يبقى حسابك فعالاً حتى نهاية دورة الفوترة الحالية</li>
              <li>يمكنك تصدير بياناتك قبل إغلاق الحساب</li>
              <li>نحتفظ بالبيانات لمدة 90 يوماً بعد الإغلاق ثم يتم حذفها نهائياً</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">12. القانون المطبق</h2>
            <p>
              تخضع هذه الشروط لأنظمة المملكة العربية السعودية. أي نزاع يُحال
              للجهات القضائية المختصة في مدينة الرياض.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">13. التعديلات</h2>
            <p>
              نحتفظ بحق تعديل هذه الشروط في أي وقت. سيتم إشعارك بالتعديلات الجوهرية
              عبر البريد الإلكتروني أو إشعار داخل المنصة قبل 30 يوماً من سريانها.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-3">14. التواصل</h2>
            <p>لأي استفسارات حول هذه الشروط:</p>
            <ul className="list-none space-y-1 mt-2">
              <li>البريد: legal@dealix.sa</li>
              <li>الموقع: dealix.sa/legal/terms</li>
            </ul>
          </section>
        </div>
      </main>

      <footer className="bg-dark text-gray-400 py-8 px-4 text-center text-sm">
        <a href="/" className="text-white hover:text-secondary transition">&larr; العودة للرئيسية</a>
        <span className="mx-4">|</span>
        <a href="/legal/privacy" className="text-white hover:text-secondary transition">سياسة الخصوصية</a>
        <p className="mt-4">&copy; 2025 Dealix. جميع الحقوق محفوظة</p>
      </footer>
    </div>
  );
}
