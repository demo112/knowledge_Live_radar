import React from 'react';
import { Globe, AlertCircle } from 'lucide-react';

interface SourceHealthSummaryProps {
  score: number;
  className?: string;
}

export default function SourceHealthSummary({ score, className = '' }: SourceHealthSummaryProps) {
  // Determine color based on score
  const colorClass = score >= 80 ? 'text-green-600 dark:text-green-400' : 
                     score >= 60 ? 'text-yellow-600 dark:text-yellow-400' : 
                     'text-red-600 dark:text-red-400';
  
  const bgClass = score >= 80 ? 'bg-green-50 dark:bg-green-900/20' : 
                  score >= 60 ? 'bg-yellow-50 dark:bg-yellow-900/20' : 
                  'bg-red-50 dark:bg-red-900/20';

  return (
    <div className={`bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1">
        <Globe className="w-4 h-4" /> 信息源健康度
      </h3>
      <div className="mt-4 flex items-center justify-between">
        <div className="flex flex-col">
          <span className={`text-3xl font-bold ${colorClass}`}>
            {score.toFixed(1)}
          </span>
          <span className="text-xs text-gray-400 mt-1">综合评分</span>
        </div>
        
        <div className={`p-3 rounded-full ${bgClass}`}>
          {score < 100 ? (
            <AlertCircle className={`w-6 h-6 ${colorClass}`} />
          ) : (
            <Globe className={`w-6 h-6 ${colorClass}`} />
          )}
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
        <div className="flex justify-between text-xs">
          <span className="text-gray-500">可用性</span>
          <span className="font-medium text-gray-900 dark:text-white">--%</span>
        </div>
        <div className="flex justify-between text-xs mt-2">
          <span className="text-gray-500">平均响应时间</span>
          <span className="font-medium text-gray-900 dark:text-white">--ms</span>
        </div>
      </div>
    </div>
  );
}
