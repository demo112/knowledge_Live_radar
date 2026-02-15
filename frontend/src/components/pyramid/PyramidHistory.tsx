'use client';

import { useState, useEffect, useCallback } from 'react';
import { pyramidApi } from '@/lib/api';
import { useTranslations, useFormatter } from 'next-intl';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RotateCcw, Plus, Eye } from 'lucide-react';
import PyramidView from './PyramidView';
import { PyramidDetail, PyramidNode } from '@/types';

interface Snapshot {
  id: string;
  version: string;
  reason: string;
  created_at: string;
}

interface SnapshotDetail extends Snapshot {
  data: {
    pyramid: {
      id: string;
      name: string;
      description?: string;
    };
    nodes: PyramidNode[];
    relations: unknown[];
  };
}

interface PyramidHistoryProps {
  pyramidId: string;
}

export default function PyramidHistory({ pyramidId }: PyramidHistoryProps) {
  const t = useTranslations('Pyramid.Detail.History');
  const tCommon = useTranslations('Common');
  const format = useFormatter();
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Dialog states
  const [createOpen, setCreateOpen] = useState(false);
  const [rollbackSnapshot, setRollbackSnapshot] = useState<Snapshot | null>(null);
  const [previewSnapshot, setPreviewSnapshot] = useState<SnapshotDetail | null>(null);
  const [reason, setReason] = useState('');
  const [processing, setProcessing] = useState(false);

  const fetchHistory = useCallback(async () => {
    try {
      const response = await pyramidApi.getHistory(pyramidId);
      if (response.success) {
        const data = response.data;
        if (Array.isArray(data)) {
           setSnapshots(data);
        } else if (data && Array.isArray(data.items)) {
           setSnapshots(data.items);
        } else {
           setSnapshots([]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch history', error);
    } finally {
      setLoading(false);
    }
  }, [pyramidId]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleCreateSnapshot = async () => {
    if (!reason.trim()) return;
    setProcessing(true);
    try {
      await pyramidApi.createSnapshot(pyramidId, reason);
      setCreateOpen(false);
      setReason('');
      fetchHistory();
    } catch (error) {
      console.error('Failed to create snapshot', error);
      alert(t('operation_failed'));
    } finally {
      setProcessing(false);
    }
  };

  const handleRollback = async () => {
    if (!rollbackSnapshot) return;
    setProcessing(true);
    try {
      await pyramidApi.rollback(pyramidId, rollbackSnapshot.id);
      setRollbackSnapshot(null);
      window.location.reload(); 
    } catch (error) {
      console.error('Failed to rollback', error);
      alert(t('operation_failed'));
    } finally {
      setProcessing(false);
    }
  };

  const handlePreview = async (snapshot: Snapshot) => {
    try {
      const response = await pyramidApi.getSnapshot(pyramidId, snapshot.id);
      if (response.success) {
        setPreviewSnapshot(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch snapshot details', error);
      alert(t('operation_failed'));
    }
  };

  if (loading) return <div>{t('loading')}</div>;

  return (
    <div className="mt-8">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">{t('title')}</h3>
        <Button onClick={() => setCreateOpen(true)} size="sm">
          <Plus className="w-4 h-4 mr-2" />
          {t('create_snapshot')}
        </Button>
      </div>

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
                  <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4 items-center">
                    <div>
                      <p className="text-sm text-gray-500">
                        {snapshot.reason} <span className="font-medium text-gray-900">({snapshot.version})</span>
                      </p>
                    </div>
                    <div className="flex items-center space-x-4">
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
                        <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handlePreview(snapshot)}
                            title={t('preview')}
                        >
                            <Eye className="w-4 h-4" />
                        </Button>
                        <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => setRollbackSnapshot(snapshot)}
                            title={t('rollback')}
                        >
                            <RotateCcw className="w-4 h-4" />
                        </Button>
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

      {/* Create Snapshot Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('create_snapshot')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="reason">{t('reason')}</Label>
              <Input
                id="reason"
                placeholder={t('reason_placeholder')}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>{tCommon('cancel')}</Button>
            <Button onClick={handleCreateSnapshot} disabled={processing || !reason.trim()}>
              {processing ? tCommon('loading') : tCommon('create')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Rollback Confirmation Dialog */}
      <Dialog open={!!rollbackSnapshot} onOpenChange={(open) => !open && setRollbackSnapshot(null)}>
        <DialogContent>
            <DialogHeader>
                <DialogTitle>{t('rollback_confirm_title')}</DialogTitle>
                <DialogDescription>
                    {rollbackSnapshot && t('rollback_confirm_message', { 
                        reason: rollbackSnapshot.reason, 
                        version: rollbackSnapshot.version 
                    })}
                </DialogDescription>
            </DialogHeader>
            <DialogFooter>
                <Button variant="outline" onClick={() => setRollbackSnapshot(null)}>{tCommon('cancel')}</Button>
                <Button variant="destructive" onClick={handleRollback} disabled={processing}>
                    {processing ? tCommon('loading') : t('rollback')}
                </Button>
            </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog open={!!previewSnapshot} onOpenChange={(open) => !open && setPreviewSnapshot(null)}>
        <DialogContent className="max-w-4xl h-[80vh]">
          <DialogHeader>
            <DialogTitle>
              {t('preview_title', { version: previewSnapshot?.version || '' })}
            </DialogTitle>
            <DialogDescription>
                {previewSnapshot?.reason}
            </DialogDescription>
          </DialogHeader>
          <div className="flex-1 overflow-hidden h-full">
            {previewSnapshot && (
              <PyramidView 
                data={{
                  ...previewSnapshot.data.pyramid,
                  created_at: '', // Placeholder
                  updated_at: '', // Placeholder
                  nodes: previewSnapshot.data.nodes
                } as PyramidDetail} 
              />
            )}
          </div>
          <DialogFooter>
            <Button onClick={() => setPreviewSnapshot(null)}>{tCommon('close')}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
