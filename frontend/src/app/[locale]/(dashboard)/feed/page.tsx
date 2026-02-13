'use client';

import { useEffect, useState } from 'react';
import { contentApi } from '@/lib/api';
import { ContentItem } from '@/types';
import { Sparkles, Tag, CheckCircle2 } from 'lucide-react';

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
                <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-lg font-semibold text-gray-900 hover:text-primary hover:underline flex-1">
                  {item.title}
                </a>
                <span className="text-xs text-gray-400 whitespace-nowrap ml-4">
                  {item.publish_time ? new Date(item.publish_time).toLocaleString('zh-CN') : '未知时间'}
                </span>
              </div>

              {/* Tags */}
              {item.tags && item.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {item.tags.map((tag, idx) => (
                    <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700">
                      <Tag className="w-3 h-3 mr-1" />
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              
              {/* Summary with AI indicator */}
              <div className="mb-3 relative group">
                {item.ai_processed && (
                  <div className="absolute -left-2 top-0 h-full w-1 bg-gradient-to-b from-purple-400 to-blue-400 rounded-full opacity-50"></div>
                )}
                <p className={`text-gray-600 text-sm leading-relaxed ${item.ai_processed ? 'pl-3' : ''}`}>
                  {item.ai_processed && (
                    <span className="inline-flex items-center text-purple-600 font-medium mr-2 text-xs">
                      <Sparkles className="w-3 h-3 mr-1" />
                      AI 摘要
                    </span>
                  )}
                  {item.summary || item.content_text?.substring(0, 300) || '暂无内容'}
                </p>
              </div>
              
              <div className="flex items-center gap-4 text-sm text-gray-500 pt-2 border-t border-gray-50 mt-4">
                <span className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                  {item.source_id ? '来自订阅源' : '用户提交'}
                </span>
                
                {item.status === 'PROCESSED' && (
                  <span className="text-green-600 text-xs flex items-center">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    已验证
                  </span>
                )}

                {/* Concepts Preview */}
                {item.concepts && item.concepts.length > 0 && (
                  <div className="flex items-center gap-2 overflow-hidden text-xs text-gray-400">
                    <span>涉及概念:</span>
                    {item.concepts.slice(0, 3).map((c, i) => (
                      <span key={i} className="bg-gray-50 px-1.5 py-0.5 rounded border border-gray-100">
                        {c.name}
                      </span>
                    ))}
                    {item.concepts.length > 3 && <span>+{item.concepts.length - 3}</span>}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
