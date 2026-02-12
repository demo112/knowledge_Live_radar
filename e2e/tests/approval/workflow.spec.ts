import { test, expect } from '../../fixtures';

test.describe('Approval Workflow', () => {
  const mockApprovals = [
    {
      id: '1',
      type: 'add_node',
      status: 'pending',
      reason: 'AI suggested adding "Transformer" node',
      confidence_score: 0.95,
      data: { node_name: 'Transformer', parent_id: 'root' },
      created_at: new Date().toISOString()
    },
    {
      id: '2',
      type: 'rename_node',
      status: 'pending',
      reason: 'Rename "LLM" to "Large Language Model"',
      confidence_score: 0.88,
      data: { node_id: 'llm', new_name: 'Large Language Model' },
      created_at: new Date().toISOString()
    }
  ];

  test.beforeEach(async ({ page, approvalPage }) => {
    // Mock GET pending approvals
    await page.route('**/api/v1/approvals/pending', async route => {
      await route.fulfill({
        json: { success: true, data: mockApprovals }
      });
    });

    await approvalPage.goto();
    await approvalPage.waitForLoad();
  });

  test('should display pending approvals list', async ({ approvalPage }) => {
    await approvalPage.expectApprovalVisible('AI suggested adding "Transformer" node');
    await approvalPage.expectApprovalVisible('Rename "LLM" to "Large Language Model"');
  });

  test('should approve a proposal successfully', async ({ page, approvalPage }) => {
    const targetReason = 'AI suggested adding "Transformer" node';
    
    // Mock Review API
    await page.route('**/api/v1/approvals/*/review', async route => {
      await route.fulfill({ json: { success: true } });
    });

    // Mock Execute API
    await page.route('**/api/v1/approvals/*/execute', async route => {
      await route.fulfill({ json: { success: true } });
    });

    // Mock Re-fetch after approval (return reduced list immediately)
    // Since the page is already loaded, the next fetch will be the re-fetch
    await page.route('**/api/v1/approvals/pending', async route => {
      await route.fulfill({
        json: { success: true, data: [mockApprovals[1]] }
      });
    });

    await approvalPage.approve(targetReason);

    // Verify it disappears (or UI updates)
    await approvalPage.expectApprovalHidden(targetReason);
    await approvalPage.expectApprovalVisible('Rename "LLM" to "Large Language Model"');
  });

  test('should reject a proposal successfully', async ({ page, approvalPage }) => {
    const targetReason = 'Rename "LLM" to "Large Language Model"';
    
    // Mock Review API
    await page.route('**/api/v1/approvals/*/review', async route => {
      await route.fulfill({ json: { success: true } });
    });

    // Mock Re-fetch after rejection (return reduced list immediately)
    await page.route('**/api/v1/approvals/pending', async route => {
      await route.fulfill({
        json: { success: true, data: [mockApprovals[0]] }
      });
    });

    await approvalPage.reject(targetReason);

    await approvalPage.expectApprovalHidden(targetReason);
    await approvalPage.expectApprovalVisible('AI suggested adding "Transformer" node');
  });

  test('should show empty state when no approvals', async ({ page, approvalPage }) => {
    // Override the beforeEach route
    await page.route('**/api/v1/approvals/pending', async route => {
      await route.fulfill({
        json: { success: true, data: [] }
      });
    });

    // Reload to apply new mock
    await approvalPage.goto();
    await approvalPage.waitForLoad();

    await approvalPage.expectEmptyState();
  });
});
