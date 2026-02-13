import { test, expect } from '@playwright/test';
import { SourcesPage } from '../pages/sources.page';
import { ContentPage } from '../pages/content.page';

test.describe('Iteration 2: Full Source Perception', () => {
  
  test('should manage information sources', async ({ page }) => {
    // Mock Data State
    const sources = [
        { id: '1', name: 'Existing Source', url: 'https://example.com/rss', type: 'rss', status: 'ACTIVE', last_crawled_at: null }
    ];

    // Mock API Interception
    await page.route('**/api/v1/sources', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
            json: { success: true, data: { items: sources, total: sources.length } }
        });
      } else if (route.request().method() === 'POST') {
        const data = route.request().postDataJSON();
        const newSource = { 
            id: String(sources.length + 1), 
            ...data, 
            status: 'ACTIVE', 
            last_crawled_at: null 
        };
        sources.push(newSource);
        await route.fulfill({ json: { success: true, data: newSource } });
      }
    });

    await page.route('**/api/v1/sources/*/crawl', async route => {
        await route.fulfill({
            json: { success: true, data: { items_new: 5 } }
        });
    });

    const sourcesPage = new SourcesPage(page);
    await sourcesPage.goto();

    // 1. Verify existing source list
    await sourcesPage.expectSourceVisible('Existing Source');

    // 2. Add new source
    // Note: 'rss' (lowercase) in mock might need to match select option values if they are case sensitive.
    // SourcesPage select options are 'RSS', 'SITEMAP', 'WEB'. 
    // The test passes 'rss', need to check if select handles case or if I should pass 'RSS'.
    // Looking at sources.page.ts: await this.typeSelect.selectOption(type);
    // Looking at frontend/src/app/sources/page.tsx: <option value="RSS">RSS</option>
    // So it should be uppercase 'RSS'.
    await sourcesPage.createSource('TechCrunch AI', 'https://techcrunch.com/category/artificial-intelligence/feed/', 'RSS');
    
    // 3. Verify new source appears in list
    await sourcesPage.expectSourceVisible('TechCrunch AI');

    // 4. Trigger Crawl
    await sourcesPage.crawlSource('TechCrunch AI');
  });

  test('should display crawled contents', async ({ page }) => {
     // Mock Contents API
     await page.route('**/api/v1/contents*', async route => {
        await route.fulfill({
            json: {
                success: true,
                data: {
                    items: [
                        { 
                            id: 'c1', 
                            title: 'DeepSeek releases new model', 
                            url: 'https://example.com/news/1', 
                            summary: 'A new open source model is out.', 
                            status: 'PROCESSED', 
                            publish_time: new Date().toISOString() 
                        },
                        { 
                            id: 'c2', 
                            title: 'OpenAI update', 
                            url: 'https://example.com/news/2', 
                            summary: 'ChatGPT gets smarter.', 
                            status: 'NEW', 
                            publish_time: new Date().toISOString() 
                        }
                    ],
                    total: 2
                }
            }
        });
     });

     const contentPage = new ContentPage(page);
     await contentPage.goto();

     // Verify contents are visible
     await contentPage.expectContentVisible('DeepSeek releases new model');
     await contentPage.expectContentVisible('OpenAI update');
  });

});
