'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { synonymApi } from '@/lib/api';
import { Synonym, SynonymCreate } from '@/types';
import { Plus, Trash2, Search, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

export default function SynonymsPage() {
  const t = useTranslations('Synonyms');
  const tCommon = useTranslations('Common');
  
  const [synonyms, setSynonyms] = useState<Synonym[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState<SynonymCreate>({
    canonical_term: '',
    synonym: '',
    confidence: 1.0,
    source: 'manual'
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchSynonyms = async () => {
    try {
      setLoading(true);
      const data = await synonymApi.getAll({ limit: 100 });
      setSynonyms(data);
    } catch (error) {
      console.error('Failed to fetch synonyms:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSynonyms();
  }, []);

  const handleDelete = async (synonym: string) => {
    if (!confirm(t('delete_confirm'))) return;
    
    try {
      await synonymApi.delete(synonym);
      fetchSynonyms();
    } catch (error) {
      console.error('Failed to delete synonym:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await synonymApi.create(formData);
      setIsModalOpen(false);
      setFormData({
        canonical_term: '',
        synonym: '',
        confidence: 1.0,
        source: 'manual'
      });
      fetchSynonyms();
    } catch (error) {
      console.error('Failed to create synonym:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const filteredSynonyms = synonyms.filter(s => 
    s.canonical_term.toLowerCase().includes(search.toLowerCase()) || 
    s.synonym.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
          <p className="text-muted-foreground">
            {t('description')}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={fetchSynonyms}>
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
          <Button onClick={() => setIsModalOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            {t('add')}
          </Button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative w-full max-w-sm">
        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder={t('search_placeholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-8"
        />
      </div>

      {/* List */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          <div className="col-span-full text-center py-10 text-muted-foreground">
            {tCommon('loading')}
          </div>
        ) : filteredSynonyms.length === 0 ? (
          <div className="col-span-full text-center py-10 text-muted-foreground border border-dashed rounded-lg">
            {t('empty')}
          </div>
        ) : (
          filteredSynonyms.map((item) => (
            <Card key={item.id} className="overflow-hidden">
              <CardHeader className="pb-2 bg-muted/50">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-base font-medium">{item.canonical_term}</CardTitle>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6 text-muted-foreground hover:text-destructive"
                    onClick={() => handleDelete(item.synonym)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{t('synonym')}:</span>
                    <span className="font-medium">{item.synonym}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{t('confidence')}:</span>
                    <Badge variant={item.confidence > 0.8 ? "default" : "secondary"}>
                      {(item.confidence * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{t('source')}:</span>
                    <span className="capitalize">
                      {['manual', 'ai', 'import'].includes(item.source) 
                        ? t(`sources.${item.source}`) 
                        : item.source}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{t('usage')}:</span>
                    <span>{item.usage_count}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Add Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-background rounded-lg shadow-xl w-full max-w-md border">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold">{t('add')}</h2>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <span className="sr-only">{tCommon('cancel')}</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="space-y-2">
                <label htmlFor="canonical" className="text-sm font-medium">
                  {t('canonical')}
                </label>
                <Input
                  id="canonical"
                  required
                  placeholder={t('placeholder_canonical')}
                  value={formData.canonical_term}
                  onChange={(e) => setFormData({ ...formData, canonical_term: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="synonym" className="text-sm font-medium">
                  {t('synonym')}
                </label>
                <Input
                  id="synonym"
                  required
                  placeholder={t('placeholder_synonym')}
                  value={formData.synonym}
                  onChange={(e) => setFormData({ ...formData, synonym: e.target.value })}
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setIsModalOpen(false)}
                  disabled={submitting}
                >
                  {tCommon('cancel')}
                </Button>
                <Button type="submit" disabled={submitting}>
                  {submitting ? tCommon('loading') : tCommon('save')}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
