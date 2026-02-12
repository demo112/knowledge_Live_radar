import { test, expect } from '../../fixtures';

test.describe('Sources Management', () => {
  test.beforeEach(async ({ sourcesPage }) => {
    await sourcesPage.goto();
    await sourcesPage.waitForLoad();
  });

  test('should allow creating a new source', async ({ sourcesPage, page }) => {
    const timestamp = Date.now();
    const name = `Test Source ${timestamp}`;
    const url = `https://example.com/rss/${timestamp}`;
    
    // Listen for dialogs (alert) as the current implementation uses alerts for success/failure
    page.on('dialog', async dialog => {
      console.log(`Dialog message: ${dialog.message()}`);
      await dialog.accept();
    });

    await sourcesPage.createSource(name, url, 'RSS');
    
    // Verify it appears in the list
    // Note: The frontend re-fetches after creation
    await sourcesPage.expectSourceVisible(name);
  });
});
