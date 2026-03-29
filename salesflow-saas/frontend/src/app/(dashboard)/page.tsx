"use client";

import { useEffect, useState } from "react";
import { dashboard, deals, appointments, leads, notifications as notificationsApi } from "@/lib/api";
import Link from "next/link";
import {
  Users, UserPlus, Handshake, TrendingUp, Trophy, Target,
  Loader2, Calendar, MessageSquare, Zap, ArrowLeft,
  Clock, CheckCircle2, AlertCircle, BarChart3,
} from "lucide-react";

interface OverviewData {
  total_leads: number;
  new_leads_today: number;
  total_deals: number;
  open_deals_value: number;
  won_deals_value: number;
  conversion_rate: number;
}

const kpiConfig = [
  { key: "total_leads" as const, label: "إجمالي العملاء المحتملين", icon: Users, color: "text-blue-600", iconBg: "bg-blue-100" },
  { key: "new_leads_today" as const, label: "عملاء جدد اليوم", icon: UserPlus, color: "text-green-600", iconBg: "bg-green-100" },
  { key: "total_deals" as const, label: "إجمالي الصفقات", icon: Handshake, color: "text-purple-600", iconBg: "bg-purple-100" },
  { key: "open_deals_value" as const, label: "قيمة الصفقات المفتوحة", icon: TrendingUp, color: "text-orange-600", iconBg: "bg-orange-100", isCurrency: true },
  { key: "won_deals_value" as const, label: "قيمة الصفقات المكتسبة", icon: Trophy, color: "text-yellow-700", iconBg: "bg-yellow-100", isCurrency: true },
  { key: "conversion_rate" as const, label: "معدل التحويل", icon: Target, color: "text-teal-600", iconBg: "bg-teal-100", isPercent: true },
];

function formatValue(value: number, isCurrency?: boolean, isPercent?: boolean): string {
  if (isCurrency) return value.toLocaleString("ar-SA") + " ر.س";
  if (isPercent) return value.toFixed(1) + "%";
  return value.toLocaleString("ar-SA");
}

function timeAgo(dateStr: string): string {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (diff < 60) return "الآن";
  if (diff < 3600) return `منذ ${Math.floor(diff / 60)} دقيقة`;
  if (diff < 86400) return `منذ ${Math.floor(diff / 3600)} ساعة`;
  return `منذ ${Math.floor(diff / 86400)} يوم`;
}

const stageLabels: Record<string, string> = {
  new: "اكتشاف", proposal: "عرض سعر", negotiation: "تفاوض",
  closed_won: "مكتسب", closed_lost: "مفقود",
};

const stageColors: Record<string, string> = {
  new: "bg-blue-500", proposal: "bg-purple-500", negotiation: "bg-yellow-500",
  closed_won: "bg-green-500", closed_lost: "bg-red-500",
};

