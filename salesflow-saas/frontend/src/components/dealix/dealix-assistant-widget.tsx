"use client";

import { useCallback, useRef, useState } from "react";
import Link from "next/link";
import { MessageCircle, Send, X, Sparkles, Loader2 } from "lucide-react";
import type { AssistantVariant } from "@/lib/dealix-assistant-knowledge";
import { matchLocalKnowledge } from "@/lib/dealix-assistant-knowledge";

type Msg = { role: "user" | "assistant"; text: string; links?: { label: string; href: string }[] };

const PRESETS: Record<AssistantVariant, string[]> = {
  marketer: [
    "كيف أشرح العمولات لعميل؟",
    "أين عروض القطاعات؟",
    "ما الفرق عن بوت واتساب؟",
  ],
  company: [
    "ماذا يوجد في لوحة التحكم؟",
    "لماذا Dealix أقوى من أداة عادية؟",
    "هل لديكم عروض لقطاعي؟",
  ],
  preview: [
    "ما الفرق بين الجولة والحساب الحقيقي؟",
    "اشرح لي التبويبات بالترتيب",
    "هل أحتاج دفعاً لأستكشف المنصة؟",
    "ماذا أرى بعد التسجيل؟",
  ],
};

function welcomeMessage(variant: AssistantVariant): string {
  if (variant === "marketer") {
    return "أنا مساعد Dealix للشركاء والمسوّقين. اسألني عن العمولات، العروض، الواتساب، أو لوحة التحكم — أو اختر سؤالاً سريعاً أدناه.";
  }
  if (variant === "preview") {
    return "أنا دليلك التفاعلي في جولة المنصة: اسأل عن أي تبويب، ماذا يتغيّر بعد التسجيل، أو الدفع — أو اختر سؤالاً جاهزاً. أجيب من معرفة محلية فورية، وأكمّل من الخادم عند توفره.";
  }
  return "أنا مساعد Dealix للشركات. اسألني عن القيمة، لوحة التحكم، القطاعات، الأمان، أو التجربة — أو اختر سؤالاً سريعاً.";
}

