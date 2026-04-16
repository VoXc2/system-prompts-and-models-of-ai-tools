"use client";

import type { LucideIcon } from "lucide-react";


import { useState } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  DollarSign,
  FileText,
  GitMerge,
  RotateCcw,
  Shield,
  XCircle,
} from "lucide-react";

type ApprovalClass = "A" | "B" | "C";
type Reversibility = "reversible" | "partially_reversible" | "irreversible";
type Sensitivity = "low" | "medium" | "high" | "critical";
type ApprovalStatus = "pending" | "approved" | "rejected";

interface Approval {
  id: string;
  title_ar: string;
  os_module: string;
  approval_class: ApprovalClass;
  reversibility: Reversibility;
  sensitivity: Sensitivity;
  financial_impact_sar?: number;
  status: ApprovalStatus;
  alternatives: string[];
  risks: string[];
  requested_by: string;
  created_at: string;
  expires_at?: string;
}

const MOCK_APPROVALS: Approval[] = [
  {
    id: "1",
    title_ar: "إرسال term sheet لشراكة مع شركة الأفق التقنية — عائد 15% + حصرية قطاع التقنية",
    os_module: "Partnership OS",
    approval_class: "B",
    reversibility: "partially_reversible",
    sensitivity: "high",
    financial_impact_sar: 2400000,
    status: "pending",
    alternatives: ["شراكة غير حصرية بعائد 10%", "تأجيل 60 يوماً لمزيد من البيانات"],
    risks: ["التزام حصرية قد يُقيّد مرونة القطاع", "نسبة العائد أعلى من السياسة القياسية"],
    requested_by: "م. أحمد الغامدي",
    created_at: "2026-04-16T08:30:00Z",
    expires_at: "2026-04-18T08:30:00Z",
  },
  {
    id: "2",
    title_ar: "إرسال عرض استحواذ على شركة تك هب — 12M SAR",
    os_module: "M&A OS",
    approval_class: "B",
    reversibility: "irreversible",
    sensitivity: "critical",
    financial_impact_sar: 12000000,
    status: "pending",
    alternatives: ["عرض بـ 10M SAR مع شرط أداء", "شراكة استراتيجية بدلاً من الاستحواذ"],
    risks: ["التزام مالي لا يمكن التراجع عنه", "يتطلب موافقة مجلس الإدارة"],
    requested_by: "م. سارة العتيبي",
    created_at: "2026-04-16T09:15:00Z",
    expires_at: "2026-04-17T09:15:00Z",
  },
  {
    id: "3",
    title_ar: "اعتماد خصم 22% للعميل: مجموعة التطوير العربية",
    os_module: "Sales OS",
    approval_class: "B",
    reversibility: "reversible",
    sensitivity: "medium",
    financial_impact_sar: 165000,
    status: "pending",
    alternatives: ["خصم 15% ضمن السياسة", "خصم 20% مع تمديد العقد لسنتين"],
    risks: ["يتجاوز حد الخصم القياسي بـ 2%"],
    requested_by: "م. خالد الشمري",
    created_at: "2026-04-16T10:00:00Z",
  },
  {
    id: "4",
    title_ar: "إطلاق دخول سوق الرياض الشمالية — canary 10%",
    os_module: "Expansion OS",
    approval_class: "B",
    reversibility: "reversible",
    sensitivity: "medium",
    financial_impact_sar: 350000,
    status: "approved",
    alternatives: [],
    risks: ["معدل توقف canary > 5% يُوقف الإطلاق تلقائياً"],
    requested_by: "م. نورة الحربي",
    created_at: "2026-04-15T14:00:00Z",
  },
];

const classColors: Record<ApprovalClass, string> = {
  A: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  B: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  C: "bg-red-500/10 text-red-400 border-red-500/20",
};

const reversibilityLabels: Record<Reversibility, string> = {
  reversible: "قابل للتراجع",
  partially_reversible: "قابل للتراجع جزئياً",
  irreversible: "غير قابل للتراجع",
};

const reversibilityColors: Record<Reversibility, string> = {
  reversible: "text-emerald-400",
  partially_reversible: "text-amber-400",
  irreversible: "text-red-400",
};

const sensitivityColors: Record<Sensitivity, string> = {
  low: "text-muted-foreground",
  medium: "text-amber-400",
  high: "text-orange-400",
  critical: "text-red-400",
};

const sensitivityLabels: Record<Sensitivity, string> = {
  low: "منخفضة",
  medium: "متوسطة",
  high: "عالية",
  critical: "حرجة",
};

