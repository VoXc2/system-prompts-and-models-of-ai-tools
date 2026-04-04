import { test, expect } from "@playwright/test";

test.describe("Auth & shell", () => {
  test("login page renders Arabic heading and form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /تسجيل الدخول/ })).toBeVisible();
    await expect(page.getByLabel(/البريد الإلكتروني/)).toBeVisible();
    await expect(page.getByRole("button", { name: /دخول/ })).toBeVisible();
  });

  test("register page renders", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("heading", { name: /إنشاء حساب شركة/ })).toBeVisible();
  });

  test("dashboard redirects unauthenticated user to login", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForURL(/\/login/, { timeout: 15_000 });
    await expect(page).toHaveURL(/\/login/);
  });

  test("deep dashboard path preserves next query for return after login", async ({ page }) => {
    await page.goto("/dashboard/pipeline");
    await page.waitForURL(/\/login/, { timeout: 15_000 });
    const u = new URL(page.url());
    expect(u.pathname).toBe("/login");
    expect(u.searchParams.get("next")).toBe("/dashboard/pipeline");
  });

  test("session cookie alone does not bypass client auth (redirects to login without JWT)", async ({
    page,
    context,
  }) => {
    await context.addCookies([
      {
        name: "dealix_has_session",
        value: "1",
        url: "http://127.0.0.1:3000/",
      },
    ]);
    await page.goto("/dashboard");
    await page.waitForURL(/\/login/, { timeout: 15_000 });
    await expect(page).toHaveURL(/\/login/);
  });
});
