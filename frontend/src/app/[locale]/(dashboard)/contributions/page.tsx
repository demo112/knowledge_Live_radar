'use client';

import { useState, useEffect } from 'react';
import { approvalApi } from '@/lib/api';

interface Contribution {
  id: string;
  type: string;
  status: string;
  data: any;
  created_at: string;
  reason?: string;
  confidence_score?: number;
}

export default function ContributionsPage() {
  const [contributions, setContributions] = useState<Contribution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContributions();
  }, []);

  const fetchContributions = async () => {
    try {
      const response = await approvalApi.getAll('executed');
      if (response.success) {
        setContributions(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch contributions', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>加载贡献记录中...</div>;

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          贡献记录
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          已执行变更的历史记录。
        </p>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {contributions.length === 0 ? (
            <li className="px-6 py-4 text-center text-gray-500">暂无贡献记录。</li>
          ) : (
            contributions.map((contribution) => (
              <li key={contribution.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {contribution.type}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {contribution.reason || '未提供原因'}
                    </p>
                    {contribution.confidence_score !== undefined && (
                      <p className="text-xs text-gray-400 mt-1">
                        置信度: {contribution.confidence_score}
                      </p>
                    )}
                    <p className="text-xs text-gray-400 mt-1">
                        应用时间: {new Date(contribution.created_at).toLocaleString('zh-CN')}
                    </p>
                     <pre className="mt-2 text-xs bg-gray-50 p-2 rounded overflow-auto max-w-lg">
                        {JSON.stringify(contribution.data, null, 2)}
                     </pre>
                  </div>
                  <div>
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      {contribution.status}
                    </span>
                  </div>
                </div>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}
