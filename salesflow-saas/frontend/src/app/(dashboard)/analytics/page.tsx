"use client";

import { useEffect, useState } from "react";
import { analytics, velocity, sla } from "@/lib/api";
import {
  BarChart3,
  TrendingUp,
  Users,
  Handshake,
  DollarSign,
  Loader2,
  Target,
  Gauge,
  Clock,
  AlertTriangle,
  Calendar,
} from "lucide-react";

interface OverviewStats {
  total_leads: number;
  total_deals: number;
  total_revenue: number;
  conversion_rate: number;
  avg_deal_value: number;
  deals_won: number;
}

interface PipelineStage {
  name: string;
  count: number;
  value: number;
}

interface VelocityData {
  pipeline_velocity: number;
  avg_sales_cycle_days: number;
  avg_deal_size: number;
  win_rate: number;
  open_pipeline_value: number;
  weighted_pipeline: number;
  forecast_30_days: number;
  forecast_60_days: number;
  forecast_90_days: number;
  funnel: { total: number; won: number; lost: number; open: number };
}

interface SLAStats {
  total_policies: number;
  active_breaches: number;
  resolved_today: number;
  avg_breach_minutes: number | null;
  breach_by_type: Record<string, number>;
}

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [pipeline, setPipeline] = useState<PipelineStage[]>([]);
  const [velocityData, setVelocityData] = useState<VelocityData | null>(null);
  const [slaStats, setSlaStats] = useState<SLAStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      analytics.overview().catch(() => null),
      analytics.pipeline().catch(() => []),
      velocity.get().catch(() => null),
      sla.stats().catch(() => null),
    ])
      .then(([overviewRes, pipelineRes, velocityRes, slaRes]: any[]) => {
        setOverview(overviewRes);
        setPipeline(
          pipelineRes.stages || pipelineRes.pipeline || pipelineRes || []
        );
        setVelocityData(velocityRes);
        setSlaStats(slaRes);
      })
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
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
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
        {error}
      </div>
    );
  }

  const overviewCards = [
    {
      label: "إجمالي العملاء",
      value: overview?.total_leads?.toLocaleString("ar-SA") ?? "0",
      icon: Users,
      color: "bg-blue-100 text-blue-600",
    },
    {
      label: "إجمالي الصفقات",
      value: overview?.total_deals?.toLocaleString("ar-SA") ?? "0",
      icon: Handshake,
      color: "bg-purple-100 text-purple-600",
    },
    {
      label: "إجمالي الإيرادات",
      value: (overview?.total_revenue?.toLocaleString("ar-SA") ?? "0") + " ر.س",
      icon: DollarSign,
      color: "bg-green-100 text-green-600",
    },
    {
      label: "معدل التحويل",
      value: (overview?.conversion_rate?.toFixed(1) ?? "0") + "%",
      icon: Target,
      color: "bg-orange-100 text-orange-600",
    },
    {
      label: "متوسط قيمة الصفقة",
      value:
        (overview?.avg_deal_value?.toLocaleString("ar-SA") ?? "0") + " ر.س",
      icon: TrendingUp,
      color: "bg-teal-100 text-teal-600",
    },
    {
      label: "صفقات مكتسبة",
      value: overview?.deals_won?.toLocaleString("ar-SA") ?? "0",
      icon: BarChart3,
      color: "bg-yellow-100 text-yellow-700",
    },
  ];

  // Find max pipeline value for bar scaling
  const maxPipelineCount = Math.max(...pipeline.map((s) => s.count), 1);

  return (
    <div>
      {/* Overview stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {overviewCards.map((card) => (
          <div
            key={card.label}
            className="bg-white rounded-xl border border-gray-200 p-5"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">{card.label}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              </div>
              <div
                className={`w-10 h-10 rounded-lg flex items-center justify-center ${card.color}`}
              >
                <card.icon className="w-5 h-5" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pipeline chart (CSS-only bar chart) */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <h3 className="font-bold text-gray-900 mb-6 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-secondary" />
          مسار الصفقات
        </h3>

        {pipeline.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">
            لا توجد بيانات
          </div>
        ) : (
          <div className="space-y-4">
            {pipeline.map((stage, i) => {
              const pct = (stage.count / maxPipelineCount) * 100;
              const colors = [
                "bg-blue-500",
                "bg-cyan-500",
                "bg-teal-500",
                "bg-green-500",
                "bg-yellow-500",
                "bg-orange-500",
                "bg-red-500",
              ];
              const color = colors[i % colors.length];

              return (
                <div key={stage.name}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-sm font-medium text-gray-700">
                      {stage.name}
                    </span>
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                      <span>{stage.count} صفقة</span>
                      <span>{stage.value?.toLocaleString("ar-SA")} ر.س</span>
                    </div>
                  </div>
                  <div className="w-full h-6 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${color} rounded-full transition-all duration-500`}
                      style={{ width: `${Math.max(pct, 2)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Pipeline Velocity Section */}
      {velocityData && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
          <h3 className="font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Gauge className="w-5 h-5 text-secondary" />
            سرعة المسار (Pipeline Velocity)
          </h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-xs text-blue-600 mb-1">السرعة (ر.س/يوم)</p>
              <p className="text-xl font-bold text-blue-900">
                {velocityData.pipeline_velocity?.toLocaleString("ar-SA", { maximumFractionDigits: 0 })}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-xs text-purple-600 mb-1">متوسط دورة البيع</p>
              <p className="text-xl font-bold text-purple-900">
                {velocityData.avg_sales_cycle_days?.toFixed(0)} يوم
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-xs text-green-600 mb-1">نسبة الفوز</p>
              <p className="text-xl font-bold text-green-900">
                {velocityData.win_rate?.toFixed(1)}%
              </p>
            </div>
            <div className="bg-teal-50 rounded-lg p-4">
              <p className="text-xs text-teal-600 mb-1">المسار المرجح</p>
              <p className="text-xl font-bold text-teal-900">
                {velocityData.weighted_pipeline?.toLocaleString("ar-SA", { maximumFractionDigits: 0 })} ر.س
              </p>
            </div>
          </div>

          {/* Revenue Forecast */}
          <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            توقعات الإيرادات
          </h4>
          <div className="grid grid-cols-3 gap-4">
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-xs text-gray-500 mb-1">30 يوم</p>
              <p className="text-lg font-bold text-gray-900">
                {velocityData.forecast_30_days?.toLocaleString("ar-SA", { maximumFractionDigits: 0 })} ر.س
              </p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-xs text-gray-500 mb-1">60 يوم</p>
              <p className="text-lg font-bold text-gray-900">
                {velocityData.forecast_60_days?.toLocaleString("ar-SA", { maximumFractionDigits: 0 })} ر.س
              </p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-xs text-gray-500 mb-1">90 يوم</p>
              <p className="text-lg font-bold text-gray-900">
                {velocityData.forecast_90_days?.toLocaleString("ar-SA", { maximumFractionDigits: 0 })} ر.س
              </p>
            </div>
          </div>

          {/* Conversion Funnel */}
          {velocityData.funnel && (
            <div className="mt-6">
              <h4 className="font-semibold text-gray-800 mb-3">قمع التحويل</h4>
              <div className="flex items-center gap-2">
                {[
                  { label: "إجمالي", value: velocityData.funnel.total, color: "bg-blue-500" },
                  { label: "مفتوح", value: velocityData.funnel.open, color: "bg-yellow-500" },
                  { label: "فاز", value: velocityData.funnel.won, color: "bg-green-500" },
                  { label: "خسر", value: velocityData.funnel.lost, color: "bg-red-500" },
                ].map((item) => (
                  <div key={item.label} className="flex-1 text-center">
                    <div className={`${item.color} text-white rounded-lg py-3 mb-1`}>
                      <p className="text-lg font-bold">{item.value}</p>
                    </div>
                    <p className="text-xs text-gray-500">{item.label}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* SLA Tracking Section */}
      {slaStats && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
          <h3 className="font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Clock className="w-5 h-5 text-secondary" />
            تتبع SLA
          </h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-xs text-blue-600 mb-1">سياسات نشطة</p>
              <p className="text-xl font-bold text-blue-900">{slaStats.total_policies}</p>
            </div>
            <div className={`rounded-lg p-4 ${slaStats.active_breaches > 0 ? "bg-red-50" : "bg-green-50"}`}>
              <p className={`text-xs mb-1 ${slaStats.active_breaches > 0 ? "text-red-600" : "text-green-600"}`}>
                انتهاكات نشطة
              </p>
              <p className={`text-xl font-bold ${slaStats.active_breaches > 0 ? "text-red-900" : "text-green-900"}`}>
                {slaStats.active_breaches}
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-xs text-green-600 mb-1">تم حلها اليوم</p>
              <p className="text-xl font-bold text-green-900">{slaStats.resolved_today}</p>
            </div>
            <div className="bg-orange-50 rounded-lg p-4">
              <p className="text-xs text-orange-600 mb-1">متوسط التجاوز</p>
              <p className="text-xl font-bold text-orange-900">
                {slaStats.avg_breach_minutes ? `${Math.round(slaStats.avg_breach_minutes)} د` : "—"}
              </p>
            </div>
          </div>
          {slaStats.active_breaches > 0 && Object.keys(slaStats.breach_by_type).length > 0 && (
            <div className="mt-4 p-3 bg-red-50 rounded-lg border border-red-100">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                <span className="text-sm font-medium text-red-700">انتهاكات حسب النوع</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(slaStats.breach_by_type).map(([type, count]) => (
                  <span key={type} className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-full">
                    {type}: {count}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Revenue trend chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-gray-900 mb-6 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-secondary" />
          اتجاه الإيرادات
        </h3>
        <div className="h-48 flex items-end justify-around gap-2 px-4">
          {["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"].map(
            (month, i) => {
              const heights = [40, 55, 45, 70, 65, 80];
              return (
                <div key={month} className="flex-1 flex flex-col items-center gap-2">
                  <div
                    className="w-full bg-gradient-to-t from-secondary to-secondary-300 rounded-t-lg transition-all duration-500"
                    style={{ height: `${heights[i]}%` }}
                  />
                  <span className="text-xs text-gray-500">{month}</span>
                </div>
              );
            }
          )}
        </div>
      </div>
    </div>
  );
}
