'use client';

import { useEffect, useState, use, useCallback } from 'react';
import { pyramidApi, nodeApi } from '@/lib/api';
import { PyramidDetail, HealthReport, VisualizationData, SplitRequest, MergeRequest, LinkRequest } from '@/types';
import HealthDashboard from '@/components/pyramid/HealthDashboard';
import PyramidVisualizer from '@/components/pyramid/PyramidVisualizer';
import { SplitNodeDialog, MergeNodesDialog, LinkNodeDialog } from '@/components/pyramid/NodeActions';
import PyramidHistory from '@/components/pyramid/PyramidHistory';
import { Button } from '@/components/ui/button';
import { Node } from 'reactflow';
import { GitMerge } from 'lucide-react';

export default function PyramidDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const pyramidId = unwrappedParams.id;
  
  const [pyramid, setPyramid] = useState<PyramidDetail | null>(null);
  const [healthReport, setHealthReport] = useState<HealthReport | null>(null);
  const [visData, setVisData] = useState<VisualizationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'view' | 'history'>('view');

  // Dialog States
  const [splitOpen, setSplitOpen] = useState(false);
  const [mergeOpen, setMergeOpen] = useState(false);
  const [linkOpen, setLinkOpen] = useState(false);
  
  // Selection & Action State
  const [selectedNodes, setSelectedNodes] = useState<Node[]>([]);
  const [actingNode, setActingNode] = useState<Node | null>(null);
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number } | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [pyramidRes, healthRes, visRes] = await Promise.all([
        pyramidApi.getById(pyramidId),
        pyramidApi.getHealth(pyramidId),
        pyramidApi.getVisualization(pyramidId)
      ]);

      if (pyramidRes.success) setPyramid(pyramidRes.data);
      if (healthRes.success) setHealthReport(healthRes.data);
      if (visRes.success) setVisData(visRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  }, [pyramidId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handlers
  const handleSplit = async (data: SplitRequest) => {
    if (!actingNode) return;
    try {
      await nodeApi.split(actingNode.id, data);
      setSplitOpen(false);
      fetchData(); // Refresh all
    } catch (error) {
      console.error('Split failed:', error);
      alert('Split failed');
    }
  };

  const handleMerge = async (data: MergeRequest) => {
    if (selectedNodes.length < 2) return;
    try {
      const requestData = { ...data, source_node_ids: selectedNodes.map(n => n.id) };
      await pyramidApi.mergeNodes(pyramidId, requestData);
      setMergeOpen(false);
      setSelectedNodes([]);
      fetchData();
    } catch (error) {
      console.error('Merge failed:', error);
      alert('Merge failed');
    }
  };

  const handleLink = async (data: LinkRequest) => {
    if (!actingNode) return;
    try {
      await nodeApi.link(actingNode.id, data);
      setLinkOpen(false);
      fetchData();
    } catch (error) {
      console.error('Link failed:', error);
      alert('Link failed');
    }
  };

  const onNodeContextMenu = (event: React.MouseEvent, node: Node) => {
    event.preventDefault();
    setActingNode(node);
    setContextMenu({ x: event.clientX, y: event.clientY });
  };

  const closeContextMenu = () => setContextMenu(null);

  const handleMenuAction = (action: 'split' | 'link') => {
    closeContextMenu();
    if (action === 'split') setSplitOpen(true);
    if (action === 'link') setLinkOpen(true);
  };

  if (loading && !pyramid) return <div className="p-8">Loading...</div>;
  if (!pyramid) return <div className="p-8">Pyramid not found</div>;

  return (
    <div className="p-6 h-screen flex flex-col space-y-4" onClick={closeContextMenu}>
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">{pyramid.name}</h1>
        <p className="text-gray-600">{pyramid.description}</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('view')}
            className={`${activeTab === 'view' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500'} whitespace-nowrap py-2 px-1 border-b-2 font-medium`}
          >
            Visualization & Health
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`${activeTab === 'history' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500'} whitespace-nowrap py-2 px-1 border-b-2 font-medium`}
          >
            History
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="flex-grow overflow-hidden flex flex-col space-y-4">
        {activeTab === 'view' ? (
          <>
            {/* Health Dashboard */}
            {healthReport && <HealthDashboard report={healthReport} />}

            {/* Visualization */}
            <div className="relative flex-grow border rounded-lg overflow-hidden">
              {visData && (
                <PyramidVisualizer
                  initialNodes={visData.nodes}
                  initialEdges={visData.edges}
                  onNodeContextMenu={onNodeContextMenu}
                  onSelectionChange={setSelectedNodes}
                />
              )}
              
              {/* Merge Button Overlay */}
              {selectedNodes.length > 1 && (
                <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10">
                  <Button onClick={() => setMergeOpen(true)} className="shadow-lg">
                    <GitMerge className="mr-2 h-4 w-4" />
                    Merge {selectedNodes.length} Nodes
                  </Button>
                </div>
              )}

              {/* Context Menu */}
              {contextMenu && (
                <div
                  className="fixed z-50 bg-white border rounded shadow-md py-1 min-w-[120px]"
                  style={{ top: contextMenu.y, left: contextMenu.x }}
                >
                  <button
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm"
                    onClick={() => handleMenuAction('split')}
                  >
                    Split Node
                  </button>
                  <button
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm"
                    onClick={() => handleMenuAction('link')}
                  >
                    Link Node
                  </button>
                </div>
              )}
            </div>
          </>
        ) : (
          <PyramidHistory pyramidId={pyramid.id} />
        )}
      </div>

      {/* Dialogs */}
      <SplitNodeDialog
        open={splitOpen}
        onOpenChange={setSplitOpen}
        onConfirm={handleSplit}
      />
      <MergeNodesDialog
        open={mergeOpen}
        onOpenChange={setMergeOpen}
        selectedNodeNames={selectedNodes.map(n => n.data.label)}
        onConfirm={handleMerge}
      />
      <LinkNodeDialog
        open={linkOpen}
        onOpenChange={setLinkOpen}
        onConfirm={handleLink}
      />
    </div>
  );
}
