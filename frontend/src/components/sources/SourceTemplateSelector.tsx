import { useState, useEffect, useCallback } from 'react';
import { sourceApi } from '@/lib/api';
import { SourceTemplate } from '@/types';
import { useTranslations } from 'next-intl';

interface SourceTemplateSelectorProps {
  onTemplateSelect: (template: SourceTemplate) => void;
  onConfigChange: (config: Record<string, unknown>) => void;
  selectedTemplateId?: string;
}

export default function SourceTemplateSelector({ 
  onTemplateSelect, 
  onConfigChange,
  selectedTemplateId 
}: SourceTemplateSelectorProps) {
  const t = useTranslations('Sources.TemplateSelector');
  const [templates, setTemplates] = useState<SourceTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState<SourceTemplate | null>(null);
  const [formValues, setFormValues] = useState<Record<string, unknown>>({});

  const fetchTemplates = async () => {
    try {
      const response = await sourceApi.getTemplates();
      if (response.success) {
        setTemplates(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateConfig = useCallback(async (templateId: string, values: Record<string, unknown>) => {
    try {
      const response = await sourceApi.renderTemplate(templateId, values);
      if (response.success) {
        onConfigChange(response.data);
      }
    } catch (error) {
      console.error('Failed to generate config:', error);
    }
  }, [onConfigChange]);

  const handleTemplateChange = useCallback((template: SourceTemplate) => {
    setSelectedTemplate(template);
    onTemplateSelect(template);
    
    // Initialize form values with defaults
    const initialValues: Record<string, unknown> = {};
    template.config_schema.forEach(field => {
      initialValues[field.name] = field.default !== undefined ? field.default : '';
    });
    setFormValues(initialValues);
    
    // Trigger config generation
    generateConfig(template.id, initialValues);
  }, [onTemplateSelect, generateConfig]);

  useEffect(() => {
    fetchTemplates();
  }, []);

  useEffect(() => {
    if (selectedTemplateId && templates.length > 0) {
      const template = templates.find(t => t.id === selectedTemplateId);
      if (template) {
        handleTemplateChange(template);
      }
    }
  }, [selectedTemplateId, templates, handleTemplateChange]);

  const handleInputChange = (name: string, value: unknown) => {
    const newValues = { ...formValues, [name]: value };
    setFormValues(newValues);
    if (selectedTemplate) {
      generateConfig(selectedTemplate.id, newValues);
    }
  };

  if (loading) return <div className="text-sm text-gray-500">{t('loading')}</div>;

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">{t('select_title')}</label>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {templates.map((template) => (
            <div
              key={template.id}
              onClick={() => handleTemplateChange(template)}
              className={`cursor-pointer rounded-lg border p-3 hover:border-primary transition-colors ${
                selectedTemplate?.id === template.id
                  ? 'border-primary bg-primary/5 ring-1 ring-primary'
                  : 'border-gray-200 bg-white'
              }`}
            >
              <div className="font-medium text-sm text-gray-900">{template.name}</div>
              <div className="text-xs text-gray-500 mt-1">{template.description}</div>
              <div className="text-xs text-gray-400 mt-2 bg-gray-50 inline-block px-1.5 py-0.5 rounded">
                {template.source_type}
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedTemplate && (
        <div className="bg-gray-50 rounded-lg p-4 space-y-3 border border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2">{t('config_title')}</h4>
          {selectedTemplate.config_schema.map((field) => (
            <div key={field.name}>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              {field.type === 'select' ? (
                <select
                  value={(formValues[field.name] as string) || ''}
                  onChange={(e) => handleInputChange(field.name, e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                >
                  <option value="">{t('select_placeholder')}</option>
                  {field.options?.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              ) : field.type === 'boolean' ? (
                <div className="flex items-center">
                   <input
                    type="checkbox"
                    checked={!!formValues[field.name]}
                    onChange={(e) => handleInputChange(field.name, e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span className="ml-2 text-xs text-gray-500">{field.description}</span>
                </div>
              ) : (
                <input
                  type={field.type === 'number' ? 'number' : 'text'}
                  value={(formValues[field.name] as string | number) || ''}
                  onChange={(e) => handleInputChange(field.name, e.target.value)}
                  placeholder={field.description}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                />
              )}
              {field.type !== 'boolean' && field.description && (
                <p className="mt-1 text-xs text-gray-500">{field.description}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
