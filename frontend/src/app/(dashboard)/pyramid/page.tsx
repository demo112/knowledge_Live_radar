'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { pyramidApi } from '@/lib/api';
import { Pyramid } from '@/types';

export default function PyramidListPage() {
  const [pyramids, setPyramids] = useState<Pyramid[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPyramid, setEditingPyramid] = useState<Pyramid | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; id: string | null }>({ open: false, id: null });

  const fetchPyramids = async () => {
    setLoading(true);
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

  useEffect(() => {
    fetchPyramids();
  }, []);

  const handleOpenCreateModal = () => {
    setEditingPyramid(null);
    setFormData({ name: '', description: '' });
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (e: React.MouseEvent, pyramid: Pyramid) => {
    e.preventDefault();
    e.stopPropagation();
    setEditingPyramid(pyramid);
    setFormData({ name: pyramid.name, description: pyramid.description || '' });
    setIsModalOpen(true);
  };

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    setDeleteConfirm({ open: true, id });
  };

  const handleConfirmDelete = async () => {
    if (!deleteConfirm.id) return;
    
    try {
      const response = await pyramidApi.delete(deleteConfirm.id);
      if (response.success) {
        fetchPyramids();
      }
    } catch (error) {
      console.error('Failed to delete pyramid:', error);
      alert('删除失败');
    } finally {
      setDeleteConfirm({ open: false, id: null });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (editingPyramid) {
        await pyramidApi.update(editingPyramid.id, formData);
      } else {
        await pyramidApi.create(formData);
      }
      setIsModalOpen(false);
      fetchPyramids();
    } catch (error) {
      console.error('Failed to save pyramid:', error);
      alert('保存失败');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && pyramids.length === 0) return <div className="p-8">加载中...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">知识金字塔</h1>
        <button 
          className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded shadow-sm transition-colors"
          onClick={handleOpenCreateModal}
        >
          新建金字塔
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pyramids.map((pyramid) => (
          <div key={pyramid.id} className="relative group">
            <Link 
              href={`/pyramid/${pyramid.id}`}
              className="block p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md hover:border-primary/50 transition duration-200 h-full"
            >
              <h5 className="mb-2 text-xl font-bold tracking-tight text-gray-900 group-hover:text-primary pr-16">{pyramid.name}</h5>
              <p className="font-normal text-gray-700 line-clamp-2">{pyramid.description || '暂无描述'}</p>
              <div className="mt-4 text-sm text-gray-500">
                  创建时间: {new Date(pyramid.created_at).toLocaleDateString('zh-CN')}
              </div>
            </Link>
            <div className="absolute top-4 right-4 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={(e) => handleOpenEditModal(e, pyramid)}
                className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                title="编辑"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                onClick={(e) => handleDelete(e, pyramid.id)}
                className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                title="删除"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        ))}
        {pyramids.length === 0 && (
            <div className="col-span-3 text-center text-gray-500 py-10 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                暂无金字塔。请创建一个开始。
            </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm.open && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-sm shadow-xl">
            <h3 className="text-lg font-bold mb-2">确认删除</h3>
            <p className="text-gray-600 mb-6">确定要删除这个金字塔吗？此操作不可撤销。</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setDeleteConfirm({ open: false, id: null })}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleConfirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h2 className="text-xl font-bold mb-4">{editingPyramid ? '编辑金字塔' : '新建金字塔'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">名称</label>
                <input
                  type="text"
                  required
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/50"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="例如：AI 知识图谱"
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
                <textarea
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/50"
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="简要描述这个金字塔的目标..."
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                  disabled={submitting}
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-white rounded hover:bg-primary/90 transition-colors disabled:opacity-50"
                  disabled={submitting}
                >
                  {submitting ? '保存中...' : '保存'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
