"use client";

import { useEffect, useState } from "react";
import { tenant as tenantApi } from "@/lib/api";
import {
  Code2, Copy, Check, Loader2, Eye, Palette,
  MessageSquare, Smartphone, Globe, Settings,
} from "lucide-react";

export default function WidgetSetupPage() {
  const [tenantData, setTenantData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [color, setColor] = useState("0FAF9A");
  const [position, setPosition] = useState("right");
  const [phone, setPhone] = useState("");
  const [title, setTitle] = useState("مرحباً! كيف نقدر نساعدك؟");

  useEffect(() => {
    tenantApi.get()
      .then((data: any) => {
        setTenantData(data);
        if (data.whatsapp_number) setPhone(data.whatsapp_number);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const tenantId = tenantData?.id || "YOUR_TENANT_ID";
  const widgetUrl = `${typeof window !== "undefined" ? window.location.origin : ""}/widget?tenant_id=${tenantId}&color=${color}&position=${position}&phone=${encodeURIComponent(phone)}&title=${encodeURIComponent(title)}`;

  const embedCode = `<!-- Dealix Widget -->
<iframe src="${widgetUrl}" style="position:fixed;bottom:0;${position}:0;width:400px;height:500px;border:none;z-index:9999;" allow="clipboard-write"></iframe>`;

  const scriptCode = `<!-- Dealix Widget Script -->
<script>
(function(){var d=document,s=d.createElement('iframe');
s.src='${widgetUrl}';
s.style='position:fixed;bottom:0;${position}:0;width:400px;height:500px;border:none;z-index:9999;pointer-events:auto;';
s.allow='clipboard-write';d.body.appendChild(s);})();
</script>`;

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-secondary" /></div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <MessageSquare className="w-6 h-6 text-secondary" /> ودجت التواصل
        </h2>
        <p className="text-sm text-gray-500">أضف زر تواصل ذكي على موقعك — يجمع بيانات العملاء ويحولهم لواتساب تلقائياً</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Settings */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5 text-secondary" /> التخصيص
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">اللون الأساسي</label>
              <div className="flex gap-2">
                <input type="color" value={`#${color}`} onChange={(e) => setColor(e.target.value.replace("#", ""))}
                  className="w-10 h-10 rounded-lg border border-gray-300 cursor-pointer" />
                <input type="text" dir="ltr" value={`#${color}`} onChange={(e) => setColor(e.target.value.replace("#", ""))}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" />
              </div>
              <div className="flex gap-2 mt-2">
                {["0FAF9A", "0B3B66", "FF6B35", "8B5CF6", "EC4899", "EF4444"].map((c) => (
                  <button key={c} onClick={() => setColor(c)}
                    className={`w-8 h-8 rounded-full border-2 transition ${color === c ? "border-gray-900 scale-110" : "border-transparent"}`}
                    style={{ backgroundColor: `#${c}` }} />
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الموضع</label>
              <div className="flex gap-2">
                <button onClick={() => setPosition("right")}
                  className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition ${position === "right" ? "bg-secondary text-white" : "bg-gray-100 text-gray-600"}`}>
                  يمين
                </button>
                <button onClick={() => setPosition("left")}
                  className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition ${position === "left" ? "bg-secondary text-white" : "bg-gray-100 text-gray-600"}`}>
                  يسار
                </button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">رقم واتساب</label>
              <input type="tel" dir="ltr" value={phone} onChange={(e) => setPhone(e.target.value)}
                placeholder="+966 5XX XXX XXXX"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">رسالة الترحيب</label>
              <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
            </div>
          </div>
        </div>

        {/* Preview */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Eye className="w-5 h-5 text-secondary" /> معاينة
          </h3>
          <div className="bg-gray-100 rounded-xl p-4 h-80 relative overflow-hidden">
            <div className="text-center text-gray-400 text-xs mt-4">موقعك هنا</div>
            <div className={`absolute bottom-4 ${position === "left" ? "left-4" : "right-4"}`}>
              <div className="mb-2 w-64 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden" dir="rtl">
                <div className="p-3 text-white text-xs" style={{ backgroundColor: `#${color}` }}>
                  <div className="flex items-center gap-1.5"><MessageSquare className="w-3.5 h-3.5" /><span className="font-bold">تواصل معنا</span></div>
                  <p className="text-white/80 mt-0.5 text-[10px]">{title}</p>
                </div>
                <div className="p-2.5 space-y-1.5">
                  <div className="h-6 bg-gray-100 rounded text-[10px] text-gray-400 flex items-center px-2">الاسم</div>
                  <div className="h-6 bg-gray-100 rounded text-[10px] text-gray-400 flex items-center px-2" dir="ltr">+966</div>
                  <div className="h-5 rounded text-white text-[10px] flex items-center justify-center" style={{ backgroundColor: `#${color}` }}>إرسال</div>
                </div>
              </div>
              <div className="w-10 h-10 rounded-full text-white flex items-center justify-center shadow-lg"
                style={{ backgroundColor: `#${color}`, marginRight: position === "left" ? "0" : "auto", marginLeft: position === "left" ? "auto" : "0" }}>
                <MessageSquare className="w-5 h-5" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Embed Codes */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Code2 className="w-5 h-5 text-secondary" /> كود التضمين
        </h3>

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">طريقة 1: Script (الأسهل)</label>
              <button onClick={() => copyCode(scriptCode)} className="flex items-center gap-1.5 text-xs text-secondary hover:text-secondary-600 transition">
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />} {copied ? "تم النسخ" : "نسخ"}
              </button>
            </div>
            <pre dir="ltr" className="bg-gray-900 text-green-400 p-4 rounded-lg text-xs overflow-x-auto font-mono leading-relaxed">{scriptCode}</pre>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">طريقة 2: iFrame</label>
              <button onClick={() => copyCode(embedCode)} className="flex items-center gap-1.5 text-xs text-secondary hover:text-secondary-600 transition">
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />} {copied ? "تم النسخ" : "نسخ"}
              </button>
            </div>
            <pre dir="ltr" className="bg-gray-900 text-green-400 p-4 rounded-lg text-xs overflow-x-auto font-mono leading-relaxed">{embedCode}</pre>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-4">
          <h4 className="font-bold text-blue-800 text-sm mb-2">كيف تضيف الودجت لموقعك؟</h4>
          <ol className="text-sm text-blue-700 space-y-1.5 list-decimal list-inside">
            <li>انسخ كود الـ Script أعلاه</li>
            <li>ألصقه قبل <code className="bg-blue-100 px-1 rounded" dir="ltr">&lt;/body&gt;</code> في موقعك</li>
            <li>احفظ وارفع التعديلات</li>
            <li>الودجت راح يظهر تلقائياً لزوار موقعك</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
