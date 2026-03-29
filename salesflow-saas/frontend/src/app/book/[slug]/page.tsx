"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import {
  Calendar, Clock, User, Phone, Mail, MessageSquare,
  Check, Share2, Loader2, MapPin, FileText, Sparkles,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export default function PublicBookingPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [form, setForm] = useState({
    name: "", phone: "", email: "", message: "",
    service_type: "", preferred_date: "", preferred_time: "",
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const update = (field: string, value: string) => setForm((p) => ({ ...p, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.phone) return setError("الاسم ورقم الجوال مطلوبين");
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/forms/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name,
          phone: form.phone,
          email: form.email,
          message: `${form.service_type ? "الخدمة: " + form.service_type + "\n" : ""}${form.preferred_date ? "التاريخ: " + form.preferred_date + "\n" : ""}${form.preferred_time ? "الوقت: " + form.preferred_time + "\n" : ""}${form.message}`,
          company: slug,
        }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "حدث خطأ");
      }
      setSuccess(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const shareUrl = typeof window !== "undefined" ? window.location.href : "";
  const shareWhatsApp = () => {
    window.open(`https://wa.me/?text=${encodeURIComponent("احجز موعدك الآن\n" + shareUrl)}`, "_blank");
  };

  const displayName = slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-primary-900 via-primary-800 to-primary-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-2xl">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Check className="w-10 h-10 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-3">تم حجز موعدك!</h1>
          <p className="text-gray-500 mb-6">سنتواصل معك قريباً لتأكيد الموعد</p>
          <div className="space-y-3">
            <button onClick={shareWhatsApp}
              className="w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-xl font-medium text-sm transition flex items-center justify-center gap-2">
              <MessageSquare className="w-5 h-5" /> شارك عبر واتساب
            </button>
            <button onClick={() => {
              const date = form.preferred_date || new Date().toISOString().split("T")[0];
              const ics = `BEGIN:VCALENDAR\nBEGIN:VEVENT\nDTSTART:${date.replace(/-/g, "")}T${(form.preferred_time || "10:00").replace(":", "")}00\nSUMMARY:موعد - ${displayName}\nEND:VEVENT\nEND:VCALENDAR`;
              const blob = new Blob([ics], { type: "text/calendar" });
              const a = document.createElement("a");
              a.href = URL.createObjectURL(blob);
              a.download = "appointment.ics";
              a.click();
            }} className="w-full bg-primary hover:bg-primary-700 text-white py-3 rounded-xl font-medium text-sm transition flex items-center justify-center gap-2">
              <Calendar className="w-5 h-5" /> أضف للتقويم
            </button>
          </div>
          <div className="mt-8 pt-4 border-t border-gray-100">
            <p className="text-xs text-gray-400 flex items-center justify-center gap-1">
              <Sparkles className="w-3 h-3" /> Powered by <a href="/" className="text-secondary font-medium">Dealix</a>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-900 via-primary-800 to-primary-900">
      {/* Header */}
      <div className="text-center pt-12 pb-8 px-4">
        <div className="w-16 h-16 bg-white/10 backdrop-blur rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Calendar className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">{displayName}</h1>
        <p className="text-primary-200 text-sm">احجز موعدك بسهولة</p>
      </div>

      {/* Form */}
      <div className="max-w-lg mx-auto px-4 pb-12">
        <div className="bg-white rounded-2xl p-6 sm:p-8 shadow-2xl">
          <h2 className="text-lg font-bold text-gray-900 mb-5">معلومات الحجز</h2>
          {error && <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">{error}</div>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الاسم *</label>
              <div className="relative">
                <User className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input type="text" required value={form.name} onChange={(e) => update("name", e.target.value)}
                  placeholder="الاسم الكامل" disabled={loading}
                  className="w-full pr-9 pl-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none disabled:opacity-50" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">رقم الجوال *</label>
              <div className="relative">
                <Phone className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input type="tel" required dir="ltr" value={form.phone} onChange={(e) => update("phone", e.target.value)}
                  placeholder="+966 5XX XXX XXXX" disabled={loading}
                  className="w-full pr-9 pl-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none disabled:opacity-50" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">البريد الإلكتروني</label>
              <div className="relative">
                <Mail className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input type="email" dir="ltr" value={form.email} onChange={(e) => update("email", e.target.value)}
                  placeholder="you@email.com" disabled={loading}
                  className="w-full pr-9 pl-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none disabled:opacity-50" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">نوع الخدمة</label>
              <select value={form.service_type} onChange={(e) => update("service_type", e.target.value)} disabled={loading}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-secondary outline-none disabled:opacity-50">
                <option value="">اختر الخدمة</option>
                <option value="consultation">استشارة</option>
                <option value="checkup">فحص / كشف</option>
                <option value="followup">متابعة</option>
                <option value="meeting">اجتماع</option>
                <option value="other">أخرى</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">التاريخ المفضل</label>
                <input type="date" value={form.preferred_date} onChange={(e) => update("preferred_date", e.target.value)}
                  disabled={loading} min={new Date().toISOString().split("T")[0]}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none disabled:opacity-50" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الوقت المفضل</label>
                <select value={form.preferred_time} onChange={(e) => update("preferred_time", e.target.value)} disabled={loading}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-secondary outline-none disabled:opacity-50">
                  <option value="">اختر</option>
                  <option value="09:00">9:00 ص</option>
                  <option value="10:00">10:00 ص</option>
                  <option value="11:00">11:00 ص</option>
                  <option value="12:00">12:00 م</option>
                  <option value="13:00">1:00 م</option>
                  <option value="14:00">2:00 م</option>
                  <option value="15:00">3:00 م</option>
                  <option value="16:00">4:00 م</option>
                  <option value="17:00">5:00 م</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
              <textarea rows={3} value={form.message} onChange={(e) => update("message", e.target.value)}
                placeholder="أي تفاصيل إضافية..." disabled={loading}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none resize-none disabled:opacity-50" />
            </div>
            <button type="submit" disabled={loading}
              className="w-full bg-secondary hover:bg-secondary-600 text-white py-3.5 rounded-xl font-bold text-sm transition flex items-center justify-center gap-2 disabled:opacity-50 shadow-lg shadow-secondary/25">
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <><Calendar className="w-5 h-5" /> احجز الآن</>}
            </button>
          </form>
        </div>

        {/* Powered by */}
        <div className="text-center mt-6">
          <p className="text-xs text-primary-300 flex items-center justify-center gap-1">
            <Sparkles className="w-3 h-3" /> Powered by <a href="/" className="text-secondary font-medium hover:underline">Dealix</a> — نظام إدارة المبيعات بالذكاء الاصطناعي
          </p>
        </div>
      </div>
    </div>
  );
}
