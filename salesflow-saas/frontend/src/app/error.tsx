"use client";

import { useEffect, useMemo } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const msg = error?.message ?? "";

  const isChunkLoad = useMemo(
    () =>
      /loading chunk/i.test(msg) ||
      /chunk load/i.test(msg) ||
      /failed to fetch dynamically imported module/i.test(msg) ||
      /app\/marketers\/page/i.test(msg) ||
      (/\bchunk\b/i.test(msg) && /failed/i.test(msg)),
    [msg]
  );

  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-2xl font-black tracking-tight">حدث خطأ غير متوقع</h1>
      {isChunkLoad ? (
        <p className="max-w-md text-sm leading-relaxed text-muted-foreground">
          تعذّر تحميل جزء من الكود (غالباً بعد تحديث أثناء التطوير). جرّب{" "}
          <strong className="text-foreground">تحديثاً كاملاً</strong> للصفحة (Ctrl+Shift+R) أو أعد
          تشغيل خادم التطوير. إذا استمرّت المشكلة، أعد المحاولة أدناه.
        </p>
      ) : (
        <p className="max-w-md text-sm text-muted-foreground">
          {msg || "تعذّر تحميل هذه الصفحة. يمكنك المحاولة مرة أخرى."}
        </p>
      )}
      <div className="flex flex-wrap items-center justify-center gap-3">
        <button
          type="button"
          onClick={() => reset()}
          className="rounded-xl bg-primary px-6 py-3 text-sm font-bold text-primary-foreground transition-colors hover:bg-primary/90"
        >
          إعادة المحاولة
        </button>
        {isChunkLoad && (
          <button
            type="button"
            onClick={() => {
              window.location.reload();
            }}
            className="rounded-xl border border-border bg-background px-6 py-3 text-sm font-bold text-foreground transition-colors hover:bg-muted"
          >
            تحديث الصفحة بالكامل
          </button>
        )}
      </div>
    </div>
  );
}
