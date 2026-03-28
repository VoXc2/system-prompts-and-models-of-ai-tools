"use client";

import { useEffect, useState } from "react";
import { leads } from "@/lib/api";
import { Users, Loader2, Search } from "lucide-react";

interface Lead {
  id: string;
  full_name: string;
  company?: string;
  phone?: string;
  status: string;
  score?: number;
  source?: string;
  created_at: string;
}

const statusMap: Record<string, { label: string; color: string }> = {
  new: { label: "جديد", color: "bg-blue-100 text-blue-700" },
  contacted: { label: "تم التواصل", color: "bg-yellow-100 text-yellow-700" },
  qualified: { label: "مؤهل", color: "bg-green-100 text-green-700" },
  proposal: { label: "عرض سعر", color: "bg-purple-100 text-purple-700" },
  negotiation: { label: "تفاوض", color: "bg-orange-100 text-orange-700" },
  won: { label: "مكتسب", color: "bg-emerald-100 text-emerald-700" },
  lost: { label: "مفقود", color: "bg-red-100 text-red-700" },
};

export default function LeadsPage() {
  const [data, setData] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    leads
      .list()
      .then((res: any) => setData(res.items || res.leads || res || []))
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = data.filter(
    (l) =>
      l.full_name?.includes(search) ||
      l.company?.includes(search) ||
      l.phone?.includes(search)
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
      {/* Search bar */}
      <div className="mb-4">
        <div className="relative max-w-sm">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في العملاء..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pr-9 pl-4 py-2.5 bg-white border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
          />
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-right px-4 py-3 font-semibold text-gray-600">
                  الاسم
                </th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">
                  الشركة
                </th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">
                  الهاتف
                </th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">
                  الحالة
                </th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">
                  التقييم
                </th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">
                  المصدر
                </th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">
                  التاريخ
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td
                    colSpan={7}
                    className="text-center py-10 text-gray-400"
                  >
                    <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    لا توجد بيانات
                  </td>
                </tr>
              ) : (
                filtered.map((lead) => {
                  const status = statusMap[lead.status] || {
                    label: lead.status,
                    color: "bg-gray-100 text-gray-600",
                  };
                  return (
                    <tr
                      key={lead.id}
                      className="border-b border-gray-100 hover:bg-gray-50 transition"
                    >
                      <td className="px-4 py-3 font-medium text-gray-900">
                        {lead.full_name}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {lead.company || "-"}
                      </td>
                      <td className="px-4 py-3 text-gray-600" dir="ltr">
                        {lead.phone || "-"}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium ${status.color}`}
                        >
                          {status.label}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {lead.score != null ? (
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-secondary rounded-full"
                                style={{
                                  width: `${Math.min(lead.score, 100)}%`,
                                }}
                              />
                            </div>
                            <span className="text-xs text-gray-500">
                              {lead.score}
                            </span>
                          </div>
                        ) : (
                          "-"
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {lead.source || "-"}
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs">
                        {new Date(lead.created_at).toLocaleDateString("ar-SA")}
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
