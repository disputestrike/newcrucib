/**
 * Layer 9 – Frontend smoke: app loads and key routes respond.
 */
const { test, expect } = require('@playwright/test');

test.describe('Smoke', () => {
  test('homepage loads and shows CrucibAI or main content', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/CrucibAI|React App/);
    const body = page.locator('body');
    await expect(body).toBeVisible();
    const root = page.locator('#root');
    await expect(root).toBeVisible();
  });

  test('auth page loads', async ({ page }) => {
    await page.goto('/auth');
    await expect(page).toHaveURL(/\/auth/);
    await expect(page.locator('body')).toBeVisible();
  });

  test('pricing or features page loads', async ({ page }) => {
    await page.goto('/pricing').catch(() => page.goto('/features'));
    await expect(page.locator('body')).toBeVisible();
  });
});
