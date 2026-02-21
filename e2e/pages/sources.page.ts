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
    super(page, '/zh/sources');
    this.addButton = page.getByRole('button', { name: /创建|Add/ });
    this.sourceList = page.locator('tbody tr');
    this.emptyState = page.getByText('未找到信息源');

    // Modal
    const modal = page.getByRole('dialog');
    this.modalTitle = modal.getByRole('heading', { name: /添加.*信息源|Add Source/ });
    
    // Scoped to modal
    this.urlInput = modal.getByLabel(/URL|链接地址/);
    this.nameInput = modal.getByLabel(/Name|名称/);
    this.typeSelect = modal.getByLabel(/Type|类型/);
    this.discoverButton = modal.getByRole('button', { name: '发现' });
    this.modalAddButton = modal.locator('button[type="submit"]');
    this.modalCancelButton = modal.getByRole('button', { name: '取消' });
  }

  async openAddModal() {
    await this.addButton.click();
    await expect(this.modalTitle).toBeVisible();
  }

  async createSource(name: string, url: string, type: 'RSS' | 'SITEMAP' | 'WEB' = 'RSS') {
    await this.openAddModal();
    await this.urlInput.fill(url);
    await this.nameInput.fill(name);
    await this.typeSelect.selectOption(type);
    await this.modalAddButton.click();
    await expect(this.modalTitle).not.toBeVisible();
  }

  async expectSourceVisible(name: string) {
    await expect(this.sourceList.filter({ hasText: name }).first()).toBeVisible();
  }

  async crawlSource(name: string) {
    const sourceItem = this.sourceList.filter({ hasText: name }).first();
    
    // Handle alert dialog
    this.page.once('dialog', async dialog => {
      console.log(`Dialog message: ${dialog.message()}`);
      await dialog.accept();
    });

    await sourceItem.getByRole('button', { name: '抓取' }).click();
  }

  async deleteSource(name: string) {
    const sourceItem = this.sourceList.filter({ hasText: name }).first();
    
    // Click delete button (using title or icon locator if needed, but title="删除" is in JSX)
    await sourceItem.getByTitle('删除').click();

    // Confirm modal
    await this.page.getByRole('alertdialog').getByRole('button', { name: '删除', exact: true }).click();
  }

  async expectSourceNotVisible(name: string) {
    await expect(this.sourceList.filter({ hasText: name })).not.toBeVisible();
  }
}
