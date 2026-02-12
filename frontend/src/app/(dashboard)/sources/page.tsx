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
      alert('Failed to create source');
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
        alert(`Discovered: ${discovered.title} (${discovered.type})`);
      } else {
        alert('No sources found');
      }
    } catch (error) {
      console.error('Discovery failed:', error);
      alert('Discovery failed');
    } finally {
      setDiscovering(false);
    }
  };

  const handleCrawl = async (id: string) => {
    setCrawling(id);
    try {
      const response = await sourceApi.crawl(id);
      if (response.success) {
        alert(`Crawl started. New items: ${response.data.items_new}`);
        fetchSources();
      }
    } catch (error) {
      console.error('Crawl failed:', error);
      alert('Crawl failed');
    } finally {
      setCrawling(null);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Information Sources</h1>
        <button 
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          onClick={() => setShowModal(true)}
        >
          Add Source
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {sources.map((source) => (
            <li key={source.id} className="px-6 py-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">{source.name}</h3>
                <p className="text-sm text-gray-500">{source.url}</p>
                <div className="mt-1 flex items-center gap-2">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    source.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {source.status}
                  </span>
                  <span className="text-xs text-gray-500">
                    Last crawled: {source.last_crawled_at ? new Date(source.last_crawled_at).toLocaleString() : 'Never'}
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleCrawl(source.id)}
                  disabled={crawling === source.id}
                  className="bg-gray-100 text-gray-700 px-3 py-1 rounded hover:bg-gray-200 disabled:opacity-50"
                >
                  {crawling === source.id ? 'Crawling...' : 'Crawl'}
                </button>
              </div>
            </li>
          ))}
          {sources.length === 0 && (
            <li className="px-6 py-4 text-center text-gray-500">No sources found.</li>
          )}
        </ul>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Add New Source</h2>
            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">URL</label>
                <div className="flex gap-2">
                  <input 
                    type="url" 
                    required
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                    value={newSource.url}
                    onChange={e => setNewSource({...newSource, url: e.target.value})}
                  />
                  <button 
                    type="button"
                    onClick={handleDiscover}
                    disabled={discovering || !newSource.url}
                    className="mt-1 px-3 py-2 bg-gray-100 rounded hover:bg-gray-200"
                  >
                    {discovering ? '...' : '🔍'}
                  </button>
                </div>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input 
                  type="text" 
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                  value={newSource.name}
                  onChange={e => setNewSource({...newSource, name: e.target.value})}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Type</label>
                <select
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                  value={newSource.type}
                  onChange={e => setNewSource({...newSource, type: e.target.value})}
                >
                  <option value="RSS">RSS</option>
                  <option value="API">API</option>
                  <option value="WEB">Web</option>
                </select>
              </div>
              <div className="flex justify-end gap-2">
                <button 
                  type="button"
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Add
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
