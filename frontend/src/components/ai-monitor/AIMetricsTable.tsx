import { AIMetric } from '@/types/ai-monitor';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { useTranslations } from 'next-intl';

interface AIMetricsTableProps {
  metrics: AIMetric[];
  loading?: boolean;
}

export function AIMetricsTable({ metrics, loading }: AIMetricsTableProps) {
  const t = useTranslations('AIMonitor.Table');
  const tCommon = useTranslations('AIMonitor');

  if (loading) {
    return <div className="p-4 text-center">{t('loading')}</div>;
  }

  if (metrics.length === 0) {
    return <div className="p-4 text-center text-muted-foreground">{t('empty')}</div>;
  }

  return (
    <div className="overflow-x-auto rounded-md border">
      <table className="w-full text-sm text-left">
        <thead className="bg-muted/50 text-xs uppercase">
          <tr>
            <th className="px-4 py-3">{t('time')}</th>
            <th className="px-4 py-3">{t('status')}</th>
            <th className="px-4 py-3">{t('module')}</th>
            <th className="px-4 py-3">{t('model')}</th>
            <th className="px-4 py-3">{t('provider')}</th>
            <th className="px-4 py-3">{t('latency')}</th>
            <th className="px-4 py-3">{t('tokens')}</th>
            <th className="px-4 py-3">{t('error')}</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((metric) => (
            <tr key={metric.id} className="border-b hover:bg-muted/50">
              <td className="px-4 py-3 whitespace-nowrap">
                {format(new Date(metric.timestamp), 'MM-dd HH:mm:ss')}
              </td>
              <td className="px-4 py-3">
                <Badge variant={metric.status === 'success' ? 'default' : 'destructive'}>
                  {tCommon(`status.${metric.status}`)}
                </Badge>
              </td>
              <td className="px-4 py-3">{metric.module ? tCommon(`modules.${metric.module}`) : '-'}</td>
              <td className="px-4 py-3">{metric.model}</td>
              <td className="px-4 py-3">{metric.provider}</td>
              <td className="px-4 py-3">{metric.latency.toFixed(2)}s</td>
              <td className="px-4 py-3">{metric.total_tokens}</td>
              <td className="px-4 py-3 max-w-[200px] truncate text-red-500" title={metric.error_message}>
                {metric.error_message}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
