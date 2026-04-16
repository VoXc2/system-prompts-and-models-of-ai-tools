"use client";

import { useEffect, useState } from "react";
import { Layers, Loader2, CheckCircle2, Circle, Clock } from "lucide-react";

interface PMIProgram {
  id: string;
  name: string;
  target_company: string;
  status: string;
  current_phase: "day_30" | "day_60" | "day_90" | "completed";
  overall_progress: number;
  tasks: PMITask[];
  started_at: string;
}

interface PMITask {
  id: string;
  title: string;
  phase: string;
  status: string;
  assignee: string;
  due_date: string;
}

const PHASE_CONFIG: Record<string, { label: string; color: string }> = {
  day_30: { label: "اليوم 30", color: "bg-blue-500" },
  day_60: { label: "اليوم 60", color: "bg-purple-500" },
  day_90: { label: "اليوم 90", color: "bg-amber-500" },
  completed: { label: "مكتمل", color: "bg-emerald-500" },
};

const TASK_STATUS_ICON: Record<string, { icon: typeof CheckCircle2; color: string }> = {
  completed: { icon: CheckCircle2, color: "text-emerald-500" },
  in_progress: { icon: Clock, color: "text-amber-500" },
  not_started: { icon: Circle, color: "text-gray-400" },
};

export default function PMIEnginePage() {
  const [programs, setPrograms] = useState<PMIProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/v1/sovereign/pmi/engine")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setPrograms(Array.isArray(d) ? d : d.items || []))
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
      <header>
        <h1 className="text-2xl font-bold text-foreground">محرك 30/60/90</h1>
        <p className="text-sm text-muted-foreground">PMI 30/60/90 Engine — إدارة برامج تكامل ما بعد الاستحواذ</p>
      </header>

      {programs.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Layers className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد برامج تكامل بعد</p>
          <p className="text-sm text-muted-foreground/70">No PMI programs yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {programs.map((prog) => {
            const phase = PHASE_CONFIG[prog.current_phase] || PHASE_CONFIG.day_30;
            const isExpanded = expanded === prog.id;

            return (
              <div key={prog.id} className="bg-card border border-border rounded-2xl overflow-hidden">
                <button
                  type="button"
                  onClick={() => setExpanded(isExpanded ? null : prog.id)}
                  className="w-full p-6 text-right"
                >
                  <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                    <div className="flex-1">
                      <h3 className="font-bold text-base mb-1">{prog.name}</h3>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span>الشركة: {prog.target_company}</span>
                        <span>•</span>
                        <span>بدأ: {new Date(prog.started_at).toLocaleDateString("ar-SA")}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="flex gap-1">
                        {(["day_30", "day_60", "day_90"] as const).map((p) => {
                          const cfg = PHASE_CONFIG[p];
                          const isActive = prog.current_phase === p;
                          const isPast =
                            (["day_30", "day_60", "day_90", "completed"] as const).indexOf(prog.current_phase) >
                            (["day_30", "day_60", "day_90", "completed"] as const).indexOf(p);
                          return (
                            <div
                              key={p}
                              className={`px-3 py-1 rounded-full text-[10px] font-bold ${
                                isActive
                                  ? `${cfg.color} text-white`
                                  : isPast
                                    ? "bg-emerald-500/20 text-emerald-500"
                                    : "bg-muted text-muted-foreground"
                              }`}
                            >
                              {cfg.label}
                            </div>
                          );
                        })}
                      </div>

                      <div className="text-center">
                        <span className="text-xl font-bold">{prog.overall_progress}%</span>
                      </div>
                    </div>
                  </div>

                  <div className="w-full bg-muted rounded-full h-2 mt-4">
                    <div
                      className="bg-primary rounded-full h-2 transition-all"
                      style={{ width: `${prog.overall_progress}%` }}
                    />
                  </div>
                </button>

                {isExpanded && prog.tasks.length > 0 && (
                  <div className="border-t border-border px-6 py-4">
                    <h4 className="text-xs font-bold text-muted-foreground mb-3">المهام</h4>
                    <div className="space-y-2">
                      {prog.tasks.map((task) => {
                        const taskCfg = TASK_STATUS_ICON[task.status] || TASK_STATUS_ICON.not_started;
                        const TaskIcon = taskCfg.icon;
                        return (
                          <div key={task.id} className="flex items-center gap-3 py-2">
                            <TaskIcon className={`w-4 h-4 shrink-0 ${taskCfg.color}`} />
                            <span className="text-sm flex-1">{task.title}</span>
                            <span className="text-[10px] text-muted-foreground">{task.phase}</span>
                            <span className="text-[10px] text-muted-foreground">{task.assignee}</span>
                            <span className="text-[10px] text-muted-foreground">
                              {new Date(task.due_date).toLocaleDateString("ar-SA")}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
