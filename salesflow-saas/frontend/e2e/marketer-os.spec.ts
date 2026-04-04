import { test, expect } from "@playwright/test";

const SAMPLE_ID = "123e4567-e89b-12d3-a456-426614174000";

test.describe("Marketer OS panel", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("http://127.0.0.1:8000/api/v1/affiliates/register", async (route) => {
      if (route.request().method() !== "POST") return route.continue();
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          id: SAMPLE_ID,
          full_name: "مسوّق اختبار",
          email: "os-e2e@dealix.test",
          phone: "0500000000",
          status: "pending",
          referral_code: "DLX-E2E001",
          total_deals_closed: 0,
          total_commission_earned: 0,
          current_month_deals: 0,
        }),
      });
    });

    await page.route(`http://127.0.0.1:8000/api/v1/affiliates/${SAMPLE_ID}`, async (route) => {
      if (route.request().method() !== "GET") return route.continue();
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: SAMPLE_ID,
          full_name: "مسوّق اختبار",
          email: "os-e2e@dealix.test",
          phone: "0500000000",
          status: "active",
          referral_code: "DLX-E2E001",
          total_deals_closed: 0,
          total_commission_earned: 0,
          current_month_deals: 0,
        }),
      });
    });

    await page.route(`http://127.0.0.1:8000/api/v1/affiliates/${SAMPLE_ID}/activate`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: SAMPLE_ID,
          full_name: "مسوّق اختبار",
          email: "os-e2e@dealix.test",
          phone: "0500000000",
          status: "active",
          referral_code: "DLX-E2E001",
          total_deals_closed: 0,
          total_commission_earned: 0,
          current_month_deals: 0,
        }),
      });
    });

    await page.route(`http://127.0.0.1:8000/api/v1/affiliates/${SAMPLE_ID}/deals`, async (route) => {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({ message: "Deal submitted successfully", commission: 44.85 }),
      });
    });
  });

  test("renders full OS panel and referral after mocked registration", async ({ page }) => {
    await page.goto("/marketers");
    await expect(page.getByTestId("marketer-os-panel")).toBeVisible();
    await expect(page.getByRole("heading", { name: /نظام التشغيل الكامل للمسوّق/ })).toBeVisible();

    await page.getByPlaceholder("البريد الإلكتروني").fill("os-e2e@dealix.test");
    await page.getByTestId("marketer-os-register").click();

    await expect(page.getByText("DLX-E2E001")).toBeVisible({ timeout: 10_000 });
  });
});
