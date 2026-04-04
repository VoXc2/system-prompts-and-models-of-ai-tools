/**
 * طلبات .md تحت public قد تُخدم كملف خام قبل redirects في next.config —
 * نعيد التوجيه هنا من middleware لضمان صفحة Markdown المقروءة.
 */
export const DEALIX_MARKETING_MD_TO_PAGE: Record<string, string> = {
  "/dealix-marketing/Dealix_Dashboard_Guide_AR.md": "/dealix-marketing/dashboard-guide",
  "/dealix-marketing/Dealix_Marketing_Arsenal.md": "/dealix-marketing/arsenal",
  "/dealix-marketing/Dealix_Company_Profile.md": "/dealix-marketing/company-profile",
  "/dealix-marketing/Dealix_Enterprise_Pitch_Deck.md": "/dealix-marketing/enterprise-pitch",
  "/dealix-marketing/Real_Estate_Presentation.md": "/dealix-marketing/real-estate",
  "/dealix-marketing/Medical_Presentation.md": "/dealix-marketing/medical",
  "/dealix-marketing/Industrial_Retail_Logistics.md": "/dealix-marketing/industrial-logistics",
};
