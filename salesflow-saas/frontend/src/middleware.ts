import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  DEALIX_SESSION_COOKIE,
  buildLoginUrlWithNext,
  dealixSessionCookieValueIsActive,
} from "@/lib/auth-gate";
import { DEALIX_MARKETING_MD_TO_PAGE } from "@/lib/dealix-marketing-md-redirects";
import { DEALIX_PARTNER_GATE_COOKIE, isPartnerRestrictedPath } from "@/lib/partner-area-paths";

function partnerGateSecretConfigured(): boolean {
  return Boolean(process.env.PARTNER_GATE_SECRET?.trim());
}

function partnerGateCookieActive(value: string | undefined): boolean {
  return value === "1";
}

/**
 * 1) Markdown تحت /dealix-marketing/*.md: إعادة توجيه لصفحة العرض (قبل خدمة الملف الخام من public).
 * 2) منطقة الشريك: عند PARTNER_GATE_SECRET — كوكي dealix_partner_gate.
 * 3) /dashboard: جلسة تطبيق عبر dealix_has_session.
 */
export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  const mdDest = DEALIX_MARKETING_MD_TO_PAGE[pathname];
  if (mdDest) {
    return NextResponse.redirect(new URL(mdDest, request.url));
  }

  if (partnerGateSecretConfigured() && isPartnerRestrictedPath(pathname)) {
    const v = request.cookies.get(DEALIX_PARTNER_GATE_COOKIE)?.value;
    if (!partnerGateCookieActive(v)) {
      const gate = new URL("/partner-gate", request.url);
      gate.searchParams.set("next", pathname + request.nextUrl.search);
      return NextResponse.redirect(gate);
    }
  }

  if (pathname.startsWith("/dashboard")) {
    const v = request.cookies.get(DEALIX_SESSION_COOKIE)?.value;
    if (!dealixSessionCookieValueIsActive(v)) {
      const login = buildLoginUrlWithNext(request.url, request.nextUrl.pathname);
      return NextResponse.redirect(login);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard",
    "/dashboard/:path*",
    "/marketers/:path*",
    "/resources",
    "/resources/:path*",
    "/strategy",
    "/strategy/:path*",
    "/dealix-marketing/:path*",
    "/dealix-presentations/:path*",
  ],
};
