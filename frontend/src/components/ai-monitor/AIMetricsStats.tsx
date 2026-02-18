import { AIStats } from '@/types/ai-monitor';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTranslations } from 'next-intl';

interface AIMetricsStatsProps {
  stats: AIStats;
}

export function AIMetricsStats({ stats }: AIMetricsStatsProps) {
  const t = useTranslations('AIMonitor.Stats');

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('total_requests')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_requests}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('success_rate')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.success_rate.toFixed(1)}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('total_tokens')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_tokens.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('avg_latency')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.avg_latency.toFixed(2)}s</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('model_performance')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs uppercase bg-muted/50">
                <tr>
                  <th className="px-4 py-2">{t('model')}</th>
                  <th className="px-4 py-2">{t('requests')}</th>
                  <th className="px-4 py-2">{t('success_rate')}</th>
                  <th className="px-4 py-2">{t('avg_latency')}</th>
                  <th className="px-4 py-2">{t('total_tokens')}</th>
                </tr>
              </thead>
              <tbody>
                {stats.models.map((model) => (
                  <tr key={model.model} className="border-b">
                    <td className="px-4 py-2 font-medium">{model.model}</td>
                    <td className="px-4 py-2">{model.count}</td>
                    <td className="px-4 py-2">{model.success_rate.toFixed(1)}%</td>
                    <td className="px-4 py-2">{model.avg_latency.toFixed(2)}s</td>
                    <td className="px-4 py-2">{model.total_tokens.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
