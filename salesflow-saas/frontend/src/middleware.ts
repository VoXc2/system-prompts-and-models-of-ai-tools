import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Server-side auth guard.
 * Redirects unauthenticated users away from dashboard routes.
 * Token validation happens client-side via API — this is a fast first-pass check.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public routes — no auth required
  const publicPaths = [
    "/",
    "/login",
    "/register",
    "/pricing",
    "/book-demo",
    "/whatsapp-crm",
    "/healthcare",
    "/real-estate",
    "/legal",
  ];

  const isPublic = publicPaths.some(
    (p) => pathname === p || pathname.startsWith(`${p}/`)
  );
  const isAsset =
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.includes(".");

  if (isPublic || isAsset) {
    return NextResponse.next();
  }

  // Dashboard routes — check for token cookie/header
  const token =
    request.cookies.get("dealix_token")?.value ||
    request.headers.get("authorization")?.replace("Bearer ", "");

  if (!token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
