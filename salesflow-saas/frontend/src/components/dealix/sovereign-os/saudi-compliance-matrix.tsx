"use client";

import type { LucideIcon } from "lucide-react";


import {
  AlertTriangle,
  CheckCircle2,
  FileText,
  Shield,
  XCircle,
} from "lucide-react";

interface ComplianceControl {
  id: string;
  framework: "PDPL" | "NCA-ECC" | "NIST-AI-RMF" | "OWASP-LLM";
  control_ar: string;
  control_en: string;
  category: string;
  status: "compliant" | "partial" | "non_compliant" | "not_assessed";
  os_modules: string[];
  remediation_ar?: string;
}

const CONTROLS: ComplianceControl[] = [
  {
    id: "PDPL-1.1",
    framework: "PDPL",
    control_ar: "الحصول على موافقة صريحة قبل معالجة البيانات الشخصية",
    control_en: "Explicit consent before personal data processing",
    category: "consent",
    status: "compliant",
    os_modules: ["Sales OS", "Partnership OS"],
  },
  {
    id: "PDPL-2.3",
    framework: "PDPL",
    control_ar: "تحديد مدة الاحتفاظ بالبيانات وآلية الحذف",
    control_en: "Data retention period and deletion mechanism",
    category: "retention",
    status: "partial",
    os_modules: ["M&A OS", "PMI OS"],
    remediation_ar: "تعريف سياسة الاحتفاظ لملفات DD",
  },
  {
    id: "PDPL-4.1",
    framework: "PDPL",
    control_ar: "حق صاحب البيانات في الوصول والتصحيح والحذف",
    control_en: "Data subject rights: access, correction, deletion",
    category: "rights",
    status: "compliant",
    os_modules: ["Trust Plane"],
  },
  {
    id: "PDPL-6.2",
    framework: "PDPL",
    control_ar: "منع نقل البيانات خارج المملكة بدون ضمانات",
    control_en: "Cross-border data transfer restrictions",
    category: "transfer",
    status: "partial",
    os_modules: ["Data Plane", "Expansion OS"],
    remediation_ar: "إضافة geo-fencing للعقود والبيانات الحساسة",
  },
  {
    id: "NCA-ECC-2.1",
    framework: "NCA-ECC",
    control_ar: "تصنيف الأصول وترتيب الأولوية بناءً على الأهمية",
    control_en: "Asset classification and criticality prioritization",
    category: "asset_management",
    status: "compliant",
    os_modules: ["Operating Plane"],
  },
  {
    id: "NCA-ECC-3.4",
    framework: "NCA-ECC",
    control_ar: "سياسة التحكم في الوصول وإدارة الهويات",
    control_en: "Access control and identity management policy",
    category: "access_control",
    status: "compliant",
    os_modules: ["Trust Plane"],
  },
  {
    id: "NCA-ECC-5.1",
    framework: "NCA-ECC",
    control_ar: "خطة الاستمرارية والتعافي من الحوادث",
    control_en: "Business continuity and incident recovery plan",
    category: "continuity",
    status: "partial",
    os_modules: ["Execution Plane", "Operating Plane"],
    remediation_ar: "توثيق playbook التعافي لـ Temporal workflows",
  },
  {
    id: "NIST-AI-MAP-1.1",
    framework: "NIST-AI-RMF",
    control_ar: "تعريف سياق الذكاء الاصطناعي وحالات الاستخدام",
    control_en: "AI context and use case definition",
    category: "govern",
    status: "compliant",
    os_modules: ["Decision Plane"],
  },
  {
    id: "NIST-AI-MEASURE-2.2",
    framework: "NIST-AI-RMF",
    control_ar: "قياس انحياز النماذج وأداء المهام الحساسة",
    control_en: "Model bias measurement and sensitive task performance",
    category: "measure",
    status: "partial",
    os_modules: ["Decision Plane"],
    remediation_ar: "تفعيل مقاييس jailbreak resistance في Benchmark Harness",
  },
  {
    id: "OWASP-LLM-01",
    framework: "OWASP-LLM",
    control_ar: "الحماية من حقن التعليمات — Prompt Injection",
    control_en: "Prompt Injection protection",
    category: "security",
    status: "compliant",
    os_modules: ["Decision Plane"],
  },
  {
    id: "OWASP-LLM-06",
    framework: "OWASP-LLM",
    control_ar: "التحكم في مخرجات النموذج والتحقق من النتائج",
    control_en: "Sensitive information disclosure prevention",
    category: "security",
    status: "partial",
    os_modules: ["Trust Plane", "Data Plane"],
    remediation_ar: "إضافة output sanitization layer قبل العرض في Executive Room",
  },
  {
    id: "OWASP-LLM-08",
    framework: "OWASP-LLM",
    control_ar: "منع التوسع غير المتحكم في صلاحيات الوكيل",
    control_en: "Excessive agency prevention",
    category: "security",
    status: "compliant",
    os_modules: ["Execution Plane", "Trust Plane"],
  },
];

