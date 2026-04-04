import path from "path";
import { readFile } from "fs/promises";
import type { Metadata } from "next";
import { MarketingMdDoc } from "@/components/dealix/marketing-md-doc";

export const metadata: Metadata = {
  title: "Dealix — ملف الشركة (2026)",
  description: "الرؤية، القيمة المضافة، البنية، وحزم الخدمات — نسخة مقروءة.",
};

export default async function CompanyProfilePage() {
  const filePath = path.join(process.cwd(), "public/dealix-marketing/Dealix_Company_Profile.md");
  const source = await readFile(filePath, "utf-8");

  return (
    <MarketingMdDoc
      source={source}
      backHref="/marketers"
      backLabel="← بوابة المسوّقين"
      downloadPath="/dealix-marketing/Dealix_Company_Profile.md"
      dir="rtl"
    />
  );
}
