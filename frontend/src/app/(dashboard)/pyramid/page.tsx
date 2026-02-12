'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { pyramidApi } from '@/lib/api';
import { Pyramid } from '@/types';

export default function PyramidListPage() {
  const [pyramids, setPyramids] = useState<Pyramid[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPyramids = async () => {
      try {
        const response = await pyramidApi.getAll();
        if (response.success) {
            setPyramids(response.data.items);
        }
      } catch (error) {
        console.error('Failed to fetch pyramids:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchPyramids();
  }, []);

  if (loading) return <div>加载中...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">知识金字塔</h1>
        <button 
          className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded shadow-sm transition-colors"
          onClick={() => alert('创建功能开发中')}
        >
          新建金字塔
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pyramids.map((pyramid) => (
          <Link 
            key={pyramid.id} 
            href={`/pyramid/${pyramid.id}`}
            className="block p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md hover:border-primary/50 transition duration-200"
          >
            <h5 className="mb-2 text-xl font-bold tracking-tight text-gray-900 group-hover:text-primary">{pyramid.name}</h5>
            <p className="font-normal text-gray-700 line-clamp-2">{pyramid.description || '暂无描述'}</p>
            <div className="mt-4 text-sm text-gray-500">
                创建时间: {new Date(pyramid.created_at).toLocaleDateString('zh-CN')}
            </div>
          </Link>
        ))}
        {pyramids.length === 0 && (
            <div className="col-span-3 text-center text-gray-500 py-10 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                暂无金字塔。请创建一个开始。
            </div>
        )}
      </div>
    </div>
  );
}
