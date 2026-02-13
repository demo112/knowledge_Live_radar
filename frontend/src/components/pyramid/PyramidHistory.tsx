'use client';

import { useState, useEffect } from 'react';
import { pyramidApi } from '@/lib/api';
import { useTranslations, useFormatter } from 'next-intl';

interface Snapshot {
  id: string;
  version: string;
  reason: string;
  created_at: string;
}

interface PyramidHistoryProps {
  pyramidId: string;
}

export default function PyramidHistory({ pyramidId }: PyramidHistoryProps) {
  const t = useTranslations('Pyramid.Detail.History');
  const format = useFormatter();
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, [pyramidId]);

  const fetchHistory = async () => {
    try {
      const response = await pyramidApi.getHistory(pyramidId);
      if (response.success) {
        setSnapshots(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch history', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>{t('loading')}</div>;

  return (
    <div className="mt-8">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{t('title')}</h3>
      <div className="flow-root">
        <ul className="-mb-8">
          {snapshots.map((snapshot, eventIdx) => (
            <li key={snapshot.id}>
              <div className="relative pb-8">
                {eventIdx !== snapshots.length - 1 ? (
                  <span
                    className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                    aria-hidden="true"
                  />
                ) : null}
                <div className="relative flex space-x-3">
                  <div>
                    <span className="h-8 w-8 rounded-full bg-gray-400 flex items-center justify-center ring-8 ring-white">
                      <svg
                        className="h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                        aria-hidden="true"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </span>
                  </div>
                  <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                    <div>
                      <p className="text-sm text-gray-500">
                        {snapshot.reason} <span className="font-medium text-gray-900">({snapshot.version})</span>
                      </p>
                    </div>
                    <div className="text-right text-sm whitespace-nowrap text-gray-500">
                      <time dateTime={snapshot.created_at}>
                        {format.dateTime(new Date(snapshot.created_at), {
                          year: 'numeric',
                          month: 'numeric',
                          day: 'numeric',
                          hour: 'numeric',
                          minute: 'numeric',
                          second: 'numeric'
                        })}
                      </time>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
          {snapshots.length === 0 && (
            <li className="text-sm text-gray-500">{t('empty')}</li>
          )}
        </ul>
      </div>
    </div>
  );
}
