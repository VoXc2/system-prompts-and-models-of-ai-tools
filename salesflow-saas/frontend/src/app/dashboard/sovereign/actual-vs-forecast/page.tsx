"use client";

import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Minus, Loader2, BarChart3 } from "lucide-react";

interface ForecastItem {
  id: string;
  market: string;
  metric: string;
  forecast_value: number;
  actual_value: number;
  variance_pct: number;
  period: string;
  status: string;
}

export default function ActualVsForecastPage() {
  const [items, setItems] = useState<ForecastItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/executive/actual-vs-forecast")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setItems(Array.isArray(d) ? d : d.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const getVarianceColor = (pct: number) => {
    if (pct >= 5) return "text-emerald-500";
    if (pct <= -5) return "text-red-500";
    return "text-amber-500";
  };

  const getVarianceIcon = (pct: number) => {
    if (pct >= 5) return TrendingUp;
    if (pct <= -5) return TrendingDown;
    return Minus;
  };

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">الفعلي مقابل المتوقع</h1>
        <p className="text-sm text-muted-foreground">Actual vs Forecast — مقارنة أداء أسواق التوسع</p>
      </header>

      {items.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <BarChart3 className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد بيانات بعد</p>
          <p className="text-sm text-muted-foreground/70">No forecast data available yet</p>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">السوق</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">المقياس</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">المتوقع</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الفعلي</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الانحراف</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الفترة</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const Icon = getVarianceIcon(item.variance_pct);
                return (
                  <tr key={item.id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                    <td className="px-5 py-4 font-medium">{item.market}</td>
                    <td className="px-5 py-4 text-xs text-muted-foreground">{item.metric}</td>
                    <td className="px-5 py-4 font-mono text-xs">{item.forecast_value.toLocaleString("ar-SA")}</td>
                    <td className="px-5 py-4 font-mono text-xs">{item.actual_value.toLocaleString("ar-SA")}</td>
                    <td className="px-5 py-4">
                      <div className={`flex items-center gap-1 ${getVarianceColor(item.variance_pct)}`}>
                        <Icon className="w-4 h-4" />
                        <span className="text-xs font-bold">{item.variance_pct > 0 ? "+" : ""}{item.variance_pct.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-xs text-muted-foreground">{item.period}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
