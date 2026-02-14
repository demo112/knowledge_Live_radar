import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { sourceApi } from '@/lib/api';

interface CrawlJob {
  id: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  items_fetched: number;
  items_new: number;
  error_message: string | null;
}

interface CrawlHistoryDialogProps {
  sourceId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function CrawlHistoryDialog({ sourceId, open, onOpenChange }: CrawlHistoryDialogProps) {
  const [history, setHistory] = useState<CrawlJob[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && sourceId) {
      loadHistory(sourceId);
    }
  }, [open, sourceId]);

  const loadHistory = async (id: string) => {
    setLoading(true);
    try {
      const response = await sourceApi.getCrawlHistory(id);
      if (response.success) {
        setHistory(response.data);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>抓取历史</DialogTitle>
        </DialogHeader>
        <div className="mt-4 max-h-[60vh] overflow-y-auto">
          {loading ? (
            <div className="text-center py-4">加载中...</div>
          ) : history.length === 0 ? (
            <div className="text-center py-4 text-gray-500">暂无抓取记录</div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">开始时间</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">获取数量</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">新增数量</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">耗时</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {history.map((job) => (
                  <tr key={job.id}>
                    <td className="px-3 py-2 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        job.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                        job.status === 'FAILED' ? 'bg-red-100 text-red-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {job.status}
                      </span>
                      {job.error_message && (
                        <div className="text-xs text-red-500 mt-1 max-w-xs truncate" title={job.error_message}>
                          {job.error_message}
                        </div>
                      )}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">
                      {new Date(job.started_at).toLocaleString('zh-CN')}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                      {job.items_fetched}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-green-600 font-medium">
                      +{job.items_new}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">
                      {job.ended_at ? 
                        `${Math.round((new Date(job.ended_at).getTime() - new Date(job.started_at).getTime()) / 1000)}s` 
                        : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
