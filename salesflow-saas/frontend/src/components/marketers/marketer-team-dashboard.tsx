"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  ChevronRight,
  Copy,
  GitBranch,
  MessageCircle,
  Network,
  Plus,
  Sparkles,
  Users,
} from "lucide-react";
import {
  type TeamMember,
  getOrCreateInviteCode,
  getParentRef,
  loadTeamState,
  saveTeamState,
} from "@/lib/marketer-team";

const MAX_TEAM = 10;

const trainingLinks = [
  {
    title: "قوالب واتساب",
    href: "/dealix-marketing/marketers/whatsapp-playbook-ar.txt",
    desc: "جاهزة للنسخ — عدّل الاسم والرابط",
  },
  {
    title: "قائمة تحقق الدخول",
    href: "/dealix-marketing/marketers/entry-checklist-ar.txt",
    desc: "قبل أول عميل",
  },
  {
    title: "أسئلة وإجابات + ترسانة تسويقية",
    href: "/dealix-marketing/arsenal",
    desc: "عمولات، مواد، هيكل",
  },
  {
    title: "العروض القطاعية",
    href: "/dealix-presentations/00-dealix-company-master-ar.html",
    desc: "10 قطاعات + ملف الشركة",
  },
  {
    title: "دليل لوحة التحكم",
    href: "/dealix-marketing/dashboard-guide",
    desc: "ميزات الداشبورد ولماذا يُعتبر أقوى أداة",
  },
];

function mockDeals(members: TeamMember[]) {
  const base = [
    { title: "تأهيل عميل — قطاع لوجستي", volume: 48000, status: "مؤهّل" as const },
    { title: "تجديد اشتراك سنوي", volume: 120000, status: "مغلق" as const },
    { title: "عرض قطاع تجزئة", volume: 22000, status: "متابعة" as const },
  ];
  const rows: {
    title: string;
    volume: number;
    status: string;
    tier: "مدير" | "تابع";
    name: string;
  }[] = [];
  rows.push(
    ...base.map((d) => ({
      ...d,
      tier: "مدير" as const,
      name: "صفقاتك المباشرة",
    }))
  );
  members.slice(0, 5).forEach((m, i) => {
    rows.push({
      title: `إحالة من ${m.name}`,
      volume: 15000 + i * 7000,
      status: i % 2 === 0 ? "مؤهّل" : "متابعة",
      tier: "تابع",
      name: m.name,
    });
  });
  return rows;
}

