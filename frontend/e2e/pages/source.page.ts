import { expect, type Locator, type Page } from '@playwright/test';

export class SourcePage {
  readonly page: Page;
  readonly addSourceButton: Locator;
  readonly urlInput: Locator;
  readonly nameInput: Locator;
  readonly typeSelect: Locator;
  readonly submitButton: Locator;
  readonly sourceList: Locator;

  constructor(page: Page) {
    this.page = page;
    this.addSourceButton = page.getByRole('button', { name: 'Add Source' });
    this.urlInput = page.locator('input[type="url"]');
    this.nameInput = page.locator('input[type="text"]');
    this.typeSelect = page.locator('select');
    // The submit button inside the modal is "Add", while the main button is "Add Source"
    this.submitButton = page.getByRole('button', { name: 'Add', exact: true });
    this.sourceList = page.locator('ul.divide-y li');
  }

  async goto() {
    await this.page.goto('/sources');
  }

  async addSource(name: string, url: string, type: string = 'rss') {
    await this.addSourceButton.click();
    await expect(this.page.getByText('Add New Source')).toBeVisible();
    await this.urlInput.fill(url);
    await this.nameInput.fill(name);
    await this.typeSelect.selectOption(type);
    await this.submitButton.click();
    // Verify modal closes
    await expect(this.page.getByText('Add New Source')).not.toBeVisible();
  }

  async expectSourceVisible(name: string) {
    await expect(this.sourceList.filter({ hasText: name })).toBeVisible();
  }

  async triggerCrawl(name: string) {
    const sourceItem = this.sourceList.filter({ hasText: name });
    await expect(sourceItem).toBeVisible();
    const crawlButton = sourceItem.getByRole('button', { name: 'Crawl' });
    
    // Wait for dialog
    const dialogPromise = this.page.waitForEvent('dialog');
    await crawlButton.click();
    const dialog = await dialogPromise;
    console.log(`Dialog message: ${dialog.message()}`);
    await dialog.dismiss();
  }
}
