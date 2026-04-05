"use client";

import { useState } from "react";
import Link from "next/link";
import {
  BarChart3,
  Users,
  Target,
  Zap,
  Bell,
  Search,
  BrainCircuit,
  Settings,
  BookOpen,
  MonitorPlay,
  FileSignature,
  ShieldCheck,
  Phone,
  Building2,
  DollarSign,
  Brain,
  LineChart,
  ClipboardList,
  Receipt,
  Layers,
  LogOut,
  Sparkles,
} from "lucide-react";

import { DashboardView } from "@/components/dealix/dashboard-view";
import { AffiliatesView } from "@/components/dealix/affiliates-view";
import { ChatbotView } from "@/components/dealix/chatbot-view";
import { PresentationsView } from "@/components/dealix/presentations-view";
import { ScriptsView } from "@/components/dealix/scripts-view";
import { AgreementsView } from "@/components/dealix/agreements-view";
import { GuaranteesView } from "@/components/dealix/guarantees-view";
import { OnboardingView } from "@/components/dealix/onboarding-view";
import { PropertiesView } from "@/components/dealix/properties-view";
import { RevenueView } from "@/components/dealix/revenue-view";
import { KnowledgeView } from "@/components/dealix/knowledge-view";
import { AnalyticsView } from "@/components/dealix/analytics-view";
import { BusinessImpactView } from "@/components/dealix/business-impact-view";
import { CustomerOnboardingJourneyView } from "@/components/dealix/customer-onboarding-journey-view";
import { IntelligenceDashboard } from "@/components/dealix/intelligence-dashboard";
import { LeadGeneratorView } from "@/components/dealix/lead-generator-view";
import { SalesOsView } from "@/components/dealix/sales-os-view";
import { FullOpsView } from "@/components/dealix/full-ops-view";

export type DealixDashboardMode = "live" | "preview";

type LiveProps = {
  mode: "live";
  userEmail: string;
  userRole: string;
  onLogout: () => void;
};

type PreviewProps = {
  mode: "preview";
};

export type DealixDashboardShellProps = LiveProps | PreviewProps;

const NAV_ITEMS = [
  { id: "overview", label: "لوحة القيادة والمراقبة", icon: BarChart3 },
  { id: "business-impact", label: "القيمة للشركات", icon: LineChart },
  { id: "customer-journey", label: "مسار التشغيل مع العميل", icon: ClipboardList },
  { id: "intelligence", label: "الذكاء المستقل — Manus", icon: BrainCircuit },
  { id: "leads", label: "توليد العملاء — AI", icon: Target },
  { id: "properties", label: "إدارة المخزون العقاري", icon: Building2 },
  { id: "affiliates", label: "المسوقين والموظفين", icon: Users },
  { id: "agents", label: "الوكلاء الأذكياء", icon: BrainCircuit },
  { id: "revenue", label: "المالية والتحصيل", icon: DollarSign },
  { id: "sales-os", label: "دفتر العمولة (Sales OS)", icon: Receipt },
  { id: "full-ops", label: "التشغيل الشامل (Full Ops)", icon: Layers },
  { id: "analytics", label: "التحليلات ونبض السوق", icon: BarChart3 },
  { id: "knowledge", label: "الذكاء والمعرفة", icon: Brain },
  { id: "presentations", label: "البرزنتيشنات القطاعية", icon: MonitorPlay },
  { id: "scripts", label: "سكربتات المبيعات", icon: Phone },
  { id: "agreements", label: "الاتفاقيات واHR", icon: FileSignature },
  { id: "guarantee", label: "الضمان الذهبي", icon: ShieldCheck },
  { id: "onboarding", label: "تأهيل المسوق", icon: BookOpen },
] as const;