export function MarketerTeamDashboard() {
  const [invite, setInvite] = useState("");
  const [parent, setParent] = useState<string | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setInvite(getOrCreateInviteCode());
    setParent(getParentRef());
    setMembers(loadTeamState().members);
  }, []);

  const registerHref = useMemo(() => {
    if (typeof window === "undefined") return "/register";
    const next = encodeURIComponent("/marketers/team");
    const ref = invite ? `&ref=${encodeURIComponent(invite)}` : "";
    return `/register?next=${next}${ref}`;
  }, [invite]);

  const copyLink = useCallback(() => {
    if (!invite || typeof window === "undefined") return;
    const url = `${window.location.origin}${registerHref}`;
    void navigator.clipboard.writeText(url).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [invite, registerHref]);

  const addSimulatedMember = useCallback(() => {
    if (members.length >= MAX_TEAM) return;
    const n = members.length + 1;
    const m: TeamMember = {
      id: `sim-${Date.now()}`,
      name: `مسوّق تجريبي ${n}`,
      joinedAt: new Date().toISOString(),
      source: "simulated",
    };
    const next = [...members, m];
    setMembers(next);
    saveTeamState({ members: next });
  }, [members]);

  const deals = useMemo(() => mockDeals(members), [members]);

  return (
    <div className="space-y-10">
      {parent && (
        <div className="rounded-2xl border border-teal-500/35 bg-teal-950/50 px-4 py-3 text-sm text-teal-100">
          مسجّل تحت رمز المدير:{" "}
          <strong className="font-mono text-white">{parent}</strong> — صفقاتك تُحسب ضمن فريقه عند
          ربط الخادم.
        </div>
      )}

      <section className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/[0.07] to-transparent p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-bold text-white">
              <Network className="h-5 w-5 text-teal-400" aria-hidden />
              أنت مدير فريق التسويق
            </h2>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-slate-400">
              شارك رابط التسجيل أدناه. كل من يُسجّل عبره يُسجَّل تحت رمزك (معاينة محلية). الهدف: حتى
              10 مسوّقين تحتك — والصفقات التي يجلبونها تظهر في جدول الفريق بشكل هرمي عند ربط المنصة.
            </p>
          </div>
          <div className="rounded-xl border border-teal-500/30 bg-black/40 px-4 py-3 text-center md:text-right">
            <p className="text-xs font-semibold uppercase tracking-wider text-teal-300/90">
              رمز دعوتك
            </p>
            <p className="mt-1 font-mono text-2xl font-black tracking-widest text-white">{invite}</p>
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            type="button"
            onClick={copyLink}
            className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-teal-500 px-4 py-3 text-sm font-bold text-slate-950 transition hover:bg-teal-400"
          >
            <Copy className="h-4 w-4" aria-hidden />
            {copied ? "تم النسخ" : "نسخ رابط التسجيل للفريق"}
          </button>
          <code className="block truncate rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-left text-xs text-slate-400 sm:max-w-md">
            {typeof window !== "undefined" ? `${window.location.origin}${registerHref}` : registerHref}
          </code>
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 bg-white/5 p-6">
        <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="flex items-center gap-2 text-lg font-bold text-white">
            <Users className="h-5 w-5 text-teal-400" aria-hidden />
            المسوّقون تحتك ({members.length}/{MAX_TEAM})
          </h2>
          <button
            type="button"
            onClick={addSimulatedMember}
            disabled={members.length >= MAX_TEAM}
            className="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Plus className="h-4 w-4" aria-hidden />
            إضافة مسوّق (محاكاة)
          </button>
        </div>

        {members.length === 0 ? (
          <p className="text-sm text-slate-500">
            لا يوجد تابعون بعد — شارك الرابط أو أضف صفاً تجريبياً لمعاينة الشجرة.
          </p>
        ) : (
          <ul className="space-y-2">
            {members.map((m, idx) => (
              <li
                key={m.id}
                className="flex items-center gap-3 rounded-xl border border-white/5 bg-black/20 px-4 py-3"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-500/20 text-xs font-bold text-teal-200">
                  {idx + 1}
                </span>
                <div className="min-w-0 flex-1 text-right">
                  <p className="font-semibold text-white">{m.name}</p>
                  <p className="text-xs text-slate-500">
                    {m.source === "simulated" ? "محاكاة" : "تسجيل"} —{" "}
                    {new Date(m.joinedAt).toLocaleDateString("ar-SA")}
                  </p>
                </div>
                <ChevronRight className="h-4 w-4 shrink-0 rotate-180 text-slate-600" aria-hidden />
              </li>
            ))}
          </ul>
        )}

        <div className="mt-6 flex items-start gap-2 rounded-xl border border-dashed border-white/15 p-4 text-xs text-slate-500">
          <GitBranch className="mt-0.5 h-4 w-4 shrink-0 text-teal-500/70" aria-hidden />
          <span>
            مع الخادم: الدعوة تُصدَّق آلياً، ويُربط كل تابع بمديره، وتُوزَّع العمولات حسب السياسة
            المعتمدة في العقد.
          </span>
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
          <Sparkles className="h-5 w-5 text-teal-400" aria-hidden />
          صفقات الفريق (عرض هرمي)
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[520px] text-right text-sm">
            <thead>
              <tr className="border-b border-white/10 text-xs text-slate-500">
                <th className="pb-3 font-medium">الصفقة</th>
                <th className="pb-3 font-medium">الحجم (ر.س)</th>
                <th className="pb-3 font-medium">الطبقة</th>
                <th className="pb-3 font-medium">الجهة</th>
                <th className="pb-3 font-medium">الحالة</th>
              </tr>
            </thead>
            <tbody>
              {deals.map((d, i) => (
                <tr key={i} className="border-b border-white/5 text-slate-300">
                  <td className="py-3 font-medium text-white">{d.title}</td>
                  <td className="py-3 font-mono tabular-nums">{d.volume.toLocaleString("ar-SA")}</td>
                  <td className="py-3">
                    <span
                      className={
                        d.tier === "مدير"
                          ? "rounded-full bg-teal-500/20 px-2 py-0.5 text-xs text-teal-200"
                          : "rounded-full bg-slate-500/20 px-2 py-0.5 text-xs text-slate-300"
                      }
                    >
                      {d.tier}
                    </span>
                  </td>
                  <td className="py-3 text-xs">{d.name}</td>
                  <td className="py-3 text-xs">{d.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-2xl border border-teal-500/20 bg-teal-950/30 p-6">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-teal-100">
          <BookOpen className="h-5 w-5" aria-hidden />
          تعليمات، أسئلة، ومواد جاهزة
        </h2>
        <ul className="grid gap-3 sm:grid-cols-2">
          {trainingLinks.map((t) => (
            <li key={t.href}>
              <a
                href={t.href}
                className="flex flex-col rounded-xl border border-white/10 bg-black/20 p-4 transition hover:border-teal-500/40 hover:bg-black/30"
              >
                <span className="font-semibold text-white">{t.title}</span>
                <span className="mt-1 text-xs text-slate-400">{t.desc}</span>
              </a>
            </li>
          ))}
        </ul>
        <div className="mt-4 flex flex-wrap gap-3 text-sm">
          <Link href="/marketers" className="text-teal-400 hover:text-teal-300">
            ← كل روابط البوابة
          </Link>
          <Link href="/resources" className="text-teal-400 hover:text-teal-300">
            مركز الموارد
          </Link>
        </div>
      </section>

      <p className="text-center text-xs text-slate-600">
        <MessageCircle className="inline h-3.5 w-3.5 align-text-bottom text-slate-500" aria-hidden />{" "}
        للأسئلة التشغيلية، راجع الملفات أعلاه ثم نسّق مع فريق Dealix قبل وعود للعملاء النهائيين.
      </p>
    </div>
  );
}
