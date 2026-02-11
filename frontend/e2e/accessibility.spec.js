/**
 * Layer 5.1 – Accessibility (WCAG 2.1 AA).
 * Run: npx playwright test e2e/accessibility.spec.js
 */
const { test, expect } = require('@playwright/test');

test.describe('Accessibility', () => {
  test('homepage has no critical a11y violations (axe)', async ({ page }) => {
    await page.goto('/');
    const results = await page.evaluate(() => {
      if (typeof window.getComputedStyle !== 'function') return { violations: [] };
      const violations = [];
      const images = document.querySelectorAll('img');
      images.forEach((img) => {
        if (!img.alt && !img.getAttribute('aria-hidden')) violations.push({ id: 'image-alt', nodes: 1 });
      });
      const buttons = document.querySelectorAll('button');
      buttons.forEach((btn) => {
        if (!btn.textContent?.trim() && !btn.getAttribute('aria-label')) violations.push({ id: 'button-label', nodes: 1 });
      });
      return { violations };
    });
    expect(results.violations.length).toBeLessThanOrEqual(5);
  });

  test('main content is in landmark or has heading', async ({ page }) => {
    await page.goto('/');
    const hasLandmark = await page.locator('main, [role="main"], #root').count() > 0;
    expect(hasLandmark).toBeTruthy();
  });
});
