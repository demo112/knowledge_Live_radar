"use client";

import React, { useEffect, useState, useCallback } from 'react';
import { approvalApi } from '@/lib/api';
import ChangeTimeline from '@/components/history/ChangeTimeline';
import ChangeDetail from '@/components/history/ChangeDetail';
import RollbackDialog from '@/components/history/RollbackDialog';
import { ChangeItem } from '@/lib/types';
import { CHANGE_TYPE_MAP } from '@/lib/constants';
import { useTranslations } from 'next-intl';

export default function HistoryPage() {
  const t = useTranslations('History');
  const tFilters = useTranslations('History.filters');
  const tRollback = useTranslations('History.rollback');
  const tTypes = useTranslations('History.types');
  
  const [history, setHistory] = useState<ChangeItem[]>([]);
  const [filteredHistory, setFilteredHistory] = useState<ChangeItem[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('executed'); // executed, rolled_back, all
  
  // Selection
  const [selectedItem, setSelectedItem] = useState<ChangeItem | null>(null);
  const [rollbackItem, setRollbackItem] = useState<ChangeItem | null>(null);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      // If statusFilter is 'all', we might want to fetch everything, but typically History is about past actions.
      // Let's fetch based on filter.
      const status = statusFilter === 'all' ? undefined : statusFilter;
      const response = await approvalApi.getAll(status);
      
      if (response.success) {
        // Filter out pending/queued/approved/rejected if we only want history (executed/rolled_back)
        // Unless user explicitly selects 'all' which might show everything.
        // For 'Change History' page, we usually care about what *happened*.
        let data = response.data;
        if (statusFilter === 'all') {
          data = data.filter((item: ChangeItem) => ['executed', 'rolled_back'].includes(item.status));
        }
        setHistory(data);
        setFilteredHistory(data);
      }
    } catch (error) {
      console.error('Failed to fetch history', error);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  useEffect(() => {
    let result = history;
    if (typeFilter !== 'all') {
      result = result.filter(item => item.type === typeFilter);
    }
    setFilteredHistory(result);
  }, [typeFilter, history]);

  const handleRollback = async () => {
    if (!rollbackItem) return;
    
    try {
      await approvalApi.rollback(rollbackItem.id);
      setRollbackItem(null);
      setSelectedItem(null);
      await fetchHistory();
      alert(tRollback('success'));
    } catch (error) {
      console.error('Rollback failed', error);
      alert(tRollback('failed'));
    }
  };

  const handleExport = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(filteredHistory, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "change_history.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('title')}</h1>
        <button
          onClick={handleExport}
          className="px-4 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:outline-none focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
        >
          {t('export')}
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-8 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div>
          <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">{tFilters('status')}</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          >
            <option value="executed">{tFilters('executed')}</option>
            <option value="rolled_back">{tFilters('rolled_back')}</option>
            <option value="all">{tFilters('all_status')}</option>
          </select>
        </div>
        <div>
          <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">{tFilters('type')}</label>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          >
            <option value="all">{tFilters('all_types')}</option>
            {Object.keys(CHANGE_TYPE_MAP).map((key) => (
              <option key={key} value={key}>{tTypes(key)}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <ChangeTimeline items={filteredHistory} onSelect={setSelectedItem} />
      )}

      {selectedItem && (
        <ChangeDetail
          change={selectedItem}
          onClose={() => setSelectedItem(null)}
          onRollback={(item) => setRollbackItem(item)}
        />
      )}

      <RollbackDialog
        isOpen={!!rollbackItem}
        onClose={() => setRollbackItem(null)}
        onConfirm={handleRollback}
        title={rollbackItem?.type ? tTypes(rollbackItem.type) : t('detail.change_data')}
      />
    </div>
  );
}
