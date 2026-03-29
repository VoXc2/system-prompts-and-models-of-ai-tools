"use client";

import { useEffect, useState } from "react";
import { subscription } from "@/lib/api";
import {
  Crown, Zap, Building2, Rocket, Check, X as XIcon,
  Loader2, Calendar, Users, MessageSquare, Brain,
  Headphones, Code2, Shield, ArrowUp, CreditCard,
} from "lucide-react";

interface SubData {
  plan: string;
  status: string;
  price_monthly?: number;
  currency?: string;
  current_period_start?: string;
  current_period_end?: string;
  seats_used?: number;
  seats_limit?: number;
  leads_used?: number;
  leads_limit?: number;
}

const PLANS = [
  {
    id: "trial",
    name: "تجريبي",
    price: 0,
    period: "14 يوم مجاناً",
    icon: Zap,
    color: "text-gray-600",
    bg: "bg-gray-50",
    border: "border-gray-200",
    features: {
      users: "2",
      leads: "100",
      whatsapp: "50 / يوم",
      dashboard: true,
      ai_agents: false,
      automations: false,
      social_listening: false,
      voice_ai: false,
      custom_fields: false,
      api_access: false,
      sla: false,
      dedicated_support: false,
    },
  },
  {
    id: "basic",
    name: "أساسي",
    price: 1500,
    period: "شهرياً",
    icon: Crown,
    color: "text-blue-600",
    bg: "bg-blue-50",
    border: "border-blue-200",
    features: {
      users: "5",
      leads: "1,000",
      whatsapp: "200 / يوم",
      dashboard: true,
      ai_agents: true,
      automations: true,
      social_listening: false,
      voice_ai: false,
      custom_fields: false,
      api_access: false,
      sla: false,
      dedicated_support: false,
    },
  },
  {
    id: "professional",
    name: "احترافي",
    price: 5000,
    period: "شهرياً",
    icon: Building2,
    color: "text-purple-600",
    bg: "bg-purple-50",
    border: "border-purple-200",
    popular: true,
    features: {
      users: "15",
      leads: "غير محدود",
      whatsapp: "500 / يوم",
      dashboard: true,
      ai_agents: true,
      automations: true,
      social_listening: true,
      voice_ai: true,
      custom_fields: true,
      api_access: false,
      sla: false,
      dedicated_support: false,
    },
  },
  {
    id: "enterprise",
    name: "مؤسسي",
    price: 15000,
    period: "شهرياً",
    icon: Rocket,
    color: "text-secondary",
    bg: "bg-secondary-50",
    border: "border-secondary-200",
    features: {
      users: "غير محدود",
      leads: "غير محدود",
      whatsapp: "غير محدود",
      dashboard: true,
      ai_agents: true,
      automations: true,
      social_listening: true,
      voice_ai: true,
      custom_fields: true,
      api_access: true,
      sla: true,
      dedicated_support: true,
    },
  },
];

const FEATURE_LABELS: Record<string, { label: string; icon: any }> = {
  users: { label: "المستخدمين", icon: Users },
  leads: { label: "العملاء المحتملين", icon: Users },
  whatsapp: { label: "رسائل واتساب", icon: MessageSquare },
  dashboard: { label: "لوحة التحكم", icon: Shield },
  ai_agents: { label: "وكلاء AI الأذكياء", icon: Brain },
  automations: { label: "الأتمتة والمتابعة", icon: Zap },
  social_listening: { label: "الاستماع الاجتماعي", icon: MessageSquare },
  voice_ai: { label: "المكالمات الذكية", icon: Headphones },
  custom_fields: { label: "حقول مخصصة", icon: Code2 },
  api_access: { label: "وصول API", icon: Code2 },
  sla: { label: "اتفاقيات SLA", icon: Shield },
  dedicated_support: { label: "دعم مخصص", icon: Headphones },
};

const planOrder = ["trial", "basic", "professional", "enterprise"];

const statusLabels: Record<string, { label: string; color: string }> = {
  active: { label: "فعّال", color: "bg-green-100 text-green-700" },
  trial: { label: "تجريبي", color: "bg-blue-100 text-blue-700" },
  past_due: { label: "متأخر", color: "bg-red-100 text-red-700" },
  cancelled: { label: "ملغي", color: "bg-gray-100 text-gray-600" },
};

