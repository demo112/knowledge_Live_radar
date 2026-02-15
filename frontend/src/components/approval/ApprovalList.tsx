'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
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
  const t = useTranslations('Approval.List');
  const tTypes = useTranslations('Approval.types');
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
      await approvalApi.review(id, status, t('default_audit_reason'), "admin");
      
      if (status === 'approved') {
        try {
            await approvalApi.execute(id);
            alert(t('alerts.approved_success'));
        } catch (execError) {
            console.error("Execution failed", execError);
            alert(t('alerts.approved_failed'));
        }
      } else {
          alert(t('alerts.rejected'));
      }
      
      fetchApprovals(); // Refresh list
    } catch (error: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      if ((error as any).response?.status === 404) {
        alert(t('alerts.not_found'));
        fetchApprovals();
      } else {
        console.error('Review failed', error);
        alert(t('alerts.failed'));
      }
    }
  };

  const riskMap: Record<string, string> = {
    high: t('impact.risk.high'),
    medium: t('impact.risk.medium'),
    low: t('impact.risk.low')
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
                <div className="flex-1 min-w-0 pr-4">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                      {tTypes.has(approval.type) ? tTypes(approval.type) : approval.type}
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
                        {t('ai_confidence')}: {Math.round((approval.confidence_score || 0) * 100)}%
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-foreground font-medium">
                    {approval.reason || t('no_reason')}
                  </p>
                   <div className="mt-2 text-xs bg-muted p-3 rounded-md overflow-auto max-w-2xl font-mono text-muted-foreground">
                      {/* Better formatting for Proposal Data */}
                      {approval.type === 'ADD_NODE' ? (
                        <div>
                          <div><strong>{t('node_name')}:</strong> {(approval.data as Record<string, unknown>).name as string}</div>
                          <div><strong>{t('parent_id')}:</strong> {(approval.data as Record<string, unknown>).parent_id as string}</div>
                          <div><strong>{t('description')}:</strong> {(approval.data as Record<string, unknown>).description as string}</div>
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
                    {expandedId === approval.id ? t('actions.hide_impact') : t('actions.analyze_impact')}
                  </button>
                  <button
                    onClick={() => handleReview(approval.id, 'approved')}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
                  >
                    {t('actions.approve')}
                  </button>
                  <button
                    onClick={() => handleReview(approval.id, 'rejected')}
                    className="inline-flex items-center px-4 py-2 border border-border text-sm font-medium rounded-md text-foreground bg-white hover:bg-muted focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
                  >
                    {t('actions.reject')}
                  </button>
                </div>
              </div>
              
              {expandedId === approval.id && impactData[approval.id] && (
                <div className="mt-4 p-4 bg-muted/50 rounded-lg border border-border">
                  <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                    {t('impact.title')} 
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${
                      impactData[approval.id].risk_level === 'high' ? 'bg-red-100 text-red-800 border-red-200' :
                      impactData[approval.id].risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
                      'bg-green-100 text-green-800 border-green-200'
                    }`}>
                      {riskMap[impactData[approval.id].risk_level] || impactData[approval.id].risk_level.toUpperCase()}
                    </span>
                  </h4>
                  <p className="text-sm text-muted-foreground mb-2">{impactData[approval.id].description}</p>
                  {impactData[approval.id].affected_nodes && impactData[approval.id].affected_nodes.length > 0 && (
                    <div className="text-sm">
                      <span className="font-medium">{t('impact.affected_nodes')}:</span>
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
