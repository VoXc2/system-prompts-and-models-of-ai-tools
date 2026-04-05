"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { LogOut } from "lucide-react";

/** يمسح كوكي منطقة الشريك (إن وُجد) ويعيد الزائر للصفحة الرئيسية. */
export function PartnerAreaExit() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);

  async function exitPartnerArea() {
    setBusy(true);
    try {
      await fetch("/api/partner-gate", { method: "DELETE" });
      router.replace("/");
      router.refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      onClick={() => void exitPartnerArea()}
      disabled={busy}
      className="inline-flex items-center gap-1.5 rounded-lg border border-white/15 px-2 py-1 text-xs text-slate-400 transition hover:border-amber-500/40 hover:text-amber-200 disabled:opacity-50"
      title="إنهاء جلسة منطقة الشريك والمواد التسويقية (منفصل عن دخول المنصة)"
    >
      <LogOut className="h-3.5 w-3.5" aria-hidden />
      {busy ? "…" : "خروج منطقة الشريك"}
    </button>
  );
}
