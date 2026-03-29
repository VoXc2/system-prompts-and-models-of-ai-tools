"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Phone, Mail, Clock, CheckCircle2, ArrowLeft, Loader2,
  Share2, Copy, Check, MessageSquare, Sparkles,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

function BookDemoForm() {
  const searchParams = useSearchParams();
  const [form, setForm] = useState({
    name: "", phone: "", email: "", company: "", industry: "", team_size: "",
  });
  const [utm, setUtm] = useState({ utm_source: "", utm_medium: "", utm_campaign: "" });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setUtm({
      utm_source: searchParams.get("utm_source") || "",
      utm_medium: searchParams.get("utm_medium") || "",
      utm_campaign: searchParams.get("utm_campaign") || "",
    });
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.phone) return setError("الاسم ورقم الجوال مطلوبين");
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/forms/demo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, ...utm }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `خطأ ${res.status}`);
      }
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "حدث خطأ، حاول مرة أخرى");
    } finally {
      setLoading(false);
    }
  };

  const shareUrl = typeof window !== "undefined" ? window.location.href : "";
  const shareText = "احجز عرض توضيحي مجاني لنظام Dealix — نظام AI لإدارة المبيعات";

  const shareWhatsApp = () => {
    window.open(`https://wa.me/?text=${encodeURIComponent(shareText + "\n" + shareUrl)}`, "_blank");
  };
  const shareTwitter = () => {
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`, "_blank");
  };
  const copyLink = () => {
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const update = (field: string, value: string) => setForm((p) => ({ ...p, [field]: value }));

  return (
    <div className="min-h-screen bg-light text-gray-900">
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 h-16 flex justify-between items-center">
          <a href="/" className="flex items-center gap-2">
            <img src="/logo.svg" alt="Dealix" className="h-9 w-9" />
            <span className="text-xl font-bold text-primary">Dealix</span>
          </a>
          <div className="flex items-center gap-2">
            <button onClick={shareWhatsApp} className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition" title="شارك عبر واتساب">
              <MessageSquare className="w-5 h-5" />
            </button>
            <button onClick={copyLink} className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition" title="نسخ الرابط">
              {copied ? <Check className="w-5 h-5 text-green-600" /> : <Copy className="w-5 h-5" />}
            </button>
          </div>
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

            {/* Share section */}
            <div className="mt-6 p-4 bg-secondary-50 rounded-xl">
              <p className="text-sm font-medium text-secondary-700 mb-3 flex items-center gap-2">
                <Share2 className="w-4 h-4" /> شارك هذا العرض مع من يحتاجه
              </p>
              <div className="flex gap-2">
                <button onClick={shareWhatsApp} className="flex-1 bg-green-500 hover:bg-green-600 text-white py-2.5 rounded-lg text-sm font-medium transition flex items-center justify-center gap-2">
                  <MessageSquare className="w-4 h-4" /> واتساب
                </button>
                <button onClick={shareTwitter} className="flex-1 bg-gray-900 hover:bg-gray-800 text-white py-2.5 rounded-lg text-sm font-medium transition flex items-center justify-center gap-2">
                  𝕏 تويتر
                </button>
                <button onClick={copyLink} className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2.5 rounded-lg text-sm font-medium transition flex items-center justify-center gap-2">
                  {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                  {copied ? "تم النسخ" : "نسخ الرابط"}
                </button>
              </div>
            </div>
          </div>

          {/* Right - Form or Success */}
          <div className="bg-white rounded-2xl border border-gray-100 p-8 shadow-sm">
            {success ? (
              <div className="text-center py-8">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle2 className="w-10 h-10 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">شكراً لك!</h2>
                <p className="text-gray-500 mb-6 leading-relaxed">
                  تم استلام طلبك بنجاح. فريقنا سيتواصل معك خلال ساعات قليلة لتحديد موعد العرض التوضيحي.
                </p>
                <div className="space-y-3">
                  <a
                    href={`https://wa.me/966500000000?text=${encodeURIComponent("مرحبا، حجزت عرض توضيحي عبر الموقع")}`}
                    target="_blank"
                    className="w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-xl font-bold text-sm transition flex items-center justify-center gap-2"
                  >
                    <MessageSquare className="w-5 h-5" /> تواصل عبر واتساب الآن
                  </a>
                  <a href="/" className="block w-full bg-gray-100 hover:bg-gray-200 text-gray-700 py-3 rounded-xl font-bold text-sm transition text-center">
                    العودة للرئيسية
                  </a>
                </div>
                <div className="mt-8 pt-6 border-t border-gray-100">
                  <p className="text-sm text-gray-400 mb-3">شارك Dealix مع أصدقائك</p>
                  <div className="flex gap-2 justify-center">
                    <button onClick={shareWhatsApp} className="p-2.5 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition">
                      <MessageSquare className="w-5 h-5" />
                    </button>
                    <button onClick={shareTwitter} className="p-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition">
                      <Share2 className="w-5 h-5" />
                    </button>
                    <button onClick={copyLink} className="p-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition">
                      {copied ? <Check className="w-5 h-5 text-green-600" /> : <Copy className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <>
                <h2 className="text-xl font-bold mb-6">معلوماتك</h2>
                {error && (
                  <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">{error}</div>
                )}
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">الاسم الكامل *</label>
                    <input type="text" required value={form.name} onChange={(e) => update("name", e.target.value)} disabled={loading}
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary disabled:opacity-50" placeholder="محمد عبدالله" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">رقم الجوال *</label>
                    <input type="tel" required dir="ltr" value={form.phone} onChange={(e) => update("phone", e.target.value)} disabled={loading}
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary disabled:opacity-50" placeholder="+966 5XX XXX XXXX" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">البريد الإلكتروني</label>
                    <input type="email" dir="ltr" value={form.email} onChange={(e) => update("email", e.target.value)} disabled={loading}
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary disabled:opacity-50" placeholder="you@company.com" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">اسم الشركة</label>
                    <input type="text" value={form.company} onChange={(e) => update("company", e.target.value)} disabled={loading}
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary disabled:opacity-50" placeholder="اسم شركتك أو عيادتك" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">القطاع</label>
                    <select value={form.industry} onChange={(e) => update("industry", e.target.value)} disabled={loading}
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary bg-white disabled:opacity-50">
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
                    <select value={form.team_size} onChange={(e) => update("team_size", e.target.value)} disabled={loading}
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary bg-white disabled:opacity-50">
                      <option value="">اختر الحجم</option>
                      <option value="1-5">1 - 5 أشخاص</option>
                      <option value="6-15">6 - 15 شخص</option>
                      <option value="16-50">16 - 50 شخص</option>
                      <option value="50+">أكثر من 50</option>
                    </select>
                  </div>
                  <button type="submit" disabled={loading}
                    className="w-full bg-accent hover:bg-accent-600 text-white py-4 rounded-xl font-bold text-lg transition shadow-lg shadow-accent/25 flex items-center justify-center gap-2 disabled:opacity-50">
                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <><span>احجز العرض الآن</span><ArrowLeft className="w-5 h-5" /></>}
                  </button>
                  <p className="text-xs text-gray-400 text-center">
                    بالضغط على الزر، أنت توافق على <a href="/legal/privacy" className="underline">سياسة الخصوصية</a> و<a href="/legal/terms" className="underline">الشروط والأحكام</a>
                  </p>
                </form>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function BookDemoPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>}>
      <BookDemoForm />
    </Suspense>
  );
}
