"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CheckCircle2,
  Circle,
  Link2,
  Loader2,
  RefreshCw,
  Rocket,
  Sparkles,
  Trash2,
  Users,
} from "lucide-react";
import { getApiBaseUrl } from "@/lib/api-base";
import {
  loadMarketerOsState,
  patchMarketerOsState,
  clearMarketerOsState,
  type MarketerOsState,
} from "@/lib/marketer-os-storage";
import { MARKETER_PROFILE_STORAGE_KEY } from "@/components/marketers/marketer-account-form";
import { loadTeamState, getOrCreateInviteCode } from "@/lib/marketer-team";

type AffiliateResponse = {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  status: string;
  referral_code: string;
  total_deals_closed: number;
  total_commission_earned: number;
  current_month_deals: number;
};

type ProfileDraft = {
  fullName: string;
  email: string;
  phone: string;
  city: string;
  nationalId: string;
};

function readLocalProfile(): ProfileDraft {
  if (typeof window === "undefined") {
    return { fullName: "", email: "", phone: "", city: "", nationalId: "" };
  }
  try {
    const raw = localStorage.getItem(MARKETER_PROFILE_STORAGE_KEY);
    if (!raw) return { fullName: "", email: "", phone: "", city: "", nationalId: "" };
    const p = JSON.parse(raw) as Record<string, string>;
    return {
      fullName: p.fullName || "",
      email: p.email || "",
      phone: p.phone || "",
      city: "",
      nationalId: p.nationalId || "",
    };
  } catch {
    return { fullName: "", email: "", phone: "", city: "", nationalId: "" };
  }
}

function profileLooksComplete(p: ProfileDraft): boolean {
  return Boolean(p.fullName.trim() && p.email.trim() && p.phone.trim());
}

