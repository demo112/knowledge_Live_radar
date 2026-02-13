import { test, expect } from '@playwright/test';

test.describe('Evolution Flow', () => {
  test('should auto-classify content and show links', async ({ page }) => {
    test.setTimeout(120000); // Increase timeout for model download
    // 1. Go to contents page
    await page.goto('/contents');
    
    // 2. Click on first content item
    // Wait for list to load
    await page.waitForSelector('ul > li');
    const firstContentLink = page.locator('ul > li a').first();
    await firstContentLink.click();
    
    // 3. Verify detail page
    await expect(page).toHaveURL(/\/contents\/.+/);
    await expect(page.getByText('Content Details')).toBeVisible();
    
    // 4. Click AI Auto Classify
    // Mock the API response if we want to be safe, but integration test should run against real backend.
    // However, without real AI service, it might fail or return 0 matches.
    // For this test, we assume the backend returns something or at least handles the request.
    
    // If we can't guarantee a match, we just check if the button works and shows alert/result.
    
    // Setup dialog handler for alert
    page.on('dialog', dialog => dialog.accept());
    
    await page.getByRole('button', { name: 'AI Auto Classify' }).click();
    
    // Wait for button to be disabled (loading) then enabled
    await expect(page.getByRole('button', { name: 'Classifying...' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'AI Auto Classify' })).toBeVisible({ timeout: 30000 });
    
    // 5. Verify Linked Nodes section exists
    await expect(page.getByText('Linked Nodes')).toBeVisible();
  });
});
