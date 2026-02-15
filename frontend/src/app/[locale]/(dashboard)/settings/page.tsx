"use client";

import React, { useEffect, useState } from 'react';
import { configApi, evolutionApi } from '@/lib/api';
import { ConfigHistory } from '@/lib/types';
import { Settings, Cpu, ListTodo, Play } from 'lucide-react';
import AIConfigForm from '@/components/settings/ai-config-form';
import { useTranslations } from 'next-intl';

export default function SettingsPage() {
  const t = useTranslations('Settings');
  const tGeneral = useTranslations('Settings.General');
  const tTasks = useTranslations('Settings.Tasks');
  const tHistory = useTranslations('Settings.History');

  const [configs, setConfigs] = useState<Record<string, unknown>>({});
  const [history, setHistory] = useState<ConfigHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'general' | 'ai' | 'history' | 'tasks'>('general');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        if (activeTab === 'general') {
          const configData = await configApi.getAll();
          setConfigs(configData);
        } else if (activeTab === 'history') {
          const historyData = await configApi.getHistory();
          setHistory(historyData);
        }
      } catch (error) {
        console.error("Failed to fetch settings", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [activeTab]);

  const handleBatchClassify = async () => {
    if (!confirm(tTasks('batch_classify.confirm'))) return;
    
    setProcessing(true);
    try {
      const result = await evolutionApi.batchClassify();
      if (result.success) {
        alert(tTasks('batch_classify.started'));
      } else {
        alert(tTasks('batch_classify.start_failed'));
      }
    } catch (error) {
      console.error('Failed to trigger batch classification', error);
      alert(tTasks('batch_classify.trigger_failed'));
    } finally {
      setProcessing(false);
    }
  };

  const handleSave = async (key: string, value: unknown) => {
    try {
      // Parse number if needed
      let parsedValue = value;
      if (!isNaN(Number(value)) && typeof configs[key] === 'number') {
        parsedValue = Number(value);
      }
      
      await configApi.update(key, parsedValue);
      // Refresh
      const newConfigs = await configApi.getAll();
      setConfigs(newConfigs);
      const newHistory = await configApi.getHistory();
      setHistory(newHistory);
      
      alert(t('save_success', { key }));
    } catch (error: unknown) {
      console.error("Failed to save setting", error);
      alert(t('save_failed'));
    }
  };

  const groupConfigs = (configs: Record<string, unknown>) => {
    const groups: Record<string, Record<string, unknown>> = {};
    Object.keys(configs).forEach(key => {
      const [group] = key.split('.');
      if (!groups[group]) groups[group] = {};
      groups[group][key] = configs[key];
    });
    return groups;
  };

  const configGroups = groupConfigs(configs);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-900 dark:text-white">
          <Settings className="w-6 h-6 text-blue-600" />
          {t('title')}
        </h1>
        <div className="flex space-x-2">
           <button
             onClick={() => setActiveTab('general')}
             className={`px-3 py-2 rounded-md text-sm font-medium ${activeTab === 'general' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
           >
             {t('tabs.general')}
           </button>
           <button
             onClick={() => setActiveTab('ai')}
             className={`px-3 py-2 rounded-md text-sm font-medium flex items-center gap-2 ${activeTab === 'ai' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
           >
             <Cpu className="w-4 h-4" />
             {t('tabs.ai')}
           </button>
           <button
             onClick={() => setActiveTab('history')}
             className={`px-3 py-2 rounded-md text-sm font-medium ${activeTab === 'history' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
           >
             {t('tabs.history')}
           </button>
           <button
             onClick={() => setActiveTab('tasks')}
             className={`px-3 py-2 rounded-md text-sm font-medium flex items-center gap-2 ${activeTab === 'tasks' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
           >
             <ListTodo className="w-4 h-4" />
             {t('tabs.tasks')}
           </button>
        </div>
      </div>

      {loading && activeTab !== 'ai' && activeTab !== 'tasks' ? (
        <div>{t('loading')}</div>
      ) : activeTab === 'ai' ? (
        <AIConfigForm />
      ) : activeTab === 'tasks' ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 space-y-6">
           <h2 className="text-lg font-semibold text-gray-900 dark:text-white border-b pb-4 mb-4">
             {tTasks('title')}
           </h2>
           
           <div className="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg border border-gray-100 dark:border-gray-700">
             <div className="flex justify-between items-center">
               <div>
                 <h3 className="font-medium text-gray-900 dark:text-white">{tTasks('batch_classify.title')}</h3>
                 <p className="text-sm text-gray-500 mt-1">
                   {tTasks('batch_classify.description')}
                 </p>
               </div>
               <button
                 onClick={handleBatchClassify}
                 disabled={processing}
                 className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
               >
                 <Play className="w-4 h-4" />
                 {processing ? tTasks('batch_classify.processing') : tTasks('batch_classify.button')}
               </button>
             </div>
           </div>
        </div>
      ) : activeTab === 'general' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(configGroups).map(([group, items]) => (
            <div key={group} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white capitalize mb-4 border-b pb-2">
                {tGeneral('title', { group })}
              </h2>
              <div className="space-y-4">
                {Object.entries(items).map(([key, value]) => (
                  <div key={key} className="flex flex-col space-y-1">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {key.split('.').slice(1).join(' ')}
                    </label>
                    <div className="flex gap-2">
                      <input
                        type={typeof value === 'number' ? 'number' : 'text'}
                        defaultValue={value as string | number}
                        onBlur={(e) => {
                          if (e.target.value != String(value)) {
                             handleSave(key, e.target.value);
                          }
                        }}
                        className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-700 p-2 border"
                      />
                    </div>
                    <p className="text-xs text-gray-400">{key}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{tHistory('columns.time')}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{tHistory('columns.config_key')}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{tHistory('columns.old_value')}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{tHistory('columns.new_value')}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{tHistory('columns.operator')}</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {history.map((h) => (
                <tr key={h.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(h.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    {h.config_key}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {JSON.stringify(h.old_value)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {JSON.stringify(h.new_value)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {h.changed_by}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
