'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { sourceApi, approvalApi } from '@/lib/api';
import { DiscoveredSource } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { Button } from '@/components/ui/button';

export default function DiscoveredSourceList() {
  const t = useTranslations('Sources');
  const tCommon = useTranslations('Common');
  const [sources, setSources] = useState<DiscoveredSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);

  useEffect(() => {
    fetchDiscovered();
  }, []);

  const fetchDiscovered = async () => {
    try {
      const response = await sourceApi.getDiscovered();
      if (response.success) {
        setSources(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch discovered sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string) => {
    setProcessing(id);
    try {
      const response = await approvalApi.approve(id);
      if (response.success) {
        setSources(prev => prev.filter(s => s.id !== id));
      } else {
        alert(t('alerts.operation_failed'));
      }
    } catch (error) {
      console.error('Approval failed:', error);
      alert(t('alerts.operation_failed'));
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (id: string) => {
    setProcessing(id);
    try {
      const response = await approvalApi.reject(id, 'User ignored');
      if (response.success) {
        setSources(prev => prev.filter(s => s.id !== id));
      } else {
        alert(t('alerts.operation_failed'));
      }
    } catch (error) {
      console.error('Rejection failed:', error);
      alert(t('alerts.operation_failed'));
    } finally {
      setProcessing(null);
    }
  };

  if (loading) {
    return <div className="p-4 text-center text-gray-500">{tCommon('loading')}</div>;
  }

  if (sources.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 border-2 border-dashed border-gray-200 rounded-lg">
        {t('discover_not_found')}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {sources.map((source) => (
        <div key={source.id} className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                  {source.type || 'RSS'}
                </span>
                <h3 className="text-base font-semibold text-gray-900 truncate" title={source.name}>
                  {source.name}
                </h3>
              </div>
              <p className="text-sm text-gray-600 line-clamp-2 mb-2" title={source.description}>
                {source.description || source.url}
              </p>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500">
                {source.reason && (
                  <span className="flex items-center gap-1" title={source.reason}>
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {source.reason}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {formatDistanceToNow(new Date(source.created_at), { addSuffix: true, locale: zhCN })}
                </span>
              </div>
            </div>
            <div className="flex flex-col gap-2 shrink-0">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleReject(source.id)}
                disabled={processing === source.id}
              >
                {tCommon('ignore')}
              </Button>
              <Button
                size="sm"
                onClick={() => handleApprove(source.id)}
                disabled={processing === source.id}
              >
                {tCommon('add')}
              </Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
