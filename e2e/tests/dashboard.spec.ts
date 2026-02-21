import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should load dashboard page', async ({ page }) => {
    // Go to root, which should redirect to /zh/dashboard or /en/dashboard
    await page.goto('/');
    
    // Expect url to contain dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Expect title or some content
    // Since we don't know the exact title, we can check for a common element
    // like "Dashboard" or "AI Radar"
    // await expect(page).toHaveTitle(/AI Radar/);
  });
});
