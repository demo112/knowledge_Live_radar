'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { aiMonitorApi, configApi } from '@/lib/api';
import { MetricFilters, AIMetric, AIStats } from '@/types/ai-monitor';
import { AIMetricsStats } from './AIMetricsStats';
import { AIMetricsTable } from './AIMetricsTable';
import { AIMetricsFilters } from './AIMetricsFilters';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, Settings, Activity } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export function AIMonitorDashboard() {
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

  const fetchData = async () => {
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
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

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
        title: result.success ? "Connection Successful" : "Connection Failed",
        description: result.message || (result.success ? "AI service is reachable" : "Could not reach AI service"),
        variant: result.success ? "default" : "destructive"
      });
    } catch (error) {
      toast({
        title: "Connection Error",
        description: "Failed to test connection",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">AI Monitor</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleTestConnection} disabled={loading}>
            <Activity className="mr-2 h-4 w-4" />
            Test Connection
          </Button>
          <Button variant="outline" onClick={() => router.push('/settings')}>
            <Settings className="mr-2 h-4 w-4" />
            Configure
          </Button>
          <Button 
            variant="destructive" 
            onClick={async () => {
              if (confirm('Are you sure you want to delete metrics older than 30 days?')) {
                await aiMonitorApi.cleanMetrics(30);
                fetchData();
              }
            }}
            disabled={loading}
          >
            Clean Old Metrics
          </Button>
        </div>
      </div>
      
      {stats && <AIMetricsStats stats={stats} />}
      
      <AIMetricsFilters onFilter={handleFilterChange} />
      
      <div className="space-y-4">
        <AIMetricsTable metrics={metrics} loading={loading} />
        
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Showing {metrics.length} of {total} results
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(filters.page - 1)}
              disabled={filters.page <= 1 || loading}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(filters.page + 1)}
              disabled={filters.page * filters.page_size >= total || loading}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
