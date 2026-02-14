'use client';

import { useState } from 'react';
import { contentApi } from '@/lib/api';
import { useRouter } from 'next/navigation';

export default function ContentSubmitForm() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'file' | 'url' | 'text'>('url');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [title, setTitle] = useState('');
  const [file, setFile] = useState<File | null>(null);

  const TAB_NAMES = {
    url: '链接',
    text: '文本',
    file: '文件'
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let response;
      if (activeTab === 'url') {
        response = await contentApi.submitUrl(url);
      } else if (activeTab === 'text') {
        response = await contentApi.submitText(text, title);
      } else if (activeTab === 'file' && file) {
        response = await contentApi.uploadFile(file);
      }

      if (response && response.success) {
        // Redirect to content details or list
        router.push('/contents');
        router.refresh();
      } else {
        setError('提交失败，请重试。');
      }
    } catch (err: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setError((err as any).response?.data?.detail || '提交过程中发生错误。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg p-6">
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {['url', 'text', 'file'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as 'text' | 'url' | 'file')}
              className={`${(
                activeTab === tab
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              )} px-3 py-2 text-sm font-medium rounded-md focus:outline-none`}
            >
              {TAB_NAMES[tab as keyof typeof TAB_NAMES]}
            </button>
          ))}
        </nav>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {activeTab === 'url' && (
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700">
              URL
            </label>
            <div className="mt-1">
              <input
                type="url"
                name="url"
                id="url"
                className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                placeholder="https://example.com/article"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
            </div>
          </div>
        )}

        {activeTab === 'text' && (
          <>
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                标题
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  name="title"
                  id="title"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="text" className="block text-sm font-medium text-gray-700">
                内容
              </label>
              <div className="mt-1">
                <textarea
                  id="text"
                  name="text"
                  rows={8}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  required
                />
              </div>
            </div>
          </>
        )}

        {activeTab === 'file' && (
          <div>
            <label htmlFor="file" className="block text-sm font-medium text-gray-700">
              文件
            </label>
            <div className="mt-1">
              <input
                type="file"
                name="file"
                id="file"
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                required
              />
            </div>
            <p className="mt-2 text-sm text-gray-500">支持的格式: PDF, Markdown, Text</p>
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? '提交中...' : '提交'}
          </button>
        </div>
      </form>
    </div>
  );
}
