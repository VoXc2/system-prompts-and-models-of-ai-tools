"use client";

import { useEffect, useState } from "react";
import { aiTraces } from "@/lib/api";
import { Brain, Loader2, AlertTriangle, DollarSign, Clock, Zap } from "lucide-react";

export default function AITracesPage() {
  const [traces, setTraces] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ provider: "", status: "" });

  useEffect(() => {
    setLoading(true);
    Promise.all([
      aiTraces.list(filter).catch(() => ({ items: [] })),
      aiTraces.stats().catch(() => ({})),
    ])
      .then(([t, s]) => {
        setTraces(t.items || []);
        setStats(s);
      })
      .finally(() => setLoading(false));
  }, [filter.provider, filter.status]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        {[
          { label: "إجمالي الاستدعاءات", value: stats?.total_calls || 0, icon: Zap },
          { label: "التكلفة ($)", value: `$${(stats?.total_cost_usd || 0).toFixed(4)}`, icon: DollarSign },
          { label: "إجمالي التوكنات", value: (stats?.total_tokens || 0).toLocaleString(), icon: Brain },
          { label: "متوسط التأخير (ms)", value: Math.round(stats?.avg_latency_ms || 0), icon: Clock },
          { label: "نسبة الأخطاء", value: `${stats?.error_rate || 0}%`, icon: AlertTriangle },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <s.icon className="w-4 h-4" />
              {s.label}
            </div>
            <p className="text-xl font-bold text-gray-900">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <select
          value={filter.provider}
          onChange={(e) => setFilter((f) => ({ ...f, provider: e.target.value }))}
          className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
        >
          <option value="">كل المزودين</option>
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
          <option value="gemini">Gemini</option>
        </select>
        <select
          value={filter.status}
          onChange={(e) => setFilter((f) => ({ ...f, status: e.target.value }))}
          className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
        >
          <option value="">كل الحالات</option>
          <option value="success">ناجح</option>
          <option value="error">خطأ</option>
        </select>
      </div>

      {/* Traces table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-right px-4 py-3 font-semibold text-gray-600">التاريخ</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">المزود</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">النموذج</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">التوكنات</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">التكلفة</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">التأخير</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">الحالة</th>
              </tr>
            </thead>
            <tbody>
              {traces.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-gray-400">
                    <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    لا توجد استدعاءات AI
                  </td>
                </tr>
              ) : (
                traces.map((t: any) => (
                  <tr key={t.id} className="border-b border-gray-100 hover:bg-gray-50 transition">
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      {t.created_at ? new Date(t.created_at).toLocaleString("ar-SA") : "-"}
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">{t.provider}</td>
                    <td className="px-4 py-3 text-gray-600 text-xs" dir="ltr">{t.model}</td>
                    <td className="px-4 py-3 text-gray-600">{t.total_tokens?.toLocaleString()}</td>
                    <td className="px-4 py-3 text-gray-600" dir="ltr">${(t.cost_usd || 0).toFixed(5)}</td>
                    <td className="px-4 py-3 text-gray-600">{t.latency_ms}ms</td>
                    <td className="px-4 py-3">
                      <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                        t.status === "success" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                      }`}>
                        {t.status === "success" ? "ناجح" : "خطأ"}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
