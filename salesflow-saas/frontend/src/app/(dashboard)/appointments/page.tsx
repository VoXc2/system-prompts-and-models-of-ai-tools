"use client";

import { useEffect, useState } from "react";
import { appointments } from "@/lib/api";
import {
  Calendar, Clock, User, Plus, Loader2, CheckCircle2,
  XCircle, AlertCircle, X, Phone, Mail, MapPin, FileText,
  Check, Ban, UserX,
} from "lucide-react";

interface Appointment {
  id: string;
  title: string;
  contact_name?: string;
  contact_phone?: string;
  contact_email?: string;
  scheduled_at?: string;
  start_time?: string;
  status: string;
  service_type?: string;
  location?: string;
  notes?: string;
  duration_minutes?: number;
}

const statusMap: Record<string, { label: string; color: string }> = {
  pending: { label: "بانتظار التأكيد", color: "bg-yellow-100 text-yellow-700" },
  confirmed: { label: "مؤكد", color: "bg-green-100 text-green-700" },
  completed: { label: "مكتمل", color: "bg-blue-100 text-blue-700" },
  no_show: { label: "لم يحضر", color: "bg-red-100 text-red-700" },
  cancelled: { label: "ملغي", color: "bg-gray-100 text-gray-600" },
};

const SERVICE_TYPES = [
  { value: "consultation", label: "استشارة" },
  { value: "checkup", label: "فحص / كشف" },
  { value: "followup", label: "متابعة" },
  { value: "meeting", label: "اجتماع" },
  { value: "other", label: "أخرى" },
];

