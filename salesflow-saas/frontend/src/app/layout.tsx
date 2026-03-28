import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dealix - نظام ذكاء تشغيلي للمبيعات | AI Revenue OS",
  description: "نظام تشغيلي ذكي يرتب مبيعاتك، ينظم المتابعة، يسرّع الرد، ويزيد فرص الإغلاق. مصمم للشركات السعودية الصغيرة والمتوسطة.",
  keywords: "Dealix, مبيعات, CRM, SaaS, ذكاء اصطناعي, أتمتة, عيادات, عقارات, الرياض, السعودية, Revenue OS",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
