import { test, expect, type Page } from "@playwright/test";
import { TEST_ORIGIN } from "./test-origin";

const OK_STATUSES = [200, 204, 301, 302, 303, 307, 308];

/**
 * جمع روابط داخلية من صفحة (مسارات فقط — بدون #fragment كطلب HTTP منفصل).
 */
async function internalPathsFromPage(page: Page, url: string): Promise<string[]> {
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForSelector('a[href^="/"]', { timeout: 30_000 });
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  return page.$$eval("a[href]", (anchors) => {
    const out = new Set<string>();
    for (const a of anchors) {
      const h = a.getAttribute("href");
      if (!h) continue;
      if (h.startsWith("mailto:") || h.startsWith("tel:")) continue;
      if (h.startsWith("https://wa.me") || h.startsWith("http://wa.me")) continue;
      if (h.startsWith("/")) {
        const path = h.split("#")[0];
        if (path && path.length > 0) out.add(path);
      }
    }
    return [...out];
  });
}

async function expectPathReachable(
  page: Page,
  path: string,
  requestBase: string
): Promise<void> {
  const res = await page.request.get(`${requestBase}${path}`, {
    maxRedirects: 0,
  });
  const st = res.status();
  if (OK_STATUSES.includes(st)) return;
  const resFollow = await page.request.get(`${requestBase}${path}`);
  const followSt = resFollow.status();
  /** وكيل Next → FastAPI: 502 متوقع في e2e عندما لا يعمل الباكند على الجهاز. */
  if (path.startsWith("/api/") && (followSt === 502 || followSt === 503)) return;
  expect(
    OK_STATUSES.includes(followSt),
    `${path}: first=${st} follow=${followSt}`
  ).toBeTruthy();
}

test.describe("Full site — route smoke (كل الصفحات المعروفة)", () => {
  const routes: { path: string; mustContain?: RegExp }[] = [
    { path: "/", mustContain: /لماذا Dealix/ },
    { path: "/landing" },
    { path: "/marketers", mustContain: /بوابة|مسوّق|Dealix/ },
    { path: "/marketers/team" },
    { path: "/marketers/deals" },
    { path: "/marketers/account", mustContain: /حساب المسوّق/ },
    { path: "/resources" },
    { path: "/help", mustContain: /الدعم|Dealix/ },
    { path: "/strategy" },
    { path: "/investors" },
    { path: "/login", mustContain: /تسجيل الدخول/ },
    { path: "/register", mustContain: /إنشاء حساب/ },
    { path: "/dealix-marketing/dashboard-guide" },
    { path: "/dealix-marketing/arsenal" },
    { path: "/dealix-marketing/company-profile" },
    { path: "/dealix-marketing/enterprise-pitch" },
    { path: "/dealix-marketing/real-estate" },
    { path: "/dealix-marketing/medical" },
    { path: "/dealix-marketing/industrial-logistics" },
    { path: "/dealix-marketing/index.html" },
    { path: "/dealix-presentations/00-dealix-company-master-ar.html" },
  ];

  for (const { path, mustContain } of routes) {
    test(`GET ${path}`, async ({ page }) => {
      await page.goto(path, { waitUntil: "domcontentloaded" });
      await expect(page.locator("body")).toBeVisible();
      if (mustContain) {
        await expect(page.getByText(mustContain).first()).toBeVisible({ timeout: 15_000 });
      }
    });
  }

  test("GET /dashboard يعيد توجيه غير المصادق إلى /login", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForURL(/\/login/, { timeout: 20_000 });
    await expect(page).toHaveURL(/\/login/);
  });

  test("GET /dealix-marketing (بدون index) يعيد التوجيه إلى index.html", async ({ page }) => {
    const r = await page.request.get(`${TEST_ORIGIN}/dealix-marketing`, {
      maxRedirects: 0,
    });
    expect([301, 302, 303, 307, 308]).toContain(r.status());
    await page.goto("/dealix-marketing");
    await expect(page).toHaveURL(/index\.html/);
  });

  test("GET /dealix-presentations يعيد التوجيه إلى العرض الرئيسي", async ({ page }) => {
    await page.goto("/dealix-presentations");
    await expect(page).toHaveURL(/dealix-company-master/);
  });

  test("middleware: طلب .md للدليل يعيد التوجيه إلى dashboard-guide", async ({ page }) => {
    const r = await page.request.get(
      `${TEST_ORIGIN}/dealix-marketing/Dealix_Dashboard_Guide_AR.md`,
      { maxRedirects: 0 }
    );
    expect([301, 302, 303, 307, 308]).toContain(r.status());
    const loc = r.headers()["location"] || "";
    expect(loc).toContain("dashboard-guide");
  });
});

