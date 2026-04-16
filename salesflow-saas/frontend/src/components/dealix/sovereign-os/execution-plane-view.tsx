"use client";

import type { LucideIcon } from "lucide-react";


import {
  Activity,
  CheckCircle2,
  Clock,
  GitBranch,
  Layers,
  Pause,
  Play,
  RefreshCw,
  XCircle,
} from "lucide-react";

type WfStatus = "pending" | "running" | "waiting_hitl" | "approved" | "rejected" | "completed" | "failed" | "timed_out";

interface Workflow {
  id: string;
  workflow_type: string;
  workflow_type_ar: string;
  os_module: string;
  status: WfStatus;
  current_step: string;
  current_step_ar: string;
  started_at: string;
  deadline_at?: string;
  correlation_id: string;
  hitl_count: number;
  checkpoint_count: number;
}

const MOCK_WORKFLOWS: Workflow[] = [
  {
    id: "wf-001",
    workflow_type: "ma_dd_orchestration",
    workflow_type_ar: "تنسيق DD — شركة تك هب",
    os_module: "M&A OS",
    status: "waiting_hitl",
    current_step: "legal_dd_review",
    current_step_ar: "مراجعة DD القانوني",
    started_at: "2026-04-14T08:00:00Z",
    deadline_at: "2026-04-20T08:00:00Z",
    correlation_id: "cor-ma-001",
    hitl_count: 2,
    checkpoint_count: 8,
  },
  {
    id: "wf-002",
    workflow_type: "partnership_term_sheet",
    workflow_type_ar: "Term Sheet — الأفق التقنية",
    os_module: "Partnership OS",
    status: "running",
    current_step: "economic_modeling",
    current_step_ar: "نمذجة الاقتصاديات",
    started_at: "2026-04-15T10:30:00Z",
    correlation_id: "cor-pa-002",
    hitl_count: 0,
    checkpoint_count: 3,
  },
  {
    id: "wf-003",
    workflow_type: "expansion_launch",
    workflow_type_ar: "إطلاق الرياض الشمالية",
    os_module: "Expansion OS",
    status: "approved",
    current_step: "canary_launch",
    current_step_ar: "إطلاق Canary 10٪",
    started_at: "2026-04-16T06:00:00Z",
    correlation_id: "cor-ex-003",
    hitl_count: 1,
    checkpoint_count: 5,
  },
  {
    id: "wf-004",
    workflow_type: "pmi_day1_readiness",
    workflow_type_ar: "جاهزية اليوم الأول — تك هب",
    os_module: "PMI OS",
    status: "pending",
    current_step: "kickoff",
    current_step_ar: "انطلاق المشروع",
    started_at: "2026-04-16T12:00:00Z",
    correlation_id: "cor-pmi-004",
    hitl_count: 0,
    checkpoint_count: 0,
  },
  {
    id: "wf-005",
    workflow_type: "sales_proposal_approval",
    workflow_type_ar: "اعتماد عرض — مجموعة التطوير",
    os_module: "Sales OS",
    status: "completed",
    current_step: "completed",
    current_step_ar: "مكتمل",
    started_at: "2026-04-13T14:00:00Z",
    correlation_id: "cor-sa-005",
    hitl_count: 1,
    checkpoint_count: 6,
  },
];