export function MarketerOsPanel() {
  const [os, setOs] = useState<MarketerOsState>(() => loadMarketerOsState());
  const [draft, setDraft] = useState<ProfileDraft>(readLocalProfile);
  const [dealCompany, setDealCompany] = useState("شركة نموذجية للتجارة");
  const [dealPlan, setDealPlan] = useState<"basic" | "professional" | "enterprise">("basic");
  const [busy, setBusy] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [teamCount, setTeamCount] = useState(0);
  const [inviteCode, setInviteCode] = useState("");

  const hydrate = useCallback(() => {
    const prof = readLocalProfile();
    const base = loadMarketerOsState();
    setDraft(prof);
    setTeamCount(loadTeamState().members.length);
    setInviteCode(getOrCreateInviteCode());
    const profileSaved = profileLooksComplete(prof) || base.steps.profileSaved;
    const next = patchMarketerOsState({
      steps: { ...base.steps, profileSaved },
    });
    setOs(next);
  }, []);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    const onProfile = () => hydrate();
    window.addEventListener("dealix-marketer-profile-saved", onProfile);
    return () => window.removeEventListener("dealix-marketer-profile-saved", onProfile);
  }, [hydrate]);

  const api = useMemo(() => getApiBaseUrl(), []);

  const applyAffiliatePayload = useCallback((a: AffiliateResponse) => {
    setOs(
      patchMarketerOsState({
        affiliateId: a.id,
        referralCode: a.referral_code,
        email: a.email,
        status: a.status,
        totalDealsClosed: a.total_deals_closed,
        totalCommissionEarned: a.total_commission_earned,
        currentMonthDeals: a.current_month_deals,
        lastSyncedAt: new Date().toISOString(),
        steps: {
          registered: true,
          profileSaved: profileLooksComplete(readLocalProfile()),
          activated: a.status === "active" || a.status === "employed",
          firstDeal: a.total_deals_closed > 0,
        },
      })
    );
  }, []);

  const refreshFromServer = useCallback(async () => {
    const st = loadMarketerOsState();
    if (!st.affiliateId) {
      setErr("لا يوجد معرّف شريك محفوظ — سجّل أولاً.");
      return;
    }
    setBusy("refresh");
    setErr(null);
    try {
      const r = await fetch(`${api}/api/v1/affiliates/${st.affiliateId}`);
      if (!r.ok) {
        const t = await r.text();
        throw new Error(t || `HTTP ${r.status}`);
      }
      const a = (await r.json()) as AffiliateResponse;
      applyAffiliatePayload(a);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "تعذر المزامنة");
    } finally {
      setBusy(null);
    }
  }, [api, applyAffiliatePayload]);

  useEffect(() => {
    const st = loadMarketerOsState();
    if (!st.affiliateId) return;
    let cancelled = false;
    void (async () => {
      try {
        const r = await fetch(`${getApiBaseUrl()}/api/v1/affiliates/${st.affiliateId}`);
        if (!r.ok || cancelled) return;
        const a = (await r.json()) as AffiliateResponse;
        if (!cancelled) applyAffiliatePayload(a);
      } catch {
        /* offline / CI */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [applyAffiliatePayload]);

  const register = async () => {
    setBusy("register");
    setErr(null);
    try {
      const body = {
        full_name: draft.fullName.trim() || "مسوّق Dealix",
        full_name_ar: draft.fullName.trim() || undefined,
        email: draft.email.trim(),
        phone: draft.phone.trim() || "0500000000",
        city: draft.city.trim() || undefined,
        national_id: draft.nationalId.trim() || undefined,
      };
      if (!body.email) {
        setErr("أدخل بريداً صالحاً (من «حسابي وهويتي» أو الحقل أدناه).");
        setBusy(null);
        return;
      }
      const r = await fetch(`${api}/api/v1/affiliates/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!r.ok) {
        const j = await r.json().catch(() => ({}));
        const detail = (j as { detail?: string }).detail;
        throw new Error(detail || (await r.text()) || `HTTP ${r.status}`);
      }
      const a = (await r.json()) as AffiliateResponse;
      applyAffiliatePayload(a);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "فشل التسجيل");
    } finally {
      setBusy(null);
    }
  };

  const activate = async () => {
    const st = loadMarketerOsState();
    if (!st.affiliateId) return;
    setBusy("activate");
    setErr(null);
    try {
      const r = await fetch(`${api}/api/v1/affiliates/${st.affiliateId}/activate`, {
        method: "POST",
      });
      if (!r.ok) throw new Error(await r.text());
      const a = (await r.json()) as AffiliateResponse;
      applyAffiliatePayload(a);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "فشل التفعيل");
    } finally {
      setBusy(null);
    }
  };

  const submitDeal = async () => {
    const st = loadMarketerOsState();
    if (!st.affiliateId) return;
    setBusy("deal");
    setErr(null);
    try {
      const r = await fetch(`${api}/api/v1/affiliates/${st.affiliateId}/deals`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_company: dealCompany.trim() || "عميل تجريبي",
          plan_type: dealPlan,
        }),
      });
      if (!r.ok) {
        const j = await r.json().catch(() => ({}));
        throw new Error((j as { detail?: string }).detail || (await r.text()));
      }
      await refreshFromServer();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "فشل تسجيل الصفقة");
    } finally {
      setBusy(null);
    }
  };

  const resetLocal = () => {
    clearMarketerOsState();
    setOs(loadMarketerOsState());
    setErr(null);
  };

  const stepIcon = (done: boolean) =>
    done ? (
      <CheckCircle2 className="h-5 w-5 shrink-0 text-teal-400" aria-hidden />
    ) : (
      <Circle className="h-5 w-5 shrink-0 text-slate-500" aria-hidden />
    );

  return (
    <section
      className="rounded-2xl border border-teal-500/35 bg-gradient-to-br from-teal-950/50 to-slate-900/80 p-6 shadow-lg"
      data-testid="marketer-os-panel"
    >
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-bold text-teal-100">
            <Rocket className="h-5 w-5 text-teal-400" aria-hidden />
            نظام التشغيل الكامل للمسوّق
          </h2>
          <p className="mt-1 text-sm leading-relaxed text-slate-400">
            تسجيل في البرنامج، ربط الهوية المحلية، تفعيل الحساب، ثم تسجيل صفقة تجريبية — مع فريقك ورمز الدعوة.
          </p>
        </div>
        <button
          type="button"
          onClick={resetLocal}
          className="inline-flex items-center gap-2 self-start rounded-xl border border-white/15 px-3 py-2 text-xs text-slate-400 transition hover:border-rose-500/40 hover:text-rose-200"
        >
          <Trash2 className="h-3.5 w-3.5" aria-hidden />
          مسح الربط المحلي
        </button>
      </div>

      <ul className="mt-6 grid gap-2 sm:grid-cols-2">
        <li className="flex items-center gap-2 text-sm text-slate-300">
          {stepIcon(os.steps.registered)}
          تسجيل في برنامج الشراكة (API)
        </li>
        <li className="flex items-center gap-2 text-sm text-slate-300">
          {stepIcon(os.steps.profileSaved)}
          حفظ هوية «حسابي وهويتي» محلياً
        </li>
        <li className="flex items-center gap-2 text-sm text-slate-300">
          {stepIcon(os.steps.activated)}
          تفعيل الحساب (نشط أو مُوظّف)
        </li>
        <li className="flex items-center gap-2 text-sm text-slate-300">
          {stepIcon(os.steps.firstDeal)}
          تسجيل صفقة عمولة
        </li>
      </ul>

      {os.referralCode && (
        <p className="mt-4 rounded-xl border border-teal-500/30 bg-teal-950/40 px-4 py-3 font-mono text-sm text-teal-200">
          رمز الإحالة: <strong>{os.referralCode}</strong>
        </p>
      )}

      {err && (
        <p className="mt-4 rounded-xl border border-rose-500/40 bg-rose-950/40 px-4 py-3 text-sm text-rose-100" role="alert">
          {err}
        </p>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="space-y-4 rounded-2xl border border-white/10 bg-white/5 p-5">
          <h3 className="flex items-center gap-2 text-sm font-bold text-white">
            <Link2 className="h-4 w-4 text-teal-400" aria-hidden />
            1) التسجيل والمزامنة
          </h3>
          <p className="text-xs text-slate-500">
            يُفضّل تعبئة «حسابي وهويتي» ثم العودة هنا — أو أدخل البيانات مباشرة.
          </p>
          <div className="grid gap-3">
            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              placeholder="الاسم الكامل"
              value={draft.fullName}
              onChange={(e) => setDraft((d) => ({ ...d, fullName: e.target.value }))}
            />
            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              placeholder="البريد الإلكتروني"
              type="email"
              value={draft.email}
              onChange={(e) => setDraft((d) => ({ ...d, email: e.target.value }))}
            />
            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              placeholder="جوال"
              value={draft.phone}
              onChange={(e) => setDraft((d) => ({ ...d, phone: e.target.value }))}
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              data-testid="marketer-os-register"
              disabled={!!busy}
              onClick={() => void register()}
              className="inline-flex items-center gap-2 rounded-xl bg-teal-500 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-50"
            >
              {busy === "register" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              تسجيل في البرنامج
            </button>
            <button
              type="button"
              data-testid="marketer-os-refresh"
              disabled={!!busy || !os.affiliateId}
              onClick={() => void refreshFromServer()}
              className="inline-flex items-center gap-2 rounded-xl border border-white/15 px-4 py-2 text-sm text-slate-200 disabled:opacity-50"
            >
              {busy === "refresh" ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              تحديث من الخادم
            </button>
          </div>
        </div>

        <div className="space-y-4 rounded-2xl border border-white/10 bg-white/5 p-5">
          <h3 className="text-sm font-bold text-white">2) التفعيل والصفقة</h3>
          <button
            type="button"
            data-testid="marketer-os-activate"
            disabled={!!busy || !os.affiliateId || os.status === "active" || os.status === "employed"}
            onClick={() => void activate()}
            className="w-full rounded-xl border border-teal-500/40 bg-teal-900/40 py-2 text-sm font-semibold text-teal-100 disabled:opacity-40"
          >
            {busy === "activate" ? "جارٍ التفعيل…" : "تفعيل الحساب (بعد المراجعة)"}
          </button>

          <div className="space-y-2">
            <label className="text-xs text-slate-400">شركة العميل</label>
            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={dealCompany}
              onChange={(e) => setDealCompany(e.target.value)}
            />
            <label className="text-xs text-slate-400">نوع الخطة</label>
            <select
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              value={dealPlan}
              onChange={(e) => setDealPlan(e.target.value as typeof dealPlan)}
            >
              <option value="basic">Basic</option>
              <option value="professional">Professional</option>
              <option value="enterprise">Enterprise</option>
            </select>
            <button
              type="button"
              data-testid="marketer-os-deal-submit"
              disabled={!!busy || !os.affiliateId}
              onClick={() => void submitDeal()}
              className="w-full rounded-xl bg-amber-500/90 py-2 text-sm font-bold text-slate-950 disabled:opacity-40"
            >
              {busy === "deal" ? "جارٍ التسجيل…" : "تسجيل صفقة عمولة"}
            </button>
          </div>

          {os.affiliateId && (
            <p className="text-xs text-slate-500">
              الصفقات: {os.totalDealsClosed} — العمولة التراكمية: {os.totalCommissionEarned.toFixed(2)} ر.س — هذا الشهر:{" "}
              {os.currentMonthDeals}
            </p>
          )}
        </div>
      </div>

      <div className="mt-6 flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-950/50 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 text-sm text-slate-300">
          <Users className="h-4 w-4 text-teal-400" aria-hidden />
          الفريق المحلي: {teamCount} عضو — رمز الدعوة:{" "}
          <span className="font-mono text-teal-200">{inviteCode || "—"}</span>
        </div>
        <a
          href="/marketers/team"
          className="text-sm text-teal-400 underline-offset-2 hover:text-teal-300"
        >
          إدارة الفريق
        </a>
      </div>
    </section>
  );
}
