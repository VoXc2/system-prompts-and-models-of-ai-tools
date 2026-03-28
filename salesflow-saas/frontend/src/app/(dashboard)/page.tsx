"use client";

import { useEffect, useState } from "react";
import { dashboard } from "@/lib/api";
import {
  Users,
  UserPlus,
  Handshake,
  TrendingUp,
  Trophy,
  Target,
  Loader2,
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
  {
    key: "total_leads" as const,
    label: "إجمالي العملاء المحتملين",
    icon: Users,
    color: "bg-blue-50 text-blue-600",
    iconBg: "bg-blue-100",
  },
  {
    key: "new_leads_today" as const,
    label: "عملاء جدد اليوم",
    icon: UserPlus,
    color: "bg-green-50 text-green-600",
    iconBg: "bg-green-100",
  },
  {
    key: "total_deals" as const,
    label: "إجمالي الصفقات",
    icon: Handshake,
    color: "bg-purple-50 text-purple-600",
    iconBg: "bg-purple-100",
  },
  {
    key: "open_deals_value" as const,
    label: "قيمة الصفقات المفتوحة",
    icon: TrendingUp,
    color: "bg-orange-50 text-orange-600",
    iconBg: "bg-orange-100",
    isCurrency: true,
  },
  {
    key: "won_deals_value" as const,
    label: "قيمة الصفقات المكتسبة",
    icon: Trophy,
    color: "bg-yellow-50 text-yellow-700",
    iconBg: "bg-yellow-100",
    isCurrency: true,
  },
  {
    key: "conversion_rate" as const,
    label: "معدل التحويل",
    icon: Target,
    color: "bg-teal-50 text-teal-600",
    iconBg: "bg-teal-100",
    isPercent: true,
  },
];

function formatValue(
  value: number,
  isCurrency?: boolean,
  isPercent?: boolean
): string {
  if (isCurrency) {
    return value.toLocaleString("ar-SA") + " ر.س";
  }
  if (isPercent) {
    return value.toFixed(1) + "%";
  }
  return value.toLocaleString("ar-SA");
}

export default function DashboardPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    dashboard
      .overview()
      .then((res: any) => setData(res))
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

  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {kpiConfig.map((kpi) => {
          const value = data?.[kpi.key] ?? 0;
          return (
            <div
              key={kpi.key}
              className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">{kpi.label}</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatValue(
                      value,
                      (kpi as any).isCurrency,
                      (kpi as any).isPercent
                    )}
                  </p>
                </div>
                <div
                  className={`w-10 h-10 rounded-lg flex items-center justify-center ${kpi.iconBg}`}
                >
                  <kpi.icon className={`w-5 h-5 ${kpi.color.split(" ")[1]}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
