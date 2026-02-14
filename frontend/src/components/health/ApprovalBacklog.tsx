import React from 'react';
import { FileText, Clock, AlertOctagon } from 'lucide-react';
import { ApprovalBacklogData } from '@/lib/types';

interface ApprovalBacklogProps {
  backlog: ApprovalBacklogData;
  className?: string;
}

export default function ApprovalBacklog({ backlog, className = '' }: ApprovalBacklogProps) {
  const totalPending = backlog?.pending_count || 0;
  const penalty = backlog?.backlog_penalty || 0;
  const oldestPending = backlog?.oldest_pending_days || 0;

  return (
    <div className={`bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1">
        <FileText className="w-4 h-4" /> 审批积压
      </h3>
      
      <div className="mt-4 flex items-center justify-between">
        <div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white">{totalPending}</div>
            <div className="text-xs text-gray-500 mt-1">待处理事项</div>
        </div>
        {penalty > 0 && (
            <div className="flex flex-col items-end text-red-500">
                <span className="text-lg font-bold">-{penalty}</span>
                <span className="text-xs">健康分扣除</span>
            </div>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-2 text-sm">
            <Clock className="w-4 h-4 text-orange-500" />
            <span className="text-gray-600 dark:text-gray-300">最长等待: </span>
            <span className={`font-medium ${oldestPending > 3 ? 'text-red-600' : 'text-gray-900 dark:text-white'}`}>
                {oldestPending} 天
            </span>
        </div>
        
        {totalPending > 10 && (
            <div className="mt-3 flex items-center gap-2 text-xs text-red-600 bg-red-50 dark:bg-red-900/20 p-2 rounded">
                <AlertOctagon className="w-3 h-3" />
                <span>积压严重，建议优先处理</span>
            </div>
        )}
      </div>
    </div>
  );
}
