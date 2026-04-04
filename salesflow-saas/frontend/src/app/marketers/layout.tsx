import type { Metadata } from "next";
import Link from "next/link";
import { BarChart3 } from "lucide-react";
import { MarketersAssistantHost } from "@/components/marketers/marketers-assistant-host";

export const metadata: Metadata = {
  title: "Dealix — بوابة المسوّقين",
  description:
    "مسار كامل للمسوّق: موارد، عروض، صفقات، عمولات، وحسابك البنكي — مع روابط التسجيل والمنصة.",
};

export default function MarketersLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-teal-950 text-slate-100">
      <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-3 px-6 py-3.5">
          <Link
            href="/marketers"
            className="flex items-center gap-2 text-sm font-bold text-white transition hover:text-teal-200"
          >
            <BarChart3 className="h-6 w-6 shrink-0 text-teal-400" aria-hidden />
            بوابة المسوّقين
          </Link>
          <nav className="flex flex-wrap items-center justify-end gap-x-4 gap-y-2 text-sm">
            <Link href="/marketers" className="text-teal-300 hover:text-teal-200">
              الرئيسية
            </Link>
            <Link href="/marketers/team" className="font-semibold text-teal-200 hover:text-teal-100">
              فريقي
            </Link>
            <Link href="/marketers/deals" className="text-slate-300 hover:text-white">
              الصفقات والعمولات
            </Link>
            <Link href="/marketers/account" className="text-slate-300 hover:text-white">
              حسابي
            </Link>
            <span className="hidden h-4 w-px bg-white/15 sm:block" aria-hidden />
            <Link href="/register?next=%2Fmarketers" className="font-semibold text-teal-400 hover:text-teal-300">
              تسجيل
            </Link>
            <Link href="/login?next=%2Fdashboard" className="text-slate-400 hover:text-white">
              دخول المنصة
            </Link>
          </nav>
        </div>
      </header>
      {children}
      <MarketersAssistantHost />
    </div>
  );
}
