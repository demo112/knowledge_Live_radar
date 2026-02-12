'use client';

import { useEffect, useState } from 'react';
import { sourceApi, discoveryApi } from '@/lib/api';
import { InformationSource } from '@/types';

export default function SourcesPage() {
  const [sources, setSources] = useState<InformationSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newSource, setNewSource] = useState({ name: '', url: '', type: 'RSS' });
  const [discovering, setDiscovering] = useState(false);
  const [crawling, setCrawling] = useState<string | null>(null);

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

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await sourceApi.create({
        ...newSource,
        config: { feed_url: newSource.url }
      });
      setShowModal(false);
      setNewSource({ name: '', url: '', type: 'RSS' });
      fetchSources();
    } catch (error) {
      alert('创建信息源失败');
    }
  };

  const handleDiscover = async () => {
    if (!newSource.url) return;
    setDiscovering(true);
    try {
      const response = await discoveryApi.discover(newSource.url);
      if (response.success && response.data.length > 0) {
        // Just pick the first one for now or show a list
        const discovered = response.data[0];
        setNewSource({ ...newSource, name: discovered.title, url: discovered.url, type: discovered.type });
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

  if (loading) return <div>加载中...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">信息源</h1>
        <button 
          className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded shadow-sm transition-colors"
          onClick={() => setShowModal(true)}
        >
          添加信息源
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md border border-gray-200">
        <ul className="divide-y divide-gray-200">
          {sources.map((source) => (
            <li key={source.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
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
                    <span>状态: {source.status}</span>
                    <span>上次抓取: {source.last_crawled_at ? new Date(source.last_crawled_at).toLocaleString('zh-CN') : '从未'}</span>
                  </div>
                </div>
                <div className="ml-4 flex-shrink-0 flex gap-2">
                   <button 
                    onClick={() => handleCrawl(source.id)}
                    disabled={!!crawling}
                    className="text-primary hover:text-primary/80 font-medium disabled:opacity-50"
                   >
                     {crawling === source.id ? '抓取中...' : '抓取'}
                   </button>
                   <button 
                    onClick={() => alert('测试功能待开发')}
                    className="text-gray-600 hover:text-gray-900 font-medium"
                   >
                     测试
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

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h2 className="text-xl font-bold mb-4">添加新信息源</h2>
            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
                <div className="flex gap-2">
                    <input 
                    type="url" 
                    required
                    className="flex-1 border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                    value={newSource.url}
                    onChange={(e) => setNewSource({...newSource, url: e.target.value})}
                    placeholder="https://example.com/rss"
                    />
                    <button 
                        type="button"
                        onClick={handleDiscover}
                        disabled={discovering || !newSource.url}
                        className="bg-secondary hover:bg-secondary/90 text-white px-3 py-2 rounded text-sm disabled:opacity-50"
                    >
                        {discovering ? '...' : '发现'}
                    </button>
                </div>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">名称</label>
                <input 
                  type="text" 
                  required
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                  value={newSource.name}
                  onChange={(e) => setNewSource({...newSource, name: e.target.value})}
                  placeholder="Example Blog"
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-1">类型</label>
                <select 
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                  value={newSource.type}
                  onChange={(e) => setNewSource({...newSource, type: e.target.value})}
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
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  取消
                </button>
                <button 
                  type="submit"
                  className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded shadow-sm"
                >
                  添加
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
