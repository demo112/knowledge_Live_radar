import { test, expect } from '@playwright/test';
import { SourcePage } from '../pages/source.page';
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

    const sourcePage = new SourcePage(page);
    await sourcePage.goto();

    // 1. Verify existing source list
    await sourcePage.expectSourceVisible('Existing Source');

    // 2. Add new source
    await sourcePage.addSource('TechCrunch AI', 'https://techcrunch.com/category/artificial-intelligence/feed/', 'rss');
    
    // 3. Verify new source appears in list
    await sourcePage.expectSourceVisible('TechCrunch AI');

    // 4. Trigger Crawl
    // Setup dialog listener is inside triggerCrawl
    await sourcePage.triggerCrawl('TechCrunch AI');
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
