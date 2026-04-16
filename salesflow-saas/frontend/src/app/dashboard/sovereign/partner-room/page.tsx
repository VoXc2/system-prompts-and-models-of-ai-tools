"use client";

import { useEffect, useState } from "react";
import { Handshake, Loader2, Plus, Users } from "lucide-react";

interface Partner {
  id: string;
  name: string;
  type: string;
  status: string;
  contact_name: string;
  contact_email: string;
  created_at: string;
  revenue_share_pct: number;
}

const STATUS_BADGE: Record<string, { class: string; label: string }> = {
  active: { class: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20", label: "نشط" },
  pending: { class: "bg-amber-500/10 text-amber-500 border-amber-500/20", label: "قيد المراجعة" },
  inactive: { class: "bg-gray-500/10 text-gray-400 border-gray-500/20", label: "غير نشط" },
  suspended: { class: "bg-red-500/10 text-red-500 border-red-500/20", label: "معلق" },
};

export default function PartnerRoomPage() {
  const [partners, setPartners] = useState<Partner[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/partnerships/")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setPartners(Array.isArray(d) ? d : d.items || []))
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

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">غرفة الشراكات</h1>
          <p className="text-sm text-muted-foreground">Partner Room — إدارة الشراكات الاستراتيجية</p>
        </div>
        <button
          type="button"
          className="flex items-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-xl text-xs font-bold hover:bg-primary/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          إضافة شريك
        </button>
      </header>

      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-2xl p-5 text-center">
          <p className="text-2xl font-bold text-foreground">{partners.length}</p>
          <p className="text-xs text-muted-foreground">إجمالي الشركاء</p>
        </div>
        <div className="bg-card border border-border rounded-2xl p-5 text-center">
          <p className="text-2xl font-bold text-emerald-500">{partners.filter((p) => p.status === "active").length}</p>
          <p className="text-xs text-muted-foreground">نشط</p>
        </div>
        <div className="bg-card border border-border rounded-2xl p-5 text-center">
          <p className="text-2xl font-bold text-amber-500">{partners.filter((p) => p.status === "pending").length}</p>
          <p className="text-xs text-muted-foreground">قيد المراجعة</p>
        </div>
        <div className="bg-card border border-border rounded-2xl p-5 text-center">
          <p className="text-2xl font-bold text-red-500">{partners.filter((p) => p.status === "suspended").length}</p>
          <p className="text-xs text-muted-foreground">معلق</p>
        </div>
      </section>

      {partners.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Users className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد شراكات بعد</p>
          <p className="text-sm text-muted-foreground/70">No partners yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {partners.map((p) => {
            const badge = STATUS_BADGE[p.status] || STATUS_BADGE.pending;
            return (
              <div key={p.id} className="bg-card border border-border rounded-2xl p-5 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
                    <Handshake className="w-5 h-5 text-purple-500" />
                  </div>
                  <span className={`inline-flex px-2.5 py-1 rounded-full text-[10px] font-bold border ${badge.class}`}>
                    {badge.label}
                  </span>
                </div>
                <h3 className="font-bold text-sm mb-1">{p.name}</h3>
                <p className="text-xs text-muted-foreground mb-2">{p.type}</p>
                <div className="space-y-1 text-[10px] text-muted-foreground">
                  <p>جهة الاتصال: {p.contact_name}</p>
                  <p>نسبة الإيرادات: {p.revenue_share_pct}%</p>
                  <p>{new Date(p.created_at).toLocaleDateString("ar-SA")}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
