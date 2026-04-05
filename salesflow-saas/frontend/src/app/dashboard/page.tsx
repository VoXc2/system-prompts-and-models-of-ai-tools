"use client";

import { useRequireAuth } from "@/contexts/auth-context";
import { DealixDashboardShell } from "@/components/dealix/dealix-dashboard-shell";

export default function DashboardPage() {
  const auth = useRequireAuth();

  if (auth.loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        جاري التحقق من الجلسة…
      </div>
    );
  }
  if (!auth.user) {
    return null;
  }

  return (
    <DealixDashboardShell
      mode="live"
      userEmail={auth.user.email || "مستخدم"}
      userRole={auth.user.role}
      onLogout={auth.logout}
    />
  );
}
