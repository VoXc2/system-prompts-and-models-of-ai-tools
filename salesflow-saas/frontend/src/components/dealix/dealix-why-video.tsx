"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronDown,
  Pause,
  Play,
  TrendingUp,
  Volume2,
  VolumeX,
} from "lucide-react";

/** ضع ملف اللوب هنا (8–10 ثوانٍ، H.264 + MP4). يمكنك إضافة WebM لاحقاً كمصدر ثانٍ. */
export const DEALIX_WHY_VIDEO_MP4 = "/dealix/why-product-loop.mp4";

function StaticWhyFallback() {
  return (
    <div className="rounded-3xl border border-teal-500/20 bg-gradient-to-br from-teal-950/50 to-slate-900/80 p-8 md:p-12">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-2 text-teal-300">
            <TrendingUp className="h-5 w-5" aria-hidden />
            <span className="text-sm font-semibold">لماذا ليس مجرد landing بسيط؟</span>
          </div>
          <p className="mt-3 max-w-xl leading-relaxed text-slate-300">
            الصفحات التسويقية تشرح القيمة. Dealix ينفّذ الدورة: بيانات، صفقات، عمولات، وربط قنوات —
            مع طبقة ذكاء وحوكمة. استخدم هذه الصفحة للجذب، ولوحة التحكم للتشغيل.
          </p>
        </div>
        <Link
          href="/resources"
          className="inline-flex shrink-0 items-center justify-center gap-2 rounded-2xl bg-white px-6 py-4 text-sm font-bold text-slate-900 hover:bg-slate-100"
        >
          مركز التحميل الكامل
          <ChevronDown className="h-4 w-4 rotate-[-90deg]" aria-hidden />
        </Link>
      </div>
    </div>
  );
}

export function DealixWhyVideo() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [loadError, setLoadError] = useState(false);
  const [paused, setPaused] = useState(true);
  const [muted, setMuted] = useState(true);
  const [hover, setHover] = useState(false);

  const togglePlay = useCallback(() => {
    const v = videoRef.current;
    if (!v) return;
    if (v.paused) void v.play();
    else v.pause();
  }, []);

  const toggleMute = useCallback(() => {
    setMuted((m) => !m);
  }, []);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    const onPlay = () => setPaused(false);
    const onPause = () => setPaused(true);
    v.addEventListener("play", onPlay);
    v.addEventListener("pause", onPause);
    return () => {
      v.removeEventListener("play", onPlay);
      v.removeEventListener("pause", onPause);
    };
  }, [loadError]);

  useEffect(() => {
    const v = videoRef.current;
    if (!v || loadError) return;
    v.muted = muted;
  }, [muted, loadError]);

  useEffect(() => {
    const v = videoRef.current;
    if (!v || loadError) return;
    void v.play().catch(() => {
      /* autoplay قد يُرفض؛ يبقى زر التشغيل */
    });
  }, [loadError]);

  if (loadError) {
    return <StaticWhyFallback />;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.45 }}
      className="group relative overflow-hidden rounded-3xl border border-teal-500/30 bg-[#050a14] shadow-[0_0_60px_-20px_rgba(20,184,166,0.35)] ring-1 ring-white/5"
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      <div className="relative aspect-video w-full max-h-[min(56vh,520px)] bg-black md:max-h-none">
        <video
          ref={videoRef}
          className="h-full w-full cursor-pointer object-cover object-center"
          muted={muted}
          loop
          playsInline
          preload="auto"
          aria-label="معاينة تفاعلية لقدرات Dealix — لوب قصير"
          onError={() => setLoadError(true)}
          onClick={togglePlay}
        >
          <source src={DEALIX_WHY_VIDEO_MP4} type="video/mp4" />
        </video>

        <div
          className="pointer-events-none absolute inset-0 bg-gradient-to-t from-[#030712]/95 via-[#030712]/25 to-[#030712]/40"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_0%,rgba(45,212,191,0.12),transparent_55%)]"
          aria-hidden
        />

        <div className="pointer-events-none absolute inset-0 flex flex-col justify-between p-4 md:p-6">
          <div className="flex items-start justify-between gap-3">
            <div className="rounded-2xl border border-white/10 bg-black/35 px-3 py-2 text-right backdrop-blur-md md:px-4">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-300/95">لمحة 8–10 ثوانٍ</p>
              <p className="mt-1 max-w-[min(100%,28rem)] text-sm font-semibold text-white md:text-base">
                لماذا ليس مجرد landing بسيط؟ شاهد الدورة: بيانات، صفقات، عمولات، وربط قنوات.
              </p>
            </div>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <p className="hidden max-w-md text-right text-xs leading-relaxed text-slate-300/95 sm:block md:text-sm">
              تفاعل مع الفيديو: إيقاف مؤقت، كتم، أو افتح مركز التحميل للمواد الكاملة.
            </p>
            <div className="pointer-events-auto flex flex-wrap items-center justify-end gap-2 sm:ms-auto">
              <Link
                href="/resources"
                onClick={(e) => e.stopPropagation()}
                className="inline-flex items-center gap-2 rounded-2xl bg-white px-4 py-2.5 text-xs font-bold text-slate-900 shadow-lg transition hover:bg-slate-100 md:px-5 md:text-sm"
              >
                مركز التحميل الكامل
                <ChevronDown className="h-4 w-4 rotate-[-90deg]" aria-hidden />
              </Link>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  togglePlay();
                }}
                className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-white/15 bg-white/10 text-white backdrop-blur-md transition hover:bg-white/20"
                aria-label={paused ? "تشغيل" : "إيقاف مؤقت"}
              >
                {paused ? <Play className="h-5 w-5" /> : <Pause className="h-5 w-5" />}
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleMute();
                }}
                className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-white/15 bg-white/10 text-white backdrop-blur-md transition hover:bg-white/20"
                aria-label={muted ? "تشغيل الصوت" : "كتم الصوت"}
              >
                {muted ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>

        <AnimatePresence>
          {hover && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="pointer-events-none absolute inset-x-0 top-1/2 flex -translate-y-1/2 justify-center"
            >
              <span className="rounded-full border border-teal-500/40 bg-teal-500/15 px-4 py-1.5 text-xs font-semibold text-teal-100 backdrop-blur-md">
                لوب احترافي — مرّر للتحكم
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
