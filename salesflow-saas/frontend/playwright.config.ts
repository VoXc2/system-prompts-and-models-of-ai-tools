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
    baseURL: "http://127.0.0.1:3000",
    trace: "on-first-retry",
  },
  // `next dev` works without a prior `next build`; set PW_WEB_SERVER=standalone to use `.next/standalone/server.js` after build.
  webServer: {
    command:
      process.env.PW_WEB_SERVER === "standalone"
        ? "node .next/standalone/server.js"
        : "npx next dev -H 127.0.0.1 -p 3000",
    url: "http://127.0.0.1:3000",
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
  },
});
