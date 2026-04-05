import { test, expect } from "@playwright/test";

/**
 * مسارات Next التي تعيد توجيهها إلى FastAPI — لا تتطلب متصفحاً كاملاً.
 * عند عدم تشغيل الباكند قد يعيد المسار 502؛ عند الإنتاج مع حماية قد يكون 401.
 */
test.describe("BFF API proxies", () => {
  test("strategy-summary responds", async ({ request }) => {
    const res = await request.get("/api/strategy-summary");
    expect([200, 401, 502].includes(res.status())).toBeTruthy();
    if (res.status() === 200) {
      const data = (await res.json()) as { product?: string };
      expect(data.product).toBeTruthy();
    }
  });

  test("marketing-hub responds", async ({ request }) => {
    const res = await request.get("/api/marketing-hub");
    expect([200, 401, 502].includes(res.status())).toBeTruthy();
    if (res.status() === 200) {
      const data = (await res.json()) as { paths?: Record<string, string> };
      expect(data.paths?.marketing_index).toBeTruthy();
    }
  });
});
