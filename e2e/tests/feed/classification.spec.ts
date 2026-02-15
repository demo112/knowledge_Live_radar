import { test, expect } from '../../fixtures';

test.describe('Feed - Content Auto-Classification', () => {
  test.beforeEach(async ({ page }) => {
    // We will navigate manually in tests to allow route setup
  });

  test('should display AI-classified content after crawling', async ({ sourcesPage, feedPage, page }) => {
    // 1. Mock Source Creation and List
    const sourceName = 'Test AI Source';
    const sourceUrl = 'http://example.com/rss';
    
    // Mock GET /api/v1/sources
    await page.route('**/api/v1/sources*', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              items: [
                {
                  id: 'src-1',
                  name: sourceName,
                  url: sourceUrl,
                  type: 'RSS',
                  status: 'active',
                  last_check_time: null
                }
              ],
              total: 1,
              page: 1,
              size: 20
            }
          })
        });
      } else if (route.request().method() === 'POST') {
        // Mock creation
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { id: 'src-1', name: sourceName, url: sourceUrl, type: 'RSS' }
          })
        });
      } else {
        await route.continue();
      }
    });

    // Mock Crawl Trigger
    await page.route('**/api/v1/sources/*/crawl', async route => {
       await route.fulfill({
         status: 200,
         contentType: 'application/json',
         body: JSON.stringify({ 
           success: true, 
           message: 'Crawl started',
           data: { items_new: 5 }
         })
       });
    });

    // 2. Add Source (Visual only since we mock list)
    await sourcesPage.goto();
    // Wait for the mock to be hit
    await page.waitForResponse(response => response.url().includes('/api/v1/sources') && response.status() === 200);
    
    await sourcesPage.expectSourceVisible(sourceName);

    // 3. Trigger Crawl
    await sourcesPage.crawlSource(sourceName);

    // 4. Navigate to Feed and verify AI content
    // Mock GET /api/v1/contents with AI data
    await page.route('**/api/v1/contents*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            items: [
              {
                id: 'content-1',
                title: 'AI Revolution in 2026',
                url: 'http://example.com/ai-2026',
                summary: 'This is an AI generated summary of the article.',
                content_text: 'Full text...',
                tags: ['Artificial Intelligence', 'Future'],
                ai_processed: true,
                publish_time: new Date().toISOString(),
                source_id: 'src-1',
                validation_result: { overall_score: 95 }
              }
            ],
            total: 1,
            page: 1,
            size: 20
          }
        })
      });
    });

    await feedPage.goto();
    await feedPage.expectContentVisible('AI Revolution in 2026');
    await feedPage.expectAISummaryVisible('AI Revolution in 2026');
    // Note: The FeedPage method might need adjustment if it looks for specific text "AI 摘要" which might be in Chinese or English depending on locale.
    // My FeedPage implementation looks for "AI 摘要".
  });
});
