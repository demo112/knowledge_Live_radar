'use client';

import { useEffect, useState, use } from 'react';
import { pyramidApi } from '@/lib/api';
import { PyramidDetail } from '@/types';
import PyramidView from '@/components/pyramid/PyramidView';
import PyramidHistory from '@/components/pyramid/PyramidHistory';

export default function PyramidDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const [pyramid, setPyramid] = useState<PyramidDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'view' | 'history'>('view');

  useEffect(() => {
    const fetchPyramid = async () => {
      try {
        const response = await pyramidApi.getById(unwrappedParams.id);
        if (response.success) {
          setPyramid(response.data);
        }
      } catch (error: any) {
        if (error.response?.status === 404) {
          // Ignore 404 errors as they are handled by the UI (pyramid is null)
          setPyramid(null);
        } else {
          console.error('Failed to fetch pyramid:', error);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchPyramid();
  }, [unwrappedParams.id]);

  if (loading) return <div>加载中...</div>;
  if (!pyramid) return <div>未找到金字塔</div>;

  return (
    <div className="p-8 h-screen flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{pyramid.name}</h1>
        <p className="text-gray-600">{pyramid.description}</p>
      </div>

      <div className="border-b border-gray-200 mb-4">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('view')}
            className={`${
              activeTab === 'view'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            可视化视图
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`${
              activeTab === 'history'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            历史记录
          </button>
        </nav>
      </div>
      
      <div className="flex-grow overflow-auto">
        {activeTab === 'view' ? (
          <PyramidView data={pyramid} />
        ) : (
          <PyramidHistory pyramidId={pyramid.id} />
        )}
      </div>
    </div>
  );
}
