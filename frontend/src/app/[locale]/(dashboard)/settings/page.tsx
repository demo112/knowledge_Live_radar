"use client";

import React, { useEffect, useState } from 'react';
import { configApi } from '@/lib/api';
import { ConfigHistory } from '@/lib/types';
import { Settings, Save, RotateCcw, History, Cpu } from 'lucide-react';
import AIConfigForm from '@/components/settings/ai-config-form';

export default function SettingsPage() {
  const [configs, setConfigs] = useState<Record<string, any>>({});
  const [history, setHistory] = useState<ConfigHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'general' | 'ai' | 'history'>('general');

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

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const handleSave = async (key: string, value: any) => {
    setSaving(true);
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
      
      alert(`Updated ${key}`);
    } catch (error) {
      console.error("Failed to save setting", error);
      alert("保存配置失败");
    } finally {
      setSaving(false);
    }
  };

  const groupConfigs = (configs: Record<string, any>) => {
    const groups: Record<string, Record<string, any>> = {};
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
          系统配置
        </h1>
        <div className="flex space-x-2">
           <button
             onClick={() => setActiveTab('general')}
             className={`px-3 py-2 rounded-md text-sm font-medium ${activeTab === 'general' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
           >
             通用配置
           </button>
           <button
             onClick={() => setActiveTab('ai')}
             className={`px-3 py-2 rounded-md text-sm font-medium flex items-center gap-2 ${activeTab === 'ai' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
           >
             <Cpu className="w-4 h-4" />
             AI 模型
           </button>
           <button
             onClick={() => setActiveTab('history')}
             className={`px-3 py-2 rounded-md text-sm font-medium ${activeTab === 'history' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
           >
             变更历史
           </button>
        </div>
      </div>

      {loading && activeTab !== 'ai' ? (
        <div>加载配置中...</div>
      ) : activeTab === 'ai' ? (
        <AIConfigForm />
      ) : activeTab === 'general' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(configGroups).map(([group, items]) => (
            <div key={group} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white capitalize mb-4 border-b pb-2">
                {group} 配置
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
                        defaultValue={value}
                        onBlur={(e) => {
                          if (e.target.value != value.toString()) {
                             handleSave(key, e.target.value);
                          }
                        }}
                        className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 p-2 border"
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">配置项</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">旧值</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">新值</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作人</th>
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
