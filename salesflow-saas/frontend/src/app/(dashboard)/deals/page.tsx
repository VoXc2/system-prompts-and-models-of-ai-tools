"use client";

import { useEffect, useState } from "react";
import { deals } from "@/lib/api";
import Modal from "@/components/ui/Modal";
import { Handshake, Loader2, Search, Plus, Pencil } from "lucide-react";

interface Deal {
  id: string;
  title: string;
  contact_name?: string;
  value: number;
  stage: string;
  status: string;
  expected_close_date?: string;
  notes?: string;
  created_at: string;
}

const stageMap: Record<string, { label: string; color: string }> = {
  discovery: { label: "اكتشاف", color: "bg-blue-100 text-blue-700" },
  proposal: { label: "عرض سعر", color: "bg-purple-100 text-purple-700" },
  negotiation: { label: "تفاوض", color: "bg-yellow-100 text-yellow-700" },
  won: { label: "مكتسب", color: "bg-green-100 text-green-700" },
  lost: { label: "مفقود", color: "bg-red-100 text-red-700" },
};

const emptyForm = {
  title: "",
  contact_name: "",
  value: "",
  stage: "discovery",
  expected_close_date: "",
  notes: "",
};

export default function DealsPage() {
  const [data, setData] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingDeal, setEditingDeal] = useState<Deal | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const fetchDeals = () => {
    setLoading(true);
    deals
      .list()
      .then((res: any) => setData(res.items || res.deals || res || []))
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchDeals();
  }, []);

  const openCreate = () => {
    setEditingDeal(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (deal: Deal) => {
    setEditingDeal(deal);
    setForm({
      title: deal.title || "",
      contact_name: deal.contact_name || "",
      value: deal.value?.toString() || "",
      stage: deal.stage || deal.status || "discovery",
      expected_close_date: deal.expected_close_date || "",
      notes: deal.notes || "",
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      const payload = {
        ...form,
        value: parseFloat(form.value) || 0,
      };
      if (editingDeal) {
        await deals.update(editingDeal.id, payload);
      } else {
        await deals.create(payload);
      }
      setModalOpen(false);
      fetchDeals();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

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

  if (error && data.length === 0) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
        {error}
      </div>
    );
  }

  return (
    <div>
      {/* Header bar */}
      <div className="mb-4 flex items-center justify-between gap-4">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في الصفقات..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pr-9 pl-4 py-2.5 bg-white border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
          />
        </div>
        <button
          onClick={openCreate}
          className="bg-secondary hover:bg-secondary-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition flex items-center gap-2 shrink-0"
        >
          <Plus className="w-4 h-4" />
          إضافة صفقة
        </button>
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
                <th className="text-right px-4 py-3 font-semibold text-gray-600 w-10"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-gray-400">
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
                      <td className="px-4 py-3">
                        <button
                          onClick={() => openEdit(deal)}
                          className="p-1.5 text-gray-400 hover:text-secondary hover:bg-secondary-50 rounded-lg transition"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingDeal ? "تعديل الصفقة" : "إضافة صفقة جديدة"}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              عنوان الصفقة *
            </label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => updateField("title", e.target.value)}
              placeholder="مشروع تطوير الموقع"
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">اسم العميل</label>
              <input
                type="text"
                value={form.contact_name}
                onChange={(e) => updateField("contact_name", e.target.value)}
                placeholder="أحمد محمد"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">القيمة (ر.س)</label>
              <input
                type="number"
                dir="ltr"
                value={form.value}
                onChange={(e) => updateField("value", e.target.value)}
                placeholder="50000"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المرحلة</label>
              <select
                value={form.stage}
                onChange={(e) => updateField("stage", e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
              >
                <option value="discovery">اكتشاف</option>
                <option value="proposal">عرض سعر</option>
                <option value="negotiation">تفاوض</option>
                <option value="won">مكتسب</option>
                <option value="lost">مفقود</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ الإغلاق المتوقع</label>
              <input
                type="date"
                dir="ltr"
                value={form.expected_close_date}
                onChange={(e) => updateField("expected_close_date", e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
            <textarea
              value={form.notes}
              onChange={(e) => updateField("notes", e.target.value)}
              rows={3}
              placeholder="ملاحظات إضافية..."
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none resize-none"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={() => setModalOpen(false)}
              className="px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              إلغاء
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !form.title.trim()}
              className="bg-secondary hover:bg-secondary-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center gap-2"
            >
              {saving && <Loader2 className="w-4 h-4 animate-spin" />}
              {editingDeal ? "حفظ التعديلات" : "إضافة"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
