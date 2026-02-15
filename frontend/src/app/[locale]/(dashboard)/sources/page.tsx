'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { sourceApi, discoveryApi } from '@/lib/api';
import { InformationSource, SourceTemplate } from '@/types';
import SourceTemplateSelector from '@/components/sources/SourceTemplateSelector';
import CrawlHistoryDialog from '@/components/sources/CrawlHistoryDialog';

export default function SourcesPage() {
  const t = useTranslations('Sources');
  const tCommon = useTranslations('Common');
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
  const [crawling, setCrawling] = useState<string | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; id: string | null }>({ open: false, id: null });

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
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const finalData: any = { ...formData };
      
      if (useTemplate && selectedTemplate && templateConfig) {
        finalData.type = selectedTemplate.source_type;
        finalData.config = templateConfig;
        finalData.template_id = selectedTemplate.id;
        
        // Try to determine URL from config if not provided
        if (!finalData.url || finalData.url.trim() === '') {
             if (templateConfig.feed_url) finalData.url = templateConfig.feed_url;
             else if (templateConfig.url) finalData.url = templateConfig.url;
             else finalData.url = `template://${selectedTemplate.id}`;
        }
      } else {
        finalData.config = { feed_url: formData.url };
      }

      if (editingSource) {
        await sourceApi.update(editingSource.id, finalData);
      } else {
        await sourceApi.create(finalData);
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

  const handleDiscover = async () => {
    if (!formData.url) return;
    setDiscovering(true);
    try {
      const response = await discoveryApi.discover(formData.url);
      if (response.success && response.data.length > 0) {
        const discovered = response.data[0];
        setFormData({ ...formData, name: discovered.title, url: discovered.url, type: discovered.type });
        alert(t('alerts.discovered', { title: discovered.title, type: discovered.type }));
      } else {
        alert(t('alerts.discover_not_found'));
      }
    } catch (error) {
      console.error('Discovery failed:', error);
      alert(t('alerts.discover_failed'));
    } finally {
      setDiscovering(false);
    }
  };

  const handleCrawl = async (id: string) => {
    setCrawling(id);
    try {
      const response = await sourceApi.crawl(id);
      if (response.success) {
        alert(t('alerts.crawl_started', { count: response.data.items_new }));
        fetchSources();
      }
    } catch (error) {
      console.error('Crawl failed:', error);
      alert(t('alerts.crawl_failed'));
    } finally {
      setCrawling(null);
    }
  };

  const handleTest = async (id: string) => {
    setTesting(id);
    try {
      const response = await sourceApi.test(id);
      if (response.success) {
        alert(t('alerts.test_success'));
      } else {
        alert(t('alerts.test_failed', { message: response.error?.message || t('alerts.test_failed_generic') }));
      }
    } catch (error) {
      console.error('Test failed:', error);
      alert(t('alerts.test_failed_generic'));
    } finally {
      setTesting(null);
    }
  };

  if (loading && sources.length === 0) return <div className="p-8">{tCommon('loading')}</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{t('title')}</h1>
        <div className="flex gap-3">
          <Link
            href="/sources/whitelist"
            className="bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 px-4 py-2 rounded shadow-sm transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {t('manage_whitelist')}
          </Link>
          <button 
            className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded shadow-sm transition-colors"
            onClick={handleOpenCreateModal}
          >
            {t('add_source')}
          </button>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md border border-gray-200">
        <ul className="divide-y divide-gray-200">
          {sources.map((source) => (
            <li key={source.id} className="px-6 py-4 hover:bg-gray-50 transition-colors group">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-medium text-gray-900 truncate">
                    {source.name}
                  </h3>
                  <p className="text-sm text-gray-500 truncate">
                    {source.url}
                  </p>
                  <div className="mt-2 flex items-center text-xs text-gray-500 gap-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full font-medium bg-blue-100 text-blue-800">
                      {sourceTypeMap[source.type] || source.type}
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full font-medium ${
                      source.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 
                      source.status === 'MONITORING' ? 'bg-yellow-100 text-yellow-800' :
                      source.status === 'ADJUSTING' ? 'bg-orange-100 text-orange-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {source.status === 'ACTIVE' ? t('status.active') : 
                       source.status === 'MONITORING' ? t('status.monitoring') :
                       source.status === 'ADJUSTING' ? t('status.adjusting') :
                       source.status}
                    </span>
                    {source.template_id && (
                       <span className="inline-flex items-center px-2.5 py-0.5 rounded-full font-medium bg-purple-100 text-purple-800">
                         {t('tags.template')}
                       </span>
                    )}
                    <span>{source.last_crawled_at ? t('last_crawled', { date: new Date(source.last_crawled_at).toLocaleString('zh-CN') }) : t('never')}</span>
                  </div>
                </div>
                <div className="ml-4 flex-shrink-0 flex items-center gap-3">
                   <button 
                    onClick={() => handleCrawl(source.id)}
                    disabled={!!crawling}
                    className="text-primary hover:text-primary/80 font-medium disabled:opacity-50"
                    title={t('actions.crawl_title')}
                   >
                     {crawling === source.id ? t('actions.crawling') : t('actions.crawl')}
                   </button>
                   <button 
                    onClick={() => handleTest(source.id)}
                    disabled={!!testing}
                    className="text-gray-600 hover:text-gray-900 font-medium disabled:opacity-50"
                    title={t('actions.test_title')}
                   >
                     {testing === source.id ? t('actions.testing') : t('actions.test')}
                   </button>
                   <button 
                    onClick={() => setHistoryDialog({ open: true, id: source.id })}
                    className="text-gray-600 hover:text-gray-900 font-medium"
                    title={t('actions.history_title')}
                   >
                     {t('actions.history')}
                   </button>
                   <div className="h-4 w-px bg-gray-300 mx-1"></div>
                   <button
                    onClick={() => handleOpenEditModal(source)}
                    className="p-1 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title={tCommon('edit')}
                   >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                   </button>
                   <button
                    onClick={() => handleDelete(source.id)}
                    className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                    title={tCommon('delete')}
                   >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                   </button>
                </div>
              </div>
            </li>
          ))}
          {sources.length === 0 && (
            <li className="px-6 py-12 text-center text-gray-500">{t('empty_list')}</li>
          )}
        </ul>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm.open && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" role="alertdialog" aria-modal="true" aria-labelledby="delete-title">
          <div className="bg-white rounded-lg p-6 w-full max-w-sm shadow-xl">
            <h3 id="delete-title" className="text-lg font-bold mb-2">{t('delete_confirm.title')}</h3>
            <p className="text-gray-600 mb-6">{t('delete_confirm.message')}</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setDeleteConfirm({ open: false, id: null })}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
              >
                {tCommon('cancel')}
              </button>
              <button
                onClick={handleConfirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                {tCommon('delete')}
              </button>
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto" role="dialog" aria-modal="true">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl shadow-xl my-8">
            <h2 className="text-xl font-bold mb-4">{editingSource ? t('modal.edit_title') : t('modal.create_title')}</h2>
            
            {!editingSource && (
              <div className="flex border-b border-gray-200 mb-6">
                <button
                  className={`px-4 py-2 font-medium text-sm transition-colors relative ${
                    !useTemplate ? 'text-primary' : 'text-gray-500 hover:text-gray-700'
                  }`}
                  onClick={() => setUseTemplate(false)}
                >
                  {t('modal.custom_add')}
                  {!useTemplate && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-primary"></span>}
                </button>
                <button
                  className={`px-4 py-2 font-medium text-sm transition-colors relative ${
                    useTemplate ? 'text-primary' : 'text-gray-500 hover:text-gray-700'
                  }`}
                  onClick={() => setUseTemplate(true)}
                >
                  {t('modal.template_add')}
                  {useTemplate && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-primary"></span>}
                </button>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('form.name')}</label>
                <input 
                  type="text" 
                  required
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary/50 outline-none"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder={t('form.name_placeholder')}
                />
              </div>

              {useTemplate ? (
                <div className="mb-6">
                  <SourceTemplateSelector 
                    onTemplateSelect={(template) => {
                      setSelectedTemplate(template);
                      // Auto-fill name if empty
                      if (!formData.name) {
                        setFormData(prev => ({ ...prev, name: template.name }));
                      }
                    }}
                    onConfigChange={(config) => setTemplateConfig(config)}
                    selectedTemplateId={selectedTemplate?.id}
                  />
                </div>
              ) : (
                <>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('form.url_id')}</label>
                    <div className="flex gap-2">
                        <input 
                        type="text" 
                        required
                        className="flex-1 border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary/50 outline-none"
                        value={formData.url}
                        onChange={(e) => setFormData({...formData, url: e.target.value})}
                        placeholder={
                          formData.type === 'WECHAT_MP' ? t('form.placeholder_wechat') :
                          formData.type === 'BILIBILI_USER' ? t('form.placeholder_bilibili') :
                          formData.type === 'JUEJIN_COLUMN' ? t('form.placeholder_juejin') :
                          t('form.placeholder_default')
                        }
                        />
                        <button 
                            type="button"
                            onClick={handleDiscover}
                            disabled={discovering || !formData.url}
                            className="bg-secondary hover:bg-secondary/90 text-white px-3 py-2 rounded text-sm disabled:opacity-50"
                        >
                            {discovering ? t('form.discovering') : t('form.discover')}
                        </button>
                    </div>
                  </div>
                  
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('form.type')}</label>
                    <select 
                      className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary/50 outline-none"
                      value={formData.type}
                      onChange={(e) => setFormData({...formData, type: e.target.value})}
                    >
                      <option value="RSS">{t('types.rss')}</option>
                      <option value="SITEMAP">{t('types.sitemap')}</option>
                      <option value="WEB">{t('types.web')}</option>
                      <option value="WECHAT_MP">{t('types.wechat_mp_hint')}</option>
                      <option value="BILIBILI_USER">{t('types.bilibili_user_hint')}</option>
                      <option value="JUEJIN_COLUMN">{t('types.juejin_column_hint')}</option>
                      <option value="YOUTUBE_CHANNEL">{t('types.youtube_channel_hint')}</option>
                    </select>
                  </div>
                </>
              )}

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                <button 
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                  disabled={submitting}
                >
                  {tCommon('cancel')}
                </button>
                <button 
                  type="submit"
                  className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded shadow-sm disabled:opacity-50 transition-colors"
                  disabled={submitting}
                >
                  {submitting ? t('form.saving') : (editingSource ? t('form.save_changes') : t('form.add_now'))}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {historyDialog.open && historyDialog.id && (
        <CrawlHistoryDialog
          open={historyDialog.open}
          sourceId={historyDialog.id}
          onOpenChange={(open) => setHistoryDialog(prev => ({ ...prev, open }))}
        />
      )}
    </div>
  );
}
