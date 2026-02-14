import { Page, Locator, expect } from '@playwright/test';

export class SettingsPage {
  readonly page: Page;
  readonly aiTabButton: Locator;
  readonly aiEnabledCheckbox: Locator;
  readonly strategyLocalFirstRadio: Locator;
  readonly strategyLocalOnlyRadio: Locator;
  readonly strategyCloudOnlyRadio: Locator;
  readonly localBaseUrlInput: Locator;
  readonly localModelNameInput: Locator;
  readonly cloudBaseUrlInput: Locator;
  readonly apiKeyInput: Locator;
  readonly saveButton: Locator;
  readonly testConnectionButton: Locator;
  readonly testResult: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Tabs
    this.aiTabButton = page.getByRole('button', { name: 'AI 模型' });

    // AI Config Form
    this.aiEnabledCheckbox = page.locator('label').filter({ hasText: '启用 AI 功能' }).getByRole('checkbox');
    this.strategyLocalFirstRadio = page.locator('input[name="ai.strategy"][value="local_first"]');
    this.strategyLocalOnlyRadio = page.locator('input[name="ai.strategy"][value="local_only"]');
    this.strategyCloudOnlyRadio = page.locator('input[name="ai.strategy"][value="cloud_only"]');
    
    // Inputs (Using nearby labels or specific placeholders if labels are tricky, but labels are best)
    // Note: The labels in the component are standard <label> blocks, so getByLabel should work if associated correctly or wrapped.
    // In the code: <label>Text</label><input ... /> (not wrapped or for=id). 
    // Wait, the code shows:
    // <label>Text</label> <input />
    // They are siblings inside a div. There is no 'for' attribute and input is not inside label.
    // So getByLabel won't work automatically.
    // I will use placeholders or specific hierarchy.
    
    this.localBaseUrlInput = page.getByPlaceholder('http://localhost:11434/v1');
    this.localModelNameInput = page.getByPlaceholder('qwen2.5:7b');
    
    this.cloudBaseUrlInput = page.getByPlaceholder('https://api.siliconflow.cn/v1');
    this.apiKeyInput = page.getByPlaceholder('sk-...');

    // Buttons
    this.saveButton = page.getByRole('button', { name: '保存配置' });
    this.testConnectionButton = page.getByRole('button', { name: '测试当前策略连接' });
    
    // Result
    this.testResult = page.locator('[data-testid="connection-test-result"]');
  }

  async goto() {
    await this.page.goto('/zh/settings');
  }

  async switchToAITab() {
    await this.aiTabButton.click();
    await expect(this.page.getByText('调度策略 (Strategy)')).toBeVisible();
  }

  async enableAI() {
    const isChecked = await this.aiEnabledCheckbox.isChecked();
    if (!isChecked) {
      await this.aiEnabledCheckbox.click();
    }
  }

  async selectStrategy(strategy: 'local_first' | 'local_only' | 'cloud_only') {
    if (strategy === 'local_first') await this.strategyLocalFirstRadio.click();
    if (strategy === 'local_only') await this.strategyLocalOnlyRadio.click();
    if (strategy === 'cloud_only') await this.strategyCloudOnlyRadio.click();
  }

  async setLocalConfig(baseUrl: string, model: string) {
    await this.localBaseUrlInput.fill(baseUrl);
    await this.localModelNameInput.fill(model);
  }

  async setCloudConfig(baseUrl: string, apiKey: string, model: string) {
    await this.cloudBaseUrlInput.fill(baseUrl);
    await this.apiKeyInput.fill(apiKey);
    // Cloud model input shares placeholder or we need another locator
    // Looking at code: placeholder="Qwen/Qwen2.5-7B-Instruct"
    await this.page.getByPlaceholder('Qwen/Qwen2.5-7B-Instruct').fill(model);
  }

  async save() {
    // Handle alert
    this.page.once('dialog', async dialog => {
      await dialog.accept();
    });
    await this.saveButton.click();
  }

  async testConnection() {
    await this.testConnectionButton.click();
  }
}
