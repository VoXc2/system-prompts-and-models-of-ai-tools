import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dealix - نظام ذكاء تشغيلي للمبيعات | AI Revenue OS",
  description: "نظام تشغيلي ذكي يرتب مبيعاتك، ينظم المتابعة، يسرّع الرد، ويزيد فرص الإغلاق. مصمم للشركات السعودية الصغيرة والمتوسطة.",
  keywords: "Dealix, مبيعات, CRM, SaaS, ذكاء اصطناعي, أتمتة, عيادات, عقارات, الرياض, السعودية, Revenue OS",
  openGraph: {
    title: "Dealix — AI Revenue Operating System",
    description: "نظام الإيرادات الذكي للشركات السعودية. Voice AI, WhatsApp CRM, Smart Booking.",
    images: [{ url: "/og-image.svg", width: 1200, height: 630, alt: "Dealix AI Revenue OS" }],
    locale: "ar_SA",
    type: "website",
    siteName: "Dealix",
  },
  twitter: {
    card: "summary_large_image",
    title: "Dealix — AI Revenue OS",
    description: "نظام الإيرادات الذكي للشركات السعودية",
    images: ["/og-image.svg"],
  },
  icons: {
    icon: "/favicon.svg",
    apple: "/apple-touch-icon.svg",
  },
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
        <link rel="apple-touch-icon" href="/apple-touch-icon.svg" />
        <meta name="theme-color" content="#0B3B66" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
