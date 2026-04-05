import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Dealix — جولة في لوحة التحكم (بدون تسجيل)",
  description:
    "استكشف شكل المنصة والتبويبات والقدرات قبل إنشاء حساب أو الدفع — بيانات نموذجية للتوضيح فقط.",
};

export default function ExploreLayout({ children }: { children: ReactNode }) {
  return children;
}
