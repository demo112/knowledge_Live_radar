'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { aiMonitorApi, configApi } from '@/lib/api';
import { MetricFilters, AIMetric, AIStats } from '@/types/ai-monitor';
import { AIMetricsStats } from './AIMetricsStats';
import { AIMetricsTable } from './AIMetricsTable';
import { AIMetricsFilters } from './AIMetricsFilters';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, Settings, Activity } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

import { useTranslations } from 'next-intl';

export function AIMonitorDashboard() {
  const t = useTranslations('AIMonitor');
  const router = useRouter();
  const { toast } = useToast();
  const [stats, setStats] = useState<AIStats | null>(null);
  const [metrics, setMetrics] = useState<AIMetric[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<MetricFilters>({
    page: 1,
    page_size: 20
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [statsData, metricsData] = await Promise.all([
        aiMonitorApi.getStats(),
        aiMonitorApi.getMetrics(filters)
      ]);
      setStats(statsData);
      setMetrics(metricsData.items);
      setTotal(metricsData.total);
    } catch (error) {
      console.error('Failed to fetch AI monitor data:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleFilterChange = (newFilters: MetricFilters) => {
    setFilters((prev) => ({
      ...prev,
      ...newFilters,
      page: 1 // Reset to page 1 on filter change
    }));
  };

  const handlePageChange = (newPage: number) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  const handleTestConnection = async () => {
    try {
      setLoading(true);
      const result = await configApi.testAIConnection('auto');
      toast({
        title: result.success ? t('toasts.connection_success') : t('toasts.connection_failed'),
        description: result.message || (result.success ? t('toasts.service_reachable') : t('toasts.service_unreachable')),
        variant: result.success ? "default" : "destructive"
      });
    } catch (error) {
      console.error('Connection test failed:', error);
      toast({
        title: t('toasts.connection_error'),
        description: t('toasts.test_failed'),
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleTestConnection} disabled={loading}>
            <Activity className="mr-2 h-4 w-4" />
            {t('actions.test_connection')}
          </Button>
          <Button variant="outline" onClick={() => router.push('/settings')}>
            <Settings className="mr-2 h-4 w-4" />
            {t('actions.configure')}
          </Button>
          <Button 
            variant="destructive" 
            onClick={async () => {
              if (!confirm(t('actions.confirm_clean'))) return;
              
              setLoading(true);
              try {
                const result = await aiMonitorApi.cleanMetrics(30);
                toast({
                  title: t('toasts.clean_success'),
                  description: t('toasts.clean_result', { count: result.deleted_count }),
                });
                fetchData();
              } catch (error) {
                console.error('Failed to clean metrics:', error);
                toast({
                  title: t('toasts.clean_error'),
                  description: t('toasts.clean_failed'),
                  variant: "destructive"
                });
              } finally {
                setLoading(false);
              }
            }}
            disabled={loading}
          >
            {t('actions.clean_old_metrics')}
          </Button>
        </div>
      </div>
      
      {stats && <AIMetricsStats stats={stats} />}
      
      <AIMetricsFilters onFilter={handleFilterChange} />
      
      <div className="space-y-4">
        <AIMetricsTable metrics={metrics} loading={loading} />
        
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            {t('pagination.showing', { count: metrics.length, total })}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(filters.page - 1)}
              disabled={filters.page <= 1 || loading}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              {t('pagination.prev')}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(filters.page + 1)}
              disabled={filters.page * filters.page_size >= total || loading}
            >
              {t('pagination.next')}
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
