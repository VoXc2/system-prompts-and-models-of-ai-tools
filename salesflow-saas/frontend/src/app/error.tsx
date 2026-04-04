"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 gap-4 text-center">
      <h1 className="text-2xl font-black tracking-tight">حدث خطأ غير متوقع</h1>
      <p className="text-sm text-muted-foreground max-w-md">
        {error.message || "تعذّر تحميل هذه الصفحة. يمكنك المحاولة مرة أخرى."}
      </p>
      <button
        type="button"
        onClick={() => reset()}
        className="rounded-xl bg-primary px-6 py-3 text-sm font-bold text-primary-foreground hover:bg-primary/90 transition-colors"
      >
        إعادة المحاولة
      </button>
    </div>
  );
}
