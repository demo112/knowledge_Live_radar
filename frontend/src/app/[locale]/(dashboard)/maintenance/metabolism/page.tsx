'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { metabolismApi } from '@/lib/api';
import { MetabolismSuggestion, MetabolismRunStats } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function MetabolismPage() {
  const t = useTranslations('Metabolism');
  const [suggestions, setSuggestions] = useState<MetabolismSuggestion[]>([]);
  const [stats, setStats] = useState<MetabolismRunStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const res = await metabolismApi.getSuggestions() as any;
      if (res && res.items) {
        setSuggestions(res.items);
      } else {
        setSuggestions([]);
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRun = async () => {
    setRunning(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const res = await metabolismApi.run() as any;
      setStats(res);
      fetchSuggestions(); // Refresh list
    } catch (error) {
      console.error('Failed to run metabolism:', error);
      alert(t('alerts.run_failed'));
    } finally {
      setRunning(false);
    }
  };

  const handleCleanup = async () => {
    if (selectedIds.size === 0) return;
    if (!confirm(t('alerts.confirm_cleanup', { count: selectedIds.size }))) return;

    try {
      await metabolismApi.cleanup(Array.from(selectedIds));
      setSelectedIds(new Set());
      fetchSuggestions();
      alert(t('alerts.cleanup_success'));
    } catch (error) {
      console.error('Failed to cleanup:', error);
      alert(t('alerts.cleanup_failed'));
    }
  };

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === suggestions.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(suggestions.map(s => s.id)));
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">{t('title')}</h1>
          <p className="text-muted-foreground">{t('description')}</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleRun} disabled={running}>
            {running ? t('actions.running') : t('actions.run')}
          </Button>
        </div>
      </div>

      {stats && (
        <Card className="bg-green-50 border-green-200">
          <CardContent className="pt-6">
            <div className="flex gap-8">
              <div>
                <div className="text-sm text-gray-500">{t('stats.processed')}</div>
                <div className="text-2xl font-bold">{stats.processed}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">{t('stats.deprecated')}</div>
                <div className="text-2xl font-bold text-orange-600">{stats.to_deprecated}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">{t('stats.archived')}</div>
                <div className="text-2xl font-bold text-gray-600">{stats.to_archived}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>{t('suggestions.title')} ({suggestions.length})</CardTitle>
            {selectedIds.size > 0 && (
              <Button 
                variant="destructive" 
                onClick={handleCleanup}
              >
                {t('actions.cleanup_selected')} ({selectedIds.size})
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <table className="w-full text-sm text-left">
              <thead className="bg-muted/50 text-muted-foreground">
                <tr>
                  <th className="p-4 w-12">
                    <input 
                      type="checkbox" 
                      checked={suggestions.length > 0 && selectedIds.size === suggestions.length}
                      onChange={toggleSelectAll}
                      className="cursor-pointer"
                    />
                  </th>
                  <th className="p-4">{t('table.title')}</th>
                  <th className="p-4">{t('table.score')}</th>
                  <th className="p-4">{t('table.age')}</th>
                  <th className="p-4">{t('table.reason')}</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">
                      {t('table.loading')}
                    </td>
                  </tr>
                ) : suggestions.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">
                      {t('table.empty')}
                    </td>
                  </tr>
                ) : (
                  suggestions.map((item) => (
                    <tr key={item.id} className="border-t hover:bg-muted/50">
                      <td className="p-4">
                        <input 
                          type="checkbox" 
                          checked={selectedIds.has(item.id)}
                          onChange={() => toggleSelect(item.id)}
                          className="cursor-pointer"
                        />
                      </td>
                      <td className="p-4 font-medium">{item.title}</td>
                      <td className="p-4">
                        <Badge variant={item.score < 40 ? "destructive" : "secondary"}>
                          {item.score.toFixed(1)}
                        </Badge>
                      </td>
                      <td className="p-4">{item.age_days.toFixed(0)} 天</td>
                      <td className="p-4 text-muted-foreground">{item.reason}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
