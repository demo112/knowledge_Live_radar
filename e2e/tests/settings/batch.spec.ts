import { test, expect } from '../../fixtures';

test.describe('Settings - Batch Processing', () => {
  test.beforeEach(async ({ settingsPage }) => {
    await settingsPage.goto();
  });

  test('should trigger batch classification via UI', async ({ settingsPage, page }) => {
    // 1. Mock the batch API
    await page.route('**/api/v1/evolution/classify/batch', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            task_id: 'task-123',
            status: 'started'
          }
        })
      });
    });

    // 2. Navigate to Tasks tab
    const tasksTab = page.getByRole('button', { name: '任务管理' });
    await tasksTab.click();
    await expect(page.getByText('后台任务控制')).toBeVisible();

    // 3. Click Trigger Button
    // We set up a listener for dialogs
    const dialogMessages: string[] = [];
    page.on('dialog', async dialog => {
      dialogMessages.push(dialog.message());
      await dialog.accept();
    });

    await page.getByRole('button', { name: '立即触发' }).click();

    // 5. Verify Success
    // The button might show '正在启动...' briefly
    // We check if success alert was shown
    // Since dialog handling is async, we might need to wait a bit
    await page.waitForTimeout(500);
    
    // Verify we got the confirmation and the success message
    expect(dialogMessages).toContainEqual(expect.stringContaining('确定要触发'));
    expect(dialogMessages).toContainEqual(expect.stringContaining('批量分类任务已启动'));
  });
});
