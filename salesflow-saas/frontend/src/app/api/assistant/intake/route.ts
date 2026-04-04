import { NextRequest, NextResponse } from "next/server";

const API_BASE =
  process.env.BACKEND_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

export async function POST(req: NextRequest) {
  let body: { message?: string; variant?: string; name?: string; phone?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const message = (body.message || "").trim();
  if (!message) {
    return NextResponse.json({ ok: false, error: "empty_message" }, { status: 400 });
  }

  const payload = {
    name: body.name || "زائر الموقع",
    phone: (body.phone || "0500000000").replace(/\D/g, "").slice(-12) || "0500000000",
    company: "",
    sector: body.variant === "marketer" ? "marketer_partner" : "company_visitor",
    message: `[${body.variant || "site"}] ${message}`,
    source: "dealix_web_assistant",
    city: "",
  };

  try {
    const ac = new AbortController();
    const to = setTimeout(() => ac.abort(), 25_000);
    const r = await fetch(`${API_BASE.replace(/\/$/, "")}/api/v1/revenue-room/intake`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: ac.signal,
    });
    clearTimeout(to);

    if (!r.ok) {
      const t = await r.text().catch(() => "");
      return NextResponse.json({ ok: false, status: r.status, detail: t.slice(0, 400) }, { status: 200 });
    }

    const data = (await r.json()) as { reply?: string; tier?: string };
    return NextResponse.json({ ok: true, reply: data.reply || "", tier: data.tier });
  } catch {
    return NextResponse.json({ ok: false, error: "backend_unreachable" }, { status: 200 });
  }
}
