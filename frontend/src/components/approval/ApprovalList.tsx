'use client';

import { useState, useEffect } from 'react';
import { approvalApi } from '@/lib/api';
import { Approval } from '@/types';
import { BrainCircuit } from 'lucide-react';

interface AffectedNode {
  id: string;
  title: string;
  type: string;
}

interface ImpactData {
  risk_level: string;
  affected_nodes: AffectedNode[];
  description: string;
}

export default function ApprovalList() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [impactData, setImpactData] = useState<Record<string, ImpactData>>({});

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

  const toggleImpact = async (id: string) => {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }
    
    setExpandedId(id);
    if (!impactData[id]) {
      try {
        const response = await approvalApi.getImpact(id);
        if (response.success) {
          setImpactData(prev => ({ ...prev, [id]: response.data }));
        }
      } catch (error) {
        console.error('Failed to fetch impact', error);
      }
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
    } catch (error: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      if ((error as any).response?.status === 404) {
        alert('提案不存在或已被处理。');
        fetchApprovals();
      } else {
        console.error('Review failed', error);
        alert('审批操作失败。');
      }
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
                    {approval.confidence_score !== undefined && (
                      <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border ${
                        (approval.confidence_score || 0) >= 0.8 
                          ? 'bg-green-50 text-green-700 border-green-200' 
                          : (approval.confidence_score || 0) >= 0.6
                          ? 'bg-yellow-50 text-yellow-700 border-yellow-200'
                          : 'bg-red-50 text-red-700 border-red-200'
                      }`}>
                        <BrainCircuit className="w-3 h-3" />
                        AI 置信度: {Math.round((approval.confidence_score || 0) * 100)}%
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-foreground font-medium">
                    {approval.reason || '未提供原因'}
                  </p>
                   <div className="mt-2 text-xs bg-muted p-3 rounded-md overflow-auto max-w-2xl font-mono text-muted-foreground">
                      {/* Better formatting for Proposal Data */}
                      {approval.type === 'ADD_NODE' ? (
                        <div>
                          <div><strong>节点名称:</strong> {(approval.data as Record<string, unknown>).name as string}</div>
                          <div><strong>父节点ID:</strong> {(approval.data as Record<string, unknown>).parent_id as string}</div>
                          <div><strong>描述:</strong> {(approval.data as Record<string, unknown>).description as string}</div>
                        </div>
                      ) : (
                        <pre>{JSON.stringify(approval.data, null, 2)}</pre>
                      )}
                   </div>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => toggleImpact(approval.id)}
                    className="inline-flex items-center px-3 py-2 border border-border text-sm font-medium rounded-md text-foreground bg-white hover:bg-muted focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
                  >
                    {expandedId === approval.id ? '隐藏影响' : '分析影响'}
                  </button>
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
              
              {expandedId === approval.id && impactData[approval.id] && (
                <div className="mt-4 p-4 bg-muted/50 rounded-lg border border-border">
                  <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                    影响分析 
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${
                      impactData[approval.id].risk_level === 'high' ? 'bg-red-100 text-red-800 border-red-200' :
                      impactData[approval.id].risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
                      'bg-green-100 text-green-800 border-green-200'
                    }`}>
                      {impactData[approval.id].risk_level.toUpperCase()}
                    </span>
                  </h4>
                  <p className="text-sm text-muted-foreground mb-2">{impactData[approval.id].description}</p>
                  {impactData[approval.id].affected_nodes && impactData[approval.id].affected_nodes.length > 0 && (
                    <div className="text-sm">
                      <span className="font-medium">受影响节点:</span>
                      <ul className="list-disc list-inside mt-1 ml-2 text-muted-foreground">
                        {impactData[approval.id].affected_nodes.map((node) => (
                          <li key={node.id}>
                            {node.title} <span className="text-xs opacity-75">({node.type})</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
