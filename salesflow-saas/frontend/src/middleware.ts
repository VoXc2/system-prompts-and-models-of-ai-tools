import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  DEALIX_SESSION_COOKIE,
  buildLoginUrlWithNext,
  dealixSessionCookieValueIsActive,
} from "@/lib/auth-gate";

/**
 * Gate /dashboard on the server: localStorage is not available here, so we mirror
 * session presence with `dealix_has_session` (set in auth-storage when JWT is stored).
 */
export function middleware(request: NextRequest) {
  const v = request.cookies.get(DEALIX_SESSION_COOKIE)?.value;
  if (!dealixSessionCookieValueIsActive(v)) {
    const login = buildLoginUrlWithNext(request.url, request.nextUrl.pathname);
    return NextResponse.redirect(login);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard", "/dashboard/:path*"],
};
