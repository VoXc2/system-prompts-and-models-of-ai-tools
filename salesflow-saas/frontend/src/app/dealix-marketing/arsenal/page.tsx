import path from "path";
import { readFile } from "fs/promises";
import type { Metadata } from "next";
import { MarketingMdDoc } from "@/components/dealix/marketing-md-doc";

export const metadata: Metadata = {
  title: "Dealix — دليل المسوّق الاستراتيجي",
  description: "هيكل العمولة، الممانعات، وملف الشركة — نسخة مقروءة من المتصفح.",
};

export default async function MarketingArsenalPage() {
  const filePath = path.join(process.cwd(), "public/dealix-marketing/Dealix_Marketing_Arsenal.md");
  const source = await readFile(filePath, "utf-8");

  return (
    <MarketingMdDoc
      source={source}
      backHref="/marketers"
      backLabel="← بوابة المسوّقين"
      downloadPath="/dealix-marketing/Dealix_Marketing_Arsenal.md"
      dir="ltr"
    />
  );
}
