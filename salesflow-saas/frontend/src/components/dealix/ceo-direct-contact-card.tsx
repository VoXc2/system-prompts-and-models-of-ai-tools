"use client";

import Link from "next/link";
import { Calendar, MessageCircle, Phone, Video } from "lucide-react";
import {
  CEO_NAME_AR,
  CEO_TITLE_AR,
  getCeoBookingUrl,
  getCeoWhatsappE164,
  getCeoWhatsappLink,
  getCeoBookingOrScheduleViaWaLink,
} from "@/lib/ceo-contact";

type Props = {
  /** إظهار رابط الصفحة الرئيسية للمساعدة */
  showHelpLink?: boolean;
};

export function CeoDirectContactCard({ showHelpLink }: Props) {
  const bookingConfigured = getCeoBookingUrl().length > 0;
  const scheduleHref = getCeoBookingOrScheduleViaWaLink();
  const waHref = getCeoWhatsappLink();
  const tel = `+${getCeoWhatsappE164()}`;

  return (
    <div
      id="ceo-contact"
      className="scroll-mt-24 rounded-2xl border border-amber-500/35 bg-gradient-to-br from-amber-950/50 via-slate-900/90 to-slate-950/95 p-6 shadow-[0_0_40px_-18px_rgba(245,158,11,0.35)] md:p-8"
    >
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 space-y-2">
          <p className="text-xs font-bold uppercase tracking-wider text-amber-300/95">
            تواصل مباشر مع القيادة
          </p>
          <h2 className="text-xl font-black tracking-tight text-white md:text-2xl">{CEO_NAME_AR}</h2>
          <p className="text-sm font-semibold text-amber-100/90">{CEO_TITLE_AR}</p>
          <p className="max-w-xl text-sm leading-relaxed text-slate-400">
            احجز اجتماعاً عبر تقويم Google (يتضمّن رابط Google Meet تلقائياً عند التفعيل)، أو تواصل مباشرة عبر
            واتساب أو اتصال — للشراكات، العروض التقديمية، والقرار الاستراتيجي.
          </p>
        </div>

        <div className="flex w-full flex-col gap-3 sm:flex-row sm:flex-wrap lg:w-auto lg:min-w-[280px] lg:flex-col">
          <a
            href={scheduleHref}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-l from-amber-500 to-amber-600 px-5 py-3.5 text-sm font-bold text-slate-950 shadow-lg shadow-amber-900/30 transition hover:from-amber-400 hover:to-amber-500"
          >
            {bookingConfigured ? (
              <>
                <Calendar className="h-5 w-5 shrink-0" aria-hidden />
                <span>حجز موعد — Google Meet</span>
                <Video className="h-4 w-4 shrink-0 opacity-80" aria-hidden />
              </>
            ) : (
              <>
                <MessageCircle className="h-5 w-5 shrink-0" aria-hidden />
                <span>طلب حجز موعد (واتساب)</span>
              </>
            )}
          </a>

          <a
            href={waHref}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 px-5 py-3.5 text-sm font-bold text-white shadow-lg shadow-teal-900/35 transition hover:bg-teal-500"
          >
            <MessageCircle className="h-5 w-5 shrink-0" aria-hidden />
            واتساب مباشر
          </a>

          <a
            href={`tel:${tel}`}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
          >
            <Phone className="h-4 w-4 shrink-0 text-teal-300" aria-hidden />
            اتصال: {formatSaPhoneDisplay(getCeoWhatsappE164())}
          </a>

          {showHelpLink ? (
            <Link
              href="/help"
              className="text-center text-xs font-medium text-slate-500 underline-offset-2 hover:text-teal-400 hover:underline"
            >
              الأسئلة الشائعة والدعم
            </Link>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function formatSaPhoneDisplay(e164: string): string {
  const d = e164.replace(/^966/, "");
  if (d.length === 9 && d.startsWith("5")) {
    const n = `0${d}`;
    return `${n.slice(0, 2)} ${n.slice(2, 5)} ${n.slice(5, 8)} ${n.slice(8)}`;
  }
  return e164;
}
