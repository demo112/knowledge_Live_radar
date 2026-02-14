'use client';

import { useEffect, useState, useCallback } from 'react';
import { contentApi, contentManagementApi } from '@/lib/api';
import { ContentItem } from '@/types';
import Link from 'next/link';

export default function ContentsPage() {
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
        setError('加载内容失败，服务器返回错误。');
      }
    } catch (error) {
      console.error('Failed to fetch contents:', error);
      setError('加载内容失败，请稍后重试。');
    } finally {
      setLoading(false);
    }
  }, [page]);

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
    if (!confirm('确定要执行一键清洗吗？这将删除所有非中文或与AI无关的内容（此操作不可恢复）。')) return;
    setIsProcessing(true);
    try {
      const result = await contentManagementApi.batchClean();
      alert(`清洗完成。共扫描 ${result.total_scanned} 条，删除了 ${result.deleted_count} 条。`);
      fetchContents();
    } catch (e) {
      console.error(e);
      alert('清洗失败，请查看控制台日志。');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBatchSummarize = async (forSelected: boolean) => {
    const ids = forSelected ? Array.from(selectedIds) : undefined;
    if (forSelected && (!ids || ids.length === 0)) return;
    
    const message = forSelected 
      ? `确定为选中的 ${ids?.length} 条内容重新生成摘要吗？` 
      : '确定为所有内容重新生成摘要吗？这可能需要较长时间，任务将在后台运行。';
      
    if (!confirm(message)) return;
    
    setIsProcessing(true);
    try {
      await contentManagementApi.batchSummarize(ids, true); // overwrite=true
      alert('摘要生成任务已后台启动。请稍后刷新页面查看更新。');
      // Ideally we should poll for status or listen to socket, but for now just refresh list
      setTimeout(fetchContents, 2000); 
    } catch (e) {
      console.error(e);
      alert('任务启动失败');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBatchDelete = async () => {
    const ids = Array.from(selectedIds);
    if (ids.length === 0) return;
    
    if (!confirm(`确定删除选中的 ${ids.length} 条内容吗？此操作不可恢复。`)) return;
    
    setIsProcessing(true);
    try {
      await contentManagementApi.batchDelete(ids);
      alert('删除成功');
      setSelectedIds(new Set());
      fetchContents();
    } catch (e) {
      console.error(e);
      alert('删除失败');
    } finally {
      setIsProcessing(false);
    }
  };

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">错误: </strong>
          <span className="block sm:inline">{error}</span>
          <button 
            onClick={() => fetchContents()}
            className="mt-2 bg-red-100 hover:bg-red-200 text-red-800 font-semibold py-1 px-3 rounded text-sm transition-colors"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  const STATUS_MAP: Record<string, string> = {
    PENDING: '待处理',
    PROCESSED: '已处理',
    FAILED: '失败',
    REJECTED: '已拒绝',
    ARCHIVED: '已归档'
  };

  const isAllSelected = contents.length > 0 && selectedIds.size === contents.length;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">内容库</h1>
        <div className="flex space-x-2">
          <button 
            onClick={handleBatchClean}
            disabled={isProcessing}
            className="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded shadow-sm transition-colors disabled:opacity-50 text-sm"
          >
            一键清洗 (非中文/无AI)
          </button>
          <button 
            onClick={() => handleBatchSummarize(false)}
            disabled={isProcessing}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded shadow-sm transition-colors disabled:opacity-50 text-sm"
          >
            全量重生成摘要
          </button>
          <Link href="/contents/submit" className="bg-primary hover:bg-primary/90 text-white font-bold py-2 px-4 rounded shadow-sm transition-colors text-sm flex items-center">
            提交内容
          </Link>
        </div>
      </div>

      {/* Bulk Actions Toolbar */}
      {selectedIds.size > 0 && (
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-md mb-4 flex items-center justify-between">
          <span className="text-blue-700 font-medium">已选择 {selectedIds.size} 项</span>
          <div className="space-x-2">
            <button
              onClick={() => handleBatchSummarize(true)}
              disabled={isProcessing}
              className="bg-white border border-blue-300 text-blue-700 hover:bg-blue-50 font-semibold py-1 px-3 rounded text-sm transition-colors disabled:opacity-50"
            >
              生成摘要
            </button>
            <button
              onClick={handleBatchDelete}
              disabled={isProcessing}
              className="bg-white border border-red-300 text-red-700 hover:bg-red-50 font-semibold py-1 px-3 rounded text-sm transition-colors disabled:opacity-50"
            >
              删除选中
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
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">全选本页</span>
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
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800" title="AI已处理">
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
                      <span className="text-gray-400 italic">暂无摘要... {content.content_text?.substring(0, 100)}</span>
                    )}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
                    <span>发布时间: {content.publish_time ? new Date(content.publish_time).toLocaleString('zh-CN') : '未知'}</span>
                    <span className="font-mono text-gray-300">{content.id.substring(0, 8)}</span>
                  </div>
                </div>
              </div>
            </li>
          ))}
          {!loading && contents.length === 0 && (
            <li className="px-6 py-12 text-center text-gray-500">暂无内容。</li>
          )}
        </ul>
      </div>

      <div className="mt-4 flex justify-between items-center">
        <button
          disabled={page === 1}
          onClick={() => setPage(p => Math.max(1, p - 1))}
          className="px-4 py-2 border rounded disabled:opacity-50 hover:bg-gray-50 text-sm"
        >
          上一页
        </button>
        <span className="text-sm text-gray-600">第 {page} 页</span>
        <button
          disabled={contents.length < 20}
          onClick={() => setPage(p => p + 1)}
          className="px-4 py-2 border rounded disabled:opacity-50 hover:bg-gray-50 text-sm"
        >
          下一页
        </button>
      </div>
    </div>
  );
}
