"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";
import {
  ChevronDown,
  Crown,
  Shield,
  TrendingUp,
  Handshake,
  Building,
  Globe2,
  Layers,
  Database,
  Rocket,
} from "lucide-react";

const sovereignNav = [
  {
    group: "القيادة والحوكمة",
    groupEn: "Executive & Governance",
    icon: Crown,
    items: [
      { href: "/dashboard/sovereign/executive-room", label: "غرفة القيادة", labelEn: "Executive Room" },
      { href: "/dashboard/sovereign/approval-center", label: "مركز الاعتماد", labelEn: "Approval Center" },
      { href: "/dashboard/sovereign/evidence-packs", label: "حزم الأدلة", labelEn: "Evidence Packs" },
      { href: "/dashboard/sovereign/risk-board", label: "لوحة المخاطر", labelEn: "Risk Board" },
      { href: "/dashboard/sovereign/policy-violations", label: "انتهاكات السياسات", labelEn: "Policy Violations" },
      { href: "/dashboard/sovereign/actual-vs-forecast", label: "الفعلي مقابل المتوقع", labelEn: "Actual vs Forecast" },
    ],
  },
  {
    group: "الإيرادات",
    groupEn: "Revenue",
    icon: TrendingUp,
    items: [
      { href: "/dashboard/sovereign/revenue-funnel", label: "مركز قمع الإيرادات", labelEn: "Revenue Funnel" },
    ],
  },
  {
    group: "الشراكات",
    groupEn: "Partnerships",
    icon: Handshake,
    items: [
      { href: "/dashboard/sovereign/partner-room", label: "غرفة الشراكات", labelEn: "Partner Room" },
      { href: "/dashboard/sovereign/partnership-scorecards", label: "بطاقات أداء الشراكات", labelEn: "Partnership Scorecards" },
    ],
  },
  {
    group: "الاستحواذ",
    groupEn: "M&A",
    icon: Building,
    items: [
      { href: "/dashboard/sovereign/dd-room", label: "غرفة العناية الواجبة", labelEn: "DD Room" },
      { href: "/dashboard/sovereign/ma-pipeline", label: "خط أنابيب الاستحواذ", labelEn: "M&A Pipeline" },
    ],
  },
  {
    group: "التوسع",
    groupEn: "Expansion",
    icon: Globe2,
    items: [
      { href: "/dashboard/sovereign/expansion-console", label: "وحدة التحكم بالتوسع", labelEn: "Expansion Console" },
    ],
  },
  {
    group: "التكامل والمشاريع",
    groupEn: "PMI/PMO",
    icon: Layers,
    items: [
      { href: "/dashboard/sovereign/pmi-engine", label: "محرك 30/60/90", labelEn: "PMI 30/60/90 Engine" },
    ],
  },
  {
    group: "الثقة والبيانات",
    groupEn: "Trust & Data",
    icon: Database,
    items: [
      { href: "/dashboard/sovereign/tool-ledger", label: "سجل التحقق من الأدوات", labelEn: "Tool Verification Ledger" },
      { href: "/dashboard/sovereign/connector-health", label: "صحة الموصلات", labelEn: "Connector Health" },
      { href: "/dashboard/sovereign/compliance-matrix", label: "مصفوفة الامتثال السعودي", labelEn: "Saudi Compliance Matrix" },
      { href: "/dashboard/sovereign/model-routing", label: "لوحة توجيه النماذج", labelEn: "Model Routing Dashboard" },
    ],
  },
  {
    group: "التشغيل",
    groupEn: "Operations",
    icon: Rocket,
    items: [
      { href: "/dashboard/sovereign/release-gates", label: "بوابات الإصدار", labelEn: "Release Gates" },
    ],
  },
];

export default function SovereignLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  const toggleGroup = (group: string) => {
    setCollapsed((prev) => ({ ...prev, [group]: !prev[group] }));
  };

  const isGroupActive = (items: { href: string }[]) =>
    items.some((item) => pathname === item.href);

  return (
    <div className="flex min-h-screen">
      <aside className="w-72 hidden lg:flex flex-col border-l border-border bg-card/60 backdrop-blur-xl shrink-0">
        <div className="h-16 flex items-center gap-3 px-6 border-b border-border">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-emerald-700 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-sm font-bold">Sovereign OS</h2>
            <p className="text-[10px] text-muted-foreground">نظام النمو السيادي</p>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {sovereignNav.map((section) => {
            const isOpen = !collapsed[section.group] || isGroupActive(section.items);
            const GroupIcon = section.icon;

            return (
              <div key={section.group}>
                <button
                  type="button"
                  onClick={() => toggleGroup(section.group)}
                  className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-xs font-bold transition-colors ${
                    isGroupActive(section.items)
                      ? "text-primary"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <GroupIcon className="w-4 h-4 shrink-0" />
                  <span className="flex-1 text-right">{section.group}</span>
                  <ChevronDown
                    className={`w-3.5 h-3.5 transition-transform duration-200 ${
                      isOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>

                {isOpen && (
                  <div className="mr-4 border-r border-border/50 space-y-0.5 pr-2 mb-2">
                    {section.items.map((item) => {
                      const isActive = pathname === item.href;
                      return (
                        <Link
                          key={item.href}
                          href={item.href}
                          className={`block px-3 py-2 rounded-lg text-xs transition-all ${
                            isActive
                              ? "bg-primary/10 text-primary font-bold border border-primary/20"
                              : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
                          }`}
                        >
                          <span className="block">{item.label}</span>
                          <span className="block text-[10px] opacity-60 mt-0.5">{item.labelEn}</span>
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </nav>

        <div className="p-3 border-t border-border/50">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-xs text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors"
          >
            <span>→</span>
            <span>العودة للوحة الرئيسية</span>
            <span className="text-[10px] opacity-60 mr-auto">Back to Dashboard</span>
          </Link>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto bg-background/50">{children}</main>
    </div>
  );
}
