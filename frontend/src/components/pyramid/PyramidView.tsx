'use client';

import React, { useEffect, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { PyramidDetail, PyramidNode } from '@/types';

interface PyramidViewProps {
  data: PyramidDetail;
}

const PyramidView: React.FC<PyramidViewProps> = ({ data }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!data || !data.nodes) return;

    // Simple auto-layout logic
    const levelMap = new Map<number, PyramidNode[]>();
    data.nodes.forEach(node => {
      const lvl = node.level;
      if (!levelMap.has(lvl)) levelMap.set(lvl, []);
      levelMap.get(lvl)?.push(node);
    });

    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];

    levelMap.forEach((levelNodes, level) => {
      const count = levelNodes.length;
      const width = 800; // arbitrary canvas width
      const spacing = width / (count + 1);

      levelNodes.forEach((node, index) => {
        newNodes.push({
          id: node.id,
          position: { x: (index + 1) * spacing - 75, y: level * 150 + 50 },
          data: { label: node.name },
          type: 'default', // 'input' for root?
          style: { 
            background: '#fff', 
            border: '1px solid #777', 
            borderRadius: '5px',
            padding: '10px',
            width: 150
          },
        });

        if (node.parent_id) {
          newEdges.push({
            id: `e-${node.parent_id}-${node.id}`,
            source: node.parent_id,
            target: node.id,
            markerEnd: { type: MarkerType.ArrowClosed },
            type: 'smoothstep',
          });
        }
      });
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [data, setNodes, setEdges]);

  return (
    <div className="h-[600px] w-full border border-gray-200 rounded-lg bg-gray-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default PyramidView;
