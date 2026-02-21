import { test, expect } from '@playwright/test';

test.describe('Knowledge Graph', () => {
  test.beforeEach(async ({ page }) => {
    // Mock nodes API
    await page.route('**/api/v1/knowledge/nodes*', async route => {
      await route.fulfill({
        json: {
          success: true,
          data: [{ id: '1', name: 'Root Node', node_type: 'concept' }]
        }
      });
    });

    // Mock graph API
    await page.route('**/api/v1/knowledge/nodes/*/graph*', async route => {
      await route.fulfill({
        json: {
          success: true,
          data: {
            root_id: '1',
            nodes: [
              { id: '1', name: 'Root Node', node_type: 'concept' },
              { id: '2', name: 'Child Node', node_type: 'concept' }
            ],
            edges: [
              { id: 'e1-2', source_node_id: '1', target_node_id: '2', relation_type: 'parent' }
            ]
          }
        }
      });
    });

    // Go to knowledge page
    await page.goto('/knowledge');
  });

  test('should display knowledge graph', async ({ page }) => {
    // Check for canvas or container
    // ReactFlow usually renders a .react-flow container
    await expect(page.locator('.react-flow')).toBeVisible();
  });

  test('should allow interaction with nodes', async ({ page }) => {
    // Wait for nodes to appear
    // ReactFlow nodes have class .react-flow__node
    const node = page.locator('.react-flow__node').filter({ hasText: 'Root Node' }).first();
    await expect(node).toBeVisible();
    
    // Click a node
    await node.click();
    
    // Expect sidebar or detail view to open
    // We check for sidebar content, e.g., "Node Details" or the node name in a header
    // Since we don't know the exact sidebar structure, let's look for the node name again in a different context
    // or a close button
    // Assuming the sidebar renders the node name in a header
    await expect(page.getByRole('heading', { name: 'Root Node' })).toBeVisible();
  });
});
