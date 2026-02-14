import React, { useCallback, useEffect } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  ConnectionMode,
  NodeMouseHandler,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useTranslations } from 'next-intl';

interface PyramidVisualizerProps {
  initialNodes: Node[];
  initialEdges: Edge[];
  onNodeContextMenu: (event: React.MouseEvent, node: Node) => void;
  onSelectionChange: (nodes: Node[]) => void;
}

const PyramidVisualizer: React.FC<PyramidVisualizerProps> = ({
  initialNodes,
  initialEdges,
  onNodeContextMenu,
  onSelectionChange,
}) => {
  const t = useTranslations('Pyramid.Visualizer');
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes/edges when props change (e.g. after split/merge)
  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  const onNodeContextMenuHandler: NodeMouseHandler = useCallback(
    (event, node) => {
      event.preventDefault();
      onNodeContextMenu(event, node);
    },
    [onNodeContextMenu]
  );

  const onSelectionChangeHandler = useCallback(
    ({ nodes }: { nodes: Node[] }) => {
      onSelectionChange(nodes);
    },
    [onSelectionChange]
  );

  return (
    <div className="h-[600px] w-full border rounded-lg bg-gray-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeContextMenu={onNodeContextMenuHandler}
        onSelectionChange={onSelectionChangeHandler}
        connectionMode={ConnectionMode.Loose}
        fitView
        attributionPosition="bottom-right"
      >
        <Controls />
        <MiniMap />
        <Background gap={12} size={1} />
        <Panel position="top-right" className="bg-white p-2 rounded shadow-sm border text-xs text-gray-500">
          <p>{t('right_click_actions')}</p>
          <p>{t('shift_click_select')}</p>
        </Panel>
      </ReactFlow>
    </div>
  );
};

export default PyramidVisualizer;
