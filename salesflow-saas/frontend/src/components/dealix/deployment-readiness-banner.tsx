"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle, Shield } from "lucide-react";
import { getApiBaseUrl } from "@/lib/api-base";

type Readiness = {
  score_percent: number;
  gaps_ar: string[];
  demo_mode: boolean;
  environment: string;
};

export function DeploymentReadinessBanner() {
  const [data, setData] = useState<Readiness | null>(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    const base = getApiBaseUrl();
    fetch(`${base}/api/v1/deployment-readiness`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setErr(true));
  }, []);

  if (err || !data) return null;
  const show = data.score_percent < 92 || (data.gaps_ar && data.gaps_ar.length > 0) || data.demo_mode;
  if (!show) return null;

  return (
    <div
      className="mb-6 rounded-2xl border border-amber-500/35 bg-gradient-to-br from-amber-950/50 to-slate-950/80 p-4 text-right shadow-lg shadow-amber-900/10"
      role="status"
      aria-live="polite"
    >
      <div className="flex flex-wrap items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/20 text-amber-300">
          <AlertTriangle className="h-5 w-5" aria-hidden />
        </div>
        <div className="min-w-0 flex-1 space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <Shield className="h-4 w-4 text-teal-400" aria-hidden />
            <span className="text-sm font-bold text-amber-100">جاهزية الخدمة الحقيقية</span>
            <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] font-semibold text-slate-300">
              {data.score_percent}%
            </span>
            {data.demo_mode && (
              <span className="rounded-full bg-teal-500/20 px-2 py-0.5 text-[10px] text-teal-300">
                وضع عرض / تجريبي
              </span>
            )}
          </div>
          <p className="text-xs leading-relaxed text-slate-400">
            الأرقام في لوحة القيادة أدناه قد تكون <strong className="text-slate-300">أمثلة واجهة</strong> حتى يُربط
            النظام ببياناتكم وبمفاتيح الإنتاج (ذكاء، واتساب، دفع، ليدات). راجع الفجوات وأغلقها للوصول لخدمة
            قوية للشركات.
          </p>
          {data.gaps_ar && data.gaps_ar.length > 0 && (
            <ul className="list-inside list-disc space-y-1 text-[11px] text-slate-500">
              {data.gaps_ar.slice(0, 5).map((g, i) => (
                <li key={i}>{g}</li>
              ))}
            </ul>
          )}
          <div className="flex flex-wrap gap-3 pt-1">
            <Link
              href="/help"
              className="text-xs font-semibold text-teal-400 underline-offset-2 hover:text-teal-300 hover:underline"
            >
              الدعم والأسئلة
            </Link>
            <Link
              href="/dealix-marketing/dashboard-guide"
              className="text-xs font-semibold text-teal-400 underline-offset-2 hover:text-teal-300 hover:underline"
            >
              دليل لوحة التحكم
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
