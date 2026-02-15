import React from 'react';
import { ChangeItem } from '@/lib/types';
import { useTranslations } from 'next-intl';

interface Props {
  change: ChangeItem;
  onClose: () => void;
  onRollback: (change: ChangeItem) => void;
}

export default function ChangeDetail({ change, onClose, onRollback }: Props) {
  const t = useTranslations('History.detail');
  const tTypes = useTranslations('History.types');
  const tStatus = useTranslations('History.status');
  const tRisk = useTranslations('History.risk');

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const canRollback = change.status === 'executed';

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col border border-gray-200 dark:border-gray-700">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            {tTypes(change.type)}
            <span className={`text-sm font-medium px-2.5 py-0.5 rounded ${
                change.status === 'executed' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            }`}>
                {tStatus(change.status)}
            </span>
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Metadata Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
              <span className="text-sm text-gray-500 dark:text-gray-400 block mb-1">{t('time')}</span>
              <span className="font-medium">{formatDate(change.created_at)}</span>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
              <span className="text-sm text-gray-500 dark:text-gray-400 block mb-1">{t('applicant')}</span>
              <span className="font-medium">{change.applicant_id || t('system')}</span>
            </div>
            {change.reason && (
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg md:col-span-2">
                <span className="text-sm text-gray-500 dark:text-gray-400 block mb-1">{t('reason')}</span>
                <span className="font-medium">{change.reason}</span>
              </div>
            )}
          </div>

          {/* Impact Analysis */}
          {change.impact_analysis && (
            <div>
              <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">{t('impact_analysis')}</h3>
              <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg border border-blue-100 dark:border-blue-800">
                <div className="flex items-center gap-4 mb-2">
                   <span className="text-sm font-semibold text-blue-800 dark:text-blue-300">
                     {t('risk_level')}: {tRisk(change.impact_analysis.risk_level)}
                   </span>
                   <span className="text-sm text-blue-700 dark:text-blue-400">
                     {t('affected_nodes')}: {change.impact_analysis.affected_nodes_count}
                   </span>
                </div>
                <p className="text-sm text-blue-900 dark:text-blue-200">
                  {change.impact_analysis.description}
                </p>
              </div>
            </div>
          )}

          {/* Data Payloads */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">{t('change_data')}</h3>
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto max-h-60 border border-gray-200 dark:border-gray-700">
                <pre className="text-xs text-gray-800 dark:text-gray-300">{JSON.stringify(change.data, null, 2)}</pre>
              </div>
            </div>
            {!!change.original_data && (
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">{t('original_data')}</h3>
                <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto max-h-60 border border-gray-200 dark:border-gray-700">
                  <pre className="text-xs text-gray-800 dark:text-gray-300">{JSON.stringify(change.original_data, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600"
          >
            {t('close')}
          </button>
          {canRollback && (
            <button
              onClick={() => onRollback(change)}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 focus:ring-4 focus:ring-red-300 dark:focus:ring-red-900"
            >
              {t('rollback_change')}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
