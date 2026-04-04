import path from "path";
import { readFile } from "fs/promises";
import type { Metadata } from "next";
import { MarketingMdDoc } from "@/components/dealix/marketing-md-doc";

export const metadata: Metadata = {
  title: "Dealix — عرض المؤسسات (Pitch Deck 2026)",
  description: "المشكلة، الحل، الوكلاء، الجدوى، Salesforce، ورؤية سعودية — نسخة مقروءة.",
};

export default async function EnterprisePitchPage() {
  const filePath = path.join(
    process.cwd(),
    "public/dealix-marketing/Dealix_Enterprise_Pitch_Deck.md"
  );
  const source = await readFile(filePath, "utf-8");

  return (
    <MarketingMdDoc
      source={source}
      backHref="/marketers"
      backLabel="← بوابة المسوّقين"
      downloadPath="/dealix-marketing/Dealix_Enterprise_Pitch_Deck.md"
      dir="rtl"
    />
  );
}
