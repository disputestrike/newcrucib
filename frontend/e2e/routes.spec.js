/**
 * Fortune 100 Layer 8: Full route coverage – every public route loads without crash.
 */
const { test, expect } = require('@playwright/test');

const PUBLIC_ROUTES = [
  { path: '/', name: 'Landing' },
  { path: '/auth', name: 'Auth' },
  { path: '/pricing', name: 'Pricing' },
  { path: '/about', name: 'About' },
  { path: '/terms', name: 'Terms' },
  { path: '/privacy', name: 'Privacy' },
  { path: '/aup', name: 'AUP' },
  { path: '/dmca', name: 'DMCA' },
  { path: '/cookies', name: 'Cookies' },
  { path: '/enterprise', name: 'Enterprise' },
  { path: '/features', name: 'Features' },
  { path: '/templates', name: 'Templates public' },
  { path: '/patterns', name: 'Patterns public' },
  { path: '/learn', name: 'Learn public' },
  { path: '/shortcuts', name: 'Shortcuts public' },
  { path: '/prompts', name: 'Prompts public' },
  { path: '/benchmarks', name: 'Benchmarks' },
];

for (const { path, name } of PUBLIC_ROUTES) {
  test(`${name} (${path}) loads`, async ({ page }) => {
    const res = await page.goto(path, { waitUntil: 'domcontentloaded', timeout: 15000 });
    expect(res?.status()).toBeLessThan(500);
    await expect(page.locator('body')).toBeVisible();
    const root = page.locator('#root');
    await expect(root).toBeVisible();
  });
}

test('admin route /app/admin loads or redirects to auth', async ({ page }) => {
  const res = await page.goto('/app/admin', { waitUntil: 'domcontentloaded', timeout: 15000 });
  expect(res?.status()).toBeLessThan(500);
  const url = page.url();
  expect(url.includes('/app/admin') || url.includes('/auth')).toBeTruthy();
  await expect(page.locator('body')).toBeVisible();
});
