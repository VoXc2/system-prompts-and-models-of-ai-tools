import { NextResponse } from "next/server";
import { backendProxyHeaders, getServerBackendBaseUrl } from "@/lib/server-backend-proxy";

export async function GET() {
  const base = getServerBackendBaseUrl();
  try {
    const res = await fetch(`${base}/api/v1/strategy/summary`, {
      headers: backendProxyHeaders(),
      cache: "no-store",
    });
    const body = await res.text();
    return new NextResponse(body, {
      status: res.status,
      headers: {
        "Content-Type": res.headers.get("Content-Type") || "application/json",
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return NextResponse.json(
      { detail: "Upstream API unreachable" },
      { status: 502 }
    );
  }
}
