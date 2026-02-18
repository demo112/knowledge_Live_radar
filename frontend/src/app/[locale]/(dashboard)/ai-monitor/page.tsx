import { AIMonitorDashboard } from '@/components/ai-monitor/AIMonitorDashboard';
import { useTranslations } from 'next-intl';

export default function AIMonitorPage() {
  const t = useTranslations('AIMonitor');

  return (
    <div className="container mx-auto py-6">
      <AIMonitorDashboard />
    </div>
  );
}
