import { test, expect } from '@playwright/test';

test.describe('Iteration 3 Features', () => {
  
  test('Synonym Management', async ({ page }) => {
    // 1. Navigate to Synonyms page
    await page.goto('/synonyms');
    await expect(page).toHaveURL(/.*\/synonyms/);
    await expect(page.getByRole('heading', { name: '同义词管理' })).toBeVisible();

    // 2. Open Create Modal
    await page.getByRole('button', { name: '添加同义词' }).click();
    await expect(page.getByText('添加同义词映射')).toBeVisible();

    // 3. Fill form (Mocking or actual creation might affect DB, so use unique names)
    const uniqueTerm = `Term_${Date.now()}`;
    await page.getByLabel('标准术语').fill(uniqueTerm);
    await page.getByLabel('同义词').fill(`Syn_${uniqueTerm}`);
    
    // 4. Submit
    // Note: Since backend might be running against real DB, we should be careful.
    // For now, we just verify the form exists and can be cancelled.
    await page.getByRole('button', { name: '取消' }).click();
    await expect(page.getByText('添加同义词映射')).not.toBeVisible();
  });

  test('Contributions View', async ({ page }) => {
    // 1. Navigate to Contributions page
    await page.goto('/contributions');
    await expect(page).toHaveURL(/.*\/contributions/);
    await expect(page.getByRole('heading', { name: '贡献记录' })).toBeVisible();

    // 2. Verify list exists
    // Wait for loading to finish
    await expect(page.getByText('加载贡献记录中...')).not.toBeVisible();
    
    // Check if there are items (might be empty, so check list container)
    const list = page.locator('ul.divide-y');
    await expect(list).toBeVisible();

    // 3. Check Stats
    await expect(page.getByText('总贡献')).toBeVisible();
    await expect(page.getByText('待处理')).toBeVisible();
    await expect(page.getByText('已采纳')).toBeVisible();
  });

  test('Approval Flow & Rollback UI', async ({ page }) => {
    // 1. Navigate to Approval page
    await page.goto('/approval');
    await expect(page).toHaveURL(/.*\/approval/);
    
    // 2. Check Tabs
    await expect(page.getByRole('tab', { name: '待审批' })).toBeVisible();
    await expect(page.getByRole('tab', { name: '审批历史' })).toBeVisible();

    // 3. Switch to History Tab
    await page.getByRole('tab', { name: '审批历史' }).click();
    
    // 4. Verify History View
    // It should show a list of history items or empty state
    // We just verify the container is present
    await expect(page.locator('div.bg-white.shadow')).toBeVisible();
  });

});
