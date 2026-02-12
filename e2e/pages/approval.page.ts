import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class ApprovalPage extends BasePage {
  readonly approvalList: Locator;
  readonly emptyState: Locator;

  constructor(page: Page) {
    super(page, '/approval');
    this.approvalList = page.locator('ul.divide-y');
    this.emptyState = page.getByText('暂无待审批提案');
  }

  getApprovalItem(reason: string): Locator {
    return this.approvalList.locator('li').filter({ hasText: reason });
  }

  async approve(reason: string) {
    const item = this.getApprovalItem(reason);
    
    // Handle dialog (alert)
    this.page.once('dialog', async dialog => {
      console.log(`Dialog message: ${dialog.message()}`);
      await dialog.accept();
    });

    await item.getByRole('button', { name: '批准' }).click();
  }

  async reject(reason: string) {
    const item = this.getApprovalItem(reason);
    
    // Handle dialog (alert)
    this.page.once('dialog', async dialog => {
      console.log(`Dialog message: ${dialog.message()}`);
      await dialog.accept();
    });

    await item.getByRole('button', { name: '拒绝' }).click();
  }

  async expectApprovalVisible(reason: string) {
    const item = this.getApprovalItem(reason);
    await expect(item).toBeVisible();
  }

  async expectApprovalHidden(reason: string) {
    const item = this.getApprovalItem(reason);
    await expect(item).toBeHidden();
  }

  async expectEmptyState() {
    await expect(this.emptyState).toBeVisible();
  }
}
