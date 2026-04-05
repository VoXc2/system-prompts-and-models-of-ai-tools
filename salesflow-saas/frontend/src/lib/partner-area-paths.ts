/**
 * مسارات محتوى الشريك/المسوّق — تُقيَّد عند تفعيل PARTNER_GATE_SECRET في middleware.
 */

export function isPartnerRestrictedPath(pathname: string): boolean {
  if (pathname.startsWith("/marketers")) return true;
  if (pathname === "/resources" || pathname.startsWith("/resources/")) return true;
  if (pathname === "/strategy" || pathname.startsWith("/strategy/")) return true;
  if (pathname.startsWith("/dealix-marketing")) return true;
  if (pathname.startsWith("/dealix-presentations")) return true;
  return false;
}

export const DEALIX_PARTNER_GATE_COOKIE = "dealix_partner_gate";
