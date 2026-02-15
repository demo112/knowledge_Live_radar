'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { whitelistApi, discoveryApi } from '@/lib/api';
import { DomainWhitelist, DiscoveredDomain } from '@/types';

export default function WhitelistPage() {
  const t = useTranslations('Sources.Whitelist');
  const [activeTab, setActiveTab] = useState<'whitelist' | 'discovered'>('whitelist');
  
  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{t('title')}</h1>
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
            {t('tabs.allowed')}
          </button>
          <button
            onClick={() => setActiveTab('discovered')}
            className={`${
              activeTab === 'discovered'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            {t('tabs.discovered')}
          </button>
        </nav>
      </div>

      {activeTab === 'whitelist' ? <WhitelistTab /> : <DiscoveredTab />}
    </div>
  );
}

function WhitelistTab() {
  const t = useTranslations('Sources.Whitelist');
  const tCommon = useTranslations('Common');
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
      alert(t('alerts.add_failed'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t('actions.confirm_remove'))) return;
    try {
      await whitelistApi.remove(id);
      fetchItems();
    } catch (error: unknown) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        if ((error as any).response?.status === 404) {
          // Already removed, just refresh
          fetchItems();
        } else {
          console.error('Failed to remove domain:', error);
          alert(t('alerts.remove_failed'));
        }
      }
  };

  if (loading) return <div>{tCommon('loading')}</div>;

  return (
    <div>
      <div className="mb-4">
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow-sm transition-colors"
        >
          {t('actions.add')}
        </button>
      </div>
      
      <div className="bg-white shadow overflow-hidden sm:rounded-md border border-gray-200">
        <ul className="divide-y divide-gray-200">
          {items.map((item) => (
            <li key={item.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{item.domain}</h3>
                  <p className="text-sm text-gray-500">{t('columns.credibility')}: {item.credibility} | {t('columns.reason')}: {item.reason || '-'}</p>
                </div>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  {t('actions.remove')}
                </button>
              </div>
            </li>
          ))}
          {items.length === 0 && <li className="px-6 py-12 text-center text-gray-500">{t('empty.allowed')}</li>}
        </ul>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h2 className="text-xl font-bold mb-4">{t('modal.title')}</h2>
            <form onSubmit={handleAdd}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">{t('modal.domain_label')}</label>
                <input
                  type="text"
                  required
                  className="w-full border rounded px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.domain}
                  onChange={e => setFormData({...formData, domain: e.target.value})}
                  placeholder={t('modal.domain_placeholder')}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">{t('modal.credibility_label')}</label>
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
                <label className="block text-sm font-medium mb-1">{t('modal.reason_label')}</label>
                <textarea
                  className="w-full border rounded px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.reason}
                  onChange={e => setFormData({...formData, reason: e.target.value})}
                />
              </div>
              <div className="flex justify-end gap-3">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">{t('modal.cancel')}</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">{t('modal.save')}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function DiscoveredTab() {
  const t = useTranslations('Sources.Whitelist');
  const tCommon = useTranslations('Common');
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
        reason: t('actions.add_reason_discovered')
      });
      alert(t('alerts.add_success'));
      fetchItems();
    } catch (error) {
      console.error('Failed to add to whitelist:', error);
      alert(t('alerts.add_failed'));
    }
  };

  if (loading) return <div>{tCommon('loading')}</div>;

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('columns.domain')}</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('columns.count')}</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('columns.status')}</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('columns.rss')}</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">{t('columns.actions')}</th>
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
                  {t('actions.add_to_whitelist')}
                </button>
              </td>
            </tr>
          ))}
          {items.length === 0 && (
            <tr>
              <td colSpan={5} className="px-6 py-12 text-center text-gray-500">{t('empty.discovered')}</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