export default function AppointmentsPage() {
  const [todayList, setTodayList] = useState<Appointment[]>([]);
  const [allList, setAllList] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const [form, setForm] = useState({
    title: "", service_type: "other", start_time: "",
    duration_minutes: "30", contact_name: "", contact_phone: "",
    contact_email: "", location: "", notes: "",
  });

  const loadData = () => {
    setLoading(true);
    Promise.all([
      appointments.today().catch(() => ({ data: [] })),
      appointments.list().catch(() => ({ data: { items: [] } })),
    ])
      .then(([todayRes, allRes]: any[]) => {
        setTodayList(todayRes.data || todayRes.items || todayRes || []);
        const items = allRes.data?.items || allRes.items || allRes.data || allRes || [];
        setAllList(Array.isArray(items) ? items : []);
      })
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadData(); }, []);

  const handleCreate = async () => {
    if (!form.start_time) return setError("يجب تحديد وقت الموعد");
    setCreating(true);
    setError("");
    try {
      await appointments.create({
        title: form.title || undefined,
        service_type: form.service_type,
        start_time: new Date(form.start_time).toISOString(),
        duration_minutes: parseInt(form.duration_minutes) || 30,
        contact_name: form.contact_name || undefined,
        contact_phone: form.contact_phone || undefined,
        contact_email: form.contact_email || undefined,
        location: form.location || undefined,
        notes: form.notes || undefined,
        booked_via: "manual",
      });
      setShowModal(false);
      setForm({ title: "", service_type: "other", start_time: "", duration_minutes: "30", contact_name: "", contact_phone: "", contact_email: "", location: "", notes: "" });
      loadData();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  const doAction = async (id: string, action: "confirm" | "complete" | "cancel" | "noShow") => {
    setActionLoading(id + action);
    try {
      if (action === "confirm") await appointments.confirm(id);
      else if (action === "complete") await appointments.complete(id);
      else if (action === "cancel") await appointments.cancel(id);
      else if (action === "noShow") await appointments.noShow(id);
      loadData();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setActionLoading(null);
    }
  };

  const update = (field: string, value: string) => setForm((p) => ({ ...p, [field]: value }));

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  function renderCard(apt: Appointment) {
    const status = statusMap[apt.status] || { label: apt.status, color: "bg-gray-100 text-gray-600" };
    const timeStr = apt.start_time || apt.scheduled_at;
    const time = timeStr ? new Date(timeStr) : null;

    return (
      <div key={apt.id} className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-gray-400" />
            {time && (
              <span className="text-sm font-semibold text-gray-900" dir="ltr">
                {time.toLocaleTimeString("ar-SA", { hour: "2-digit", minute: "2-digit" })}
              </span>
            )}
          </div>
          <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium ${status.color}`}>
            {status.label}
          </span>
        </div>

        <h3 className="font-semibold text-gray-900 mb-2">{apt.title || apt.service_type || "موعد"}</h3>

        <div className="space-y-1.5 text-sm text-gray-600">
          {apt.contact_name && (
            <div className="flex items-center gap-2"><User className="w-4 h-4 text-gray-400" />{apt.contact_name}</div>
          )}
          {apt.contact_phone && (
            <div className="flex items-center gap-2" dir="ltr"><Phone className="w-4 h-4 text-gray-400" />{apt.contact_phone}</div>
          )}
          {apt.location && (
            <div className="flex items-center gap-2"><MapPin className="w-4 h-4 text-gray-400" />{apt.location}</div>
          )}
        </div>

        {time && <div className="mt-2 text-xs text-gray-400">{time.toLocaleDateString("ar-SA")}</div>}

        {/* Actions */}
        <div className="mt-3 pt-3 border-t border-gray-100 flex gap-2 flex-wrap">
          {apt.status === "pending" && (
            <>
              <button onClick={() => doAction(apt.id, "confirm")} disabled={!!actionLoading}
                className="flex items-center gap-1 px-2.5 py-1.5 bg-green-50 text-green-700 hover:bg-green-100 rounded-lg text-xs font-medium transition disabled:opacity-50">
                {actionLoading === apt.id + "confirm" ? <Loader2 className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />} تأكيد
              </button>
              <button onClick={() => doAction(apt.id, "cancel")} disabled={!!actionLoading}
                className="flex items-center gap-1 px-2.5 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 rounded-lg text-xs font-medium transition disabled:opacity-50">
                {actionLoading === apt.id + "cancel" ? <Loader2 className="w-3 h-3 animate-spin" /> : <Ban className="w-3 h-3" />} إلغاء
              </button>
            </>
          )}
          {apt.status === "confirmed" && (
            <>
              <button onClick={() => doAction(apt.id, "complete")} disabled={!!actionLoading}
                className="flex items-center gap-1 px-2.5 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-lg text-xs font-medium transition disabled:opacity-50">
                {actionLoading === apt.id + "complete" ? <Loader2 className="w-3 h-3 animate-spin" /> : <CheckCircle2 className="w-3 h-3" />} مكتمل
              </button>
              <button onClick={() => doAction(apt.id, "noShow")} disabled={!!actionLoading}
                className="flex items-center gap-1 px-2.5 py-1.5 bg-orange-50 text-orange-700 hover:bg-orange-100 rounded-lg text-xs font-medium transition disabled:opacity-50">
                {actionLoading === apt.id + "noShow" ? <Loader2 className="w-3 h-3 animate-spin" /> : <UserX className="w-3 h-3" />} لم يحضر
              </button>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div>
      {error && <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">{error}</div>}

      <div className="mb-6 flex justify-end">
        <button onClick={() => { setShowModal(true); setError(""); }}
          className="bg-secondary hover:bg-secondary-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2 transition">
          <Plus className="w-4 h-4" /> حجز موعد جديد
        </button>
      </div>

      {/* Today */}
      <div className="mb-8">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-secondary" /> مواعيد اليوم
        </h3>
        {todayList.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400 text-sm">
            <Calendar className="w-8 h-8 mx-auto mb-2 opacity-50" /> لا توجد مواعيد اليوم
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">{todayList.map(renderCard)}</div>
        )}
      </div>

      {/* All */}
      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-4">جميع المواعيد</h3>
        {allList.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400 text-sm">لا توجد مواعيد</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">{allList.map(renderCard)}</div>
        )}
      </div>

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg p-6 shadow-xl max-h-[90vh] overflow-y-auto" dir="rtl">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-gray-900">حجز موعد جديد</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">عنوان الموعد</label>
                <input type="text" value={form.title} onChange={(e) => update("title", e.target.value)}
                  placeholder="مثال: كشف أولي" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">نوع الخدمة</label>
                  <select value={form.service_type} onChange={(e) => update("service_type", e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-secondary outline-none">
                    {SERVICE_TYPES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">المدة (دقيقة)</label>
                  <select value={form.duration_minutes} onChange={(e) => update("duration_minutes", e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-secondary outline-none">
                    <option value="15">15 دقيقة</option>
                    <option value="30">30 دقيقة</option>
                    <option value="45">45 دقيقة</option>
                    <option value="60">ساعة</option>
                    <option value="90">ساعة ونص</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">التاريخ والوقت *</label>
                <input type="datetime-local" value={form.start_time} onChange={(e) => update("start_time", e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">اسم العميل</label>
                  <input type="text" value={form.contact_name} onChange={(e) => update("contact_name", e.target.value)}
                    placeholder="محمد" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">رقم العميل</label>
                  <input type="tel" dir="ltr" value={form.contact_phone} onChange={(e) => update("contact_phone", e.target.value)}
                    placeholder="+966 5XX" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">البريد الإلكتروني</label>
                <input type="email" dir="ltr" value={form.contact_email} onChange={(e) => update("contact_email", e.target.value)}
                  placeholder="client@email.com" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الموقع</label>
                <input type="text" value={form.location} onChange={(e) => update("location", e.target.value)}
                  placeholder="العيادة الرئيسية / أونلاين" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
                <textarea rows={2} value={form.notes} onChange={(e) => update("notes", e.target.value)}
                  placeholder="ملاحظات إضافية..." className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none resize-none" />
              </div>
            </div>

            <div className="mt-5 flex items-center justify-end gap-3">
              <button onClick={() => setShowModal(false)} className="px-4 py-2.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition">إلغاء</button>
              <button onClick={handleCreate} disabled={creating || !form.start_time}
                className="bg-secondary hover:bg-secondary-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center gap-2">
                {creating && <Loader2 className="w-4 h-4 animate-spin" />} حجز الموعد
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
