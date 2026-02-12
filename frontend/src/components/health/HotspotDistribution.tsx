import React from 'react';
import { TrendingUp } from 'lucide-react';
import { Hotspot } from '@/lib/types';

interface HotspotDistributionProps {
  distribution: Record<string, number>;
  hotspots: Hotspot[];
  className?: string;
}

export default function HotspotDistribution({ distribution, hotspots, className = '' }: HotspotDistributionProps) {
  // Sort hotspots by heat_score or recent_7d_count
  const sortedHotspots = [...hotspots].sort((a, b) => (b.recent_7d_count || 0) - (a.recent_7d_count || 0)).slice(0, 5);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'trending': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'emerging': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
      case 'mature': return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300';
      case 'cooling': return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col ${className}`}>
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-purple-500" />
          热点分布 (Hotspots)
        </h3>
      </div>
      
      <div className="p-4 flex-1">
        {/* Distribution Bar */}
        <div className="flex h-4 w-full rounded-full overflow-hidden mb-6 bg-gray-100 dark:bg-gray-700">
          {Object.entries(distribution || {}).map(([status, count], index) => {
            const total = Object.values(distribution || {}).reduce((a, b) => a + b, 0);
            const percent = total > 0 ? (count / total) * 100 : 0;
            if (percent === 0) return null;
            
            let color = 'bg-gray-400';
            if (status === 'trending') color = 'bg-green-500';
            if (status === 'emerging') color = 'bg-blue-500';
            if (status === 'mature') color = 'bg-purple-500';
            
            return (
              <div 
                key={status} 
                className={`${color} h-full`} 
                style={{ width: `${percent}%` }} 
                title={`${status}: ${count}`}
              />
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex flex-wrap gap-3 mb-6">
          {Object.entries(distribution || {}).map(([status, count]) => (
            <div key={status} className="flex items-center gap-1.5 text-xs">
              <div className={`w-2 h-2 rounded-full ${
                status === 'trending' ? 'bg-green-500' :
                status === 'emerging' ? 'bg-blue-500' :
                status === 'mature' ? 'bg-purple-500' : 'bg-gray-400'
              }`} />
              <span className="capitalize text-gray-600 dark:text-gray-300">{status}: {count}</span>
            </div>
          ))}
        </div>

        {/* Top List */}
        <div className="space-y-4">
          {sortedHotspots.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">暂无热点数据</p>
          ) : (
            sortedHotspots.map((h) => (
              <div key={h.id} className="flex justify-between items-center border-b border-gray-100 dark:border-gray-700 pb-2 last:border-0 last:pb-0">
                <div>
                  <div className="font-medium text-sm text-gray-900 dark:text-white">{h.keyword}</div>
                  <div className="text-xs text-gray-500 flex gap-2 mt-1">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${getStatusColor(h.status)}`}>
                      {h.status ? h.status.toUpperCase() : 'UNKNOWN'}
                    </span>
                    {h.growth_rate !== undefined && (
                      <span className={h.growth_rate >= 0 ? 'text-green-600' : 'text-red-600'}>
                         {h.growth_rate > 0 ? '+' : ''}{h.growth_rate.toFixed(1)}%
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-900 dark:text-white">{h.recent_7d_count}</div>
                  <div className="text-xs text-gray-500">7天提及</div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
