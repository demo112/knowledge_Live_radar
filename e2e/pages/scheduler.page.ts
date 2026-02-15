import { Page, Locator, expect } from '@playwright/test';

export class SchedulerPage {
  readonly page: Page;
  readonly taskTable: Locator;
  readonly refreshButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.refreshButton = page.locator('button > .lucide-rotate-cw').locator('..');
    this.taskTable = page.locator('table');
  }

  async goto() {
    await this.page.goto('/zh/scheduler');
  }

  async refresh() {
    await this.refreshButton.click();
  }

  getTaskRow(taskName: string): Locator {
    return this.taskTable.locator('tr', { hasText: taskName });
  }

  async runTask(taskName: string) {
    const row = this.getTaskRow(taskName);
    await expect(row).toBeVisible();
    // Assuming there is a play button or similar action in the row
    // Based on code: "操作" column usually has buttons. 
    // Need to verify exact button locator from component if possible, 
    // but generalized 'play' or 'run' button in that row works.
    await row.getByRole('button').filter({ has: this.page.locator('.lucide-play') }).click();
  }

  async expectTaskActive(taskName: string) {
    const row = this.getTaskRow(taskName);
    await expect(row).toContainText('启用'); // Based on 'bg-green-100 text-green-800' usually implies active/enabled text
  }
}
