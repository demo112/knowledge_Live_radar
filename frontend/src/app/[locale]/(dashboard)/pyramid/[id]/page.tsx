'use client';

import { useEffect, useState, use, useCallback } from 'react';
import { pyramidApi, nodeApi } from '@/lib/api';
import { PyramidDetail, HealthReport, VisualizationData, SplitRequest, MergeRequest, LinkRequest } from '@/types';
import HealthDashboard from '@/components/pyramid/HealthDashboard';
import EvolutionPanel from '@/components/pyramid/EvolutionPanel';
import PyramidVisualizer from '@/components/pyramid/PyramidVisualizer';
import { SplitNodeDialog, MergeNodesDialog, LinkNodeDialog } from '@/components/pyramid/NodeActions';
import PyramidHistory from '@/components/pyramid/PyramidHistory';
import { NodeContents } from '@/components/pyramid/NodeContents';
import { Button } from '@/components/ui/button';
import { Node } from 'reactflow';
import { GitMerge, Download } from 'lucide-react';
import { useTranslations } from 'next-intl';

export default function PyramidDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const pyramidId = unwrappedParams.id;
  const t = useTranslations('Pyramid.Detail');
  const tCommon = useTranslations('Common');
  
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
      await nodeApi.split(pyramidId, actingNode.id, data);
      setSplitOpen(false);
      fetchData(); // Refresh all
    } catch (error) {
      console.error('Split failed:', error);
      alert(t('split_failed'));
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
      alert(t('merge_failed'));
    }
  };

  const handleLink = async (data: LinkRequest) => {
    if (!actingNode) return;
    try {
      await nodeApi.link(pyramidId, actingNode.id, data);
      setLinkOpen(false);
      fetchData();
    } catch (error) {
      console.error('Link failed:', error);
      alert(t('link_failed'));
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

  const handleExport = async () => {
    try {
      const response = await pyramidApi.exportTemplate(pyramidId);
      if (response.success) {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(response.data, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `${pyramid?.name || 'pyramid'}_template.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
      }
    } catch (error) {
      console.error('Failed to export:', error);
      alert(t('export_failed'));
    }
  };

  if (loading && !pyramid) return <div className="p-8">{tCommon('loading')}</div>;
  if (!pyramid) return <div className="p-8">{t('not_found')}</div>;

  return (
    <div className="p-6 h-screen flex flex-col space-y-4" onClick={closeContextMenu}>
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
            <h1 className="text-2xl font-bold">{pyramid.name}</h1>
            <p className="text-gray-600">{pyramid.description}</p>
        </div>
        <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            {t('export_template')}
        </Button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('view')}
            className={`${activeTab === 'view' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500'} whitespace-nowrap py-2 px-1 border-b-2 font-medium`}
          >
            {t('tabs.view')}
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`${activeTab === 'history' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500'} whitespace-nowrap py-2 px-1 border-b-2 font-medium`}
          >
            {t('tabs.history')}
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="flex-grow overflow-hidden flex flex-col space-y-4">
        {activeTab === 'view' ? (
          <div className="flex flex-col h-full space-y-4">
            {healthReport && (
              <div className="flex-shrink-0">
                <HealthDashboard report={healthReport} />
              </div>
            )}

            <div className="flex-grow flex flex-col space-y-4 overflow-hidden h-full pb-2">
              {/* Top: Evolution Panel */}
              <div className="flex-shrink-0 max-h-[300px] overflow-y-auto">
                <EvolutionPanel pyramidId={pyramidId} onUpdate={fetchData} />
              </div>

              {/* Middle: Visualization */}
              <div className="flex-grow relative border rounded-lg overflow-hidden flex flex-col bg-white shadow-sm min-w-0 min-h-[400px]">
                {visData ? (
                  <PyramidVisualizer
                    initialNodes={visData.nodes}
                    initialEdges={visData.edges}
                    onNodeContextMenu={onNodeContextMenu}
                    onSelectionChange={setSelectedNodes}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    {loading ? tCommon('loading') : t('no_data')}
                  </div>
                )}
                
                {/* Merge Button Overlay */}
                {selectedNodes.length > 1 && (
                  <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10">
                    <Button onClick={() => setMergeOpen(true)} className="shadow-lg">
                      <GitMerge className="mr-2 h-4 w-4" />
                      {t('actions.merge_nodes', { count: selectedNodes.length })}
                    </Button>
                  </div>
                )}

                {/* Context Menu */}
                {contextMenu && (
                  <div
                    className="fixed bg-white border shadow-lg rounded-md py-1 z-50 min-w-[120px]"
                    style={{ top: contextMenu.y, left: contextMenu.x }}
                  >
                    <button
                      className="block w-full text-left px-4 py-2 hover:bg-gray-100 text-sm"
                      onClick={() => handleMenuAction('split')}
                    >
                      {t('actions.split_node')}
                    </button>
                    <button
                      className="block w-full text-left px-4 py-2 hover:bg-gray-100 text-sm"
                      onClick={() => handleMenuAction('link')}
                    >
                      {t('actions.link_content')}
                    </button>
                  </div>
                )}
              </div>

              {/* Bottom: Node Contents */}
              {selectedNodes.length === 1 && (
                <div className="flex-shrink-0 max-h-[300px] overflow-y-auto">
                  <NodeContents nodeId={selectedNodes[0].id} />
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="h-full overflow-y-auto">
            <PyramidHistory pyramidId={pyramidId} />
          </div>
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
