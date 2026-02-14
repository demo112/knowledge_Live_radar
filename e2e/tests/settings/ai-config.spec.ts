import { test, expect } from '../../fixtures';

test.describe('Settings - AI Configuration', () => {
  test.beforeEach(async ({ settingsPage }) => {
    await settingsPage.goto();
  });

  test('should allow modifying AI configuration and testing connection', async ({ settingsPage, page }) => {
    // Mock the connection test endpoint
    await page.route('**/api/v1/config/ai/test*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: 'Local AI 连接测试成功',
          latency_ms: 45,
          model: 'qwen2.5:7b'
        })
      });
    });

    // Mock GET all configs
    await page.route('**/api/v1/config', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                'ai.enabled': true,
                'ai.strategy': 'local_first',
                'ai.local.base_url': 'http://localhost:11434/v1',
                'ai.local.model': 'qwen2.5:7b',
                'ai.base_url': 'https://api.siliconflow.cn/v1',
                'ai.model': 'Qwen/Qwen2.5-7B-Instruct',
                'ai.api_key': 'sk-***',
                'ai.temperature': 0.7,
                'ai.max_retries': 3
            })
        });
      } else {
        await route.continue();
      }
    });

    // Mock the config update endpoints
    // The frontend calls PUT /api/v1/config/{key} for each field
    // We just need to ensure they return success
    await page.route('**/api/v1/config/*', async route => {
      if (route.request().method() === 'PUT') {
        const url = route.request().url();
        const key = url.split('/').pop();
        const postData = route.request().postDataJSON();
        
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            status: 'success',
            key: key,
            value: postData.value
          })
        });
      } else {
        await route.continue();
      }
    });

    // 1. Navigate to AI tab
    await settingsPage.switchToAITab();
    
    // 2. Select strategy
    await settingsPage.enableAI();
    await settingsPage.selectStrategy('local_first');
    
    // 3. Update Local AI settings
    const testUrl = 'http://localhost:11434/v1';
    const testModel = 'qwen2.5:7b';
    
    await settingsPage.setLocalConfig(testUrl, testModel);
    
    // 4. Test connection (Success case)
    await settingsPage.testConnection();
    await expect(settingsPage.testResult).toBeVisible();
    await expect(settingsPage.testResult).toContainText('连接成功');
    await expect(settingsPage.testResult).toContainText('Local AI 连接测试成功');
    
    // 5. Test connection (Failure case)
    await page.route('**/api/v1/config/ai/test*', async route => {
      await route.fulfill({
        status: 200, // The API returns 200 even on logical failure, usually? 
                     // Checking AITestService: it returns a dict. 
                     // The router returns it directly.
                     // Frontend handles the result.success check.
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          message: 'Connection refused',
          code: 'CONNECTION_FAILED',
          latency_ms: 100
        })
      });
    });
    
    await settingsPage.testConnection();
    await expect(settingsPage.testResult).toContainText('连接失败');
    await expect(settingsPage.testResult).toContainText('Connection refused');

    // 6. Save configuration
    // Verify that saving triggers the alert and updates values (mocked)
    let saveRequestCount = 0;
    page.on('request', request => {
      if (request.method() === 'PUT' && request.url().includes('/api/v1/config/')) {
        saveRequestCount++;
      }
    });

    await settingsPage.save();
    
    // Since save calls multiple endpoints, we wait a bit or wait for the alert handling
    // The alert handling is set up in settingsPage.save()
    
    // Verify inputs still have values
    await expect(settingsPage.localBaseUrlInput).toHaveValue(testUrl);
  });
});