const statusConfig: Record<WfStatus, { label: string; color: string; icon: LucideIcon; animate?: boolean }> = {
  pending: { label: "في الانتظار", color: "text-muted-foreground bg-secondary/30 border-border", icon: Clock },
  running: { label: "جاري", color: "text-blue-400 bg-blue-500/10 border-blue-500/20", icon: Play, animate: true },
  waiting_hitl: { label: "بانتظار HITL", color: "text-amber-400 bg-amber-500/10 border-amber-500/20", icon: Pause },
  approved: { label: "معتمد", color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20", icon: CheckCircle2 },
  rejected: { label: "مرفوض", color: "text-red-400 bg-red-500/10 border-red-500/20", icon: XCircle },
  completed: { label: "مكتمل", color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20", icon: CheckCircle2 },
  failed: { label: "فشل", color: "text-red-400 bg-red-500/10 border-red-500/20", icon: XCircle },
  timed_out: { label: "انتهت المهلة", color: "text-red-400 bg-red-500/10 border-red-500/20", icon: Clock },
};

const moduleColors: Record<string, string> = {
  "M&A OS": "bg-purple-500/10 text-purple-400",
  "Partnership OS": "bg-blue-500/10 text-blue-400",
  "Expansion OS": "bg-emerald-500/10 text-emerald-400",
  "PMI OS": "bg-orange-500/10 text-orange-400",
  "Sales OS": "bg-primary/10 text-primary",
};

export function ExecutionPlaneView() {
  const running = MOCK_WORKFLOWS.filter((w) => ["running", "waiting_hitl", "approved"].includes(w.status)).length;

  return (
    <div className="p-6 space-y-5" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Execution Plane — سير العمليات الدائمة</h1>
          <p className="text-sm text-muted-foreground mt-1">Durable Workflows مع Checkpoints وHITL Interrupts</p>
        </div>
        <div className="flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 px-3 py-1.5 rounded-xl">
          <Activity className="w-4 h-4 text-blue-400 animate-pulse" />
          <span className="text-sm font-bold text-blue-400">{running} نشط</span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "إجمالي العمليات", value: MOCK_WORKFLOWS.length, icon: Layers, color: "text-primary" },
          { label: "جارية الآن", value: MOCK_WORKFLOWS.filter((w) => w.status === "running").length, icon: Play, color: "text-blue-400" },
          { label: "بانتظار HITL", value: MOCK_WORKFLOWS.filter((w) => w.status === "waiting_hitl").length, icon: Pause, color: "text-amber-400" },
          { label: "مكتملة", value: MOCK_WORKFLOWS.filter((w) => w.status === "completed").length, icon: CheckCircle2, color: "text-emerald-400" },
        ].map((s) => (
          <div key={s.label} className="bg-card/50 border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <s.icon className={`w-4 h-4 ${s.color}`} />
              <p className="text-xs text-muted-foreground">{s.label}</p>
            </div>
            <p className="text-2xl font-bold text-foreground">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        {MOCK_WORKFLOWS.map((wf) => {
          const cfg = statusConfig[wf.status];
          const StatusIcon = cfg.icon;
          return (
            <div key={wf.id} className="bg-card/50 border border-border rounded-2xl p-5 hover:border-primary/20 transition-all">
              <div className="flex items-start justify-between gap-3 mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <GitBranch className="w-4 h-4 text-muted-foreground" />
                    <h3 className="font-bold text-foreground">{wf.workflow_type_ar}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${moduleColors[wf.os_module] || "bg-secondary/40 text-muted-foreground"}`}>
                      {wf.os_module}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    الخطوة الحالية: <span className="text-foreground">{wf.current_step_ar}</span>
                  </p>
                </div>
                <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border flex-shrink-0 ${cfg.color}`}>
                  <StatusIcon className={`w-3.5 h-3.5 ${cfg.animate ? "animate-pulse" : ""}`} />
                  {cfg.label}
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
                <div className="bg-secondary/20 rounded-xl p-2.5">
                  <p className="text-xs text-muted-foreground">Checkpoints</p>
                  <p className="text-sm font-bold text-foreground">{wf.checkpoint_count}</p>
                </div>
                <div className="bg-secondary/20 rounded-xl p-2.5">
                  <p className="text-xs text-muted-foreground">HITL</p>
                  <p className="text-sm font-bold text-foreground">{wf.hitl_count}</p>
                </div>
                <div className="bg-secondary/20 rounded-xl p-2.5 col-span-2">
                  <p className="text-xs text-muted-foreground">Correlation ID</p>
                  <p className="text-xs font-mono text-primary">{wf.correlation_id}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {wf.status === "waiting_hitl" && (
                  <button
                    type="button"
                    className="flex items-center gap-1.5 text-xs bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/20 px-3 py-1.5 rounded-lg transition-all"
                  >
                    <Pause className="w-3.5 h-3.5" />
                    مراجعة HITL
                  </button>
                )}
                {wf.status === "running" && (
                  <button
                    type="button"
                    className="flex items-center gap-1.5 text-xs bg-secondary/40 hover:bg-secondary/70 text-foreground px-3 py-1.5 rounded-lg transition-all"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    عرض Trace
                  </button>
                )}
                <p className="text-xs text-muted-foreground mr-auto font-mono">{wf.id}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
