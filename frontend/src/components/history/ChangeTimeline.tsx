import React from 'react';
import { ChangeItem } from '@/lib/types';
import { useTranslations } from 'next-intl';

interface Props {
  items: ChangeItem[];
  onSelect: (item: ChangeItem) => void;
}

export default function ChangeTimeline({ items, onSelect }: Props) {
  const t = useTranslations('History');
  const tTypes = useTranslations('History.types');
  const tStatus = useTranslations('History.status');

  if (!items.length) {
    return <div className="text-gray-500 text-center py-10">{t('timeline.empty')}</div>;
  }

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

  return (
    <div className="relative border-l border-gray-200 dark:border-gray-700 ml-3">
      {items.map((item) => (
        <div key={item.id} className="mb-10 ml-6">
          <span className={`absolute flex items-center justify-center w-6 h-6 rounded-full -left-3 ring-8 ring-white dark:ring-gray-900 ${
            item.status === 'executed' ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'
          }`}>
            <svg className={`w-2.5 h-2.5 ${item.status === 'executed' ? 'text-green-800 dark:text-green-300' : 'text-red-800 dark:text-red-300'}`} aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
              <path d="M20 4a2 2 0 0 0-2-2h-2V1a1 1 0 0 0-2 0v1h-3V1a1 1 0 0 0-2 0v1H6V1a1 1 0 0 0-2 0v1H2a2 2 0 0 0-2 2v2h20V4ZM0 18a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8H0v10Zm5-8h10a1 1 0 0 1 0 2H5a1 1 0 0 1 0-2Z"/>
            </svg>
          </span>
          <h3 className="flex items-center mb-1 text-lg font-semibold text-gray-900 dark:text-white">
            {tTypes(item.type)}
            {item.applicant_id && (
                <span className="bg-blue-100 text-blue-800 text-sm font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-blue-900 dark:text-blue-300 ml-3">
                    {item.applicant_id}
                </span>
            )}
            <span className={`ml-2 text-sm font-medium px-2.5 py-0.5 rounded ${
                item.status === 'executed' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            }`}>
                {tStatus(item.status)}
            </span>
          </h3>
          <time className="block mb-2 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">
            {formatDate(item.created_at)}
          </time>
          <div className="mb-4 text-base font-normal text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-4 rounded-lg overflow-x-auto">
            <pre className="text-xs">{JSON.stringify(item.data, null, 2)}</pre>
          </div>
          <button 
            onClick={() => onSelect(item)}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:outline-none focus:ring-gray-200 focus:text-blue-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 dark:focus:ring-gray-700"
          >
            {t('timeline.details')}
            <svg className="w-3 h-3 ml-2 rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10">
                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 5h12m0 0L9 1m4 4L9 9"/>
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}