export default function DashboardPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [recentDeals, setRecentDeals] = useState<any[]>([]);
  const [todayAppts, setTodayAppts] = useState<any[]>([]);
  const [recentLeads, setRecentLeads] = useState<any[]>([]);
  const [notifs, setNotifs] = useState<any[]>([]);

  useEffect(() => {
    dashboard
      .overview()
      .then((res: any) => setData(res))
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));

    deals.list().then((res: any) => {
      const items = res.items || res.deals || res || [];
      setRecentDeals(items.slice(0, 5));
    }).catch(() => {});

    appointments.today().then((res: any) => {
      const items = Array.isArray(res) ? res : res.items || res.data || [];
      setTodayAppts(items.slice(0, 5));
    }).catch(() => {});

    leads.list().then((res: any) => {
      const items = res.items || res.leads || res || [];
      setRecentLeads(items.slice(0, 5));
    }).catch(() => {});

    notificationsApi.list().then((res: any) => {
      const items = Array.isArray(res) ? res : res.items || res.data || [];
      setNotifs(items.filter((n: any) => !n.read_at).slice(0, 5));
    }).catch(() => {});
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">{error}</div>
    );
  }

  // Pipeline data for mini chart
  const pipelineStages = ["new", "proposal", "negotiation", "closed_won", "closed_lost"];
  const stageCounts: Record<string, number> = {};
  recentDeals.forEach((d) => {
    const s = d.stage || d.status || "new";
    stageCounts[s] = (stageCounts[s] || 0) + 1;
  });
  const maxCount = Math.max(1, ...Object.values(stageCounts));

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {kpiConfig.map((kpi) => {
          const value = data?.[kpi.key] ?? 0;
          return (
            <div key={kpi.key} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">{kpi.label}</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatValue(value, (kpi as any).isCurrency, (kpi as any).isPercent)}
                  </p>
                </div>
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${kpi.iconBg}`}>
                  <kpi.icon className={`w-5 h-5 ${kpi.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Pipeline Mini Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-secondary" /> خط الأنابيب
            </h3>
            <Link href="/dashboard/deals" className="text-xs text-secondary hover:text-secondary-600 flex items-center gap-1">
              عرض الكل <ArrowLeft className="w-3 h-3" />
            </Link>
          </div>
          <div className="flex items-end gap-4 h-32">
            {pipelineStages.map((stage) => {
              const count = stageCounts[stage] || 0;
              const height = count > 0 ? Math.max(20, (count / maxCount) * 100) : 8;
              return (
                <div key={stage} className="flex-1 flex flex-col items-center gap-2">
                  <span className="text-xs font-bold text-gray-700">{count}</span>
                  <div
                    className={`w-full rounded-t-lg transition-all ${stageColors[stage] || "bg-gray-300"}`}
                    style={{ height: `${height}%` }}
                  />
                  <span className="text-[10px] text-gray-500 text-center">{stageLabels[stage]}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Today's Appointments */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-secondary" /> مواعيد اليوم
            </h3>
            <Link href="/dashboard/appointments" className="text-xs text-secondary hover:text-secondary-600 flex items-center gap-1">
              عرض الكل <ArrowLeft className="w-3 h-3" />
            </Link>
          </div>
          {todayAppts.length === 0 ? (
            <div className="text-center py-6 text-gray-400">
              <Calendar className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-xs">لا توجد مواعيد اليوم</p>
            </div>
          ) : (
            <div className="space-y-3">
              {todayAppts.map((appt) => (
                <div key={appt.id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    appt.status === "confirmed" ? "bg-green-100 text-green-600" :
                    appt.status === "completed" ? "bg-blue-100 text-blue-600" :
                    "bg-yellow-100 text-yellow-600"
                  }`}>
                    {appt.status === "completed" ? <CheckCircle2 className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{appt.title || appt.contact_name || "موعد"}</p>
                    <p className="text-xs text-gray-500">
                      {appt.start_time ? new Date(appt.start_time).toLocaleTimeString("ar-SA", { hour: "2-digit", minute: "2-digit" }) : ""}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent Leads */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900 flex items-center gap-2">
              <Users className="w-5 h-5 text-secondary" /> آخر العملاء المحتملين
            </h3>
            <Link href="/dashboard/leads" className="text-xs text-secondary hover:text-secondary-600 flex items-center gap-1">
              عرض الكل <ArrowLeft className="w-3 h-3" />
            </Link>
          </div>
          {recentLeads.length === 0 ? (
            <div className="text-center py-6 text-gray-400">
              <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-xs">لا يوجد عملاء محتملين</p>
            </div>
          ) : (
            <div className="space-y-2">
              {recentLeads.map((lead) => (
                <div key={lead.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 transition">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-xs font-bold">
                      {(lead.name || lead.full_name || "?").charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{lead.name || lead.full_name}</p>
                      <p className="text-xs text-gray-500">{lead.source || lead.phone || ""}</p>
                    </div>
                  </div>
                  <span className="text-xs text-gray-400">{lead.created_at ? timeAgo(lead.created_at) : ""}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Activity Feed / Notifications */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900 flex items-center gap-2">
              <Zap className="w-5 h-5 text-secondary" /> آخر الأنشطة
            </h3>
          </div>
          {notifs.length === 0 && recentDeals.length === 0 ? (
            <div className="text-center py-6 text-gray-400">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-xs">لا توجد أنشطة حديثة</p>
            </div>
          ) : (
            <div className="space-y-3">
              {notifs.map((n) => (
                <div key={n.id} className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 transition">
                  <div className="w-2 h-2 bg-secondary rounded-full mt-2 shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-gray-700">{n.body || n.message || n.title}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{n.created_at ? timeAgo(n.created_at) : ""}</p>
                  </div>
                </div>
              ))}
              {notifs.length === 0 && recentDeals.map((d) => (
                <div key={d.id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    d.stage === "closed_won" ? "bg-green-100 text-green-600" : "bg-blue-100 text-blue-600"
                  }`}>
                    <Handshake className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{d.title}</p>
                    <p className="text-xs text-gray-500">{d.value?.toLocaleString("ar-SA")} ر.س — {stageLabels[d.stage] || d.stage}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid sm:grid-cols-4 gap-3">
        {[
          { href: "/dashboard/leads", label: "إضافة عميل", icon: UserPlus, color: "bg-blue-50 text-blue-700 hover:bg-blue-100" },
          { href: "/dashboard/deals", label: "إضافة صفقة", icon: Handshake, color: "bg-purple-50 text-purple-700 hover:bg-purple-100" },
          { href: "/dashboard/appointments", label: "حجز موعد", icon: Calendar, color: "bg-green-50 text-green-700 hover:bg-green-100" },
          { href: "/dashboard/automations", label: "إنشاء أتمتة", icon: Zap, color: "bg-orange-50 text-orange-700 hover:bg-orange-100" },
        ].map((action) => (
          <Link
            key={action.href}
            href={action.href}
            className={`flex items-center gap-3 p-4 rounded-xl border border-gray-200 transition ${action.color}`}
          >
            <action.icon className="w-5 h-5 shrink-0" />
            <span className="text-sm font-medium">{action.label}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
