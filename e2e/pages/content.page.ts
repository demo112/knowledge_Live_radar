import { expect, type Locator, type Page } from '@playwright/test';
import { BasePage } from './base.page';

export class ContentPage extends BasePage {
  readonly contentList: Locator;
  readonly contentItems: Locator;

  constructor(page: Page) {
    super(page, '/contents');
    this.contentList = page.locator('ul.divide-y');
    this.contentItems = this.contentList.locator('li');
  }

  async expectContentVisible(title: string) {
    await expect(this.contentItems.filter({ hasText: title })).toBeVisible();
  }
}
