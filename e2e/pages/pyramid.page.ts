import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class PyramidPage extends BasePage {
  readonly createButton: Locator;
  readonly pyramidList: Locator;
  readonly emptyState: Locator;

  constructor(page: Page) {
    super(page, '/pyramid');
    this.createButton = page.getByRole('button', { name: '新建金字塔' });
    this.pyramidList = page.locator('.grid a'); // Links in the grid
    this.emptyState = page.getByText('暂无金字塔');
  }

  async createPyramid(name: string) {
    await this.createButton.click();
    await this.page.getByLabel('名称').fill(name);
    await this.page.getByRole('button', { name: '保存', exact: true }).click();
    // Wait for navigation or list update
    await this.page.waitForLoadState('networkidle');
  }

  async getPyramidCard(name: string): Promise<Locator> {
    return this.page.getByRole('link').filter({ hasText: name });
  }

  async expectPyramidVisible(name: string) {
    const card = await this.getPyramidCard(name);
    await expect(card).toBeVisible();
  }

  async clickPyramid(name: string) {
    const card = await this.getPyramidCard(name);
    await card.click();
  }

  async expectLoaded() {
    await expect(this.page.getByRole('heading', { name: '知识金字塔' })).toBeVisible();
  }
}
