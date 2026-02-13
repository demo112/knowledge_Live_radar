import React from 'react';
import { HealthReport } from '@/types';
import { Activity, Layers, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTranslations } from 'next-intl';

interface HealthDashboardProps {
  report: HealthReport;
  isLoading?: boolean;
}

const HealthDashboard: React.FC<HealthDashboardProps> = ({ report, isLoading }) => {
  const t = useTranslations('Pyramid.Health');
  const tCommon = useTranslations('Common');

  if (isLoading) {
    return <div className="animate-pulse h-32 bg-gray-100 rounded-lg"></div>;
  }

  if (!report) {
    return null;
  }

  const { score, details, suggestions } = report;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Overall Score */}
        <Card className="col-span-1 md:col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('overall')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-4xl font-bold ${getScoreColor(score)}`}>{score}</div>
            <p className="text-xs text-gray-400 mt-1">{t('out_of_100')}</p>
          </CardContent>
        </Card>

        {/* Depth Balance */}
        <Card>
          <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium text-gray-500">{t('depth_balance')}</CardTitle>
            <Layers className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{details.depth_score}</div>
            <p className="text-xs text-gray-400 mt-1">{t('structural_balance')}</p>
          </CardContent>
        </Card>

        {/* Node Coverage */}
        <Card>
          <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium text-gray-500">{t('content_coverage')}</CardTitle>
            <CheckCircle className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{details.coverage_score}%</div>
            <p className="text-xs text-gray-400 mt-1">{t('nodes_with_content')}</p>
          </CardContent>
        </Card>

        {/* Activity */}
        <Card>
          <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium text-gray-500">{t('activity')}</CardTitle>
            <Activity className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{details.activity_score}</div>
            <p className="text-xs text-gray-400 mt-1">{t('recent_updates')}</p>
          </CardContent>
        </Card>
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Info className="h-4 w-4 text-blue-500" />
              {t('suggestions')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {suggestions.map((suggestion, index) => (
                <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                  <span className="mt-1">•</span>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default HealthDashboard;
