"use client";

import { usePathname } from "next/navigation";
import { DealixAssistantWidget } from "@/components/dealix/dealix-assistant-widget";

/**
 * مساعد ذكي على معظم الصفحات. في /marketers يُبقى مساعد الشريك من الـ layout الخاص دون تكرار.
 */
export function GlobalAssistantHost() {
  const pathname = usePathname() || "";
  if (pathname.startsWith("/marketers")) {
    return null;
  }
  const variant = pathname.startsWith("/explore") ? "preview" : "company";
  return <DealixAssistantWidget key={variant} variant={variant} />;
}
