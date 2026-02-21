'use client';

import { useEffect, useState, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { sourceApi } from '@/lib/api';
import { InformationSource, SourceTemplate } from '@/types';
import SourceTemplateSelector from '@/components/sources/SourceTemplateSelector';
import CrawlHistoryDialog from '@/components/sources/CrawlHistoryDialog';
import DiscoveredSourceList from '@/components/sources/DiscoveredSourceList';
import DiscoveryProgress from '@/components/sources/DiscoveryProgress';
import DiscoverySetupDialog from '@/components/sources/DiscoverySetupDialog';
import { useToast } from '@/hooks/use-toast';

export default function SourcesPage() {
  const t = useTranslations('Sources');
  const tCommon = useTranslations('Common');
  const { toast } = useToast();
  const [sources, setSources] = useState<InformationSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [historyDialog, setHistoryDialog] = useState<{ open: boolean; id: string | null }>({ open: false, id: null });
  const [editingSource, setEditingSource] = useState<InformationSource | null>(null);
  const [formData, setFormData] = useState({ name: '', url: '', type: 'RSS' });
  const [useTemplate, setUseTemplate] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<SourceTemplate | null>(null);
  const [templateConfig, setTemplateConfig] = useState<Record<string, unknown> | null>(null);
  const [discovering, setDiscovering] = useState(false);
  const [showDiscoveryProgress, setShowDiscoveryProgress] = useState(false);
  const [showDiscoverySetup, setShowDiscoverySetup] = useState(false);
  const [discoveryPyramidId, setDiscoveryPyramidId] = useState<string | undefined>(undefined);
  const [refreshDiscoveryKey, setRefreshDiscoveryKey] = useState(0);
  const [crawling, setCrawling] = useState<string | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; id: string | null }>({ open: false, id: null });
  
  // Tab state: 'managed' | 'discovery'
  const [activeTab, setActiveTab] = useState<'managed' | 'discovery'>('managed');

  const sourceTypeMap: Record<string, string> = {
    RSS: t('types.rss'),
    SITEMAP: t('types.sitemap'),
    WEB: t('types.web'),
    WECHAT_MP: t('types.wechat_mp'),
    BILIBILI_USER: t('types.bilibili_user'),
    JUEJIN_COLUMN: t('types.juejin_column'),
    YOUTUBE_CHANNEL: t('types.youtube_channel')
  };

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const response = await sourceApi.getAll();
      if (response.success) {
        setSources(response.data.items);
      }
    } catch (error: unknown) {
      console.error('Failed to fetch sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDiscover = () => {
    setShowDiscoverySetup(true);
  };

  const handleStartDiscovery = (pyramidId: string | undefined) => {
    setDiscoveryPyramidId(pyramidId);
    setShowDiscoverySetup(false);
    setShowDiscoveryProgress(true);
    setDiscovering(true);
    setActiveTab('discovery');
  };

  const handleDiscoveryFinish = useCallback((count: number) => {
    setDiscovering(false);
    setShowDiscoveryProgress(false);
    toast({
      title: t('alerts.discovery_complete', { count }),
      description: t('discovery.started', { count }),
    });
    setRefreshDiscoveryKey(prev => prev + 1);
  }, [t, toast]);

  const handleDiscoveryError = useCallback((err: string) => {
    setDiscovering(false);
    // Don't hide progress immediately on error so user can see logs?
    // But if we want to stop the loop, we MUST hide it or ensure it doesn't reconnect.
    // Let's hide it for now to be safe against loops.
    setShowDiscoveryProgress(false);
    console.error('Discovery error:', err);
    toast({
      title: t('alerts.discover_failed'),
      description: err,
      variant: "destructive"
    });
  }, [t, toast]);

  const handleOpenCreateModal = () => {
    setEditingSource(null);
    setFormData({ name: '', url: '', type: 'RSS' });
    setUseTemplate(false);
    setSelectedTemplate(null);
    setTemplateConfig(null);
    setShowModal(true);
  };

  const handleOpenEditModal = (source: InformationSource) => {
    setEditingSource(source);
    setFormData({ name: source.name, url: source.url, type: source.type });
    setUseTemplate(false); // Currently not supporting switching to template mode on edit
    setShowModal(true);
  };

  const handleDelete = (id: string) => {
    setDeleteConfirm({ open: true, id });
  };

  const handleConfirmDelete = async () => {
    if (!deleteConfirm.id) return;
    
    try {
      const response = await sourceApi.delete(deleteConfirm.id);
      if (response.success) {
        fetchSources();
      }
    } catch (error: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      if ((error as any).response?.status === 404) {
        // Already deleted, just refresh
        fetchSources();
      } else {
        console.error('Failed to delete source:', error);
        alert(t('alerts.delete_failed'));
      }
    } finally {
      setDeleteConfirm({ open: false, id: null });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const data = useTemplate 
        ? {
            name: formData.name,
            type: selectedTemplate?.source_type || formData.type,
            url: formData.url, // Might be empty if using template, handled by backend
            template_id: selectedTemplate?.id,
            config: templateConfig
          }
        : formData;

      if (editingSource) {
        await sourceApi.update(editingSource.id, data);
      } else {
        await sourceApi.create(data);
      }
      setShowModal(false);
      fetchSources();
    } catch (error) {
      console.error('Failed to save source:', error);
      alert(t('alerts.save_failed'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleCrawl = async (id: string) => {
    setCrawling(id);
    try {
      await sourceApi.crawl(id);
      alert(t('alerts.crawl_started'));
      fetchSources();
    } catch (error) {
      console.error('Failed to start crawl:', error);
      alert(t('alerts.operation_failed'));
    } finally {
      setCrawling(null);
    }
  };

  const handleTest = async (id: string) => {
    setTesting(id);
    try {
      const res = await sourceApi.test(id);
      if (res.success) {
        alert(t('alerts.test_success', { count: res.data.count }));
      }
    } catch (error) {
      console.error('Test failed:', error);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const msg = (error as any).response?.data?.detail || t('alerts.test_failed');
      alert(msg);
    } finally {
      setTesting(null);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{t('title')}</h1>
        <div className="flex gap-2">
          <button
            onClick={handleDiscover}
            disabled={discovering}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50"
          >
            {discovering ? 'Searching...' : '🔍 Discover New Sources'}
          </button>
          <button
            onClick={handleOpenCreateModal}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
          >
            <span>+</span> {tCommon('create')}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          className={`py-2 px-4 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'managed'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('managed')}
        >
          {t('tabs.managed')}
        </button>
        <button
          className={`py-2 px-4 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'discovery'
              ? 'border-purple-600 text-purple-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('discovery')}
        >
          {t('tabs.discovery')}
        </button>
      </div>

      {activeTab === 'managed' ? (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('columns.name')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('columns.type')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('columns.status')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('columns.last_crawled')}
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('columns.actions')}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    {tCommon('loading')}
                  </td>
                </tr>
              ) : sources.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    {t('no_data')}
                  </td>
                </tr>
              ) : (
                sources.map((source) => (
                  <tr key={source.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col">
                        <span className="font-medium text-gray-900">{source.name}</span>
                        <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-xs text-gray-500 hover:text-blue-600 truncate max-w-xs">
                          {source.url}
                        </a>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {sourceTypeMap[source.type] || source.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        source.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {source.status}
                      </span>
                      {source.error_count > 0 && (
                        <span className="ml-2 text-xs text-red-600" title="Error Count">
                          ⚠️ {source.error_count}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {source.last_crawled_at ? new Date(source.last_crawled_at).toLocaleString() : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleCrawl(source.id)}
                        disabled={crawling === source.id}
                        className="text-indigo-600 hover:text-indigo-900 mr-4 disabled:opacity-50"
                        title={t('actions.crawl_now')}
                      >
                        {crawling === source.id ? '...' : '🔄'}
                      </button>
                      <button
                        onClick={() => handleTest(source.id)}
                        disabled={testing === source.id}
                        className="text-green-600 hover:text-green-900 mr-4 disabled:opacity-50"
                        title={t('actions.test')}
                      >
                        {testing === source.id ? '...' : '🧪'}
                      </button>
                      <button
                        onClick={() => setHistoryDialog({ open: true, id: source.id })}
                        className="text-gray-600 hover:text-gray-900 mr-4"
                        title={t('actions.history')}
                      >
                        📜
                      </button>
                      <button
                        onClick={() => handleOpenEditModal(source)}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        {tCommon('edit')}
                      </button>
                      <button
                        onClick={() => handleDelete(source.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        {tCommon('delete')}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="space-y-6">
          {showDiscoveryProgress && (
            <div className="relative">
              <button 
                onClick={() => setShowDiscoveryProgress(false)}
                className="absolute top-4 right-4 z-10 p-1 rounded-full hover:bg-gray-100 text-gray-400 hover:text-gray-600"
                title={tCommon('close')}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
              <DiscoveryProgress
                pyramidId={discoveryPyramidId}
                onFinish={handleDiscoveryFinish}
                onError={handleDiscoveryError}
              />
            </div>
          )}
          <DiscoveredSourceList key={refreshDiscoveryKey} />
        </div>
      )}

      <DiscoverySetupDialog 
        open={showDiscoverySetup} 
        onOpenChange={setShowDiscoverySetup}
        onStart={handleStartDiscovery}
      />

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" role="dialog" aria-modal="true">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingSource ? t('edit_source') : t('create_source')}
            </h2>
            
            {!editingSource && (
               <div className="mb-6">
                 <div className="flex border-b border-gray-200">
                   <button
                     className={`py-2 px-4 font-medium text-sm ${
                       !useTemplate ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'
                     }`}
                     onClick={() => setUseTemplate(false)}
                   >
                     {t('manual_config')}
                   </button>
                   <button
                     className={`py-2 px-4 font-medium text-sm ${
                       useTemplate ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'
                     }`}
                     onClick={() => setUseTemplate(true)}
                   >
                     {t('use_template')}
                   </button>
                 </div>
               </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {useTemplate ? (
                <SourceTemplateSelector
                  onTemplateSelect={(template) => {
                    setSelectedTemplate(template);
                  }}
                  onConfigChange={(config) => {
                    setTemplateConfig(config);
                    // Also auto-fill name if empty
                    if (selectedTemplate && !formData.name && config.target_id) {
                       setFormData(prev => ({ ...prev, name: `${selectedTemplate.name} - ${config.target_id}` }));
                    }
                  }}
                />
              ) : (
                <>
                  <div>
                    <label htmlFor="source-name" className="block text-sm font-medium text-gray-700">{t('columns.name')}</label>
                    <input
                      id="source-name"
                      type="text"
                      required
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                  </div>
                  <div>
                    <label htmlFor="source-type" className="block text-sm font-medium text-gray-700">{t('columns.type')}</label>
                    <select
                      id="source-type"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                      disabled={!!editingSource} // Prevent type change on edit
                    >
                      {Object.entries(sourceTypeMap).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label htmlFor="source-url" className="block text-sm font-medium text-gray-700">{t('columns.url')}</label>
                    <input
                      id="source-url"
                      type="url"
                      required
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      value={formData.url}
                      onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                    />
                  </div>
                </>
              )}
              
              {/* Common Name field if using template */}
              {useTemplate && selectedTemplate && (
                 <div>
                    <label className="block text-sm font-medium text-gray-700">{t('columns.name')}</label>
                    <input
                      type="text"
                      required
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                 </div>
              )}

              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  {tCommon('actions.cancel')}
                </button>
                <button
                  type="submit"
                  disabled={submitting || (useTemplate && (!selectedTemplate || !templateConfig))}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50"
                >
                  {submitting ? tCommon('status.processing') : tCommon('actions.save')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm.open && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-sm w-full p-6">
            <h3 className="text-lg font-bold mb-2">{tCommon('alerts.confirm_delete')}</h3>
            <p className="text-gray-500 mb-6">{tCommon('alerts.delete_warning')}</p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setDeleteConfirm({ open: false, id: null })}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                {tCommon('actions.cancel')}
              </button>
              <button
                onClick={handleConfirmDelete}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md"
              >
                {tCommon('actions.delete')}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* History Dialog */}
      <CrawlHistoryDialog
        open={historyDialog.open}
        sourceId={historyDialog.id || ''}
        onOpenChange={(open) => {
          if (!open) setHistoryDialog({ open: false, id: null });
        }}
      />
    </div>
  );
}
