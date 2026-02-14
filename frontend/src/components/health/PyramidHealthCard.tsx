import React from 'react';
import { Layers } from 'lucide-react';

interface PyramidHealthCardProps {
  scores: Record<string, number>;
  className?: string;
}

export default function PyramidHealthCard({ scores, className = '' }: PyramidHealthCardProps) {
  const scoreValues = Object.values(scores);
  const averageScore = scoreValues.length > 0 
    ? scoreValues.reduce((a, b) => a + b, 0) / scoreValues.length 
    : 100;

  return (
    <div className={`bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1">
        <Layers className="w-4 h-4" /> 金字塔结构健康度
      </h3>
      <div className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
        {averageScore.toFixed(1)}
      </div>
      <p className="text-xs text-gray-400 mt-1">平均分</p>
      
      <div className="mt-4 space-y-2">
        {Object.entries(scores).length === 0 ? (
          <p className="text-xs text-gray-400 italic">暂无金字塔数据</p>
        ) : (
          Object.entries(scores).map(([id, score]) => (
            <div key={id} className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-300 truncate max-w-[150px]" title={id}>
                ID: {id.substring(0, 8)}...
              </span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      score >= 80 ? 'bg-green-500' : 
                      score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${score}%` }}
                  />
                </div>
                <span className="text-xs font-medium w-8 text-right">{score.toFixed(0)}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
