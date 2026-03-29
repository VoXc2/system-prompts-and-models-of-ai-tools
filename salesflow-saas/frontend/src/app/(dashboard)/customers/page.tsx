"use client";

import { useEffect, useState } from "react";
import { customers } from "@/lib/api";
import Modal from "@/components/ui/Modal";
import { UserCheck, Loader2, Search, Plus, Pencil } from "lucide-react";

interface Customer {
  id: string;
  full_name: string;
  company?: string;
  email?: string;
  phone?: string;
  city?: string;
  industry?: string;
  notes?: string;
  created_at: string;
}

const emptyForm = {
  full_name: "",
  company: "",
  email: "",
  phone: "",
  city: "",
  industry: "",
  notes: "",
};

export default function CustomersPage() {
  const [data, setData] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Customer | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const fetchData = () => {
    setLoading(true);
    customers
      .list(search ? { search } : undefined)
      .then((res: any) => setData(res.items || []))
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (c: Customer) => {
    setEditing(c);
    setForm({
      full_name: c.full_name || "",
      company: c.company || "",
      email: c.email || "",
      phone: c.phone || "",
      city: c.city || "",
      industry: c.industry || "",
      notes: c.notes || "",
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.full_name.trim()) return;
    setSaving(true);
    try {
      if (editing) {
        await customers.update(editing.id, form);
      } else {
        await customers.create(form);
      }
      setModalOpen(false);
      fetchData();
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
    (c) =>
      c.full_name?.includes(search) ||
      c.company?.includes(search) ||
      c.phone?.includes(search)
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  return (
    <div>
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

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-right px-4 py-3 font-semibold text-gray-600">الاسم</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">الشركة</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">الهاتف</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">البريد</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">المدينة</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">التاريخ</th>
                <th className="w-10"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-gray-400">
                    <UserCheck className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    لا يوجد عملاء
                  </td>
                </tr>
              ) : (
                filtered.map((c) => (
                  <tr key={c.id} className="border-b border-gray-100 hover:bg-gray-50 transition">
                    <td className="px-4 py-3 font-medium text-gray-900">{c.full_name}</td>
                    <td className="px-4 py-3 text-gray-600">{c.company || "-"}</td>
                    <td className="px-4 py-3 text-gray-600" dir="ltr">{c.phone || "-"}</td>
                    <td className="px-4 py-3 text-gray-600" dir="ltr">{c.email || "-"}</td>
                    <td className="px-4 py-3 text-gray-600">{c.city || "-"}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      {c.created_at ? new Date(c.created_at).toLocaleDateString("ar-SA") : "-"}
                    </td>
                    <td className="px-4 py-3">
                      <button onClick={() => openEdit(c)} className="p-1.5 text-gray-400 hover:text-secondary hover:bg-secondary-50 rounded-lg transition">
                        <Pencil className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editing ? "تعديل العميل" : "إضافة عميل جديد"}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">الاسم الكامل *</label>
            <input type="text" value={form.full_name} onChange={(e) => updateField("full_name", e.target.value)} placeholder="أحمد محمد" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الشركة</label>
              <input type="text" value={form.company} onChange={(e) => updateField("company", e.target.value)} className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المدينة</label>
              <input type="text" value={form.city} onChange={(e) => updateField("city", e.target.value)} className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الهاتف</label>
              <input type="text" dir="ltr" value={form.phone} onChange={(e) => updateField("phone", e.target.value)} placeholder="+966 5XX XXX XXXX" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">البريد</label>
              <input type="email" dir="ltr" value={form.email} onChange={(e) => updateField("email", e.target.value)} className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">القطاع</label>
            <select value={form.industry} onChange={(e) => updateField("industry", e.target.value)} className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none">
              <option value="">اختر القطاع</option>
              <option value="healthcare">عيادات / صحي</option>
              <option value="real_estate">عقارات</option>
              <option value="construction">مقاولات</option>
              <option value="education">تعليم / تدريب</option>
              <option value="services">خدمات B2B</option>
              <option value="retail">تجزئة</option>
              <option value="other">أخرى</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
            <textarea value={form.notes} onChange={(e) => updateField("notes", e.target.value)} rows={3} className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none resize-none" />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button onClick={() => setModalOpen(false)} className="px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition">إلغاء</button>
            <button onClick={handleSave} disabled={saving || !form.full_name.trim()} className="bg-secondary hover:bg-secondary-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center gap-2">
              {saving && <Loader2 className="w-4 h-4 animate-spin" />}
              {editing ? "حفظ التعديلات" : "إضافة"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
