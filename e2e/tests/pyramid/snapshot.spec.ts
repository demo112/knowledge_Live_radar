import { test, expect } from '../../fixtures';

test.describe('Pyramid Snapshot Management', () => {
  let pyramidName: string;

  test.beforeEach(async ({ pyramidPage, page }) => {
    // Debug console logs
    page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
    
    // 1. Create a new pyramid for testing
    await pyramidPage.goto();
    await pyramidPage.createButton.click();
    
    // Fill creation form
    pyramidName = `Test Pyramid ${Date.now()}`;
    await page.getByLabel('名称').fill(pyramidName);
    await page.getByRole('button', { name: '保存', exact: true }).click();
    
    // Wait for navigation or list update
    await expect(page.getByText(pyramidName)).toBeVisible();
  });

  test('should create and rollback snapshot', async ({ pyramidPage, pyramidDetailPage, page }) => {
    // 2. Go to detail page
    await pyramidPage.clickPyramid(pyramidName);
    
    // 3. Go to history tab
    await pyramidDetailPage.clickHistoryTab();
    
    // 4. Create snapshot
    const snapshotReason = `Snapshot for testing ${Date.now()}`;
    await pyramidDetailPage.createSnapshot(snapshotReason);
    
    // 4. Verify snapshot appears in list
    const snapshotRow = await pyramidDetailPage.getSnapshotRow(snapshotReason);
    await expect(snapshotRow).toBeVisible();
    
    // 6. Perform rollback
    // First, let's pretend we changed something (optional, but good for verification)
    // For now, just verify rollback UI flow
    await snapshotRow.getByRole('button', { name: '回滚' }).click();
    
    // Verify dialog content
    await expect(page.getByRole('dialog').getByText('确认回滚')).toBeVisible();
    await expect(page.getByRole('dialog').getByText(snapshotReason)).toBeVisible();
    
    // Confirm rollback
    await page.getByRole('dialog').getByRole('button', { name: '回滚' }).click();
    
    // Verify success message or state
    // Assuming a toast or notification appears
    // await expect(page.getByText('回滚成功')).toBeVisible(); 
  });
});
