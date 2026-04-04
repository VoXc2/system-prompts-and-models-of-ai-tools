import path from "path";
import { readFile } from "fs/promises";
import type { Metadata } from "next";
import { MarketingMdDoc } from "@/components/dealix/marketing-md-doc";

export const metadata: Metadata = {
  title: "Dealix — لوجستيات وتجزئة وصناعة",
  description: "لوجستيات، تجارة، وتصنيع — عرض قطاعي مقروء.",
};

export default async function IndustrialRetailLogisticsPage() {
  const filePath = path.join(
    process.cwd(),
    "public/dealix-marketing/Industrial_Retail_Logistics.md"
  );
  const source = await readFile(filePath, "utf-8");

  return (
    <MarketingMdDoc
      source={source}
      backHref="/marketers"
      backLabel="← بوابة المسوّقين"
      downloadPath="/dealix-marketing/Industrial_Retail_Logistics.md"
      dir="ltr"
    />
  );
}
