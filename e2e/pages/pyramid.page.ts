import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class PyramidPage extends BasePage {
  readonly createButton: Locator;
  readonly pyramidList: Locator;
  readonly emptyState: Locator;

  constructor(page: Page) {
    super(page, '/pyramid');
    this.createButton = page.getByRole('button', { name: 'Create New' });
    this.pyramidList = page.locator('.grid > a'); // Links in the grid
    this.emptyState = page.getByText('No pyramids found');
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
    await expect(this.page.getByRole('heading', { name: 'Knowledge Pyramids' })).toBeVisible();
  }
}
