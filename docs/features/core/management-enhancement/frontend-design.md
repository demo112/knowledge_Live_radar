# Frontend Design: Core Management Enhancement

## 1. Overview
Implement frontend components for Knowledge Pyramid advanced management, including Visualization (ReactFlow), Health Evaluation, and Node Operations (Split/Merge/Link).

## 2. API Client Extensions (`src/lib/api.ts`)

```typescript
export const pyramidApi = {
  // ... existing methods
  getHealth: async (id: string) => {
    const response = await api.get(`/pyramids/${id}/health`);
    return response.data; // { score, details, suggestions }
  },
  getVisualization: async (id: string) => {
    const response = await api.get(`/pyramids/${id}/visualization`);
    return response.data; // { nodes, edges }
  },
  mergeNodes: async (id: string, data: MergeRequest) => {
    const response = await api.post(`/pyramids/${id}/merge`, data);
    return response.data;
  }
};

export const nodeApi = { // New object
  split: async (id: string, data: SplitRequest) => {
    const response = await api.post(`/nodes/${id}/split`, data);
    return response.data;
  },
  link: async (id: string, data: LinkRequest) => {
    const response = await api.post(`/nodes/${id}/link`, data);
    return response.data;
  }
};
```

## 3. Component Design

### 3.1 `HealthDashboard` (`src/components/pyramid/HealthDashboard.tsx`)
- **Visuals**:
  - Overall Score (Circular Progress or Big Number).
  - Metrics Cards: Depth Balance, Node Coverage, Activity.
  - Suggestions List: Warning/Info alerts.
- **Props**: `pyramidId`.

### 3.2 `PyramidVisualizer` (`src/components/pyramid/PyramidVisualizer.tsx`)
- **Library**: `reactflow`.
- **Features**:
  - Auto-layout (from backend or using `dagre` on frontend if needed, but backend provides positions).
  - Node Context Menu: Trigger Split/Link/Delete.
  - Multi-select: Trigger Merge.
  - MiniMap, Controls, Background.

### 3.3 `NodeActionDialogs` (`src/components/pyramid/NodeActions.tsx`)
- **SplitDialog**:
  - Input: List of sub-nodes (Name, Content, Type).
  - Checkbox: Delete original?
- **MergeDialog**:
  - Input: Target Node Name, Content.
  - Strategy Selection (Create New / Merge to First).
- **LinkDialog**:
  - Search: Target Pyramid / Node.
  - Select: Relation Type.

## 4. Page Layout (`src/app/(dashboard)/pyramid/[id]/page.tsx`)
- **Header**: Pyramid Title, Breadcrumbs.
- **Top Section**: `HealthDashboard` (Collapsible or Card).
- **Main Section**: `PyramidVisualizer` (Full height/width).
- **Sidebar/Drawer**: Node Details (when clicked).

## 5. State Management
- Use `zustand` or local state for Dialog visibility and selected nodes.
- ReactFlow maintains its own state for viewport and selection.
