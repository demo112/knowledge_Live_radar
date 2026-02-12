'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { sourceApi, discoveryApi } from '@/lib/api';
import { InformationSource } from '@/types';

export default function SourcesPage() {
  const [sources, setSources] = useState<InformationSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingSource, setEditingSource] = useState<InformationSource | null>(null);
  const [formData, setFormData] = useState({ name: '', url: '', type: 'RSS' });
  const [discovering, setDiscovering] = useState(false);
  const [crawling, setCrawling] = useState<string | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; id: string | null }>({ open: false, id: null });

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const response = await sourceApi.getAll();
      if (response.success) {
        setSources(response.data.items);
      }
    } catch (error) {
      console.error('Failed to fetch sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreateModal = () => {
    setEditingSource(null);
    setFormData({ name: '', url: '', type: 'RSS' });
    setShowModal(true);
  };

  const handleOpenEditModal = (source: InformationSource) => {
    setEditingSource(source);
    setFormData({ name: source.name, url: source.url, type: source.type });
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
    } catch (error) {
      console.error('Failed to delete source:', error);
      alert('删除失败');
    } finally {
      setDeleteConfirm({ open: false, id: null });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (editingSource) {
        await sourceApi.update(editingSource.id, {
          ...formData,
          config: { feed_url: formData.url }
        });
      } else {
        await sourceApi.create({
          ...formData,
          config: { feed_url: formData.url }
        });
      }
      setShowModal(false);
      fetchSources();
    } catch (error) {
      console.error('Failed to save source:', error);
      alert('保存失败');
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
        alert(`已发现: ${discovered.title} (${discovered.type})`);
      } else {
        alert('未找到信息源');
      }
    } catch (error) {
      console.error('Discovery failed:', error);
      alert('发现失败');
    } finally {
      setDiscovering(false);
    }
  };

  const handleCrawl = async (id: string) => {
    setCrawling(id);
    try {
      const response = await sourceApi.crawl(id);
      if (response.success) {
        alert(`抓取已开始。新增项目: ${response.data.items_new}`);
        fetchSources();
      }
    } catch (error) {
      console.error('Crawl failed:', error);
      alert('抓取失败');
    } finally {
      setCrawling(null);
    }
  };

  const handleTest = async (id: string) => {
    setTesting(id);
    try {
      const response = await sourceApi.test(id);
      if (response.success) {
        alert('测试成功！信息源可正常访问。');
      } else {
        alert(`测试失败: ${response.error?.message || '未知错误'}`);
      }
    } catch (error) {
      console.error('Test failed:', error);
      alert('测试失败');
    } finally {
      setTesting(null);
    }
  };

  if (loading && sources.length === 0) return <div className="p-8">加载中...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">信息源</h1>
        <div className="flex gap-3">
          <Link
            href="/sources/whitelist"
            className="bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 px-4 py-2 rounded shadow-sm transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            管理白名单
          </Link>
          <button 
            className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded shadow-sm transition-colors"
            onClick={handleOpenCreateModal}
          >
            添加信息源
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
                      {source.type}
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full font-medium ${source.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {source.status}
                    </span>
                    <span>上次抓取: {source.last_crawled_at ? new Date(source.last_crawled_at).toLocaleString('zh-CN') : '从未'}</span>
                  </div>
                </div>
                <div className="ml-4 flex-shrink-0 flex items-center gap-3">
                   <button 
                    onClick={() => handleCrawl(source.id)}
                    disabled={!!crawling}
                    className="text-primary hover:text-primary/80 font-medium disabled:opacity-50"
                    title="立即抓取"
                   >
                     {crawling === source.id ? '抓取中...' : '抓取'}
                   </button>
                   <button 
                    onClick={() => handleTest(source.id)}
                    disabled={!!testing}
                    className="text-gray-600 hover:text-gray-900 font-medium disabled:opacity-50"
                    title="测试连接"
                   >
                     {testing === source.id ? '测试中...' : '测试'}
                   </button>
                   <div className="h-4 w-px bg-gray-300 mx-1"></div>
                   <button
                    onClick={() => handleOpenEditModal(source)}
                    className="p-1 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="编辑"
                   >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                   </button>
                   <button
                    onClick={() => handleDelete(source.id)}
                    className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="删除"
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
            <li className="px-6 py-12 text-center text-gray-500">未找到信息源。</li>
          )}
        </ul>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm.open && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-sm shadow-xl">
            <h3 className="text-lg font-bold mb-2">确认删除</h3>
            <p className="text-gray-600 mb-6">确定要删除这个信息源吗？此操作不可撤销。</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setDeleteConfirm({ open: false, id: null })}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleConfirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h2 className="text-xl font-bold mb-4">{editingSource ? '编辑信息源' : '添加新信息源'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
                <div className="flex gap-2">
                    <input 
                    type="url" 
                    required
                    className="flex-1 border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary/50 outline-none"
                    value={formData.url}
                    onChange={(e) => setFormData({...formData, url: e.target.value})}
                    placeholder="https://example.com/rss"
                    />
                    <button 
                        type="button"
                        onClick={handleDiscover}
                        disabled={discovering || !formData.url}
                        className="bg-secondary hover:bg-secondary/90 text-white px-3 py-2 rounded text-sm disabled:opacity-50"
                    >
                        {discovering ? '发现中' : '发现'}
                    </button>
                </div>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">名称</label>
                <input 
                  type="text" 
                  required
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary/50 outline-none"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="例如：技术博客"
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-1">类型</label>
                <select 
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary/50 outline-none"
                  value={formData.type}
                  onChange={(e) => setFormData({...formData, type: e.target.value})}
                >
                  <option value="RSS">RSS</option>
                  <option value="SITEMAP">Sitemap</option>
                  <option value="WEB">Website</option>
                </select>
              </div>
              <div className="flex justify-end gap-3">
                <button 
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                  disabled={submitting}
                >
                  取消
                </button>
                <button 
                  type="submit"
                  className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded shadow-sm disabled:opacity-50 transition-colors"
                  disabled={submitting}
                >
                  {submitting ? '保存中...' : (editingSource ? '保存修改' : '立即添加')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
