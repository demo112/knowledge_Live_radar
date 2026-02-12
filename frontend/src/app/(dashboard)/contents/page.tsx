'use client';

import { useEffect, useState } from 'react';
import { contentApi } from '@/lib/api';
import { ContentItem } from '@/types';
import Link from 'next/link';

export default function ContentsPage() {
  const [contents, setContents] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchContents();
  }, [page]);

  const fetchContents = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await contentApi.getAll({ skip: (page - 1) * 20, limit: 20 });
      if (response.success) {
        setContents(response.data.items);
        setTotal(response.data.total);
      } else {
        setError('加载内容失败，服务器返回错误。');
      }
    } catch (error) {
      console.error('Failed to fetch contents:', error);
      setError('加载内容失败，请稍后重试。');
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">错误: </strong>
          <span className="block sm:inline">{error}</span>
          <button 
            onClick={() => fetchContents()}
            className="mt-2 bg-red-100 hover:bg-red-200 text-red-800 font-semibold py-1 px-3 rounded text-sm transition-colors"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  const STATUS_MAP: Record<string, string> = {
    PENDING: '待处理',
    PROCESSED: '已处理',
    FAILED: '失败',
    REJECTED: '已拒绝',
    ARCHIVED: '已归档'
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">内容库</h1>
        <Link href="/contents/submit" className="bg-primary hover:bg-primary/90 text-white font-bold py-2 px-4 rounded shadow-sm transition-colors">
          提交内容
        </Link>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md border border-gray-200">
        <ul className="divide-y divide-gray-200">
          {contents.map((content) => (
            <li key={content.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900 truncate max-w-2xl">
                  <a href={content.url} target="_blank" rel="noopener noreferrer" className="hover:text-primary hover:underline">
                    {content.title}
                  </a>
                </h3>
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  content.status === 'PROCESSED' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {STATUS_MAP[content.status] || content.status}
                </span>
              </div>
              <p className="mt-1 text-sm text-gray-500 line-clamp-2">{content.summary || content.content_text?.substring(0, 200)}</p>
              <div className="mt-2 text-xs text-gray-400">
                发布时间: {content.publish_time ? new Date(content.publish_time).toLocaleString('zh-CN') : '未知'}
              </div>
            </li>
          ))}
          {!loading && contents.length === 0 && (
            <li className="px-6 py-12 text-center text-gray-500">暂无内容。</li>
          )}
        </ul>
      </div>

      <div className="mt-4 flex justify-between items-center">
        <button
          disabled={page === 1}
          onClick={() => setPage(p => Math.max(1, p - 1))}
          className="px-4 py-2 border rounded disabled:opacity-50 hover:bg-gray-50 text-sm"
        >
          上一页
        </button>
        <span className="text-sm text-gray-600">第 {page} 页</span>
        <button
          disabled={contents.length < 20} // Simple check, ideally verify with total
          onClick={() => setPage(p => p + 1)}
          className="px-4 py-2 border rounded disabled:opacity-50 hover:bg-gray-50 text-sm"
        >
          下一页
        </button>
      </div>
    </div>
  );
}
