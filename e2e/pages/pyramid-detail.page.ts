import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class PyramidDetailPage extends BasePage {
  readonly historyTab: Locator;
  readonly viewTab: Locator;
  readonly createSnapshotButton: Locator;
  readonly snapshotList: Locator;
  readonly snapshotReasonInput: Locator;
  readonly confirmSnapshotButton: Locator;
  readonly rollbackDialog: Locator;
  readonly confirmRollbackButton: Locator;

  constructor(page: Page) {
    super(page, '/pyramid');
    // Tabs
    this.historyTab = page.getByRole('button', { name: '历史记录' });
    this.viewTab = page.getByRole('button', { name: '可视化与健康度' });

    // Snapshot creation
    this.createSnapshotButton = page.getByRole('button', { name: '创建快照' });
    this.snapshotReasonInput = page.getByLabel('快照原因');
    this.confirmSnapshotButton = page.getByRole('button', { name: '创建' }); // In dialog

    // Snapshot list
    this.snapshotList = page.locator('ul li').filter({ has: page.locator('time') });

    // Rollback
    this.rollbackDialog = page.getByRole('dialog', { name: '确认回滚' });
    this.confirmRollbackButton = page.getByRole('button', { name: '回滚' }); // In dialog
  }

  async goto(id: string) {
    await this.page.goto(`/pyramid/${id}`);
  }

  async clickHistoryTab() {
    await this.historyTab.click();
    // Wait for loading to finish
    await expect(this.page.getByText('加载历史记录中...')).toBeHidden();
  }

  async clickCreateSnapshot() {
    await expect(this.createSnapshotButton).toBeVisible();
    await expect(this.createSnapshotButton).toBeEnabled();
    await this.createSnapshotButton.click();
  }

  async createSnapshot(reason: string) {
    await this.clickCreateSnapshot();
    // Wait for dialog
    await expect(this.page.getByRole('dialog')).toBeVisible();
    await this.snapshotReasonInput.fill(reason);
    // Click the Create button inside the dialog
    await this.page.getByRole('dialog').getByRole('button', { name: '创建' }).click();
  }

  async getSnapshotRow(reason: string) {
    return this.snapshotList.filter({ hasText: reason }).first();
  }

  async rollbackToSnapshot(reason: string) {
    const row = await this.getSnapshotRow(reason);
    await row.getByRole('button', { name: '回滚' }).click();
    await this.confirmRollbackButton.click();
  }

  async previewSnapshot(reason: string) {
    const row = await this.getSnapshotRow(reason);
    await row.getByRole('button', { name: '预览' }).click(); // Assuming title="预览" or text
  }

  async expectNodeVisible(name: string) {
    // ReactFlow nodes usually have text content
    await expect(this.page.locator('.react-flow__node').filter({ hasText: name })).toBeVisible();
  }
}
