'use client';

import { useEffect, useState } from 'react';
import { contentApi } from '@/lib/api';
import { ContentItem } from '@/types';

export default function FeedPage() {
  const [contents, setContents] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFeed();
  }, []);

  const fetchFeed = async () => {
    setLoading(true);
    try {
      const response = await contentApi.getAll({ limit: 20 });
      if (response.success) {
        setContents(response.data.items);
      } else {
        setError('加载动态失败');
      }
    } catch (err) {
      console.error(err);
      setError('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex justify-center">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 text-red-700 p-4 rounded mb-4">
          {error}
          <button onClick={fetchFeed} className="ml-4 underline">重试</button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">最新动态</h1>
      
      {contents.length === 0 ? (
        <div className="bg-white p-8 rounded-lg shadow text-center text-gray-500">
          暂无动态，请先在信息源中添加订阅或手动触发抓取。
        </div>
      ) : (
        <div className="space-y-6">
          {contents.map((item) => (
            <div key={item.id} className="bg-white p-6 rounded-lg shadow border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-lg font-semibold text-gray-900 hover:text-primary hover:underline">
                  {item.title}
                </a>
                <span className="text-xs text-gray-400 whitespace-nowrap ml-4">
                  {item.publish_time ? new Date(item.publish_time).toLocaleString('zh-CN') : '未知时间'}
                </span>
              </div>
              
              <p className="text-gray-600 mb-3 line-clamp-3">
                {item.summary || item.content_text?.substring(0, 300) || '暂无摘要'}
              </p>
              
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <span className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                  {item.source_id ? '来自订阅源' : '用户提交'}
                </span>
                {item.status === 'PROCESSED' && (
                  <span className="text-green-600 text-xs flex items-center">
                    ✓ 已验证
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
