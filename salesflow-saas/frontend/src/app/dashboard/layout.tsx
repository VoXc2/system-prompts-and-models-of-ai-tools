import type { ReactNode } from "react";

/** Auth is provided by root `AppProviders`; layout kept for future dashboard-only UI. */
export default function DashboardLayout({ children }: { children: ReactNode }) {
  return children;
}
