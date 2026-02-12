'use client';

import { useState, useEffect } from 'react';
import { approvalApi } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface Approval {
  id: string;
  type: string;
  status: string;
  data: any;
  created_at: string;
  applicant_id?: string;
  reason?: string;
  confidence_score?: number;
}

export default function ApprovalList() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchApprovals();
  }, []);

  const fetchApprovals = async () => {
    try {
      const response = await approvalApi.getPending();
      if (response.success) {
        setApprovals(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch approvals', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (id: string, status: 'approved' | 'rejected') => {
    try {
      await approvalApi.review(id, status, "UI 界面审核", "admin");
      
      if (status === 'approved') {
        try {
            await approvalApi.execute(id);
            alert('审批已通过并执行成功！');
        } catch (execError) {
            console.error("Execution failed", execError);
            alert('已批准，但执行失败。请检查日志。');
        }
      } else {
          alert('提案已拒绝。');
      }
      
      fetchApprovals(); // Refresh list
    } catch (error) {
      console.error('Review failed', error);
      alert('审批操作失败。');
    }
  };

  if (loading) return <div>加载审批列表中...</div>;

  return (
    <div className="bg-card shadow-sm border border-border sm:rounded-lg">
      <ul className="divide-y divide-border">
        {approvals.length === 0 ? (
          <li className="px-6 py-12 text-center text-muted-foreground">暂无待审批提案。</li>
        ) : (
          approvals.map((approval) => (
            <li key={approval.id} className="px-6 py-4 hover:bg-muted/50 transition-colors duration-200">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0 pr-4">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                      {approval.type}
                    </span>
                    {approval.confidence_score && (
                      <span className="text-xs text-muted-foreground">
                        AI 置信度: {(approval.confidence_score * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-foreground font-medium">
                    {approval.reason || '未提供原因'}
                  </p>
                   <pre className="mt-2 text-xs bg-muted p-3 rounded-md overflow-auto max-w-2xl font-mono text-muted-foreground">
                      {JSON.stringify(approval.data, null, 2)}
                   </pre>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleReview(approval.id, 'approved')}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
                  >
                    批准
                  </button>
                  <button
                    onClick={() => handleReview(approval.id, 'rejected')}
                    className="inline-flex items-center px-4 py-2 border border-border text-sm font-medium rounded-md text-foreground bg-white hover:bg-muted focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
                  >
                    拒绝
                  </button>
                </div>
              </div>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