export function DealixDashboardShell(props: DealixDashboardShellProps) {
  const [activeTab, setActiveTab] = useState("overview");
  const isPreview = props.mode === "preview";

  const renderContent = () => {
    switch (activeTab) {
      case "overview":
        return <DashboardView />;
      case "business-impact":
        return <BusinessImpactView />;
      case "customer-journey":
        return <CustomerOnboardingJourneyView />;
      case "intelligence":
        return <IntelligenceDashboard />;
      case "leads":
        return <LeadGeneratorView />;
      case "properties":
        return <PropertiesView />;
      case "affiliates":
        return <AffiliatesView />;
      case "agents":
        return <ChatbotView />;
      case "revenue":
        return <RevenueView />;
      case "sales-os":
        return <SalesOsView />;
      case "full-ops":
        return <FullOpsView />;
      case "analytics":
        return <AnalyticsView />;
      case "knowledge":
        return <KnowledgeView />;
      case "presentations":
        return <PresentationsView />;
      case "scripts":
        return <ScriptsView />;
      case "agreements":
        return <AgreementsView />;
      case "guarantee":
        return <GuaranteesView />;
      case "onboarding":
        return <OnboardingView />;
      default:
        return <DashboardView />;
    }
  };

  const displayEmail = isPreview ? "معاينة — بيانات نموذجية" : props.userEmail || "مستخدم";
  const displayRole = isPreview ? "جولة قبل الدفع" : props.userRole;
  const initials = isPreview ? "عر" : (props.userEmail || "?").slice(0, 2).toUpperCase();

  return (
    <div className="flex min-h-screen w-full">
      <aside className="hidden w-72 flex-col border-l border-border bg-card/50 backdrop-blur-xl lg:flex">
        <div className="flex h-20 items-center border-b border-border px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-primary to-accent shadow-lg shadow-primary/20">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <span className="bg-gradient-to-r from-white to-white/70 bg-clip-text text-xl font-bold tracking-tight text-transparent">
              Dealix OS
            </span>
          </div>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-4">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setActiveTab(item.id)}
              className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 transition-all duration-200 ${
                activeTab === item.id
                  ? "border border-primary/20 bg-primary/10 font-bold text-primary shadow-sm"
                  : "font-medium text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
              }`}
            >
              <item.icon className={`h-5 w-5 ${activeTab === item.id ? "text-primary" : "opacity-70"}`} />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="mt-auto border-t border-border/50 bg-secondary/10 p-4">
          {isPreview ? (
            <p className="px-2 text-center text-[11px] leading-relaxed text-muted-foreground">
              الإعدادات والربط الحقيقي للبيانات بعد إنشاء الحساب.
            </p>
          ) : (
            <button
              type="button"
              className="flex w-full items-center gap-3 rounded-xl px-4 py-3 font-medium text-muted-foreground transition-all hover:bg-secondary/50"
            >
              <Settings className="h-5 w-5" />
              <span>الإعدادات المتقدمة</span>
            </button>
          )}
        </div>
      </aside>

      <main className="flex h-screen flex-1 flex-col overflow-y-auto bg-background/50">
        {isPreview ? (
          <div className="sticky top-0 z-20 border-b border-teal-500/25 bg-gradient-to-l from-teal-950/95 to-slate-950/95 px-4 py-3 text-center backdrop-blur-md">
            <div className="mx-auto flex max-w-4xl flex-col items-center justify-center gap-2 sm:flex-row sm:gap-4">
              <p className="flex items-center justify-center gap-2 text-sm font-semibold text-teal-100">
                <Sparkles className="h-4 w-4 shrink-0 text-amber-300" aria-hidden />
                جولة تعريفية — استكشف التبويبات كما تظهر للشركات بعد التسجيل. البيانات هنا نموذجية ولا تُحفظ.
              </p>
              <div className="flex flex-wrap items-center justify-center gap-2">
                <Link
                  href="/register?next=%2Fdashboard"
                  className="rounded-full bg-teal-500 px-4 py-1.5 text-xs font-bold text-slate-950 shadow hover:bg-teal-400"
                >
                  إنشاء حساب
                </Link>
                <Link
                  href="/login?next=%2Fdashboard"
                  className="rounded-full border border-white/20 px-4 py-1.5 text-xs font-semibold text-white hover:bg-white/10"
                >
                  لدي حساب
                </Link>
              </div>
            </div>
          </div>
        ) : null}

        <header className="sticky top-0 z-10 flex h-20 items-center justify-between border-b border-border bg-card/50 px-4 backdrop-blur-md transition-all sm:px-8">
          <div className="relative max-w-md flex-1 lg:w-96">
            <Search className="absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              readOnly={isPreview}
              title={isPreview ? "بحث فعلي بعد تسجيل الدخول" : undefined}
              placeholder={
                isPreview
                  ? "بحث تجريبي — سجّل لربط عملائك وصفقاتك الحقيقية…"
                  : "البحث الشامل في Dealix (عميل، مسوق، صفقة)…"
              }
              className="w-full rounded-full border border-border bg-secondary/50 py-2.5 pl-4 pr-12 text-sm font-sans transition-all focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>

          <div className="flex items-center gap-3 sm:gap-6">
            <button
              type="button"
              className="relative p-2 text-muted-foreground transition-colors hover:text-foreground"
            >
              <Bell className="h-5 w-5" />
              <span className="absolute right-1.5 top-1.5 h-2.5 w-2.5 animate-pulse rounded-full border-2 border-background bg-primary" />
            </button>
            <div className="flex items-center gap-2 border-l border-border pl-3 sm:gap-3 sm:pl-4">
              {isPreview ? (
                <>
                  <Link
                    href="/register?next=%2Fdashboard"
                    className="hidden rounded-lg border border-primary/40 px-3 py-1.5 text-xs font-bold text-primary hover:bg-primary/10 sm:inline-block"
                  >
                    تسجيل
                  </Link>
                  <Link href="/login?next=%2Fdashboard" className="text-xs text-muted-foreground hover:text-foreground">
                    دخول
                  </Link>
                </>
              ) : (
                <button
                  type="button"
                  onClick={() => props.onLogout()}
                  className="hidden items-center gap-1.5 rounded-lg border border-border/60 px-2 py-1 text-xs text-muted-foreground hover:text-foreground sm:inline-flex"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  خروج
                </button>
              )}
              <div className="hidden text-left md:block">
                <p className="max-w-[200px] truncate text-sm font-bold">{displayEmail}</p>
                <p className="text-xs text-muted-foreground">{displayRole}</p>
              </div>
              <div className="rounded-full bg-gradient-to-tr from-blue-500 to-primary p-[2px]">
                <div className="flex h-full w-full items-center justify-center rounded-full border-2 border-background bg-card">
                  <span className="text-sm font-bold text-foreground">{initials}</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="mx-auto w-full max-w-[1600px] flex-1 pb-24 lg:pb-0">{renderContent()}</div>

        <nav className="fixed bottom-6 left-1/2 z-50 flex w-[90%] max-w-md -translate-x-1/2 items-center justify-around rounded-3xl border border-white/10 bg-card/80 px-4 py-4 shadow-2xl backdrop-blur-2xl lg:hidden">
          {[
            { id: "overview", icon: BarChart3 },
            { id: "agents", icon: BrainCircuit },
            { id: "presentations", icon: MonitorPlay },
            { id: "scripts", icon: Phone },
          ].map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setActiveTab(item.id)}
              className={`flex flex-col items-center gap-1 transition-all ${
                activeTab === item.id ? "scale-110 text-primary" : "text-muted-foreground opacity-60"
              }`}
            >
              <item.icon className="h-6 w-6" />
              {activeTab === item.id ? <span className="h-1 w-1 rounded-full bg-primary" /> : null}
            </button>
          ))}
        </nav>
      </main>
    </div>
  );
}
