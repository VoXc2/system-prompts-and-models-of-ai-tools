"use client";

import {
  BarChart3,
  Brain,
  CheckCircle2,
  Clock,
  DollarSign,
  Globe,
  Star,
  TrendingUp,
  Zap,
} from "lucide-react";

interface ModelStat {
  name: string;
  displayName: string;
  successRate: number;
  avgLatencyMs: number;
  avgCostUsd: number;
  schemaAdherence: number;
  arabicQuality: number;
  contradictionRate: number;
  recommendedFor: string[];
  totalRuns: number;
}

const MOCK_MODELS: ModelStat[] = [
  {
    name: "gpt-5-4-high",
    displayName: "GPT-5.4 High",
    successRate: 97,
    avgLatencyMs: 2100,
    avgCostUsd: 0.018,
    schemaAdherence: 99,
    arabicQuality: 91,
    contradictionRate: 1.2,
    recommendedFor: ["architecture", "executive_memo", "complex_tool_workflow"],
    totalRuns: 1240,
  },
  {
    name: "claude-opus-4-6-high",
    displayName: "Opus 4.6 High",
    successRate: 96,
    avgLatencyMs: 3800,
    avgCostUsd: 0.025,
    schemaAdherence: 98,
    arabicQuality: 93,
    contradictionRate: 0.9,
    recommendedFor: ["board_synthesis", "strategic_comparison", "heavy_decision"],
    totalRuns: 680,
  },
  {
    name: "claude-sonnet-4-6-high",
    displayName: "Sonnet 4.6 High",
    successRate: 94,
    avgLatencyMs: 1400,
    avgCostUsd: 0.008,
    schemaAdherence: 96,
    arabicQuality: 89,
    contradictionRate: 2.1,
    recommendedFor: ["drafting", "structured_content", "throughput"],
    totalRuns: 3120,
  },
  {
    name: "codex-5-3-high-fast",
    displayName: "Codex 5.3 High Fast",
    successRate: 98,
    avgLatencyMs: 800,
    avgCostUsd: 0.004,
    schemaAdherence: 97,
    arabicQuality: 72,
    contradictionRate: 0.8,
    recommendedFor: ["implementation", "refactoring", "test_fixes"],
    totalRuns: 5600,
  },
  {
    name: "gpt-5-4-high-fast",
    displayName: "GPT-5.4 High Fast",
    successRate: 95,
    avgLatencyMs: 950,
    avgCostUsd: 0.007,
    schemaAdherence: 98,
    arabicQuality: 88,
    contradictionRate: 1.5,
    recommendedFor: ["typed_outputs", "sales_copy", "routing"],
    totalRuns: 2890,
  },
];

const TASK_ROUTING: Array<{ task: string; task_ar: string; recommended: string }> = [
  { task: "architecture", task_ar: "تصميم المعمارية", recommended: "GPT-5.4 High" },
  { task: "executive_memo", task_ar: "المذكرة التنفيذية", recommended: "Opus 4.6 High" },
  { task: "board_synthesis", task_ar: "تقرير مجلس الإدارة", recommended: "Opus 4.6 High" },
  { task: "arabic_nlp", task_ar: "معالجة اللغة العربية", recommended: "Opus 4.6 High" },
  { task: "implementation", task_ar: "التطبير البرمجي", recommended: "Codex 5.3 High Fast" },
  { task: "drafting", task_ar: "صياغة المحتوى", recommended: "Sonnet 4.6 High" },
  { task: "typed_outputs", task_ar: "المخرجات المهيكلة", recommended: "GPT-5.4 High Fast" },
  { task: "throughput", task_ar: "المعالجة الكثيفة", recommended: "Sonnet 4.6 High" },
];

function ScoreBar({ value, max = 100, color = "bg-primary" }: { value: number; max?: number; color?: string }) {
  return (
    <div className="h-1.5 bg-secondary/40 rounded-full overflow-hidden">
      <div
        className={`h-full rounded-full ${color}`}
        style={{ width: `${(value / max) * 100}%` }}
      />
    </div>
  );
}

