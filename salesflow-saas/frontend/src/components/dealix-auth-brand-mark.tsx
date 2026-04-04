"use client";

import { motion, useReducedMotion } from "framer-motion";

/** أعمدة متحركة (شارت حي) — لوب لا نهائي مع إيقاف عند تقليل الحركة */
function AnimatedMarkBars({ reducedMotion }: { reducedMotion: boolean }) {
  const bars: { delay: number; heights: number[] }[] = [
    { delay: 0, heights: [6, 15, 9, 14, 7, 6] },
    { delay: 0.32, heights: [12, 7, 16, 10, 13, 12] },
    { delay: 0.64, heights: [9, 14, 8, 16, 11, 9] },
  ];

  return (
    <div
      className="flex h-[18px] w-[22px] items-end justify-center gap-[3px]"
      aria-hidden
    >
      {bars.map((b, i) => (
        <motion.div
          key={i}
          className="w-[3px] rounded-[1px] bg-teal-200 shadow-[0_0_10px_rgba(45,212,191,0.5)]"
          initial={{ height: b.heights[0] }}
          animate={
            reducedMotion
              ? { height: b.heights[2] }
              : { height: b.heights }
          }
          transition={{
            duration: 2.8,
            repeat: reducedMotion ? 0 : Infinity,
            ease: "easeInOut",
            delay: b.delay,
            times: [0, 0.18, 0.36, 0.55, 0.75, 1],
          }}
        />
      ))}
    </div>
  );
}

/** شعار Dealix لصفحات الدخول والتسجيل — حدود تقنية دوّارة وتفاعل خفيف */
export function DealixAuthBrandMark() {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      className="relative mx-auto flex h-[4.5rem] w-[4.5rem] items-center justify-center"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      whileHover={reduceMotion ? undefined : { scale: 1.04 }}
      whileTap={reduceMotion ? undefined : { scale: 0.96 }}
      aria-label="Dealix"
    >
      <motion.div
        className="pointer-events-none absolute -inset-4 rounded-[1.35rem] bg-teal-500/25 blur-2xl"
        aria-hidden
        animate={reduceMotion ? { opacity: 0.45 } : { opacity: [0.35, 0.6, 0.35] }}
        transition={
          reduceMotion ? { duration: 0 } : { duration: 3.8, repeat: Infinity, ease: "easeInOut" }
        }
      />
      <motion.div
        className="absolute inset-0 rounded-2xl"
        style={{
          background:
            "conic-gradient(from 90deg at 50% 50%, #2dd4bf, #22d3ee, #34d399, #14b8a6, #2dd4bf)",
        }}
        aria-hidden
        animate={reduceMotion ? { rotate: 0 } : { rotate: 360 }}
        transition={
          reduceMotion ? { duration: 0 } : { duration: 16, repeat: Infinity, ease: "linear" }
        }
      />
      <div className="absolute inset-[2px] flex items-center justify-center rounded-[14px] border border-white/[0.12] bg-gradient-to-b from-[#0b1220] to-[#030712] shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
        <AnimatedMarkBars reducedMotion={!!reduceMotion} />
      </div>
      <span
        className="pointer-events-none absolute -left-0.5 -top-0.5 h-2.5 w-2.5 rounded-tl-md border-l-2 border-t-2 border-teal-400/90"
        aria-hidden
      />
      <span
        className="pointer-events-none absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-tr-md border-r-2 border-t-2 border-teal-400/90"
        aria-hidden
      />
      <span
        className="pointer-events-none absolute -bottom-0.5 -left-0.5 h-2.5 w-2.5 rounded-bl-md border-b-2 border-l-2 border-cyan-400/80"
        aria-hidden
      />
      <span
        className="pointer-events-none absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-br-md border-b-2 border-r-2 border-cyan-400/80"
        aria-hidden
      />
    </motion.div>
  );
}
