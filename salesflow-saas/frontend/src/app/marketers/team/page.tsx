import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { MarketerTeamDashboard } from "@/components/marketers/marketer-team-dashboard";

export default function MarketerTeamPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <Link
        href="/marketers"
        className="mb-6 inline-flex items-center gap-2 text-sm text-teal-400 hover:text-teal-300"
      >
        <ArrowLeft className="h-4 w-4 rotate-180" aria-hidden />
        العودة للبوابة
      </Link>
      <h1 className="text-2xl font-bold tracking-tight text-white">فريق المسوّقين والمدراء</h1>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">
        رمز دعوة واحد، رابط تسجيل للتابعين، وعرض هرمي للصفقات — مع مواد تدريبية وروابط جاهزة.
      </p>
      <div className="mt-8">
        <MarketerTeamDashboard />
      </div>
    </div>
  );
}
