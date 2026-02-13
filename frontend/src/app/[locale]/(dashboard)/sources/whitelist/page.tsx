'use client';

import { useEffect, useState } from 'react';
import { whitelistApi, discoveryApi } from '@/lib/api';
import { DomainWhitelist, DiscoveredDomain } from '@/types';

export default function WhitelistPage() {
  const [activeTab, setActiveTab] = useState<'whitelist' | 'discovered'>('whitelist');
  
  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">域名白名单管理</h1>
      </div>

      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('whitelist')}
            className={`${
              activeTab === 'whitelist'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            已允许域名
          </button>
          <button
            onClick={() => setActiveTab('discovered')}
            className={`${
              activeTab === 'discovered'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            新发现域名
          </button>
        </nav>
      </div>

      {activeTab === 'whitelist' ? <WhitelistTab /> : <DiscoveredTab />}
    </div>
  );
}

function WhitelistTab() {
  const [items, setItems] = useState<DomainWhitelist[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ domain: '', credibility: 50, reason: '' });

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await whitelistApi.getAll();
      setItems(response.items);
    } catch (error) {
      console.error('Failed to fetch whitelist:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await whitelistApi.add({
        domain: formData.domain,
        credibility: formData.credibility,
        reason: formData.reason
      });
      setShowModal(false);
      fetchItems();
      setFormData({ domain: '', credibility: 50, reason: '' });
    } catch (error) {
      console.error('Failed to add domain:', error);
      alert('添加失败');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定要移除该域名吗？')) return;
    try {
      await whitelistApi.remove(id);
      fetchItems();
    } catch (error: any) {
      if (error.response?.status === 404) {
        // Already removed, just refresh
        fetchItems();
      } else {
        console.error('Failed to remove domain:', error);
        alert('移除失败');
      }
    }
  };

  if (loading) return <div>加载中...</div>;

  return (
    <div>
      <div className="mb-4">
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow-sm transition-colors"
        >
          添加域名
        </button>
      </div>
      
      <div className="bg-white shadow overflow-hidden sm:rounded-md border border-gray-200">
        <ul className="divide-y divide-gray-200">
          {items.map((item) => (
            <li key={item.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{item.domain}</h3>
                  <p className="text-sm text-gray-500">可信度: {item.credibility} | 原因: {item.reason || '-'}</p>
                </div>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  移除
                </button>
              </div>
            </li>
          ))}
          {items.length === 0 && <li className="px-6 py-12 text-center text-gray-500">暂无数据</li>}
        </ul>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h2 className="text-xl font-bold mb-4">添加白名单域名</h2>
            <form onSubmit={handleAdd}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">域名</label>
                <input
                  type="text"
                  required
                  className="w-full border rounded px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.domain}
                  onChange={e => setFormData({...formData, domain: e.target.value})}
                  placeholder="example.com 或 *.example.com"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">可信度 (0-100)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  className="w-full border rounded px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.credibility}
                  onChange={e => setFormData({...formData, credibility: parseInt(e.target.value)})}
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium mb-1">原因</label>
                <textarea
                  className="w-full border rounded px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.reason}
                  onChange={e => setFormData({...formData, reason: e.target.value})}
                />
              </div>
              <div className="flex justify-end gap-3">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">取消</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">保存</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function DiscoveredTab() {
  const [items, setItems] = useState<DiscoveredDomain[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await discoveryApi.getDiscoveredDomains();
      if (response.success && response.data) {
        setItems(response.data);
      } else if (response.items) {
        setItems(response.items);
      }
    } catch (error) {
      console.error('Failed to fetch discovered domains:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToWhitelist = async (domain: string) => {
    try {
      await whitelistApi.add({
        domain,
        credibility: 50,
        reason: "Added from discovered list"
      });
      alert('已添加到白名单');
      fetchItems();
    } catch (error) {
      console.error('Failed to add to whitelist:', error);
      alert('添加失败');
    }
  };

  if (loading) return <div>加载中...</div>;

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">域名</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">出现次数</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RSS</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {items.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.domain}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.occurrence_count}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  item.evaluation_status === 'APPROVED' ? 'bg-green-100 text-green-800' :
                  item.evaluation_status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {item.evaluation_status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.has_rss ? '✅' : '❌'}</td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => addToWhitelist(item.domain)}
                  className="text-blue-600 hover:text-blue-900"
                >
                  添加白名单
                </button>
              </td>
            </tr>
          ))}
          {items.length === 0 && (
            <tr>
              <td colSpan={5} className="px-6 py-12 text-center text-gray-500">暂无新发现域名</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
