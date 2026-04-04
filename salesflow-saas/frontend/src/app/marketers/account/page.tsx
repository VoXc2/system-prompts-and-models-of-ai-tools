import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { MarketerAccountForm } from "@/components/marketers/marketer-account-form";

export default function MarketerAccountPage() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Link
        href="/marketers"
        className="mb-6 inline-flex items-center gap-2 text-sm text-teal-400 hover:text-teal-300"
      >
        <ArrowLeft className="h-4 w-4 rotate-180" aria-hidden />
        العودة للبوابة
      </Link>
      <h1 className="text-2xl font-bold tracking-tight text-white">حساب المسوّق</h1>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">
        عرّف هويتك وبيانات التحويل كما ستظهر في التسويات — استخدم نفس البيانات عند التوقيع على عقد
        الشريك مع Dealix.
      </p>
      <div className="mt-8">
        <MarketerAccountForm />
      </div>
    </div>
  );
}
