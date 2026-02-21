'use client';

import React, { useState, useEffect } from 'react';
import KnowledgeGraph from '@/components/knowledge/KnowledgeGraph';
import NodeDetailSidebar from '@/components/knowledge/NodeDetailSidebar';
import IntentInput from '@/components/knowledge/IntentInput';
import { knowledgeApi, KnowledgeGraphData, KnowledgeNode } from '@/lib/api/knowledge';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { Plus } from 'lucide-react';

export default function KnowledgePage() {
  const [graphData, setGraphData] = useState<KnowledgeGraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<KnowledgeNode | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [rootNodeId, setRootNodeId] = useState<string | null>(null);
  const [isIntentDialogOpen, setIsIntentDialogOpen] = useState(false);

  // Fetch initial data (e.g., list of nodes to pick a root, or a default root)
  // For now, let's fetch the first node and use it as root.
  useEffect(() => {
    const fetchInitialRoot = async () => {
      try {
        const response = await knowledgeApi.getNodes({ limit: 1 });
        if (response.success && response.data && response.data.length > 0) {
          setRootNodeId(response.data[0].id);
        } else {
          setLoading(false);
        }
      } catch (error) {
        console.error('Failed to fetch nodes:', error);
        setLoading(false);
      }
    };

    fetchInitialRoot();
  }, []);

  // Fetch graph data when rootNodeId changes
  useEffect(() => {
    if (!rootNodeId) return;

    const fetchGraph = async () => {
      setLoading(true);
      try {
        const response = await knowledgeApi.getGraph(rootNodeId, 2); // Depth 2
        if (response.success) {
            setGraphData(response.data);
        }
      } catch (error) {
        console.error('Failed to fetch graph:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, [rootNodeId]);

  const handleNodeClick = (node: KnowledgeNode) => {
    setSelectedNode(node);
  };

  const handleCloseSidebar = () => {
    setSelectedNode(null);
  };

  return (
    <div className="flex h-[calc(100vh-64px)] w-full flex-col">
      <div className="flex items-center justify-between border-b bg-white px-6 py-4">
        <h1 className="text-xl font-semibold text-gray-900">Knowledge Graph</h1>
        <div className="flex items-center gap-2">
            <Button className="gap-2" onClick={() => setIsIntentDialogOpen(true)}>
              <Plus className="h-4 w-4" />
              New Intent
            </Button>
            <Dialog open={isIntentDialogOpen} onOpenChange={setIsIntentDialogOpen}>
              <DialogContent className="sm:max-w-[600px]">
                <DialogTitle>Create New Intent</DialogTitle>
                <IntentInput />
              </DialogContent>
            </Dialog>
          </div>
      </div>

      <div className="relative flex-1 overflow-hidden bg-gray-50">
        <KnowledgeGraph 
          data={graphData} 
          onNodeClick={handleNodeClick} 
          loading={loading}
        />
        
        {selectedNode && (
          <NodeDetailSidebar 
            node={selectedNode} 
            onClose={handleCloseSidebar} 
          />
        )}
      </div>
    </div>
  );
}