const frameworkColors: Record<string, string> = {
  PDPL: "bg-green-500/10 text-green-400 border-green-500/20",
  "NCA-ECC": "bg-blue-500/10 text-blue-400 border-blue-500/20",
  "NIST-AI-RMF": "bg-purple-500/10 text-purple-400 border-purple-500/20",
  "OWASP-LLM": "bg-orange-500/10 text-orange-400 border-orange-500/20",
};

const statusConfig: Record<string, { label: string; color: string; icon: LucideIcon }> = {
  compliant: { label: "ملتزم", color: "text-emerald-400", icon: CheckCircle2 },
  partial: { label: "جزئي", color: "text-amber-400", icon: AlertTriangle },
  non_compliant: { label: "غير ملتزم", color: "text-red-400", icon: XCircle },
  not_assessed: { label: "لم يُقيَّم", color: "text-muted-foreground", icon: FileText },
};

export function SaudiComplianceMatrix() {
  const compliant = CONTROLS.filter((c) => c.status === "compliant").length;
  const partial = CONTROLS.filter((c) => c.status === "partial").length;
  const non_compliant = CONTROLS.filter((c) => c.status === "non_compliant").length;
  const total = CONTROLS.length;
  const score = Math.round((compliant / total) * 100);

  const byFramework = CONTROLS.reduce((acc, c) => {
    acc[c.framework] = acc[c.framework] || [];
    acc[c.framework].push(c);
    return acc;
  }, {} as Record<string, ComplianceControl[]>);

  return (
    <div className="p-6 space-y-5" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">مصفوفة الامتثال السعودية</h1>
          <p className="text-sm text-muted-foreground mt-1">PDPL + NCA ECC + NIST AI RMF + OWASP LLM Top 10</p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-emerald-400">{score}٪</p>
          <p className="text-xs text-muted-foreground">درجة الامتثال الكلية</p>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4 text-center">
          <p className="text-2xl font-bold text-emerald-400">{compliant}</p>
          <p className="text-xs text-muted-foreground mt-1">ملتزم</p>
        </div>
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4 text-center">
          <p className="text-2xl font-bold text-amber-400">{partial}</p>
          <p className="text-xs text-muted-foreground mt-1">جزئي — يحتاج معالجة</p>
        </div>
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 text-center">
          <p className="text-2xl font-bold text-red-400">{non_compliant}</p>
          <p className="text-xs text-muted-foreground mt-1">غير ملتزم</p>
        </div>
      </div>

      {/* Controls by framework */}
      <div className="space-y-4">
        {Object.entries(byFramework).map(([framework, controls]) => (
          <div key={framework} className="bg-card/50 border border-border rounded-2xl p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                <h2 className="font-bold text-foreground">{framework}</h2>
                <span className={`text-xs px-2 py-0.5 rounded-full border ${frameworkColors[framework]}`}>
                  {controls.length} ضوابط
                </span>
              </div>
              <span className="text-sm font-bold text-foreground">
                {controls.filter((c) => c.status === "compliant").length}/{controls.length} ملتزم
              </span>
            </div>
            <div className="space-y-2">
              {controls.map((control) => {
                const cfg = statusConfig[control.status];
                const StatusIcon = cfg.icon;
                return (
                  <div key={control.id} className="flex items-start gap-3 p-3 bg-secondary/20 rounded-xl">
                    <StatusIcon className={`w-4 h-4 flex-shrink-0 mt-0.5 ${cfg.color}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <span className="text-xs text-muted-foreground font-mono">{control.id}</span>
                          <p className="text-sm text-foreground">{control.control_ar}</p>
                        </div>
                        <span className={`text-xs font-medium flex-shrink-0 ${cfg.color}`}>{cfg.label}</span>
                      </div>
                      {control.os_modules.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {control.os_modules.map((m) => (
                            <span key={m} className="text-xs bg-secondary/50 text-muted-foreground px-1.5 py-0.5 rounded">{m}</span>
                          ))}
                        </div>
                      )}
                      {control.remediation_ar && (
                        <p className="text-xs text-amber-400 mt-1.5">
                          <AlertTriangle className="w-3 h-3 inline ml-1" />
                          {control.remediation_ar}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
