import path from "path";
import { readFile } from "fs/promises";
import type { Metadata } from "next";
import { MarketingMdDoc } from "@/components/dealix/marketing-md-doc";

export const metadata: Metadata = {
  title: "Dealix — قطاع العقار",
  description: "من الاستفسار إلى المعاينة — عرض قطاعي مقروء.",
};

export default async function RealEstatePresentationPage() {
  const filePath = path.join(
    process.cwd(),
    "public/dealix-marketing/Real_Estate_Presentation.md"
  );
  const source = await readFile(filePath, "utf-8");

  return (
    <MarketingMdDoc
      source={source}
      backHref="/marketers"
      backLabel="← بوابة المسوّقين"
      downloadPath="/dealix-marketing/Real_Estate_Presentation.md"
      dir="ltr"
    />
  );
}
