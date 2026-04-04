import path from "path";
import { readFile } from "fs/promises";
import type { Metadata } from "next";
import { MarketingMdDoc } from "@/components/dealix/marketing-md-doc";

export const metadata: Metadata = {
  title: "Dealix — دليل لوحة التحكم",
  description: "شرح تبويبات المنصة وقيمة Dealix للشركات والشركاء.",
};

export default async function DashboardGuidePage() {
  const filePath = path.join(process.cwd(), "public/dealix-marketing/Dealix_Dashboard_Guide_AR.md");
  const source = await readFile(filePath, "utf-8");

  return (
    <MarketingMdDoc
      source={source}
      backHref="/marketers"
      backLabel="← بوابة المسوّقين"
      downloadPath="/dealix-marketing/Dealix_Dashboard_Guide_AR.md"
      dir="rtl"
    />
  );
}
