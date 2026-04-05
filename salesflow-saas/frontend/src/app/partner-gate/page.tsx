"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";
import Link from "next/link";
import { Lock, ArrowLeft } from "lucide-react";

function PartnerGateForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextRaw = searchParams.get("next") || "/marketers";
  const [secret, setSecret] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setBusy(true);
    try {
      const r = await fetch("/api/partner-gate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ secret: secret.trim() }),
      });
      const data = (await r.json().catch(() => ({}))) as { error?: string };
      if (!r.ok) {
        setErr(data.error || `فشل التحقق (${r.status})`);
        return;
      }
      const dest = nextRaw.startsWith("/") ? nextRaw : "/marketers";
      router.replace(dest);
      router.refresh();
    } catch {
      setErr("تعذّر الاتصال بالخادم.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="w-full max-w-md space-y-8 rounded-2xl border border-white/10 bg-slate-950/80 p-8 shadow-2xl backdrop-blur-md">
      <div className="flex items-center gap-3 text-teal-300">
        <Lock className="h-8 w-8 shrink-0" aria-hidden />
        <div>
          <h1 className="text-xl font-bold text-white">منطقة الشركاء والمسوّقين</h1>
          <p className="mt-1 text-sm text-slate-400">
            هذه الصفحات مخصّصة لفريق GTM والشركاء المعتمدين — أدخل الرمز الذي يزوّدك به فريق Dealix.
          </p>
        </div>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-slate-300">رمز الدخول</span>
          <input
            type="password"
            name="secret"
            autoComplete="current-password"
            value={secret}
            onChange={(e) => setSecret(e.target.value)}
            className="w-full rounded-xl border border-white/15 bg-black/30 px-4 py-3 text-slate-100 outline-none ring-teal-500/40 focus:border-teal-500/50 focus:ring-2"
            placeholder="••••••••"
            disabled={busy}
          />
        </label>
        {err ? (
          <p className="rounded-lg border border-red-500/30 bg-red-950/40 px-3 py-2 text-sm text-red-200">{err}</p>
        ) : null}
        <button
          type="submit"
          disabled={busy || !secret.trim()}
          className="w-full rounded-xl bg-teal-600 py-3 text-sm font-bold text-white shadow-lg shadow-teal-900/40 transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? "جارٍ التحقق…" : "متابعة"}
        </button>
      </form>

      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm text-slate-500 transition hover:text-teal-400"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        العودة للصفحة الرئيسية
      </Link>
    </div>
  );
}

export default function PartnerGatePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#030712] px-6 py-16 text-slate-100">
      <Suspense
        fallback={
          <div className="w-full max-w-md animate-pulse rounded-2xl border border-white/10 bg-slate-950/50 p-8 text-center text-sm text-slate-500">
            جارٍ التحميل…
          </div>
        }
      >
        <PartnerGateForm />
      </Suspense>
    </div>
  );
}
