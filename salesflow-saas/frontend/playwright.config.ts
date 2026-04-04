import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? "github" : "list",
  use: {
    ...devices["Desktop Chrome"],
    /** منفذ مخصص للاختبار لتفادي تعارض مع `next dev` يدوي أو خدمات أخرى على 3000. */
    baseURL: process.env.PW_PORT ? `http://127.0.0.1:${process.env.PW_PORT}` : "http://127.0.0.1:3001",
    trace: "on-first-retry",
  },
  // `next dev` works without a prior `next build`; set PW_WEB_SERVER=standalone to use `.next/standalone/server.js` after build.
  webServer: {
    command:
      process.env.PW_WEB_SERVER === "standalone"
        ? "node .next/standalone/server.js"
        : `npx next dev -H 127.0.0.1 -p ${process.env.PW_PORT || "3001"}`,
    url: `http://127.0.0.1:${process.env.PW_PORT || "3001"}`,
    /** أول تشغيل لـ `next dev` قد يتجاوز دقيقتين على أجهزة بطيئة أو باردات كاش. */
    timeout: 300_000,
    /** إذا كان CI=true وشغّلت `next dev` على 3000، عطّل CI محلياً أو أوقف الخادم اليدوي. */
    reuseExistingServer: process.env.CI !== "true",
  },
});
