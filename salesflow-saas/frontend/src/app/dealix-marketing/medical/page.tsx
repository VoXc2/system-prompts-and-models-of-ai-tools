import path from "path";
import { readFile } from "fs/promises";
import type { Metadata } from "next";
import { MarketingMdDoc } from "@/components/dealix/marketing-md-doc";

export const metadata: Metadata = {
  title: "Dealix — القطاع الصحي",
  description: "العيادات والرعاية الصحية — عرض قطاعي مقروء.",
};

export default async function MedicalPresentationPage() {
  const filePath = path.join(process.cwd(), "public/dealix-marketing/Medical_Presentation.md");
  const source = await readFile(filePath, "utf-8");

  return (
    <MarketingMdDoc
      source={source}
      backHref="/marketers"
      backLabel="← بوابة المسوّقين"
      downloadPath="/dealix-marketing/Medical_Presentation.md"
      dir="ltr"
    />
  );
}