const statusBadge: Record<ApprovalStatus, { label: string; color: string; icon: LucideIcon }> = {
  pending: { label: "بانتظار الاعتماد", color: "text-amber-400 bg-amber-500/10 border-amber-500/20", icon: Clock },
  approved: { label: "مُعتمد", color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20", icon: CheckCircle2 },
  rejected: { label: "مرفوض", color: "text-red-400 bg-red-500/10 border-red-500/20", icon: XCircle },
};

export function ApprovalCenter() {
  const [selected, setSelected] = useState<Approval | null>(null);
  const [filterStatus, setFilterStatus] = useState<ApprovalStatus | "all">("pending");

  const filtered = MOCK_APPROVALS.filter((a) => filterStatus === "all" || a.status === filterStatus);

  if (selected) {
    const badge = statusBadge[selected.status];
    const BadgeIcon = badge.icon;
    return (
      <div className="p-6" dir="rtl">
        <button
          type="button"
          onClick={() => setSelected(null)}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          العودة إلى مركز الاعتماد
        </button>

        <div className="max-w-3xl mx-auto space-y-5">
          <div className="bg-card/50 border border-border rounded-2xl p-6">
            <div className="flex items-start justify-between gap-4 mb-4">
              <h2 className="text-lg font-bold text-foreground leading-tight">{selected.title_ar}</h2>
              <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border flex-shrink-0 ${badge.color}`}>
                <BadgeIcon className="w-3.5 h-3.5" />
                {badge.label}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
              <div className="bg-secondary/30 rounded-xl p-3">
                <p className="text-xs text-muted-foreground mb-1">درجة الاعتماد</p>
                <span className={`text-sm font-bold px-2 py-0.5 rounded border ${classColors[selected.approval_class]}`}>
                  Class {selected.approval_class}
                </span>
              </div>
              <div className="bg-secondary/30 rounded-xl p-3">
                <p className="text-xs text-muted-foreground mb-1">قابلية التراجع</p>
                <p className={`text-sm font-bold ${reversibilityColors[selected.reversibility]}`}>
                  {reversibilityLabels[selected.reversibility]}
                </p>
              </div>
              <div className="bg-secondary/30 rounded-xl p-3">
                <p className="text-xs text-muted-foreground mb-1">درجة الحساسية</p>
                <p className={`text-sm font-bold ${sensitivityColors[selected.sensitivity]}`}>
                  {sensitivityLabels[selected.sensitivity]}
                </p>
              </div>
              {selected.financial_impact_sar && (
                <div className="bg-secondary/30 rounded-xl p-3">
                  <p className="text-xs text-muted-foreground mb-1">الأثر المالي</p>
                  <p className="text-sm font-bold text-foreground">
                    {(selected.financial_impact_sar / 1000000).toFixed(1)}M SAR
                  </p>
                </div>
              )}
            </div>

            {selected.alternatives.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-bold text-foreground mb-2 flex items-center gap-1.5">
                  <GitMerge className="w-4 h-4 text-primary" />
                  البدائل المتاحة
                </h3>
                <ul className="space-y-1.5">
                  {selected.alternatives.map((alt, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <span className="w-5 h-5 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</span>
                      {alt}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {selected.risks.length > 0 && (
              <div>
                <h3 className="text-sm font-bold text-foreground mb-2 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  المخاطر المحتملة
                </h3>
                <ul className="space-y-1.5">
                  {selected.risks.map((risk, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-amber-300/80">
                      <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {selected.status === "pending" && (
            <div className="flex gap-3">
              <button
                type="button"
                className="flex-1 flex items-center justify-center gap-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 rounded-xl py-3 text-sm font-bold transition-all"
              >
                <CheckCircle2 className="w-4 h-4" />
                اعتماد القرار
              </button>
              <button
                type="button"
                className="flex-1 flex items-center justify-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 rounded-xl py-3 text-sm font-bold transition-all"
              >
                <XCircle className="w-4 h-4" />
                رفض القرار
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-5" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">مركز الاعتماد</h1>
          <p className="text-sm text-muted-foreground mt-1">القرارات التي تتطلب صلاحية بشرية — Approval Center</p>
        </div>
        <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-xl">
          <Clock className="w-4 h-4 text-amber-400" />
          <span className="text-sm font-bold text-amber-400">{MOCK_APPROVALS.filter((a) => a.status === "pending").length} معلقة</span>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {(["all", "pending", "approved", "rejected"] as const).map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFilterStatus(f)}
            className={`px-4 py-1.5 rounded-xl text-sm font-medium transition-all ${
              filterStatus === f
                ? "bg-primary text-primary-foreground"
                : "bg-secondary/40 text-muted-foreground hover:text-foreground"
            }`}
          >
            {f === "all" ? "الكل" : f === "pending" ? "معلق" : f === "approved" ? "معتمد" : "مرفوض"}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filtered.map((approval) => {
          const badge = statusBadge[approval.status];
          const BadgeIcon = badge.icon;
          return (
            <button
              key={approval.id}
              type="button"
              onClick={() => setSelected(approval)}
              className="w-full bg-card/50 border border-border rounded-2xl p-4 hover:border-primary/30 hover:bg-card/80 transition-all text-right"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${classColors[approval.approval_class]}`}>
                      Class {approval.approval_class}
                    </span>
                    <span className="text-xs bg-secondary/50 px-2 py-0.5 rounded-full text-muted-foreground">{approval.os_module}</span>
                    <span className={`text-xs ${reversibilityColors[approval.reversibility]}`}>
                      <RotateCcw className="w-3 h-3 inline mr-0.5" />
                      {reversibilityLabels[approval.reversibility]}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-foreground leading-tight mb-2 line-clamp-2">{approval.title_ar}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    {approval.financial_impact_sar && (
                      <span className="flex items-center gap-1">
                        <DollarSign className="w-3 h-3" />
                        {(approval.financial_impact_sar / 1000000).toFixed(1)}M SAR
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <Shield className={`w-3 h-3 ${sensitivityColors[approval.sensitivity]}`} />
                      {sensitivityLabels[approval.sensitivity]}
                    </span>
                    <span>{approval.requested_by}</span>
                  </div>
                </div>
                <span className={`inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full border flex-shrink-0 ${badge.color}`}>
                  <BadgeIcon className="w-3 h-3" />
                  {badge.label}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
