import { expect, type Locator, type Page } from '@playwright/test';

export class ContentPage {
  readonly page: Page;
  readonly contentList: Locator;
  readonly contentItems: Locator;

  constructor(page: Page) {
    this.page = page;
    this.contentList = page.locator('ul.divide-y');
    this.contentItems = this.contentList.locator('li');
  }

  async goto() {
    await this.page.goto('/contents');
  }

  async expectContentVisible(title: string) {
    await expect(this.contentItems.filter({ hasText: title })).toBeVisible();
  }
}
