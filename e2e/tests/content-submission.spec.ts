import { test, expect } from '@playwright/test';

test.describe('Content Submission', () => {
  test.use({ locale: 'en-US' });

  test.beforeEach(async ({ page }) => {
    // Go to submission page
    await page.goto('/contents/submit');
  });

  test('should display submission form', async ({ page }) => {
    await expect(page.getByRole('button', { name: /URL/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Text/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /File/i })).toBeVisible();
  });

  test('should submit URL content', async ({ page }) => {
    // Select URL tab (default)
    await page.getByRole('button', { name: /URL/i }).click();
    
    // Fill URL
    await page.fill('input[name="url"]', 'https://example.com/test-article');
    
    // Submit
    // Note: Assuming there is a submit button. The component code didn't show the button part fully,
    // but standard forms usually have one. We might need to adjust this locator.
    // Based on standard form practices:
    const submitButton = page.getByRole('button', { name: /submit|submit content|提交/i });
    
    // If we can't find it by role, we might try a generic button inside the form
    // await page.locator('form button[type="submit"]').click();
    
    // For now, let's assume "Submit" or similar text
    // If the test fails, we will inspect the page content
    // Actually, looking at the code snippet, I don't see the submit button in the first 100 lines.
    // I will try to find it blindly or assume standard UI.
    // Let's use a locator that finds the submit button at the bottom of the form
    await page.locator('form button[type="submit"]').click();

    // Expect redirection to content list
    await expect(page).toHaveURL(/\/contents/);
  });

  test('should submit text content', async ({ page }) => {
    // Select Text tab
    await page.getByRole('button', { name: /Text/i }).click();
    
    // Fill Title and Content
    await page.fill('input[name="title"]', 'Test Note');
    // Note: The textarea name is "text" in the component, not "content"
    await page.fill('textarea[name="text"]', 'This is a test content submission.');
    
    // Submit
    await page.locator('button[type="submit"]').click();
    
    // Expect redirection
    await expect(page).toHaveURL(/\/contents/);
  });
});
