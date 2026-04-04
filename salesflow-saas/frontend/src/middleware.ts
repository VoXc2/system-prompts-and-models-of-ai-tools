import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  DEALIX_SESSION_COOKIE,
  buildLoginUrlWithNext,
  dealixSessionCookieValueIsActive,
} from "@/lib/auth-gate";
import { DEALIX_MARKETING_MD_TO_PAGE } from "@/lib/dealix-marketing-md-redirects";

/**
 * 1) Markdown تحت /dealix-marketing/*.md: إعادة توجيه لصفحة العرض (قبل خدمة الملف الخام من public).
 * 2) Gate /dashboard: جلسة عبر الكوكي dealix_has_session.
 */
export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  const mdDest = DEALIX_MARKETING_MD_TO_PAGE[pathname];
  if (mdDest) {
    return NextResponse.redirect(new URL(mdDest, request.url));
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
  matcher: ["/dashboard", "/dashboard/:path*", "/dealix-marketing/:path*"],
};
