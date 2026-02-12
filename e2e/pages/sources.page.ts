import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class SourcesPage extends BasePage {
  readonly addButton: Locator;
  readonly sourceList: Locator;
  readonly emptyState: Locator;
  
  // Modal
  readonly modalTitle: Locator;
  readonly urlInput: Locator;
  readonly nameInput: Locator;
  readonly typeSelect: Locator;
  readonly discoverButton: Locator;
  readonly modalAddButton: Locator;
  readonly modalCancelButton: Locator;

  constructor(page: Page) {
    super(page, '/sources');
    this.addButton = page.getByRole('button', { name: 'Add Source' });
    this.sourceList = page.locator('ul > li');
    this.emptyState = page.getByText('No sources found');

    // Modal
    this.modalTitle = page.getByRole('heading', { name: 'Add New Source' });
    // Using getByLabel which is more robust if labels are correctly associated
    // If not, we might need to fallback to getByRole or css
    // In the code: <label>Name</label><input ...> - they are not linked with htmlFor/id
    // So getByLabel won't work automatically unless wrapped.
    // Code: <div><label>...</label><input></div>
    // We'll use layout selector or placeholder if available? No placeholder.
    // Let's use CSS for now based on the structure we saw
    this.urlInput = page.locator('input[type="url"]');
    this.nameInput = page.locator('input[type="text"]');
    this.typeSelect = page.locator('select');
    this.discoverButton = page.getByRole('button', { name: '🔍' });
    this.modalAddButton = page.getByRole('button', { name: 'Add', exact: true });
    this.modalCancelButton = page.getByRole('button', { name: 'Cancel' });
  }

  async openAddModal() {
    await this.addButton.click();
    await expect(this.modalTitle).toBeVisible();
  }

  async createSource(name: string, url: string, type: 'RSS' | 'API' | 'WEB' = 'RSS') {
    await this.openAddModal();
    await this.urlInput.fill(url);
    await this.nameInput.fill(name);
    await this.typeSelect.selectOption(type);
    await this.modalAddButton.click();
    await expect(this.modalTitle).not.toBeVisible();
  }

  async expectSourceVisible(name: string) {
    await expect(this.page.getByRole('heading', { name: name })).toBeVisible();
  }

  async crawlSource(name: string) {
    const sourceItem = this.page.locator('li').filter({ hasText: name });
    await sourceItem.getByRole('button', { name: 'Crawl' }).click();
    // Wait for crawl to start/finish - in the UI it shows an alert
    // Handling dialogs in Playwright:
    // page.on('dialog', dialog => dialog.accept());
  }
}
