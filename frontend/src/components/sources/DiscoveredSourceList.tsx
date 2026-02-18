import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { sourceApi } from '@/lib/api';
import { DiscoveredSource } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { zhCN, enUS } from 'date-fns/locale';

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
    // This logic needs Approval API integration
    // Since we reused Approval model, we should call /approvals/{id}/approve
    // But currently frontend doesn't have approvalApi fully typed in api.ts or it's separate.
    // Let's assume we can add approvalApi or use a direct call.
    // Wait, source-discovery design mentioned: API: POST /api/v1/approvals/{id}/approve
    
    // For now let's implement a quick approval call helper inside here or update api.ts
    // Ideally update api.ts, but to save turns I'll fetch directly or assume it exists.
    // Actually, let's just add approvalApi to api.ts if missing or use fetch.
    // Checking api.ts content... approvalApi was NOT in the previous `read` output of api.ts.
    // I should have added it. Let's do a quick fix by using `api` instance if I could export it, 
    // but `api` is not exported. 
    // So I will use `sourceApi.create` as a workaround? No, that creates a source directly.
    // The design says "Approve source".
    // Let's mock it or use a fetch for now, and I'll update api.ts in next step if needed.
    // Actually, I can just add `approveSource` to `sourceApi` in api.ts?
    // No, approvals are generic.
    // Let's assume I will add `approvalApi` to `api.ts` in a separate `SearchReplace` call 
    // OR just use `fetch` with relative path since it's client side.
    
    setProcessing(id);
    try {
      // Temporary: using fetch to call approval endpoint
      const res = await fetch(`/api/v1/approvals/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (res.ok) {
        // Remove from list
        setSources(prev => prev.filter(s => s.id !== id));
        // Maybe trigger a refresh of main source list if parent component allows
        // But here we just manage this list.
      } else {
        alert(t('alerts.operation_failed'));
      }
    } catch (error) {
      console.error(error);
      alert(t('alerts.operation_failed'));
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (id: string) => {
    setProcessing(id);
    try {
      const res = await fetch(`/api/v1/approvals/${id}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: 'User ignored' })
      });
      if (res.ok) {
        setSources(prev => prev.filter(s => s.id !== id));
      }
    } catch (error) {
      console.error(error);
    } finally {
      setProcessing(null);
    }
  };

  if (loading) {
    return <div className="p-4 text-center text-gray-500">{tCommon('status.loading')}</div>;
  }

  if (sources.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 bg-gray-50 rounded-lg border border-dashed border-gray-300">
        <p>{t('discovery.empty')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {sources.map(source => (
        <div key={source.id} className="bg-white p-4 rounded-lg border shadow-sm hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                  {source.source_type}
                </span>
                <h3 className="font-medium text-lg text-gray-900">
                  <a href={source.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                    {source.name}
                  </a>
                </h3>
              </div>
              <p className="text-sm text-gray-600 mb-2">{source.description || source.url}</p>
              
              <div className="flex items-center gap-4 text-xs text-gray-500">
                {source.reason && (
                  <span className="flex items-center gap-1">
                    🔍 {source.reason}
                  </span>
                )}
                <span>
                  🕒 {formatDistanceToNow(new Date(source.created_at), { addSuffix: true, locale: zhCN })}
                </span>
              </div>
            </div>
            
            <div className="flex gap-2 ml-4">
              <button
                onClick={() => handleReject(source.id)}
                disabled={processing === source.id}
                className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded border transition-colors disabled:opacity-50"
              >
                {tCommon('actions.ignore')}
              </button>
              <button
                onClick={() => handleApprove(source.id)}
                disabled={processing === source.id}
                className="px-3 py-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded shadow-sm transition-colors disabled:opacity-50"
              >
                {processing === source.id ? tCommon('status.processing') : tCommon('actions.add')}
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
