import { MetricFilters } from '@/types/ai-monitor';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search, RotateCcw } from 'lucide-react';
import { useState } from 'react';
import { useTranslations } from 'next-intl';

interface AIMetricsFiltersProps {
  onFilter: (filters: MetricFilters) => void;
}

export function AIMetricsFilters({ onFilter }: AIMetricsFiltersProps) {
  const t = useTranslations('AIMonitor.Filters');
  const [filters, setFilters] = useState<MetricFilters>({
    page: 1,
    page_size: 20,
    module: undefined,
    model: undefined,
    provider: undefined,
    status: undefined,
  });

  const handleSearch = () => {
    onFilter(filters);
  };

  const handleReset = () => {
    const defaultFilters = {
      page: 1,
      page_size: 20,
      module: undefined,
      model: undefined,
      provider: undefined,
      status: undefined,
    };
    setFilters(defaultFilters);
    onFilter(defaultFilters);
  };

  return (
    <div className="flex flex-col gap-4 p-4 border rounded-lg bg-card">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Input
          placeholder={t('module_placeholder')}
          value={filters.module || ''}
          onChange={(e) => setFilters({ ...filters, module: e.target.value || undefined })}
        />
        <Input
          placeholder={t('model_placeholder')}
          value={filters.model || ''}
          onChange={(e) => setFilters({ ...filters, model: e.target.value || undefined })}
        />
        <Select
          value={filters.provider}
          onValueChange={(value) => setFilters({ ...filters, provider: value === 'all' ? undefined : value })}
        >
          <SelectTrigger>
            <SelectValue placeholder={t('provider_placeholder')} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t('provider_all')}</SelectItem>
            <SelectItem value="cloud">{t('provider_cloud')}</SelectItem>
            <SelectItem value="local">{t('provider_local')}</SelectItem>
          </SelectContent>
        </Select>
        <Select
          value={filters.status}
          onValueChange={(value) => setFilters({ ...filters, status: value === 'all' ? undefined : value })}
        >
          <SelectTrigger>
            <SelectValue placeholder={t('status_placeholder')} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t('status_all')}</SelectItem>
            <SelectItem value="success">{t('status_success')}</SelectItem>
            <SelectItem value="error">{t('status_error')}</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={handleReset}>
          <RotateCcw className="mr-2 h-4 w-4" />
          {t('reset')}
        </Button>
        <Button onClick={handleSearch}>
          <Search className="mr-2 h-4 w-4" />
          {t('search')}
        </Button>
      </div>
    </div>
  );
}
