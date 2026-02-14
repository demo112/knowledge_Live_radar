'use client';

import { useState, useEffect } from 'react';
import { approvalApi } from '@/lib/api';
import { Approval } from '@/types';
import { format } from 'date-fns';

export default function ApprovalHistory() {
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
    if (!confirm('确定要回滚此操作吗？这将撤销所有相关变更。')) return;
    
    try {
      await approvalApi.rollback(id);
      alert('回滚成功');
      fetchHistory();
    } catch (error) {
      console.error('Rollback failed', error);
      alert('回滚失败');
    }
  };

  if (loading) return <div>加载历史记录...</div>;

  return (
    <div className="bg-card shadow-sm border border-border sm:rounded-lg">
      <ul className="divide-y divide-border">
        {approvals.length === 0 ? (
          <li className="px-6 py-12 text-center text-muted-foreground">暂无历史记录。</li>
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
                      {approval.status === 'executed' ? '已执行' :
                       approval.status === 'rejected' ? '已拒绝' :
                       approval.status === 'rolled_back' ? '已回滚' : approval.status}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {format(new Date(approval.updated_at), 'yyyy-MM-dd HH:mm')}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                      {approval.type}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-foreground">
                    {approval.reason || '无描述'}
                  </p>
                </div>
                
                {approval.status === 'executed' && (
                  <button
                    onClick={() => handleRollback(approval.id)}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    回滚
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
