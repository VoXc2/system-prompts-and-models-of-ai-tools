"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { tenant as tenantApi, users as usersApi } from "@/lib/api";
import {
  Rocket, Building2, MessageSquare, UsersRound, PartyPopper,
  ArrowLeft, ArrowRight, Loader2, Plus, Trash2, Check,
  Phone, Mail, Globe, Smartphone, QrCode,
} from "lucide-react";

const STEPS = [
  { title: "مرحباً", icon: Rocket },
  { title: "معلومات الشركة", icon: Building2 },
  { title: "ربط واتساب", icon: MessageSquare },
  { title: "دعوة الفريق", icon: UsersRound },
  { title: "جاهز!", icon: PartyPopper },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [company, setCompany] = useState({
    name: "", name_ar: "", phone: "", email: "", whatsapp_number: "", industry: "",
  });

  const [members, setMembers] = useState<{ email: string; role: string; password: string }[]>([]);

  const saveCompany = async () => {
    setLoading(true);
    setError("");
    try {
      await tenantApi.update(company);
      setStep(2);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const inviteMembers = async () => {
    const valid = members.filter((m) => m.email);
    if (valid.length === 0) { setStep(4); return; }
    setLoading(true);
    setError("");
    try {
      for (const m of valid) {
        await usersApi.create({ email: m.email, role: m.role, password: m.password || "Temp@1234" });
      }
      setStep(4);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addMember = () => setMembers([...members, { email: "", role: "agent", password: "" }]);
  const removeMember = (i: number) => setMembers(members.filter((_, idx) => idx !== i));
  const updateMember = (i: number, field: string, value: string) =>
    setMembers(members.map((m, idx) => (idx === i ? { ...m, [field]: value } : m)));

  const next = () => {
    if (step === 1) return saveCompany();
    if (step === 3) return inviteMembers();
    setStep(step + 1);
  };

  return (
    <div className="max-w-2xl mx-auto py-8">
      {/* Step Indicator */}
      <div className="flex items-center justify-center mb-10 px-4">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
              i < step ? "bg-green-500 text-white" : i === step ? "bg-secondary text-white scale-110" : "bg-gray-200 text-gray-500"
            }`}>
              {i < step ? <Check className="w-5 h-5" /> : i + 1}
            </div>
            {i < STEPS.length - 1 && (
              <div className={`w-12 sm:w-20 h-1 mx-1 rounded ${i < step ? "bg-green-500" : "bg-gray-200"}`} />
            )}
          </div>
        ))}
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 p-6 sm:p-8 shadow-sm">
        {error && <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">{error}</div>}

        {step === 0 && (
          <div className="text-center py-6">
            <div className="w-20 h-20 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Rocket className="w-10 h-10 text-secondary" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-4">مرحباً بك في Dealix!</h1>
            <p className="text-gray-500 text-lg mb-8 leading-relaxed max-w-md mx-auto">
              نظام الذكاء الاصطناعي لإدارة المبيعات. خلنا نجهز حسابك في دقائق.
            </p>
            <div className="grid sm:grid-cols-2 gap-4 text-right mb-8">
              {[
                { icon: MessageSquare, text: "ربط واتساب بيزنس لاستقبال العملاء تلقائياً" },
                { icon: UsersRound, text: "إدارة فريق المبيعات والصلاحيات" },
                { icon: Building2, text: "لوحة تحكم ذكية لمتابعة الصفقات" },
                { icon: Globe, text: "صفحة حجز عامة لعملائك" },
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50">
                  <item.icon className="w-5 h-5 text-secondary mt-0.5 shrink-0" />
                  <p className="text-sm text-gray-700">{item.text}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 1 && (
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1 flex items-center gap-2">
              <Building2 className="w-5 h-5 text-secondary" /> معلومات شركتك
            </h2>
            <p className="text-sm text-gray-500 mb-6">هذي المعلومات تظهر لعملائك في صفحة الحجز والتواصل</p>
            <div className="grid sm:grid-cols-2 gap-4">
              {[
                { key: "name", label: "اسم الشركة (English)", placeholder: "Success Co.", dir: "ltr" },
                { key: "name_ar", label: "اسم الشركة (عربي)", placeholder: "شركة النجاح" },
                { key: "phone", label: "رقم الهاتف", placeholder: "+966 5XX", dir: "ltr" },
                { key: "email", label: "البريد الإلكتروني", placeholder: "info@co.com", dir: "ltr" },
                { key: "whatsapp_number", label: "واتساب بيزنس", placeholder: "+966 5XX", dir: "ltr" },
                { key: "industry", label: "القطاع", placeholder: "عقارات، عيادات..." },
              ].map((f) => (
                <div key={f.key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{f.label}</label>
                  <input type="text" dir={f.dir || "rtl"} placeholder={f.placeholder}
                    value={company[f.key as keyof typeof company]}
                    onChange={(e) => setCompany({ ...company, [f.key]: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none" />
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-green-600" /> ربط واتساب بيزنس
            </h2>
            <p className="text-sm text-gray-500 mb-6">اربط حسابك لاستقبال والرد على العملاء تلقائياً</p>
            <div className="space-y-6">
              <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
                <div className="w-32 h-32 bg-white rounded-2xl border-2 border-dashed border-green-300 flex items-center justify-center mx-auto mb-4">
                  <QrCode className="w-16 h-16 text-green-400" />
                </div>
                <p className="text-sm text-green-700 font-medium">امسح الرمز بتطبيق واتساب بيزنس</p>
                <p className="text-xs text-green-600 mt-1">افتح واتساب ← الأجهزة المرتبطة ← ربط جهاز</p>
              </div>
              <div className="text-center text-sm text-gray-400">أو</div>
              <div className="bg-gray-50 rounded-xl p-4">
                <p className="text-sm font-medium text-gray-700 mb-2">أدخل رقم واتساب بيزنس يدوياً</p>
                <div className="flex gap-2">
                  <input type="tel" dir="ltr" placeholder="+966 5XX XXX XXXX"
                    className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
                  <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">ربط</button>
                </div>
              </div>
              <div className="text-xs text-gray-400 space-y-1">
                <p>• تحتاج حساب واتساب بيزنس (مو العادي)</p>
                <p>• تقدر تتخطى وتربط لاحقاً من الإعدادات</p>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1 flex items-center gap-2">
              <UsersRound className="w-5 h-5 text-secondary" /> دعوة فريقك
            </h2>
            <p className="text-sm text-gray-500 mb-6">أضف أعضاء فريقك عشان يقدرون يستخدمون النظام معك</p>
            {members.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <UsersRound className="w-10 h-10 mx-auto mb-3 opacity-50" />
                <p className="text-sm mb-4">ما ضفت أحد بعد. تقدر تضيف لاحقاً من الإعدادات.</p>
              </div>
            ) : (
              <div className="space-y-3 mb-4">
                {members.map((m, i) => (
                  <div key={i} className="flex gap-2 items-start">
                    <input type="email" dir="ltr" placeholder="email@company.com" value={m.email}
                      onChange={(e) => updateMember(i, "email", e.target.value)}
                      className="flex-1 px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
                    <select value={m.role} onChange={(e) => updateMember(i, "role", e.target.value)}
                      className="px-3 py-2.5 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-secondary outline-none">
                      <option value="agent">موظف</option>
                      <option value="manager">مدير</option>
                      <option value="admin">مشرف</option>
                    </select>
                    <button onClick={() => removeMember(i)} className="p-2.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
            <button onClick={addMember} className="w-full border-2 border-dashed border-gray-300 hover:border-secondary text-gray-500 hover:text-secondary py-3 rounded-lg text-sm font-medium transition flex items-center justify-center gap-2">
              <Plus className="w-4 h-4" /> إضافة عضو
            </button>
          </div>
        )}

        {step === 4 && (
          <div className="text-center py-6">
            <div className="text-6xl mb-6">🎉</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">حسابك جاهز!</h2>
            <p className="text-gray-500 mb-8">ممتاز! كل شي مجهز. ابدأ باستقبال عملائك الآن.</p>
            <div className="grid sm:grid-cols-3 gap-3">
              <button onClick={() => router.push("/dashboard")} className="bg-secondary hover:bg-secondary-600 text-white py-3 rounded-xl font-medium text-sm transition">لوحة التحكم</button>
              <button onClick={() => router.push("/dashboard/leads")} className="bg-primary hover:bg-primary-700 text-white py-3 rounded-xl font-medium text-sm transition">العملاء المحتملين</button>
              <button onClick={() => router.push("/dashboard/conversations")} className="bg-green-500 hover:bg-green-600 text-white py-3 rounded-xl font-medium text-sm transition">المحادثات</button>
            </div>
          </div>
        )}

        {step < 4 && (
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-100">
            {step > 0 ? (
              <button onClick={() => { setStep(step - 1); setError(""); }}
                className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition">
                <ArrowRight className="w-4 h-4" /> السابق
              </button>
            ) : <div />}
            <button onClick={next} disabled={loading}
              className="bg-secondary hover:bg-secondary-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium transition flex items-center gap-2 disabled:opacity-50">
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {step === 0 ? "ابدأ الآن" : step === 3 ? (members.length > 0 ? "دعوة وإكمال" : "تخطي") : "التالي"}
              {!loading && <ArrowLeft className="w-4 h-4" />}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
