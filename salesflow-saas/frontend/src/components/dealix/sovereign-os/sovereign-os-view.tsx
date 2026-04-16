"use client";

import type { LucideIcon } from "lucide-react";


import { useState } from "react";
import {
  Activity,
  BarChart3,
  Brain,
  Building2,
  CheckCircle2,
  Crown,
  Database,
  FileText,
  GitBranch,
  Globe,
  Layers,
  Network,
  Shield,
  ShieldCheck,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";

import { ExecutiveRoom } from "./executive-room";
import { ApprovalCenter } from "./approval-center";
import { MAPipeline } from "./ma-pipeline";
import { PartnerRoom } from "./partner-room";
import { ModelRoutingDashboard } from "./model-routing-dashboard";
import { SaudiComplianceMatrix } from "./saudi-compliance-matrix";
import { ExecutionPlaneView } from "./execution-plane-view";

type NavId =
  | "executive-room"
  | "approval-center"
  | "ma-pipeline"
  | "partner-room"
  | "execution-plane"
  | "model-routing"
  | "compliance-matrix";

interface NavItem {
  id: NavId;
  label: string;
  icon: LucideIcon;
  badge?: string;
  badgeColor?: string;
  plane: string;
}

const NAV: NavItem[] = [
  { id: "executive-room", label: "غرفة القيادة التنفيذية", icon: Crown, plane: "Executive OS" },
  { id: "approval-center", label: "مركز الاعتماد", icon: CheckCircle2, badge: "٧", badgeColor: "bg-amber-500", plane: "Trust Plane" },
  { id: "execution-plane", label: "العمليات الدائمة", icon: Activity, badge: "٣", badgeColor: "bg-blue-500", plane: "Execution Plane" },
  { id: "ma-pipeline", label: "لوحة الاستحواذ M&A", icon: GitBranch, plane: "M&A OS" },
  { id: "partner-room", label: "غرفة الشراكات", icon: Users, plane: "Partnership OS" },
  { id: "model-routing", label: "توجيه النماذج", icon: Brain, plane: "Decision Plane" },
  { id: "compliance-matrix", label: "مصفوفة الامتثال", icon: ShieldCheck, badge: "٣", badgeColor: "bg-amber-500", plane: "Saudi Compliance" },
];

const PLANE_SUMMARY = [
  {
    name: "Decision Plane",
    name_ar: "طبقة القرار",
    desc: "Responses API + Structured Outputs + MCP + Guardrails",
    icon: Brain,
    color: "text-primary",
    bg: "bg-primary/10 border-primary/20",
    status: "active",
  },
  {
    name: "Execution Plane",
    name_ar: "طبقة التنفيذ",
    desc: "LangGraph + Durable Workflows + HITL Interrupts",
    icon: Activity,
    color: "text-blue-400",
    bg: "bg-blue-500/10 border-blue-500/20",
    status: "active",
  },
  {
    name: "Trust Plane",
    name_ar: "طبقة الثقة",
    desc: "OPA Policies + OpenFGA + Vault + Approval Classes",
    icon: Shield,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10 border-emerald-500/20",
    status: "active",
  },
  {
    name: "Data Plane",
    name_ar: "طبقة البيانات",
    desc: "CloudEvents + pgvector + Great Expectations + OTel",
    icon: Database,
    color: "text-amber-400",
    bg: "bg-amber-500/10 border-amber-500/20",
    status: "active",
  },
  {
    name: "Operating Plane",
    name_ar: "طبقة التشغيل",
    desc: "Release Gates + OIDC + Provenance + Audit Stream",
    icon: Layers,
    color: "text-purple-400",
    bg: "bg-purple-500/10 border-purple-500/20",
    status: "active",
  },
];

const OS_MODULES = [
  { label: "Sales & Revenue OS", icon: BarChart3, color: "text-emerald-400" },
  { label: "Partnership OS", icon: Users, color: "text-blue-400" },
  { label: "M&A / Corporate Dev OS", icon: Building2, color: "text-purple-400" },
  { label: "Expansion OS", icon: Globe, color: "text-orange-400" },
  { label: "PMI / Strategic PMO OS", icon: Network, color: "text-pink-400" },
  { label: "Executive / Board OS", icon: Crown, color: "text-amber-400" },
];

function PlaneCard({ plane }: { plane: typeof PLANE_SUMMARY[0] }) {
  return (
    <div className={`rounded-2xl border p-4 ${plane.bg}`}>
      <div className="flex items-center gap-2 mb-2">
        <plane.icon className={`w-5 h-5 ${plane.color}`} />
        <div>
          <p className="text-sm font-bold text-foreground">{plane.name_ar}</p>
          <p className="text-xs text-muted-foreground">{plane.name}</p>
        </div>
        <span className="mr-auto text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full">
          نشط
        </span>
      </div>
      <p className="text-xs text-muted-foreground leading-relaxed">{plane.desc}</p>
    </div>
  );
}

export function SovereignOSView() {
  const [activeNav, setActiveNav] = useState<NavId>("executive-room");
  const [showOverview, setShowOverview] = useState(false);

  const renderContent = () => {
    switch (activeNav) {
      case "executive-room": return <ExecutiveRoom />;
      case "approval-center": return <ApprovalCenter />;
      case "execution-plane": return <ExecutionPlaneView />;
      case "ma-pipeline": return <MAPipeline />;
      case "partner-room": return <PartnerRoom />;
      case "model-routing": return <ModelRoutingDashboard />;
      case "compliance-matrix": return <SaudiComplianceMatrix />;
      default: return <ExecutiveRoom />;
    }
  };

  return (
    <div className="flex h-full" dir="rtl">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 border-l border-border bg-card/30 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-accent flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-foreground">Sovereign OS</p>
              <p className="text-xs text-muted-foreground">نظام التشغيل المؤسسي</p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setShowOverview(!showOverview)}
            className="mt-3 w-full text-xs text-primary hover:underline text-right"
          >
            {showOverview ? "إخفاء نظرة عامة" : "عرض نظرة عامة"}
          </button>
        </div>

        {/* Overview panel */}
        {showOverview && (
          <div className="p-3 border-b border-border space-y-2">
            {PLANE_SUMMARY.map((p) => (
              <div key={p.name} className={`rounded-xl border p-2.5 ${p.bg}`}>
                <div className="flex items-center gap-1.5">
                  <p.icon className={`w-3.5 h-3.5 ${p.color}`} />
                  <p className="text-xs font-medium text-foreground">{p.name_ar}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {NAV.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setActiveNav(item.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition-all text-right ${
                activeNav === item.id
                  ? "bg-primary/10 text-primary border border-primary/20"
                  : "text-muted-foreground hover:bg-secondary/40 hover:text-foreground"
              }`}
            >
              <item.icon className={`w-4 h-4 flex-shrink-0 ${activeNav === item.id ? "text-primary" : "opacity-60"}`} />
              <span className="text-sm font-medium flex-1">{item.label}</span>
              {item.badge && (
                <span className={`text-white text-xs font-bold px-1.5 py-0.5 rounded-full ${item.badgeColor || "bg-primary"}`}>
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </nav>

        {/* OS Modules quick ref */}
        <div className="p-3 border-t border-border">
          <p className="text-xs text-muted-foreground mb-2">وحدات OS</p>
          <div className="space-y-1">
            {OS_MODULES.map((m) => (
              <div key={m.label} className="flex items-center gap-2 text-xs text-muted-foreground">
                <m.icon className={`w-3 h-3 ${m.color}`} />
                <span>{m.label}</span>
              </div>
            ))}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {renderContent()}
      </main>
    </div>
  );
}