export default function BillingPage() {
  const [sub, setSub] = useState<SubData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [upgrading, setUpgrading] = useState("");

  useEffect(() => {
    subscription
      .get()
      .then((data: any) => setSub(data))
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleUpgrade = async (planId: string) => {
    setUpgrading(planId);
    setError("");
    try {
      const data = await subscription.update({ plan: planId });
      setSub(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUpgrading("");
    }
  };

  const currentPlanIndex = sub ? planOrder.indexOf(sub.plan) : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">{error}</div>
      )}

      {/* Current Plan */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <CreditCard className="w-6 h-6 text-secondary" /> الاشتراك الحالي
        </h2>
        {sub ? (
          <div className="grid sm:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-500 mb-1">الخطة</p>
              <p className="text-lg font-bold text-gray-900">
                {PLANS.find((p) => p.id === sub.plan)?.name || sub.plan}
              </p>
              {sub.status && (
                <span className={`inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${statusLabels[sub.status]?.color || "bg-gray-100 text-gray-600"}`}>
                  {statusLabels[sub.status]?.label || sub.status}
                </span>
              )}
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">السعر الشهري</p>
              <p className="text-lg font-bold text-gray-900">
                {sub.price_monthly?.toLocaleString("ar-SA") || "0"} ر.س
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">فترة الاشتراك</p>
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Calendar className="w-4 h-4 text-gray-400" />
                {sub.current_period_start
                  ? `${new Date(sub.current_period_start).toLocaleDateString("ar-SA")} — ${new Date(sub.current_period_end || "").toLocaleDateString("ar-SA")}`
                  : "غير محدد"}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-500">لا يوجد اشتراك حالي</p>
        )}

        {/* Usage bars */}
        {sub && (
          <div className="mt-6 grid sm:grid-cols-2 gap-4">
            {sub.seats_limit && (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">المستخدمين</span>
                  <span className="font-medium">{sub.seats_used || 0} / {sub.seats_limit}</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-secondary rounded-full transition-all" style={{ width: `${Math.min(100, ((sub.seats_used || 0) / sub.seats_limit) * 100)}%` }} />
                </div>
              </div>
            )}
            {sub.leads_limit && (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">العملاء المحتملين</span>
                  <span className="font-medium">{sub.leads_used || 0} / {sub.leads_limit}</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${Math.min(100, ((sub.leads_used || 0) / sub.leads_limit) * 100)}%` }} />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Plans Grid */}
      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-4">اختر خطتك</h3>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {PLANS.map((plan, idx) => {
            const isCurrent = sub?.plan === plan.id;
            const isHigher = idx > currentPlanIndex;
            return (
              <div
                key={plan.id}
                className={`relative bg-white rounded-xl border-2 p-5 transition ${
                  isCurrent
                    ? "border-secondary shadow-lg shadow-secondary/10"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                {(plan as any).popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-secondary text-white text-xs font-bold px-3 py-0.5 rounded-full">
                    الأكثر طلباً
                  </div>
                )}
                {isCurrent && (
                  <div className="absolute -top-3 right-4 bg-primary-900 text-white text-xs font-bold px-3 py-0.5 rounded-full">
                    خطتك الحالية
                  </div>
                )}
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-3 ${plan.bg}`}>
                  <plan.icon className={`w-6 h-6 ${plan.color}`} />
                </div>
                <h4 className="text-lg font-bold text-gray-900">{plan.name}</h4>
                <div className="mt-2 mb-4">
                  <span className="text-3xl font-bold text-gray-900">
                    {plan.price === 0 ? "مجاناً" : plan.price.toLocaleString("ar-SA")}
                  </span>
                  {plan.price > 0 && (
                    <span className="text-sm text-gray-500 mr-1">ر.س / {plan.period}</span>
                  )}
                  {plan.price === 0 && (
                    <p className="text-xs text-gray-500 mt-0.5">{plan.period}</p>
                  )}
                </div>
                <ul className="space-y-2 text-sm mb-5">
                  <li className="flex items-center gap-2 text-gray-700">
                    <Users className="w-4 h-4 text-gray-400 shrink-0" />
                    {plan.features.users} مستخدم
                  </li>
                  <li className="flex items-center gap-2 text-gray-700">
                    <Users className="w-4 h-4 text-gray-400 shrink-0" />
                    {plan.features.leads} عميل
                  </li>
                  <li className="flex items-center gap-2 text-gray-700">
                    <MessageSquare className="w-4 h-4 text-gray-400 shrink-0" />
                    {plan.features.whatsapp} رسالة
                  </li>
                </ul>
                {isHigher && !isCurrent ? (
                  <button
                    onClick={() => handleUpgrade(plan.id)}
                    disabled={!!upgrading}
                    className="w-full bg-secondary hover:bg-secondary-600 text-white py-2.5 rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {upgrading === plan.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <ArrowUp className="w-4 h-4" />
                    )}
                    ترقية
                  </button>
                ) : isCurrent ? (
                  <div className="w-full bg-gray-100 text-gray-500 py-2.5 rounded-lg text-sm font-medium text-center">
                    خطتك الحالية
                  </div>
                ) : (
                  <div className="w-full py-2.5" />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Feature Comparison */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-900">مقارنة المميزات</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-right px-6 py-3 font-semibold text-gray-600">الميزة</th>
                {PLANS.map((p) => (
                  <th key={p.id} className={`text-center px-4 py-3 font-semibold ${sub?.plan === p.id ? "text-secondary" : "text-gray-600"}`}>
                    {p.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(FEATURE_LABELS).map(([key, { label, icon: Icon }]) => (
                <tr key={key} className="border-t border-gray-100">
                  <td className="px-6 py-3 text-gray-700 flex items-center gap-2">
                    <Icon className="w-4 h-4 text-gray-400 shrink-0" /> {label}
                  </td>
                  {PLANS.map((p) => {
                    const val = (p.features as any)[key];
                    return (
                      <td key={p.id} className={`text-center px-4 py-3 ${sub?.plan === p.id ? "bg-secondary/5" : ""}`}>
                        {typeof val === "boolean" ? (
                          val ? (
                            <Check className="w-5 h-5 text-green-500 mx-auto" />
                          ) : (
                            <XIcon className="w-5 h-5 text-gray-300 mx-auto" />
                          )
                        ) : (
                          <span className="font-medium text-gray-900">{val}</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Billing History */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-secondary" /> سجل الفواتير
        </h3>
        <div className="text-center py-10 text-gray-400">
          <CreditCard className="w-10 h-10 mx-auto mb-3 opacity-50" />
          <p className="text-sm font-medium">قريباً</p>
          <p className="text-xs mt-1">سيتم عرض سجل الفواتير والمدفوعات هنا</p>
        </div>
      </div>
    </div>
  );
}
