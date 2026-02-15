import { test, expect } from '../../fixtures';

test.describe('Sources - Lifecycle Management', () => {
  test('should create and delete a source', async ({ sourcesPage, page }) => {
    const sourceName = 'Lifecycle Test Source';
    const sourceUrl = 'http://lifecycle.test/rss';
    
    // Stateful Mock Data
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let sources: any[] = [];

    // Mock GET and POST /api/v1/sources
    await page.route('**/api/v1/sources', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              items: sources,
              total: sources.length,
              page: 1,
              size: 20
            }
          })
        });
      } else if (route.request().method() === 'POST') {
        const postData = route.request().postDataJSON();
        const newSource = {
          ...postData,
          id: 'src-' + Date.now(),
          status: 'active',
          // Assuming template handling is done by frontend before sending, or backend defaults
          // Frontend sends: { name, url, type, config }
          // We just echo it back with ID
          type: postData.type || 'RSS'
        };
        sources.push(newSource);
        
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: newSource
          })
        });
      } else {
        await route.continue();
      }
    });

    // Mock DELETE /api/v1/sources/{id}
    await page.route('**/api/v1/sources/*', async route => {
      if (route.request().method() === 'DELETE') {
        const id = route.request().url().split('/').pop();
        sources = sources.filter(s => s.id !== id);
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true })
        });
      } else {
        await route.continue();
      }
    });

    // 1. Initial State: Empty
    await sourcesPage.goto();
    await expect(page.getByText('未找到信息源')).toBeVisible();

    // 2. Create Source
    await sourcesPage.createSource(sourceName, sourceUrl);
    
    // 3. Verify Visible
    await sourcesPage.expectSourceVisible(sourceName);

    // 4. Delete Source
    await sourcesPage.deleteSource(sourceName);
    
    // 5. Verify Gone
    await sourcesPage.expectSourceNotVisible(sourceName);
    await expect(page.getByText('未找到信息源')).toBeVisible();
  });
});
