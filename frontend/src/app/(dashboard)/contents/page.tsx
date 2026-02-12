'use client';

import { useEffect, useState } from 'react';
import { contentApi } from '@/lib/api';
import { ContentItem } from '@/types';

export default function ContentsPage() {
  const [contents, setContents] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchContents();
  }, [page]);

  const fetchContents = async () => {
    setLoading(true);
    try {
      const response = await contentApi.getAll({ skip: (page - 1) * 20, limit: 20 });
      if (response.success) {
        setContents(response.data.items);
        setTotal(response.data.total);
      }
    } catch (error) {
      console.error('Failed to fetch contents:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Contents</h1>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {contents.map((content) => (
            <li key={content.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900 truncate max-w-2xl">
                  <a href={content.url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 hover:underline">
                    {content.title}
                  </a>
                </h3>
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  content.status === 'PROCESSED' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {content.status}
                </span>
              </div>
              <p className="mt-1 text-sm text-gray-500 line-clamp-2">{content.summary || content.content_text?.substring(0, 200)}</p>
              <div className="mt-2 text-xs text-gray-400">
                Published: {content.publish_time ? new Date(content.publish_time).toLocaleString() : 'Unknown'}
              </div>
            </li>
          ))}
          {!loading && contents.length === 0 && (
            <li className="px-6 py-4 text-center text-gray-500">No contents found.</li>
          )}
        </ul>
      </div>

      <div className="mt-4 flex justify-between items-center">
        <button
          disabled={page === 1}
          onClick={() => setPage(p => Math.max(1, p - 1))}
          className="px-4 py-2 border rounded disabled:opacity-50"
        >
          Previous
        </button>
        <span>Page {page}</span>
        <button
          disabled={contents.length < 20} // Simple check, ideally verify with total
          onClick={() => setPage(p => p + 1)}
          className="px-4 py-2 border rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}
