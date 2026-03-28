"use client";

import { useEffect, useState } from "react";
import { analytics } from "@/lib/api";
import {
  BarChart3,
  TrendingUp,
  Users,
  Handshake,
  DollarSign,
  Loader2,
  Target,
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

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [pipeline, setPipeline] = useState<PipelineStage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      analytics.overview().catch(() => null),
      analytics.pipeline().catch(() => []),
    ])
      .then(([overviewRes, pipelineRes]: any[]) => {
        setOverview(overviewRes);
        setPipeline(
          pipelineRes.stages || pipelineRes.pipeline || pipelineRes || []
        );
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

      {/* Simple line chart placeholder */}
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
