'use client';

import { useEffect, useState, useCallback } from 'react';
import { contentApi, contentManagementApi } from '@/lib/api';
import { ContentItem } from '@/types';
import Link from 'next/link';
import { useTranslations } from 'next-intl';

export default function ContentsPage() {
  const t = useTranslations('Contents');
  const tCommon = useTranslations('Common');
  const [contents, setContents] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  
  // Selection & Batch Operations State
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isProcessing, setIsProcessing] = useState(false);

  const fetchContents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await contentApi.getAll({ skip: (page - 1) * 20, limit: 20 });
      if (response.success) {
        setContents(response.data.items);
        // Clear selection on page change or refresh
        setSelectedIds(new Set());
      } else {
        setError(t('error_loading'));
      }
    } catch (error) {
      console.error('Failed to fetch contents:', error);
      setError(t('error_generic'));
    } finally {
      setLoading(false);
    }
  }, [page, t]);

  useEffect(() => {
    fetchContents();
  }, [fetchContents]);

  // Selection Handlers
  const handleSelectOne = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedIds.size === contents.length && contents.length > 0) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(contents.map(c => c.id)));
    }
  };

  // Batch Action Handlers
  const handleBatchClean = async () => {
    if (!confirm(t('alerts.confirm_clean'))) return;
    setIsProcessing(true);
    try {
      const result = await contentManagementApi.batchClean();
      alert(t('alerts.clean_success', { scanned: result.total_scanned, deleted: result.deleted_count }));
      fetchContents();
    } catch (e) {
      console.error(e);
      alert(t('alerts.clean_failed'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBatchSummarize = async (forSelected: boolean) => {
    const ids = forSelected ? Array.from(selectedIds) : undefined;
    if (forSelected && (!ids || ids.length === 0)) return;
    
    const message = forSelected 
      ? t('alerts.confirm_regenerate_selected', { count: ids ? ids.length : 0 })
      : t('alerts.confirm_regenerate_all');
      
    if (!confirm(message)) return;
    
    setIsProcessing(true);
    try {
      await contentManagementApi.batchSummarize(ids, true); // overwrite=true
      alert(t('alerts.task_started'));
      // Ideally we should poll for status or listen to socket, but for now just refresh list
      setTimeout(fetchContents, 2000); 
    } catch (e) {
      console.error(e);
      alert(t('alerts.task_failed'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBatchDelete = async () => {
    const ids = Array.from(selectedIds);
    if (ids.length === 0) return;
    
    if (!confirm(t('alerts.confirm_delete', { count: ids.length }))) return;
    
    setIsProcessing(true);
    try {
      await contentManagementApi.batchDelete(ids);
      alert(t('alerts.delete_success'));
      setSelectedIds(new Set());
      fetchContents();
    } catch (e) {
      console.error(e);
      alert(t('alerts.delete_failed'));
    } finally {
      setIsProcessing(false);
    }
  };

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">{tCommon('error')}: </strong>
          <span className="block sm:inline">{error}</span>
          <button 
            onClick={() => fetchContents()}
            className="mt-2 bg-red-100 hover:bg-red-200 text-red-800 font-semibold py-1 px-3 rounded text-sm transition-colors"
          >
            {t('retry')}
          </button>
        </div>
      </div>
    );
  }

  const STATUS_MAP: Record<string, string> = {
    PENDING: t('status.pending'),
    PROCESSED: t('status.processed'),
    FAILED: t('status.failed'),
    REJECTED: t('status.rejected'),
    ARCHIVED: t('status.archived')
  };

  const isAllSelected = contents.length > 0 && selectedIds.size === contents.length;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{t('title')}</h1>
        <div className="flex space-x-2">
          <button 
            onClick={handleBatchClean}
            disabled={isProcessing}
            className="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded shadow-sm transition-colors disabled:opacity-50 text-sm"
          >
            {t('actions.batch_clean')}
          </button>
          <button 
            onClick={() => handleBatchSummarize(false)}
            disabled={isProcessing}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded shadow-sm transition-colors disabled:opacity-50 text-sm"
          >
            {t('actions.regenerate_summary')}
          </button>
          <Link href="/contents/submit" className="bg-primary hover:bg-primary/90 text-white font-bold py-2 px-4 rounded shadow-sm transition-colors text-sm flex items-center">
            {t('actions.submit')}
          </Link>
        </div>
      </div>

      {/* Bulk Actions Toolbar */}
      {selectedIds.size > 0 && (
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-md mb-4 flex items-center justify-between">
          <span className="text-blue-700 font-medium">{t('actions.selected_count', { count: selectedIds.size })}</span>
          <div className="space-x-2">
            <button
              onClick={() => handleBatchSummarize(true)}
              disabled={isProcessing}
              className="bg-white border border-blue-300 text-blue-700 hover:bg-blue-50 font-semibold py-1 px-3 rounded text-sm transition-colors disabled:opacity-50"
            >
              {t('actions.generate_summary')}
            </button>
            <button
              onClick={handleBatchDelete}
              disabled={isProcessing}
              className="bg-white border border-red-300 text-red-700 hover:bg-red-50 font-semibold py-1 px-3 rounded text-sm transition-colors disabled:opacity-50"
            >
              {t('actions.delete_selected')}
            </button>
          </div>
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md border border-gray-200">
        <div className="px-6 py-3 border-b border-gray-200 bg-gray-50 flex items-center">
          <input
            type="checkbox"
            className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded mr-4"
            checked={isAllSelected}
            onChange={handleSelectAll}
          />
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">{t('actions.select_all_page')}</span>
        </div>
        <ul className="divide-y divide-gray-200">
          {contents.map((content) => (
            <li key={content.id} className={`px-6 py-4 hover:bg-gray-50 transition-colors ${selectedIds.has(content.id) ? 'bg-blue-50' : ''}`}>
              <div className="flex items-start">
                <div className="flex items-center h-full pt-1 mr-4">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    checked={selectedIds.has(content.id)}
                    onChange={() => handleSelectOne(content.id)}
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-gray-900 truncate max-w-2xl">
                      <Link href={`/contents/${content.id}`} className="hover:text-primary hover:underline">
                        {content.title}
                      </Link>
                    </h3>
                    <div className="flex items-center space-x-2">
                      {content.ai_processed && (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800" title={t('status.ai_processed')}>
                          AI
                        </span>
                      )}
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        content.status === 'PROCESSED' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {STATUS_MAP[content.status] || content.status}
                      </span>
                    </div>
                  </div>
                  <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                    {content.summary ? (
                      <span className="text-gray-700">{content.summary}</span>
                    ) : (
                      <span className="text-gray-400 italic">{t('item.no_summary')} {content.content_text?.substring(0, 100)}</span>
                    )}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
                    <span>{t('item.publish_time', { time: content.publish_time ? new Date(content.publish_time).toLocaleString('zh-CN') : t('item.unknown_time') })}</span>
                    <span className="font-mono text-gray-300">{content.id.substring(0, 8)}</span>
                  </div>
                </div>
              </div>
            </li>
          ))}
          {!loading && contents.length === 0 && (
            <li className="px-6 py-12 text-center text-gray-500">{t('empty')}</li>
          )}
        </ul>
      </div>

      <div className="mt-4 flex justify-between items-center">
        <button
          disabled={page === 1}
          onClick={() => setPage(p => Math.max(1, p - 1))}
          className="px-4 py-2 border rounded disabled:opacity-50 hover:bg-gray-50 text-sm"
        >
          {t('actions.prev_page')}
        </button>
        <span className="text-sm text-gray-600">{t('actions.page_info', { page })}</span>
        <button
          disabled={contents.length < 20}
          onClick={() => setPage(p => p + 1)}
          className="px-4 py-2 border rounded disabled:opacity-50 hover:bg-gray-50 text-sm"
        >
          {t('actions.next_page')}
        </button>
      </div>
    </div>
  );
}