export function DealixAssistantWidget({ variant }: { variant: AssistantVariant }) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Msg[]>(() => [{ role: "assistant", text: welcomeMessage(variant) }]);
  const endRef = useRef<HTMLDivElement>(null);

  const scrollEnd = () => endRef.current?.scrollIntoView({ behavior: "smooth" });

  const pushAssistant = useCallback((text: string, links?: { label: string; href: string }[]) => {
    setMessages((m) => [...m, { role: "assistant", text, links }]);
    setTimeout(scrollEnd, 80);
  }, []);

  const send = useCallback(
    async (textRaw: string) => {
      const text = textRaw.trim();
      if (!text || loading) return;
      setMessages((m) => [...m, { role: "user", text }]);
      setInput("");
      setLoading(true);
      setTimeout(scrollEnd, 50);

      try {
        const res = await fetch("/api/assistant/intake", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text, variant }),
        });
        const data = (await res.json()) as { ok?: boolean; reply?: string };

        if (data.ok && data.reply && String(data.reply).length > 0) {
          pushAssistant(String(data.reply).trim());
        } else {
          const local = matchLocalKnowledge(variant, text);
          pushAssistant(local.reply, local.links);
        }
      } catch {
        const local = matchLocalKnowledge(variant, text);
        pushAssistant(local.reply, local.links);
      } finally {
        setLoading(false);
      }
    },
    [loading, pushAssistant, variant]
  );

  const title =
    variant === "marketer" ? "مساعد الشركاء" : variant === "preview" ? "دليل الجولة الذكي" : "مساعد الشركات";
  const sub =
    variant === "marketer" ? "Dealix Partner" : variant === "preview" ? "جولة + أسئلة سريعة" : "Dealix B2B";

  return (
    <div className="pointer-events-none fixed bottom-5 left-5 z-[60] flex flex-col items-start md:bottom-8 md:left-8">
      {open ? (
        <div
          className="pointer-events-auto mb-3 flex w-[min(100vw-2rem,420px)] flex-col overflow-hidden rounded-2xl border border-teal-500/35 bg-slate-950/95 shadow-2xl shadow-teal-900/40 backdrop-blur-xl"
          role="dialog"
          aria-label={title}
        >
          <div className="flex items-center justify-between border-b border-white/10 bg-gradient-to-l from-teal-900/50 to-slate-900/80 px-4 py-3">
            <div className="flex items-center gap-2 text-right">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-500/20 text-teal-300">
                <Sparkles className="h-5 w-5" aria-hidden />
              </span>
              <div>
                <p className="text-sm font-bold text-white">{title}</p>
                <p className="text-[10px] text-teal-200/80">{sub}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="rounded-lg p-1.5 text-slate-400 transition hover:bg-white/10 hover:text-white"
              aria-label="إغلاق"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="max-h-[min(52vh,440px)] space-y-3 overflow-y-auto px-3 py-3 text-right">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex flex-col gap-1 ${m.role === "user" ? "items-start" : "items-end"}`}
              >
                <div
                  className={`max-w-[95%] rounded-2xl px-3 py-2.5 text-sm leading-relaxed transition-all ${
                    m.role === "user"
                      ? "bg-teal-600/30 text-teal-50"
                      : "border border-white/10 bg-white/5 text-slate-200 shadow-sm"
                  }`}
                >
                  {m.text}
                </div>
                {m.links && m.links.length > 0 ? (
                  <div className="flex flex-wrap justify-end gap-1.5">
                    {m.links.map((l) => (
                      <Link
                        key={l.href}
                        href={l.href}
                        className="rounded-full border border-teal-500/30 bg-teal-950/50 px-2.5 py-1 text-[11px] font-semibold text-teal-200 hover:border-teal-400/50"
                      >
                        {l.label}
                      </Link>
                    ))}
                  </div>
                ) : null}
              </div>
            ))}
            {loading ? (
              <div className="flex items-center justify-end gap-2 text-teal-400/90" aria-live="polite">
                <span className="text-[11px] text-slate-500">جارٍ التفكير</span>
                <span className="inline-flex gap-1">
                  <span className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-teal-400 [animation-delay:-0.2s]" />
                  <span className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-teal-400 [animation-delay:-0.1s]" />
                  <span className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-teal-400" />
                </span>
                <Loader2 className="h-4 w-4 animate-spin opacity-60" aria-hidden />
              </div>
            ) : null}
            <div ref={endRef} />
          </div>

          <div className="max-h-[5.5rem] overflow-y-auto border-t border-white/5 px-2 py-2">
            <div className="flex flex-wrap justify-end gap-1.5">
              {PRESETS[variant].map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => send(p)}
                  disabled={loading}
                  className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] text-slate-300 hover:border-teal-500/30 hover:text-white disabled:opacity-50"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-2 border-t border-white/10 p-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send(input)}
              placeholder={variant === "preview" ? "اسأل عن تبويب أو قدرة…" : "اكتب سؤالك…"}
              className="min-w-0 flex-1 rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:border-teal-500/40 focus:outline-none"
              dir="rtl"
            />
            <button
              type="button"
              onClick={() => send(input)}
              disabled={loading || !input.trim()}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-teal-600 text-white shadow-lg shadow-teal-900/40 hover:bg-teal-500 disabled:opacity-40"
              aria-label="إرسال"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      ) : null}

      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="pointer-events-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-teal-500 to-emerald-700 text-white shadow-xl shadow-teal-900/50 transition hover:scale-105"
        aria-expanded={open}
        aria-label={open ? "إغلاق المساعد" : "فتح مساعد Dealix"}
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-7 w-7" />}
      </button>
    </div>
  );
}
