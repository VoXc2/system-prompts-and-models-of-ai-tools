"use client";

import type { ReactNode } from "react";
import { AuthProvider } from "@/contexts/auth-context";
import { GlobalAssistantHost } from "@/components/dealix/global-assistant-host";

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      {children}
      <GlobalAssistantHost />
    </AuthProvider>
  );
}
