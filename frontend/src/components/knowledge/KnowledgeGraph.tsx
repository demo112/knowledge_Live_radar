'use client';

import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  MarkerType,
  BackgroundVariant,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { KnowledgeGraphData, KnowledgeNode, KnowledgeRelation } from '@/lib/api/knowledge';

interface KnowledgeGraphProps {
  data: KnowledgeGraphData | null;
  onNodeClick?: (node: KnowledgeNode) => void;
  loading?: boolean;
}

const nodeTypes = {
  // Custom node types can be added here
};

const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({ data, onNodeClick, loading }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!data) return;

    // Transform backend data to ReactFlow format
    const newNodes: Node[] = data.nodes.map((node, index) => ({
      id: node.id,
      type: 'default', // Can be customized based on node.node_type
      data: { label: node.name, ...node },
      position: { x: (index % 5) * 200, y: Math.floor(index / 5) * 100 }, // Simple grid layout for now
      style: { 
        background: node.id === data.root_id ? '#eff6ff' : '#fff',
        border: node.id === data.root_id ? '2px solid #2563eb' : '1px solid #777',
        width: 150,
      }
    }));

    const newEdges: Edge[] = data.edges.map((edge) => ({
      id: edge.id,
      source: edge.source_node_id,
      target: edge.target_node_id,
      label: edge.relation_type,
      type: 'smoothstep',
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
      style: { stroke: '#b1b1b7' },
      labelStyle: { fill: '#b1b1b7', fontWeight: 700 },
    }));

    setNodes(newNodes);
    setEdges(newEdges);
  }, [data, setNodes, setEdges]);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node.data as KnowledgeNode);
      }
    },
    [onNodeClick]
  );

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-gray-50">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
      </div>
    );
  }

  if (!data && !loading) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-gray-50 text-gray-500">
        No graph data available.
      </div>
    );
  }

  return (
    <div className="h-full w-full bg-white">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-right"
      >
        <Controls />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        <MiniMap 
            nodeStrokeColor={(n) => {
                if (n.style?.background) return n.style.background as string;
                return '#eee';
            }}
            nodeColor={(n) => {
                if (n.style?.background) return n.style.background as string;
                return '#fff';
            }}
            nodeBorderRadius={2}
        />
        <Panel position="top-right" className="bg-white p-2 shadow-sm rounded border text-xs text-gray-500">
          <div>Nodes: {nodes.length}</div>
          <div>Edges: {edges.length}</div>
        </Panel>
      </ReactFlow>
    </div>
  );
};

export default KnowledgeGraph;
