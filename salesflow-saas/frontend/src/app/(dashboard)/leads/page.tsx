"use client";

import { useEffect, useState } from "react";
import { leads } from "@/lib/api";
import Modal from "@/components/ui/Modal";
import { Users, Loader2, Search, Plus, Pencil } from "lucide-react";

interface Lead {
  id: string;
  full_name: string;
  company?: string;
  phone?: string;
  email?: string;
  status: string;
  score?: number;
  source?: string;
  city?: string;
  notes?: string;
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

const emptyForm = {
  full_name: "",
  company: "",
  phone: "",
  email: "",
  source: "",
  city: "",
  notes: "",
};

export default function LeadsPage() {
  const [data, setData] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingLead, setEditingLead] = useState<Lead | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const fetchLeads = () => {
    setLoading(true);
    leads
      .list()
      .then((res: any) => setData(res.items || res.leads || res || []))
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  const openCreate = () => {
    setEditingLead(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (lead: Lead) => {
    setEditingLead(lead);
    setForm({
      full_name: lead.full_name || "",
      company: lead.company || "",
      phone: lead.phone || "",
      email: lead.email || "",
      source: lead.source || "",
      city: lead.city || "",
      notes: lead.notes || "",
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.full_name.trim()) return;
    setSaving(true);
    try {
      if (editingLead) {
        await leads.update(editingLead.id, form);
      } else {
        await leads.create(form);
      }
      setModalOpen(false);
      fetchLeads();
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
            placeholder="بحث في العملاء..."
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
          إضافة عميل
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-right px-4 py-3 font-semibold text-gray-600">الاسم</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">الشركة</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">الهاتف</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">الحالة</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">التقييم</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">المصدر</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">التاريخ</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600 w-10"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-10 text-gray-400">
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
                      <td className="px-4 py-3">
                        <button
                          onClick={() => openEdit(lead)}
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
        title={editingLead ? "تعديل العميل" : "إضافة عميل جديد"}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              الاسم الكامل *
            </label>
            <input
              type="text"
              value={form.full_name}
              onChange={(e) => updateField("full_name", e.target.value)}
              placeholder="أحمد محمد"
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الشركة</label>
              <input
                type="text"
                value={form.company}
                onChange={(e) => updateField("company", e.target.value)}
                placeholder="اسم الشركة"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المدينة</label>
              <input
                type="text"
                value={form.city}
                onChange={(e) => updateField("city", e.target.value)}
                placeholder="الرياض"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الهاتف</label>
              <input
                type="text"
                dir="ltr"
                value={form.phone}
                onChange={(e) => updateField("phone", e.target.value)}
                placeholder="+966 5XX XXX XXXX"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">البريد</label>
              <input
                type="email"
                dir="ltr"
                value={form.email}
                onChange={(e) => updateField("email", e.target.value)}
                placeholder="email@example.com"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">المصدر</label>
            <select
              value={form.source}
              onChange={(e) => updateField("source", e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
            >
              <option value="">اختر المصدر</option>
              <option value="whatsapp">واتساب</option>
              <option value="website">الموقع</option>
              <option value="referral">إحالة</option>
              <option value="social">وسائل التواصل</option>
              <option value="cold_outreach">تواصل مباشر</option>
              <option value="other">أخرى</option>
            </select>
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
              disabled={saving || !form.full_name.trim()}
              className="bg-secondary hover:bg-secondary-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center gap-2"
            >
              {saving && <Loader2 className="w-4 h-4 animate-spin" />}
              {editingLead ? "حفظ التعديلات" : "إضافة"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
