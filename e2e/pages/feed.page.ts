import { Page, Locator, expect } from '@playwright/test';

export class FeedPage {
  readonly page: Page;
  readonly contentItems: Locator;

  constructor(page: Page) {
    this.page = page;
    this.contentItems = page.locator('div.bg-white.p-6.rounded-lg.shadow');
  }

  async goto() {
    await this.page.goto('/zh/feed');
  }

  async expectContentVisible(title: string) {
    await expect(this.contentItems.filter({ hasText: title })).toBeVisible();
  }

  async expectAISummaryVisible(title: string) {
    const item = this.contentItems.filter({ hasText: title });
    await expect(item.locator('text=AI 摘要')).toBeVisible();
    // Check for the summary text presence (non-empty)
    const summary = item.locator('p.text-gray-600');
    await expect(summary).not.toBeEmpty();
  }

  async expectAITagsVisible(title: string, tags: string[]) {
    const item = this.contentItems.filter({ hasText: title });
    for (const tag of tags) {
      await expect(item.locator(`text=${tag}`)).toBeVisible();
    }
  }
}
