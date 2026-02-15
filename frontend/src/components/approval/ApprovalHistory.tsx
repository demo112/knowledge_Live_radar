'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { approvalApi } from '@/lib/api';
import { Approval } from '@/types';
import { format } from 'date-fns';

export default function ApprovalHistory() {
  const t = useTranslations('Approval.History');
  const tTypes = useTranslations('Approval.types');
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      // Fetch different statuses
      const [executedRes, rejectedRes, rolledBackRes] = await Promise.all([
        approvalApi.getAll('executed'),
        approvalApi.getAll('rejected'),
        approvalApi.getAll('rolled_back')
      ]);
      
      let all: Approval[] = [];
      if (executedRes.success) all = [...all, ...executedRes.data];
      if (rejectedRes.success) all = [...all, ...rejectedRes.data];
      if (rolledBackRes.success) all = [...all, ...rolledBackRes.data];
      
      // Sort by updated_at desc
      all.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
      
      setApprovals(all);
    } catch (error) {
      console.error('Failed to fetch approval history', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (id: string) => {
    if (!confirm(t('actions.rollback_confirm'))) return;
    
    try {
      await approvalApi.rollback(id);
      alert(t('actions.rollback_success'));
      fetchHistory();
    } catch (error) {
      console.error('Rollback failed', error);
      alert(t('actions.rollback_failed'));
    }
  };

  const statusMap: Record<string, string> = {
    executed: t('status.executed'),
    rejected: t('status.rejected'),
    rolled_back: t('status.rolled_back')
  };

  if (loading) return <div>{t('loading')}</div>;

  return (
    <div className="bg-card shadow-sm border border-border sm:rounded-lg">
      <ul className="divide-y divide-border">
        {approvals.length === 0 ? (
          <li className="px-6 py-12 text-center text-muted-foreground">{t('empty')}</li>
        ) : (
          approvals.map((approval) => (
            <li key={approval.id} className="px-6 py-4 hover:bg-muted/50 transition-colors duration-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      approval.status === 'executed' ? 'bg-green-100 text-green-800' :
                      approval.status === 'rejected' ? 'bg-red-100 text-red-800' :
                      approval.status === 'rolled_back' ? 'bg-gray-100 text-gray-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {statusMap[approval.status] || approval.status}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {format(new Date(approval.updated_at), 'yyyy-MM-dd HH:mm')}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                      {tTypes.has(approval.type) ? tTypes(approval.type) : approval.type}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-foreground">
                    {approval.reason || t('no_description')}
                  </p>
                </div>
                
                {approval.status === 'executed' && (
                  <button
                    onClick={() => handleRollback(approval.id)}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    {t('actions.rollback')}
                  </button>
                )}
              </div>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