function ModelCard({ model }: { model: ModelStat }) {
  return (
    <div className="bg-card/50 border border-border rounded-2xl p-5 hover:border-primary/20 transition-all">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-bold text-foreground">{model.displayName}</h3>
          <p className="text-xs text-muted-foreground mt-0.5">{model.totalRuns.toLocaleString()} تشغيل</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-emerald-400">{model.successRate}٪</p>
          <p className="text-xs text-muted-foreground">معدل النجاح</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-muted-foreground flex items-center gap-1"><Globe className="w-3 h-3" />جودة عربية</span>
            <span className="text-foreground font-medium">{model.arabicQuality}٪</span>
          </div>
          <ScoreBar value={model.arabicQuality} color="bg-blue-400" />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-muted-foreground flex items-center gap-1"><CheckCircle2 className="w-3 h-3" />التزام Schema</span>
            <span className="text-foreground font-medium">{model.schemaAdherence}٪</span>
          </div>
          <ScoreBar value={model.schemaAdherence} color="bg-emerald-400" />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-muted-foreground flex items-center gap-1"><Clock className="w-3 h-3" />التأخير</span>
            <span className="text-foreground font-medium">{model.avgLatencyMs}ms</span>
          </div>
          <ScoreBar value={100 - (model.avgLatencyMs / 50)} color="bg-amber-400" />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-muted-foreground flex items-center gap-1"><DollarSign className="w-3 h-3" />التكلفة</span>
            <span className="text-foreground font-medium">${model.avgCostUsd.toFixed(3)}</span>
          </div>
          <ScoreBar value={100 - (model.avgCostUsd * 2000)} color="bg-purple-400" />
        </div>
      </div>

      <div>
        <p className="text-xs text-muted-foreground mb-1.5">موصى به لـ:</p>
        <div className="flex flex-wrap gap-1">
          {model.recommendedFor.map((task) => (
            <span key={task} className="text-xs bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded-full">
              {task}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ModelRoutingDashboard() {
  return (
    <div className="p-6 space-y-6" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">لوحة توجيه النماذج</h1>
          <p className="text-sm text-muted-foreground mt-1">Benchmark Harness داخلي — توجيه ذكي بناءً على الأداء الفعلي</p>
        </div>
        <div className="flex items-center gap-2 bg-secondary/40 border border-border px-3 py-2 rounded-xl text-xs text-muted-foreground">
          <Brain className="w-4 h-4 text-primary" />
          <span>سيادة المعايير الداخلية</span>
        </div>
      </div>

      {/* Routing Table */}
      <div className="bg-card/50 border border-border rounded-2xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="w-5 h-5 text-primary" />
          <h2 className="font-bold text-foreground">جدول التوجيه الذكي</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/50">
                <th className="pb-2 text-right text-xs text-muted-foreground font-medium">المهمة</th>
                <th className="pb-2 text-right text-xs text-muted-foreground font-medium">النموذج الموصى به</th>
                <th className="pb-2 text-right text-xs text-muted-foreground font-medium">السبب</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/30">
              {TASK_ROUTING.map((row) => (
                <tr key={row.task}>
                  <td className="py-2.5">
                    <span className="text-foreground font-medium">{row.task_ar}</span>
                    <span className="text-xs text-muted-foreground block">{row.task}</span>
                  </td>
                  <td className="py-2.5">
                    <span className="inline-flex items-center gap-1 bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded-full text-xs font-medium">
                      <Star className="w-3 h-3" />
                      {row.recommended}
                    </span>
                  </td>
                  <td className="py-2.5">
                    <span className="text-xs text-muted-foreground">أفضل أداء في الفئة</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Model Cards */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-5 h-5 text-primary" />
          <h2 className="font-bold text-foreground">أداء النماذج</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {MOCK_MODELS.map((m) => (
            <ModelCard key={m.name} model={m} />
          ))}
        </div>
      </div>

      {/* Benchmark note */}
      <div className="bg-primary/5 border border-primary/20 rounded-2xl p-4">
        <div className="flex items-start gap-3">
          <TrendingUp className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-bold text-foreground mb-1">قاعدة التوجيه السيادي</p>
            <p className="text-xs text-muted-foreground leading-relaxed">
              لا تختر أفضل نموذج مرة واحدة. الـ Benchmark Harness الداخلي يقيس latency وschema adherence وtool-call reliability وcontradiction rate وArabic memo quality وcost per successful task — وهنا تبدأ السيادة الفعلية بدلاً من الاعتماد على الانطباع.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
