'use client';

import { useState, useEffect } from 'react';
import { contributionApi } from '@/lib/api';
import { Contribution, ContributionStats } from '@/lib/types';
import ContributionDetailModal from '@/components/contribution/ContributionDetailModal';

export default function ContributionsPage() {
  const [contributions, setContributions] = useState<Contribution[]>([]);
  const [stats, setStats] = useState<ContributionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedContribution, setSelectedContribution] = useState<Contribution | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [listRes, statsRes] = await Promise.all([
        contributionApi.getAll(),
        contributionApi.getStats()
      ]);
      
      if (listRes) {
        setContributions(listRes);
      }
      if (statsRes) {
        setStats(statsRes);
      }
    } catch (error) {
      console.error('Failed to fetch contributions', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (contribution: Contribution) => {
    setSelectedContribution(contribution);
    setIsModalOpen(true);
  };

  if (loading) return <div>加载贡献记录中...</div>;

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          贡献记录
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          您的知识贡献历史与处理状态。
        </p>
      </div>

      {stats && (
        <div className="mb-8 grid grid-cols-1 gap-5 sm:grid-cols-3">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">总贡献</dt>
              <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.total}</dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">待处理</dt>
              <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.by_status?.pending || 0}</dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">已采纳</dt>
              <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.by_status?.processed || 0}</dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">已拒绝</dt>
              <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.by_status?.rejected || 0}</dd>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {contributions.map((contribution) => (
            <li key={contribution.id}>
              <div 
                className="px-4 py-4 sm:px-6 hover:bg-gray-50 cursor-pointer transition duration-150 ease-in-out"
                onClick={() => handleViewDetails(contribution)}
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-indigo-600 truncate">
                    {contribution.input_type.toUpperCase()}: {contribution.original_input.substring(0, 50)}
                    {contribution.original_input.length > 50 && '...'}
                  </p>
                  <div className="ml-2 flex-shrink-0 flex">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      ${contribution.status === 'processed' ? 'bg-green-100 text-green-800' : 
                        contribution.status === 'failed' ? 'bg-red-100 text-red-800' : 
                        'bg-yellow-100 text-yellow-800'}`}>
                      {contribution.status}
                    </span>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <p className="flex items-center text-sm text-gray-500">
                      提取概念: {contribution.extracted_concepts?.length || 0} 个
                    </p>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <p>
                      {new Date(contribution.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <ContributionDetailModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        contribution={selectedContribution}
      />
    </div>
  );
}
