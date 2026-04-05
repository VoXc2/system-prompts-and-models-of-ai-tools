"use client";

import { useId } from "react";
import { motion, useReducedMotion } from "framer-motion";

/** أربعة أعمدة تصاعدية + حركة «نبض إيراد» — تدرج أزرق → سماوي → تركواز */
function ProfitPulseBars({ reducedMotion }: { reducedMotion: boolean }) {
  const gradId = useId().replace(/:/g, "");
  const bars = [
    { min: 5, max: 9, delay: 0 },
    { min: 7, max: 12, delay: 0.12 },
    { min: 9, max: 15, delay: 0.24 },
    { min: 11, max: 19, delay: 0.36 },
  ];

  return (
    <div
      className="relative flex h-[22px] w-[28px] items-end justify-center gap-[3px]"
      aria-hidden
    >
      {/* خط اتجاه صاعد خفيف — يرمز للربح دون ازدحام */}
      <svg
        className="pointer-events-none absolute -right-0.5 -top-1 h-7 w-7 opacity-[0.22] transition-opacity duration-300 group-hover:opacity-[0.38]"
        viewBox="0 0 32 32"
        fill="none"
      >
        <path
          d="M4 24 L12 16 L20 18 L28 8"
          stroke={`url(#profitLine-${gradId})`}
          strokeWidth="1.25"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <defs>
          <linearGradient id={`profitLine-${gradId}`} x1="4" y1="24" x2="28" y2="8" gradientUnits="userSpaceOnUse">
            <stop stopColor="#38bdf8" />
            <stop offset="1" stopColor="#2dd4bf" />
          </linearGradient>
        </defs>
      </svg>

      {bars.map((b, i) => (
        <motion.div
          key={i}
          className="relative w-[3px] rounded-[1px] bg-gradient-to-t from-sky-800 via-sky-400 to-teal-200 shadow-[0_0_10px_rgba(56,189,248,0.45)] ring-1 ring-white/10 transition-[filter] duration-300 group-hover:shadow-[0_0_14px_rgba(45,212,191,0.55)]"
          style={{ originY: 1 }}
          initial={{ height: b.min }}
          animate={
            reducedMotion
              ? { height: (b.min + b.max) / 2 }
              : {
                  height: [b.min, b.max, b.max * 0.92, b.min + (b.max - b.min) * 0.75, b.max],
                }
          }
          transition={{
            duration: 2.6,
            repeat: reducedMotion ? 0 : Infinity,
            ease: "easeInOut",
            delay: b.delay,
            times: [0, 0.28, 0.5, 0.72, 1],
          }}
        />
      ))}
    </div>
  );
}

/** شعار Dealix لصفحات الدخول والتسجيل — نمو/ربح بتدرج أزرق احترافي وتفاعل خفيف */
export function DealixAuthBrandMark() {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      className="group relative mx-auto flex h-[4.5rem] w-[4.5rem] cursor-default items-center justify-center"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      whileHover={reduceMotion ? undefined : { scale: 1.05 }}
      whileTap={reduceMotion ? undefined : { scale: 0.97 }}
      aria-label="Dealix — نمو الإيرادات"
    >
      <motion.div
        className="pointer-events-none absolute -inset-4 rounded-[1.35rem] bg-gradient-to-br from-sky-500/20 via-teal-500/25 to-cyan-500/15 blur-2xl"
        aria-hidden
        animate={
          reduceMotion ? { opacity: 0.42 } : { opacity: [0.32, 0.58, 0.36, 0.52, 0.32] }
        }
        transition={
          reduceMotion ? { duration: 0 } : { duration: 4.2, repeat: Infinity, ease: "easeInOut" }
        }
      />
      <motion.div
        className="absolute inset-0 rounded-2xl"
        style={{
          background:
            "conic-gradient(from 90deg at 50% 50%, #0ea5e9, #22d3ee, #2dd4bf, #38bdf8, #14b8a6, #0ea5e9)",
        }}
        aria-hidden
        animate={reduceMotion ? { rotate: 0 } : { rotate: 360 }}
        transition={
          reduceMotion ? { duration: 0 } : { duration: 18, repeat: Infinity, ease: "linear" }
        }
      />
      <motion.div
        className="absolute inset-[2px] flex items-center justify-center rounded-[14px] border border-white/[0.12] bg-gradient-to-b from-[#0b1220] to-[#030712] shadow-[inset_0_1px_0_rgba(255,255,255,0.06)] transition-[box-shadow,border-color] duration-300 group-hover:border-cyan-400/25 group-hover:shadow-[inset_0_0_24px_rgba(34,211,238,0.12),inset_0_1px_0_rgba(255,255,255,0.08)]"
        whileHover={reduceMotion ? undefined : { scale: 1.02 }}
        transition={{ type: "spring", stiffness: 420, damping: 28 }}
      >
        <ProfitPulseBars reducedMotion={!!reduceMotion} />
      </motion.div>
      <span
        className="pointer-events-none absolute -left-0.5 -top-0.5 h-2.5 w-2.5 rounded-tl-md border-l-2 border-t-2 border-sky-400/90 transition-colors duration-300 group-hover:border-teal-300"
        aria-hidden
      />
      <span
        className="pointer-events-none absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-tr-md border-r-2 border-t-2 border-sky-400/90 transition-colors duration-300 group-hover:border-cyan-300"
        aria-hidden
      />
      <span
        className="pointer-events-none absolute -bottom-0.5 -left-0.5 h-2.5 w-2.5 rounded-bl-md border-b-2 border-l-2 border-cyan-400/80 transition-colors duration-300 group-hover:border-teal-400/90"
        aria-hidden
      />
      <span
        className="pointer-events-none absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-br-md border-b-2 border-r-2 border-cyan-400/80 transition-colors duration-300 group-hover:border-sky-400/90"
        aria-hidden
      />
    </motion.div>
  );
}
