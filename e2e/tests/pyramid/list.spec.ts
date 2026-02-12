import { test, expect } from '../../fixtures';

test.describe('Pyramid Management', () => {
  test.beforeEach(async ({ pyramidPage }) => {
    await pyramidPage.goto();
    await pyramidPage.waitForLoad();
  });

  test('should display pyramid list page', async ({ pyramidPage }) => {
    await pyramidPage.expectLoaded();
  });

  test('should show empty state or list', async ({ pyramidPage }) => {
    // We assume empty state initially or list if data exists
    // This test just verifies that one of them is visible
    const emptyVisible = await pyramidPage.emptyState.isVisible();
    const listVisible = await pyramidPage.pyramidList.first().isVisible();
    
    expect(emptyVisible || listVisible).toBeTruthy();
  });

  test('create button should be visible', async ({ pyramidPage }) => {
    await expect(pyramidPage.createButton).toBeVisible();
  });
});
