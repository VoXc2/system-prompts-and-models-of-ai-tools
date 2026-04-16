"use client";

import { Shield, CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react";

const frameworks = [
  {
    id: "PDPL",
    name: "نظام حماية البيانات الشخصية",
    controls: [
      { id: "PDPL-1", name: "التحكم في الموافقة", status: "compliant" },
      { id: "PDPL-2", name: "حقوق صاحب البيانات", status: "compliant" },
      { id: "PDPL-3", name: "تتبع المعالجة", status: "compliant" },
      { id: "PDPL-4", name: "نقل البيانات عبر الحدود", status: "partial" },
      { id: "PDPL-5", name: "إشعار الاختراق", status: "compliant" },
    ],
  },
  {
    id: "NCA_ECC",
    name: "ضوابط الأمن السيبراني الأساسية",
    controls: [
      { id: "ECC-1", name: "حوكمة الأمن السيبراني", status: "compliant" },
      { id: "ECC-2", name: "إدارة الأصول", status: "partial" },
      { id: "ECC-3", name: "التحكم بالوصول", status: "compliant" },
      { id: "ECC-4", name: "التشفير", status: "compliant" },
      { id: "ECC-5", name: "إدارة الثغرات", status: "partial" },
    ],
  },
  {
    id: "NIST_AI_RMF",
    name: "إطار إدارة مخاطر الذكاء الاصطناعي",
    controls: [
      { id: "AI-GOV-1", name: "حوكمة AI", status: "compliant" },
      { id: "AI-MAP-1", name: "تصنيف المخاطر", status: "partial" },
      { id: "AI-MEAS-1", name: "قياس وتقييم", status: "not_assessed" },
      { id: "AI-MAN-1", name: "إدارة المخاطر", status: "partial" },
    ],
  },
  {
    id: "OWASP_LLM",
    name: "OWASP Top 10 لتطبيقات LLM",
    controls: [
      { id: "LLM-01", name: "حقن الأوامر", status: "compliant" },
      { id: "LLM-02", name: "معالجة المخرجات", status: "compliant" },
      { id: "LLM-03", name: "تسميم بيانات التدريب", status: "not_applicable" },
      { id: "LLM-06", name: "كشف المعلومات الحساسة", status: "partial" },
      { id: "LLM-08", name: "صلاحيات مفرطة للوكلاء", status: "compliant" },
    ],
  },
];

const statusConfig: Record<string, { icon: typeof CheckCircle2; color: string; label: string }> = {
  compliant: { icon: CheckCircle2, color: "text-emerald-500", label: "متوافق" },
  partial: { icon: AlertTriangle, color: "text-amber-500", label: "جزئي" },
  non_compliant: { icon: XCircle, color: "text-red-500", label: "غير متوافق" },
  not_assessed: { icon: Clock, color: "text-gray-400", label: "لم يقيّم" },
  not_applicable: { icon: Shield, color: "text-blue-400", label: "لا ينطبق" },
};

export function ComplianceMatrixView() {
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-right">
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-1">مصفوفة الامتثال السعودية</h1>
        <p className="text-sm text-muted-foreground">PDPL • NCA ECC 2-2024 • NIST AI RMF • OWASP LLM Top 10</p>
      </div>

      {frameworks.map((fw) => {
        const compliantCount = fw.controls.filter((c) => c.status === "compliant").length;
        return (
          <div key={fw.id} className="glass-card overflow-hidden">
            <div className="p-4 border-b border-border/50 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Shield className="w-5 h-5 text-primary" />
                <div>
                  <h2 className="text-base font-bold">{fw.name}</h2>
                  <p className="text-xs text-muted-foreground">{fw.id}</p>
                </div>
              </div>
              <span className="text-xs font-bold bg-primary/10 text-primary px-3 py-1 rounded-full">
                {compliantCount}/{fw.controls.length} متوافق
              </span>
            </div>
            <div className="divide-y divide-border/20">
              {fw.controls.map((c) => {
                const cfg = statusConfig[c.status] || statusConfig.not_assessed;
                return (
                  <div key={c.id} className="flex items-center justify-between p-3 hover:bg-secondary/20 transition-colors">
                    <div className="flex items-center gap-3">
                      <cfg.icon className={`w-4 h-4 ${cfg.color}`} />
                      <span className="text-sm">{c.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">{c.id}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                        c.status === "compliant" ? "bg-emerald-500/20 text-emerald-400" :
                        c.status === "partial" ? "bg-amber-500/20 text-amber-400" :
                        c.status === "non_compliant" ? "bg-red-500/20 text-red-400" :
                        "bg-gray-500/20 text-gray-400"
                      }`}>
                        {cfg.label}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
