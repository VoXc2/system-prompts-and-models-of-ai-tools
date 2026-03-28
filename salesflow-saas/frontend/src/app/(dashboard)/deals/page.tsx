"use client";

import { useEffect, useState } from "react";
import { deals } from "@/lib/api";
import { Handshake, Loader2, Search } from "lucide-react";

interface Deal {
  id: string;
  title: string;
  contact_name?: string;
  value: number;
  stage: string;
  status: string;
  created_at: string;
}

const stageMap: Record<string, { label: string; color: string }> = {
  discovery: { label: "اكتشاف", color: "bg-blue-100 text-blue-700" },
  proposal: { label: "عرض سعر", color: "bg-purple-100 text-purple-700" },
  negotiation: { label: "تفاوض", color: "bg-yellow-100 text-yellow-700" },
  won: { label: "مكتسب", color: "bg-green-100 text-green-700" },
  lost: { label: "مفقود", color: "bg-red-100 text-red-700" },
};

export default function DealsPage() {
  const [data, setData] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    deals
      .list()
      .then((res: any) => setData(res.items || res.deals || res || []))
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = data.filter(
    (d) =>
      d.title?.includes(search) ||
      d.contact_name?.includes(search)
  );

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
      <div className="mb-4">
        <div className="relative max-w-sm">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في الصفقات..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pr-9 pl-4 py-2.5 bg-white border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
          />
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-right px-4 py-3 font-semibold text-gray-600">العنوان</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">العميل</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">القيمة</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">المرحلة</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">التاريخ</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-10 text-gray-400">
                    <Handshake className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    لا توجد صفقات
                  </td>
                </tr>
              ) : (
                filtered.map((deal) => {
                  const stage = stageMap[deal.stage] || stageMap[deal.status] || {
                    label: deal.stage || deal.status,
                    color: "bg-gray-100 text-gray-600",
                  };
                  return (
                    <tr key={deal.id} className="border-b border-gray-100 hover:bg-gray-50 transition">
                      <td className="px-4 py-3 font-medium text-gray-900">{deal.title}</td>
                      <td className="px-4 py-3 text-gray-600">{deal.contact_name || "-"}</td>
                      <td className="px-4 py-3 text-gray-900 font-medium">
                        {deal.value?.toLocaleString("ar-SA")} ر.س
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium ${stage.color}`}>
                          {stage.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs">
                        {new Date(deal.created_at).toLocaleDateString("ar-SA")}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
