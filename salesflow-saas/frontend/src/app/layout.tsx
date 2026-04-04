import type { Metadata } from "next";
import { Noto_Kufi_Arabic } from "next/font/google";
import "./globals.css";
import { AppProviders } from "./providers";

const kufi = Noto_Kufi_Arabic({ 
  subsets: ["arabic", "latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-kufi",
});

export const metadata: Metadata = {
  title: "Dealix — نظام تشغيل الإيرادات B2B",
  description:
    "اكتشاف، تأهيل، قنوات متعددة، وتحليلات — مع حوكمة وذاكرة. سوق سعودي.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" className="dark">
      <body className={`${kufi.variable} font-sans antialiased`}>
        {/* Background Gradients for depth */}
        <div className="fixed inset-0 z-[-1] bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-background to-background pointer-events-none" />
        <div className="pointer-events-none fixed top-20 left-10 z-[-1] h-96 w-96 rounded-full bg-accent/10 opacity-50 mix-blend-multiply blur-[100px]" />

        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
