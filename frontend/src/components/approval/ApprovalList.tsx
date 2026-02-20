'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { approvalApi } from '@/lib/api';
import { Approval } from '@/types';
import { BrainCircuit } from 'lucide-react';
import { Button } from '@/components/ui/button';

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
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchApprovals();
  }, []);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      const response = await approvalApi.getPending();
      if (response.success) {
        setApprovals(response.data);
        // Clear selection if items are gone (optional but safer)
        setSelectedIds(new Set());
      }
    } catch (error) {
      console.error('Failed to fetch approvals', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === approvals.length && approvals.length > 0) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(approvals.map(a => a.id)));
    }
  };

  const handleBatchAction = async (action: 'approve' | 'reject') => {
    if (selectedIds.size === 0) return;
    try {
      setLoading(true);
      await approvalApi.batchReview(Array.from(selectedIds), action, "Batch operation");
      await fetchApprovals();
      // alert(t('alerts.batch_success')); // Use toast instead? But keeping consistent with existing alert
    } catch (error) {
      console.error('Batch action failed', error);
      alert(t('alerts.failed'));
    } finally {
      setLoading(false);
    }
  };

  const handleCleanup = async () => {
    if (!confirm(t('alerts.confirm_cleanup') || 'Confirm clear all?')) return;
    try {
      setLoading(true);
      await approvalApi.cleanup();
      await fetchApprovals();
    } catch (error) {
      console.error('Cleanup failed', error);
      alert(t('alerts.failed'));
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
    <div className="space-y-4 relative pb-20">
      {/* Top Bar: Selection & Cleanup */}
      <div className="flex flex-col sm:flex-row justify-between items-center bg-card p-4 rounded-lg border border-border gap-4">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <input 
            type="checkbox" 
            checked={approvals.length > 0 && selectedIds.size === approvals.length}
            onChange={toggleSelectAll}
            className="h-4 w-4 rounded border-input bg-background text-primary focus:ring-primary"
          />
          <span className="text-sm font-medium">
            {selectedIds.size} {t('selected', { defaultMessage: 'selected' })}
          </span>
        </div>
        <div className="flex gap-2 w-full sm:w-auto justify-end">
          <Button 
            variant="destructive" 
            size="sm"
            onClick={handleCleanup}
            disabled={approvals.length === 0}
            className="w-full sm:w-auto"
          >
            {t('actions.cleanup', { defaultMessage: 'Clear All' })}
          </Button>
        </div>
      </div>

      <div className="bg-card shadow-sm border border-border sm:rounded-lg">
        <ul className="divide-y divide-border">
          {approvals.length === 0 ? (
            <li className="px-6 py-12 text-center text-muted-foreground">{t('empty')}</li>
          ) : (
            approvals.map((approval) => (
              <li key={approval.id} className="px-6 py-4 hover:bg-muted/50 transition-colors duration-200">
                <div className="flex items-center justify-between gap-4">
                  {/* Selection Checkbox */}
                  <div className="flex-shrink-0">
                     <input 
                        type="checkbox" 
                        checked={selectedIds.has(approval.id)}
                        onChange={() => toggleSelect(approval.id)}
                        className="h-4 w-4 rounded border-input bg-background text-primary focus:ring-primary"
                     />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                        {tTypes.has(approval.type) ? tTypes(approval.type) : approval.type}
                      </span>
                      {approval.confidence_score !== undefined && (
                        <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border ${
                          (approval.confidence_score || 0) >= 0.8 
                            ? 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800' 
                            : (approval.confidence_score || 0) >= 0.6
                            ? 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300 dark:border-yellow-800'
                            : 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800'
                        }`}>
                          <BrainCircuit className="w-3 h-3" />
                          {t('ai_confidence')}: {Math.round((approval.confidence_score || 0) * 100)}%
                        </span>
                      )}
                    </div>
                    <p className="mt-2 text-sm text-foreground font-medium break-words">
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
                  <div className="flex flex-col sm:flex-row items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => toggleImpact(approval.id)}
                    >
                      {expandedId === approval.id ? t('actions.hide_impact') : t('actions.analyze_impact')}
                    </Button>
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => handleReview(approval.id, 'approved')}
                    >
                      {t('actions.approve')}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleReview(approval.id, 'rejected')}
                    >
                      {t('actions.reject')}
                    </Button>
                  </div>
                </div>
                
                {expandedId === approval.id && impactData[approval.id] && (
                  <div className="mt-4 p-4 bg-muted/50 rounded-lg border border-border">
                    <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                      {t('impact.title')} 
                      <span className={`text-xs px-2 py-0.5 rounded-full border ${
                        impactData[approval.id].risk_level === 'high' ? 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800' :
                        impactData[approval.id].risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300 dark:border-yellow-800' :
                        'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800'
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

      {/* Floating Bottom Batch Actions */}
      {selectedIds.size > 0 && (
        <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 animate-in slide-in-from-bottom-5 fade-in duration-300">
          <div className="bg-popover border border-border shadow-lg rounded-full px-6 py-3 flex items-center gap-4">
            <span className="text-sm font-medium mr-2 whitespace-nowrap">
              {selectedIds.size} {t('selected', { defaultMessage: 'selected' })}
            </span>
            <div className="h-4 w-px bg-border mx-2 hidden sm:block"></div>
            <div className="flex gap-2">
              <Button 
                variant="secondary" 
                size="sm"
                onClick={() => handleBatchAction('reject')}
                className="hover:bg-destructive/10 hover:text-destructive"
              >
                {t('actions.batch_reject', { defaultMessage: 'Reject' })}
              </Button>
              <Button 
                variant="default" 
                size="sm"
                onClick={() => handleBatchAction('approve')}
              >
                {t('actions.batch_approve', { defaultMessage: 'Approve' })}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
