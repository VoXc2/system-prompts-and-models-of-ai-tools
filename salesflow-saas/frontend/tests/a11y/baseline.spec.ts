/**
 * V007 — Accessibility Baseline (Playwright + axe-core)
 *
 * Covers 5 critical routes in both LTR (en) and RTL (ar) locales.
 * Writes a combined JSON report to docs/baselines/a11y_YYYYMMDD.json.
 * Every future a11y claim references that file.
 *
 * Run:
 *   pnpm --filter frontend exec playwright test tests/a11y/baseline.spec.ts
 */
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs';
import path from 'node:path';

const ROUTES = [
  '/',
  '/login',
  '/deals',
  '/approvals',
  '/executive-room',
];

const LOCALES = ['en', 'ar'] as const;

type Result = {
  route: string;
  locale: string;
  violations: number;
  critical: number;
  serious: number;
};

const results: Result[] = [];

for (const locale of LOCALES) {
  for (const route of ROUTES) {
    test(`a11y: ${locale} ${route}`, async ({ page }) => {
      await page.goto(`${route}?locale=${locale}`);
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
        .analyze();

      const violations = accessibilityScanResults.violations;
      const critical = violations.filter(v => v.impact === 'critical').length;
      const serious = violations.filter(v => v.impact === 'serious').length;

      results.push({
        route,
        locale,
        violations: violations.length,
        critical,
        serious,
      });

      expect(critical, `Critical a11y violations on ${locale} ${route}`).toBe(0);
    });
  }
}

test.afterAll(async () => {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const outDir = path.resolve(__dirname, '../../../docs/baselines');
  fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, `a11y_${date}.json`);
  fs.writeFileSync(outFile, JSON.stringify({ date, results }, null, 2));
  // eslint-disable-next-line no-console
  console.log(`V007 baseline written to ${outFile}`);
});
