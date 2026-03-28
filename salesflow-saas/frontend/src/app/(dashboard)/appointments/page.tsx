"use client";

import { useEffect, useState } from "react";
import { appointments } from "@/lib/api";
import {
  Calendar,
  Clock,
  User,
  Plus,
  Loader2,
  CheckCircle2,
  XCircle,
  AlertCircle,
} from "lucide-react";

interface Appointment {
  id: string;
  title: string;
  contact_name?: string;
  contact_phone?: string;
  scheduled_at: string;
  status: string;
  service_type?: string;
  notes?: string;
}

const statusMap: Record<string, { label: string; color: string }> = {
  pending: { label: "بانتظار التأكيد", color: "bg-yellow-100 text-yellow-700" },
  confirmed: { label: "مؤكد", color: "bg-green-100 text-green-700" },
  completed: { label: "مكتمل", color: "bg-blue-100 text-blue-700" },
  no_show: { label: "لم يحضر", color: "bg-red-100 text-red-700" },
  cancelled: { label: "ملغي", color: "bg-gray-100 text-gray-600" },
};

export default function AppointmentsPage() {
  const [todayList, setTodayList] = useState<Appointment[]>([]);
  const [allList, setAllList] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      appointments.today().catch(() => []),
      appointments.list().catch(() => []),
    ])
      .then(([todayRes, allRes]: any[]) => {
        setTodayList(
          todayRes.items || todayRes.appointments || todayRes || []
        );
        setAllList(allRes.items || allRes.appointments || allRes || []);
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

  function renderAppointmentCard(apt: Appointment) {
    const status = statusMap[apt.status] || {
      label: apt.status,
      color: "bg-gray-100 text-gray-600",
    };
    const time = new Date(apt.scheduled_at);

    return (
      <div
        key={apt.id}
        className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition"
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-sm font-semibold text-gray-900" dir="ltr">
              {time.toLocaleTimeString("ar-SA", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          </div>
          <span
            className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium ${status.color}`}
          >
            {status.label}
          </span>
        </div>

        <h3 className="font-semibold text-gray-900 mb-2">{apt.title}</h3>

        <div className="space-y-1.5 text-sm text-gray-600">
          {apt.contact_name && (
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-gray-400" />
              <span>{apt.contact_name}</span>
            </div>
          )}
          {apt.service_type && (
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span>{apt.service_type}</span>
            </div>
          )}
        </div>

        <div className="mt-3 text-xs text-gray-400">
          {time.toLocaleDateString("ar-SA")}
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Action button */}
      <div className="mb-6 flex justify-end">
        <button className="bg-secondary hover:bg-secondary-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2 transition">
          <Plus className="w-4 h-4" />
          حجز موعد جديد
        </button>
      </div>

      {/* Today's appointments */}
      <div className="mb-8">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-secondary" />
          مواعيد اليوم
        </h3>
        {todayList.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400 text-sm">
            <Calendar className="w-8 h-8 mx-auto mb-2 opacity-50" />
            لا توجد مواعيد اليوم
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {todayList.map(renderAppointmentCard)}
          </div>
        )}
      </div>

      {/* All appointments */}
      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-4">جميع المواعيد</h3>
        {allList.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400 text-sm">
            لا توجد مواعيد
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {allList.map(renderAppointmentCard)}
          </div>
        )}
      </div>
    </div>
  );
}
