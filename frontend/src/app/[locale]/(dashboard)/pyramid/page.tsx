'use client';

import { useEffect, useState, useRef } from 'react';
import {Link} from '@/i18n/routing';
import { pyramidApi } from '@/lib/api';
import { Pyramid, PyramidTemplate } from '@/types';
import { Upload } from 'lucide-react';
import { useTranslations, useFormatter } from 'next-intl';

export default function PyramidListPage() {
  const t = useTranslations('Pyramid.List');
  const format = useFormatter();
  const [pyramids, setPyramids] = useState<Pyramid[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPyramid, setEditingPyramid] = useState<Pyramid | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; id: string | null }>({ open: false, id: null });
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Template support
  const [templates, setTemplates] = useState<PyramidTemplate[]>([]);
  const [creationMode, setCreationMode] = useState<'blank' | 'template'>('blank');
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('');

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
  
  const fetchTemplates = async () => {
    try {
      const response = await pyramidApi.getTemplates();
      if (response.success) {
        setTemplates(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
        try {
            const json = JSON.parse(event.target?.result as string);
            await pyramidApi.importTemplate(json);
            fetchPyramids();
            alert(t('alerts.import_success'));
        } catch (error) {
            console.error('Import failed:', error);
            alert(t('alerts.import_failed'));
        }
    };
    reader.readAsText(file);
    // Reset input
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  useEffect(() => {
    fetchPyramids();
  }, []);

  const handleOpenCreateModal = () => {
    setEditingPyramid(null);
    setFormData({ name: '', description: '' });
    setCreationMode('blank');
    setSelectedTemplateId('');
    setIsModalOpen(true);
    fetchTemplates();
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
    console.log('Delete button clicked for pyramid:', id);
    setDeleteConfirm({ open: true, id });
  };

  const handleConfirmDelete = async () => {
    if (!deleteConfirm.id) return;
    
    try {
      console.log('Sending delete request for:', deleteConfirm.id);
      const response = await pyramidApi.delete(deleteConfirm.id);
      console.log('Delete response:', response);
      if (response.success) {
        fetchPyramids();
      }
    } catch (error: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      if ((error as any).response?.status === 404) {
        // Already deleted, just refresh
        fetchPyramids();
      } else {
        console.error('Failed to delete pyramid:', error);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errorMessage = (error as any).response?.data?.error?.message || (error as Error).message || t('alerts.delete_failed');
        alert(`${t('alerts.delete_failed')}: ${errorMessage}`);
      }
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
        if (creationMode === 'template' && selectedTemplateId) {
           await pyramidApi.createFromTemplate(selectedTemplateId, formData.name);
        } else {
           await pyramidApi.create(formData);
        }
      }
      setIsModalOpen(false);
      fetchPyramids();
    } catch (error) {
      console.error('Failed to save pyramid:', error);
      alert(t('alerts.save_failed'));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && pyramids.length === 0) return <div className="p-8">{t('loading')}</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{t('title')}</h1>
        <div className="flex gap-2">
            <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                className="hidden" 
                accept=".json"
            />
            <button 
                className="flex items-center gap-2 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-2 rounded shadow-sm transition-colors"
                onClick={handleImportClick}
            >
                <Upload className="w-4 h-4" />
                {t('import')}
            </button>
            <button 
              className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded shadow-sm transition-colors"
              onClick={handleOpenCreateModal}
            >
              {t('new_pyramid')}
            </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pyramids.map((pyramid) => (
          <div key={pyramid.id} className="relative group">
            <Link 
              href={`/pyramid/${pyramid.id}`}
              className="block p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md hover:border-primary/50 transition duration-200 h-full"
            >
              <h5 className="mb-2 text-xl font-bold tracking-tight text-gray-900 group-hover:text-primary pr-16">{pyramid.name}</h5>
              <p className="font-normal text-gray-700 line-clamp-2">{pyramid.description || t('no_description')}</p>
              <div className="mt-4 text-sm text-gray-500">
                  {t('created_at', { date: format.dateTime(new Date(pyramid.created_at), {dateStyle: 'short'}) })}
              </div>
            </Link>
            <div className="absolute top-4 right-4 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity z-20">
              <button
                onClick={(e) => handleOpenEditModal(e, pyramid)}
                className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                title={t('edit')}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                onClick={(e) => handleDelete(e, pyramid.id)}
                className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                title={t('delete')}
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
                {t('empty')}
            </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm.open && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-sm shadow-xl">
            <h3 className="text-lg font-bold mb-2">{t('delete_confirm.title')}</h3>
            <p className="text-gray-600 mb-6">{t('delete_confirm.message')}</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setDeleteConfirm({ open: false, id: null })}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
              >
                {t('delete_confirm.cancel')}
              </button>
              <button
                onClick={handleConfirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                {t('delete_confirm.confirm')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h2 className="text-xl font-bold mb-4">{editingPyramid ? t('modal.title_edit') : t('modal.title_create')}</h2>
            <form onSubmit={handleSubmit}>
              {!editingPyramid && (
                <div className="flex mb-6 border-b">
                  <button
                    type="button"
                    className={`pb-2 px-4 ${creationMode === 'blank' ? 'border-b-2 border-primary text-primary font-medium' : 'text-gray-500'}`}
                    onClick={() => setCreationMode('blank')}
                  >
                    {t('modal.create_blank')}
                  </button>
                  <button
                    type="button"
                    className={`pb-2 px-4 ${creationMode === 'template' ? 'border-b-2 border-primary text-primary font-medium' : 'text-gray-500'}`}
                    onClick={() => setCreationMode('template')}
                  >
                    {t('modal.create_template')}
                  </button>
                </div>
              )}

              {creationMode === 'template' && !editingPyramid && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('modal.select_template')}</label>
                  <select
                    required={creationMode === 'template'}
                    className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={selectedTemplateId}
                    onChange={(e) => {
                        const tId = e.target.value;
                        setSelectedTemplateId(tId);
                        const tmpl = templates.find(t => t.id === tId);
                        if (tmpl) {
                            setFormData(prev => ({ ...prev, description: tmpl.description }));
                        }
                    }}
                  >
                    <option value="">{t('modal.select_template_placeholder')}</option>
                    {templates.map(t => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="mb-4">
                <label htmlFor="pyramid-name" className="block text-sm font-medium text-gray-700 mb-1">{t('modal.name_label')}</label>
                <input
                  id="pyramid-name"
                  type="text"
                  required
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/50"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder={t('modal.name_placeholder')}
                />
              </div>
              <div className="mb-6">
                <label htmlFor="pyramid-desc" className="block text-sm font-medium text-gray-700 mb-1">{t('modal.description_label')}</label>
                <textarea
                  id="pyramid-desc"
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/50"
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder={t('modal.description_placeholder')}
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                  disabled={submitting}
                >
                  {t('modal.cancel')}
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-white rounded hover:bg-primary/90 transition-colors disabled:opacity-50"
                  disabled={submitting}
                >
                  {submitting ? t('modal.saving') : t('modal.save')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
