import { test, expect } from "@playwright/test";

test("homepage shows competitive moat section", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#market-moat")).toBeVisible();
  await expect(page.getByRole("heading", { name: /لماذا ليس/ })).toBeVisible();
});
