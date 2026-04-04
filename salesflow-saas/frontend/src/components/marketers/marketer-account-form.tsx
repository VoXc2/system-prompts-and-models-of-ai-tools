"use client";

import { useCallback, useEffect, useState } from "react";
import { Building2, CreditCard, Save, User } from "lucide-react";

export const MARKETER_PROFILE_STORAGE_KEY = "dealix_marketer_profile_v1";

export type MarketerProfile = {
  fullName: string;
  email: string;
  phone: string;
  nationalId: string;
  bankName: string;
  iban: string;
  accountHolderName: string;
  notes: string;
};

const empty: MarketerProfile = {
  fullName: "",
  email: "",
  phone: "",
  nationalId: "",
  bankName: "",
  iban: "",
  accountHolderName: "",
  notes: "",
};

export function MarketerAccountForm() {
  const [data, setData] = useState<MarketerProfile>(empty);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(MARKETER_PROFILE_STORAGE_KEY);
      if (raw) {
        const p = JSON.parse(raw) as Partial<MarketerProfile>;
        setData({ ...empty, ...p });
      }
    } catch {
      /* ignore */
    }
  }, []);

  const onSave = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      try {
        localStorage.setItem(MARKETER_PROFILE_STORAGE_KEY, JSON.stringify(data));
        setSavedAt(new Date().toLocaleString("ar-SA", { dateStyle: "medium", timeStyle: "short" }));
        window.dispatchEvent(new CustomEvent("dealix-marketer-profile-saved", { detail: data }));
      } catch {
        setSavedAt(null);
      }
    },
    [data]
  );

  const field = (key: keyof MarketerProfile, label: string, placeholder: string, type = "text") => (
    <div className="space-y-2 text-right">
      <label htmlFor={key} className="text-sm font-medium text-slate-200">
        {label}
      </label>
      <input
        id={key}
        type={type}
        autoComplete="off"
        value={data[key]}
        onChange={(e) => setData((d) => ({ ...d, [key]: e.target.value }))}
        placeholder={placeholder}
        className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-teal-500/50 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
      />
    </div>
  );

  return (
    <form onSubmit={onSave} className="space-y-8">
      <p className="rounded-2xl border border-amber-500/25 bg-amber-950/30 px-4 py-3 text-sm leading-relaxed text-amber-100/95">
        للمعاينة: تُحفظ البيانات في متصفحك فقط. عند ربط Dealix بالخادم ستُستبدل بحساب موثّق وتحويلات
        رسمية وفق العقد.
      </p>

      <section className="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
          <User className="h-5 w-5 text-teal-400" aria-hidden />
          الهوية والتواصل
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          {field("fullName", "الاسم الكامل", "مثال: فلان الفلاني")}
          {field("email", "البريد الإلكتروني", "name@example.com", "email")}
          {field("phone", "رقم الجوال", "05xxxxxxxx")}
          {field("nationalId", "الهوية / الإقامة", "10 أرقام")}
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
          <Building2 className="h-5 w-5 text-teal-400" aria-hidden />
          البنك والتحويل (واقعي للعرض)
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          {field("bankName", "اسم البنك", "مثال: الراجحي، الإنماء…")}
          {field("accountHolderName", "اسم صاحب الحساب", "كما في البنك")}
          {field("iban", "الآيبان IBAN", "SAxxxxxxxxxxxxxxxxxxxxxxxxxx")}
        </div>
        <div className="mt-4 flex items-start gap-2 text-xs text-slate-400">
          <CreditCard className="mt-0.5 h-4 w-4 shrink-0 text-teal-500/80" aria-hidden />
          <span>
            تأكد من تطابق الاسم مع العقد والعمولة. الأرقام المعروضة هنا للتنسيق الداخلي فقط حتى يتم
            تفعيل التسوية عبر المنصة.
          </span>
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 className="mb-4 text-lg font-bold text-white">ملاحظات داخلية</h2>
        <textarea
          value={data.notes}
          onChange={(e) => setData((d) => ({ ...d, notes: e.target.value }))}
          rows={4}
          placeholder="نطاق عملك، قطاعات تركز عليها، مواعيد متابعة…"
          className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-teal-500/50 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
        />
      </section>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <button
          type="submit"
          className="inline-flex items-center justify-center gap-2 rounded-2xl bg-teal-500 px-6 py-3 text-sm font-bold text-slate-950 transition hover:bg-teal-400"
        >
          <Save className="h-4 w-4" aria-hidden />
          حفظ محلياً
        </button>
        {savedAt && (
          <p className="text-sm text-teal-300/90" role="status">
            تم الحفظ: {savedAt}
          </p>
        )}
      </div>
    </form>
  );
}
