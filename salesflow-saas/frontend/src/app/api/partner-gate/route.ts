import { NextResponse } from "next/server";
import { DEALIX_PARTNER_GATE_COOKIE } from "@/lib/partner-area-paths";

function cookieOptions() {
  const maxAge = 60 * 60 * 24 * 30;
  return {
    httpOnly: true as const,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/",
    maxAge,
  };
}

/**
 * يضبط كوكي الوصول لمنطقة الشريك بعد مطابقة السرّ مع PARTNER_GATE_SECRET (خادم فقط).
 * إذا لم يُضبط السرّ في البيئة، يعيد 503 ولا يضبط كوكي — والـ middleware لا يفرض البوابة أصلاً.
 */
export async function POST(request: Request) {
  const expected = process.env.PARTNER_GATE_SECRET?.trim();
  if (!expected) {
    return NextResponse.json(
      { error: "بوابة الشريك غير مفعّلة على الخادم (لا يوجد PARTNER_GATE_SECRET)." },
      { status: 503 }
    );
  }

  let body: { secret?: string } = {};
  try {
    body = (await request.json()) as { secret?: string };
  } catch {
    return NextResponse.json({ error: "جسيم غير صالح" }, { status: 400 });
  }

  const secret = typeof body.secret === "string" ? body.secret : "";
  if (secret !== expected) {
    return NextResponse.json({ error: "رمز غير صحيح" }, { status: 401 });
  }

  const res = NextResponse.json({ ok: true });
  res.cookies.set(DEALIX_PARTNER_GATE_COOKIE, "1", cookieOptions());
  return res;
}

export async function DELETE() {
  const res = NextResponse.json({ ok: true });
  res.cookies.set(DEALIX_PARTNER_GATE_COOKIE, "", { path: "/", maxAge: 0 });
  return res;
}
