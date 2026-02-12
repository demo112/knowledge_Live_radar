import React from 'react';
import { Database, CheckCircle, XCircle } from 'lucide-react';

interface CrawlStatsProps {
  stats: Record<string, any>;
  className?: string;
}

export default function CrawlStats({ stats, className = '' }: CrawlStatsProps) {
  const totalCrawled = stats?.total_crawled || 0;
  const successRate = stats?.success_rate || 0;
  const avgProcessingTime = stats?.avg_processing_time || 0;
  
  return (
    <div className={`bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1">
        <Database className="w-4 h-4" /> 抓取与校验统计
      </h3>
      
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className="bg-blue-50 dark:bg-blue-900/10 p-3 rounded-md">
            <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">总抓取量</div>
            <div className="text-xl font-bold text-blue-700 dark:text-blue-300">{totalCrawled}</div>
        </div>
        
        <div className="bg-green-50 dark:bg-green-900/10 p-3 rounded-md">
            <div className="text-xs text-green-600 dark:text-green-400 mb-1">成功率</div>
            <div className="text-xl font-bold text-green-700 dark:text-green-300">{(successRate * 100).toFixed(1)}%</div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 space-y-3">
        <div className="flex justify-between text-sm items-center">
            <span className="text-gray-500 flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-green-500" /> 校验通过
            </span>
            <span className="font-medium text-gray-900 dark:text-white">{stats?.validated_count || 0}</span>
        </div>
        <div className="flex justify-between text-sm items-center">
            <span className="text-gray-500 flex items-center gap-1">
                <XCircle className="w-3 h-3 text-red-500" /> 校验失败
            </span>
            <span className="font-medium text-gray-900 dark:text-white">{stats?.rejected_count || 0}</span>
        </div>
        <div className="flex justify-between text-sm items-center">
            <span className="text-gray-500">平均处理耗时</span>
            <span className="font-medium text-gray-900 dark:text-white">{avgProcessingTime.toFixed(2)}s</span>
        </div>
      </div>
    </div>
  );
}
