import { Page, Locator, expect } from '@playwright/test';

export class HealthPage {
  readonly page: Page;
  readonly overallScore: Locator;
  readonly detectButton: Locator;
  readonly optimizeButton: Locator;
  readonly pyramidCard: Locator;
  readonly sourceCard: Locator;
  readonly hotspotCard: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Header Buttons
    this.detectButton = page.getByRole('button', { name: /立即检测|检测中/ });
    this.optimizeButton = page.getByRole('button', { name: '优化抓取策略' });
    
    // Metrics
    this.overallScore = page.locator('.text-4xl').first(); // "42" / 100
    
    // Cards (identified by headers or text content)
    this.pyramidCard = page.locator('h3', { hasText: '金字塔结构' }).locator('..');
    this.sourceCard = page.locator('h3', { hasText: '信息源健康' }).locator('..');
    this.hotspotCard = page.locator('h3', { hasText: '热点分布' }).locator('..');
  }

  async goto() {
    await this.page.goto('/zh/health');
  }

  async triggerDetection() {
    await this.detectButton.click();
    await expect(this.detectButton).toHaveText('检测中...');
    // Wait for it to finish (revert to '立即检测')
    await expect(this.detectButton).toHaveText('立即检测', { timeout: 30000 });
  }

  async triggerOptimization() {
    // Handling potential alert dialog
    this.page.once('dialog', async dialog => {
        await dialog.accept();
    });
    await this.optimizeButton.click();
  }

  async expectHealthyScore() {
    await expect(this.overallScore).toBeVisible();
    const scoreText = await this.overallScore.textContent();
    const score = parseInt(scoreText || '0');
    expect(score).toBeGreaterThanOrEqual(0);
    expect(score).toBeLessThanOrEqual(100);
  }
}