test.describe("الصفحة الرئيسية — روابط داخلية تستجيب", () => {
  test("روابط من / تُرجع حالة مقبولة", async ({ page }) => {
    const base = TEST_ORIGIN;
    const paths = await internalPathsFromPage(page, "/");
    expect(paths.length, "يجب أن توجد روابط داخلية").toBeGreaterThan(3);
    for (const p of paths) {
      await expectPathReachable(page, p, base);
    }
  });

  test("شريط التنقل: الموارد، المسوّقون، الاستراتيجية، دخول المنصة", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: /التحميلات|موارد/ }).first().click();
    await expect(page).toHaveURL(/\/resources/);

    await page.goto("/");
    await page.getByRole("navigation").getByRole("link", { name: /المسوّقون/ }).click();
    await expect(page).toHaveURL(/\/marketers/);

    await page.goto("/");
    await page.getByRole("navigation").getByRole("link", { name: /الاستراتيجية/ }).click();
    await expect(page).toHaveURL(/\/strategy/);

    await page.goto("/");
    await page.getByRole("link", { name: /دخول المنصة/ }).first().click();
    await expect(page).toHaveURL(/\/login/);
  });

  test("تذييل: دليل لوحة التحكم والموارد وبوابة المسوّقين", async ({ page }) => {
    await page.goto("/");
    const foot = page.locator("footer");
    await foot.locator('a[href="/dealix-marketing/dashboard-guide"]').scrollIntoViewIfNeeded();
    await foot.locator('a[href="/dealix-marketing/dashboard-guide"]').click({ force: true });
    await expect(page).toHaveURL(/\/dealix-marketing\/dashboard-guide/);

    await page.goto("/");
    await foot.locator('a[href="/resources"]').scrollIntoViewIfNeeded();
    await foot.locator('a[href="/resources"]').click({ force: true });
    await expect(page).toHaveURL(/\/resources/);

    await page.goto("/");
    await foot.locator('a[href="/marketers"]').scrollIntoViewIfNeeded();
    await foot.locator('a[href="/marketers"]').click({ force: true });
    await expect(page).toHaveURL(/\/marketers/);
  });

  test("مساعد الشركات: فتح، سؤال سريع، إغلاق", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "فتح مساعد Dealix" }).click();
    await expect(page.getByRole("dialog", { name: "مساعد الشركات" })).toBeVisible();
    await page.getByRole("button", { name: "ماذا يوجد في لوحة التحكم؟" }).click();
    const dlg = page.getByRole("dialog", { name: "مساعد الشركات" });
    await expect(dlg.getByText(/لوحة|تبويب|مسار|صفقة|وكلاء/, { exact: false }).first()).toBeVisible({
      timeout: 20_000,
    });
    await page.getByRole("button", { name: "إغلاق" }).first().click();
    await expect(page.getByRole("dialog", { name: "مساعد الشركات" })).toBeHidden();
  });
});

test.describe("بوابة المسوّقين — تنقّل ومساعد", () => {
  test("شريط الترويسة: الرئيسية، فريقي، الصفقات، حسابي، تسجيل، دخول", async ({ page }) => {
    await page.goto("/marketers");
    await page.getByRole("link", { name: "فريقي" }).click();
    await expect(page).toHaveURL(/\/marketers\/team/);

    await page.getByRole("link", { name: "الصفقات والعمولات" }).click();
    await expect(page).toHaveURL(/\/marketers\/deals/);

    await page.getByRole("link", { name: "حسابي" }).click();
    await expect(page).toHaveURL(/\/marketers\/account/);

    await page.getByRole("link", { name: "الرئيسية" }).click();
    await expect(page).toHaveURL(/\/marketers$/);

    await page.locator('header a[href="/register?next=%2Fmarketers"]').click();
    await expect(page).toHaveURL(/\/register/);

    await page.goto("/marketers");
    await page.getByRole("link", { name: "دخول المنصة" }).click();
    await expect(page).toHaveURL(/\/login/);
  });

  test("روابط من /marketers", async ({ page }) => {
    const base = TEST_ORIGIN;
    const paths = await internalPathsFromPage(page, "/marketers");
    expect(paths.length).toBeGreaterThan(5);
    for (const p of paths) {
      await expectPathReachable(page, p, base);
    }
  });

  test("مساعد المسوّقين: فتح وإرسال نص محلي", async ({ page }) => {
    await page.goto("/marketers");
    await page.getByRole("button", { name: "فتح مساعد Dealix" }).click();
    await expect(page.getByRole("dialog", { name: "مساعد الشركاء" })).toBeVisible();
    await page.getByPlaceholder("اكتب سؤالك…").fill("أين عروض القطاعات؟");
    await page.getByRole("button", { name: "إرسال" }).click();
    await expect(page.getByText(/عرض|قطاع|HTML|dealix-presentations/i).first()).toBeVisible({
      timeout: 20_000,
    });
  });
});

test.describe("موارد ومساعدة", () => {
  test("صفحة الموارد: روابط داخلية تستجيب", async ({ page }) => {
    const base = TEST_ORIGIN;
    const paths = await internalPathsFromPage(page, "/resources");
    expect(paths.length).toBeGreaterThan(3);
    for (const p of paths) {
      await expectPathReachable(page, p, base);
    }
  });

  test("نقر على بطاقة سكربتات الفيديو", async ({ page }) => {
    await page.goto("/resources");
    await page.getByRole("link", { name: /سكربتات فيديو|إطار إنتاج/ }).click();
    await expect(page).toHaveURL(/Dealix_Video_Scripts_Master_AR\.md/);
  });
});

test.describe("API المساعد", () => {
  test("POST /api/assistant/intake يعيد JSON", async ({ request }) => {
    const res = await request.post("/api/assistant/intake", {
      data: { message: "اختبار", variant: "company" },
    });
    expect(res.ok()).toBeTruthy();
    const j = (await res.json()) as { ok?: boolean };
    expect(j).toHaveProperty("ok");
  });

  test("POST بدون رسالة = 400", async ({ request }) => {
    const res = await request.post("/api/assistant/intake", {
      data: { variant: "marketer" },
    });
    expect(res.status()).toBe(400);
  });
});

test.describe("/landing تفاعلات أساسية", () => {
  test("تبديل اللغة EN/عربي", async ({ page }) => {
    await page.goto("/landing");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    const btn = page.getByRole("button", { name: /^EN$|^عربي$/ });
    await btn.click();
    await btn.click();
  });
});
