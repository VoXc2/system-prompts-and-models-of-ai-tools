"use client";

import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { MessageSquare, X, Send, Loader2, Sparkles } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

function WidgetInner() {
  const params = useSearchParams();
  const tenantId = params.get("tenant_id") || "";
  const color = params.get("color") || "0FAF9A";
  const position = params.get("position") || "right";
  const phone = params.get("phone") || "";
  const title = params.get("title") || "مرحباً! كيف نقدر نساعدك؟";

  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", phone: "", message: "" });
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const accent = `#${color}`;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.phone) return;
    setLoading(true);
    try {
      await fetch(`${API_BASE}/forms/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: form.name, phone: form.phone, message: form.message, tenant_id: tenantId }),
      });
    } catch {}
    setSent(true);
    setLoading(false);
    if (phone) {
      const waMsg = encodeURIComponent(`مرحباً، اسمي ${form.name}. ${form.message}`);
      setTimeout(() => window.open(`https://wa.me/${phone.replace(/[^0-9]/g, "")}?text=${waMsg}`, "_blank"), 1500);
    }
  };

  return (
    <div className="fixed bottom-4 z-[9999]" style={{ [position === "left" ? "left" : "right"]: "16px" }}>
      {open && (
        <div className="mb-3 w-80 bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden" dir="rtl">
          <div className="p-4 text-white" style={{ backgroundColor: accent }}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2"><MessageSquare className="w-5 h-5" /><span className="font-bold text-sm">تواصل معنا</span></div>
              <button onClick={() => setOpen(false)} className="text-white/70 hover:text-white"><X className="w-4 h-4" /></button>
            </div>
            <p className="text-sm text-white/80 mt-1">{title}</p>
          </div>
          {sent ? (
            <div className="p-6 text-center">
              <div className="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-3" style={{ backgroundColor: accent + "20" }}>
                <MessageSquare className="w-7 h-7" style={{ color: accent }} />
              </div>
              <p className="font-bold text-gray-900 mb-1">شكراً لتواصلك!</p>
              <p className="text-sm text-gray-500">سنرد عليك في أقرب وقت</p>
              {phone && <p className="text-xs text-gray-400 mt-2">جاري تحويلك لواتساب...</p>}
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="p-4 space-y-3">
              <input type="text" required placeholder="الاسم" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
              <input type="tel" required dir="ltr" placeholder="+966 5XX XXX XXXX" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
              <textarea rows={2} placeholder="رسالتك..." value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none resize-none" />
              <button type="submit" disabled={loading}
                className="w-full text-white py-2.5 rounded-lg text-sm font-medium transition flex items-center justify-center gap-2 disabled:opacity-50"
                style={{ backgroundColor: accent }}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /> إرسال</>}
              </button>
            </form>
          )}
          <div className="px-4 py-2 bg-gray-50 border-t text-center">
            <a href="/" target="_blank" className="text-xs text-gray-400 hover:text-gray-500 flex items-center justify-center gap-1">
              <Sparkles className="w-3 h-3" /> Powered by Dealix
            </a>
          </div>
        </div>
      )}
      <button onClick={() => { setOpen(!open); setSent(false); }}
        className="w-14 h-14 rounded-full text-white shadow-lg hover:shadow-xl transition-all hover:scale-105 flex items-center justify-center"
        style={{ backgroundColor: accent }}>
        {open ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </button>
    </div>
  );
}

export default function WidgetPage() {
  return <Suspense fallback={null}><WidgetInner /></Suspense>;
}
