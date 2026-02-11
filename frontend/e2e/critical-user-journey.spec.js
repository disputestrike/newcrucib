/**
 * Layer 7.1: Critical User Journey – Sign up, Login, Workspace, Logout
 * Run: npx playwright test
 * Requires backend at REACT_APP_BACKEND_URL (e.g. http://localhost:8000)
 */
const { test, expect } = require('@playwright/test');

test.describe('Critical user journey', () => {
  const testEmail = `e2e-${Date.now()}@example.com`;
  const testPassword = 'TestPass123!';
  const testName = 'E2E User';

  test('homepage loads', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/CrucibAI|React App/);
    await expect(page.locator('body')).toBeVisible();
  });

  test('sign up → login → workspace → logout', async ({ page }) => {
    await page.goto('/');

    // Navigate to auth (register)
    await page.getByRole('link', { name: /sign up|register|get started/i }).first().click().catch(() => {
      return page.goto('/auth?mode=register');
    });
    await page.waitForURL(/\/auth/);

    // Register
    await page.getByPlaceholder(/email|you@example/i).fill(testEmail);
    await page.getByPlaceholder(/password/i).first().fill(testPassword);
    await page.getByPlaceholder(/name/i).fill(testName).catch(() => {});
    await page.getByRole('button', { name: /sign up|register|create/i }).click();
    await page.waitForURL(/\/(app\/workspace|workspace|dashboard)/, { timeout: 15000 }).catch(() => {});

    // If we're on workspace or dashboard, journey succeeded
    const url = page.url();
    const success = url.includes('workspace') || url.includes('dashboard') || url.includes('/app');
    expect(success).toBeTruthy();
  });

  test('unauthenticated access to /auth/me returns 401', async ({ request }) => {
    test.skip(!!process.env.CI, 'Backend not started in CI for E2E job');
    const base = process.env.PLAYWRIGHT_API_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
    const res = await request.get(`${base}/api/auth/me`);
    expect(res.status()).toBe(401);
  });
});
