"use client";

import { DealixDashboardShell } from "@/components/dealix/dealix-dashboard-shell";

/** معاينة عامة لـ Dealix OS — لا يتطلب تسجيلاً؛ البيانات نموذجية. */
export default function ExplorePlatformPage() {
  return <DealixDashboardShell mode="preview" />;
}
