'use client';

import { useEffect, useState } from 'react';
import { dashboardApi } from '@/lib/api';
import { DashboardStats, DashboardTrend } from '@/types';
import { Globe, Shield, CheckCircle, Database, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useTranslations } from 'next-intl';

export default function DashboardPage() {
  const t = useTranslations('Dashboard');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [trend, setTrend] = useState<DashboardTrend | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsData, trendData] = await Promise.all([
        dashboardApi.getStats(),
        dashboardApi.getTrend(7)
      ]);
      setStats(statsData);
      setTrend(trendData);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8">{t('loading')}</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">
        {t('title')}
      </h1>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Information Sources Card */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-500 text-sm font-medium">{t('cards.sources.title')}</h3>
            <Globe className="w-5 h-5 text-blue-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-3xl font-bold text-gray-900">{stats?.active_sources || 0}</span>
            <span className="ml-2 text-sm text-gray-500">{t('cards.sources.active', { total: stats?.total_sources || 0 })}</span>
          </div>
        </div>

        {/* Discovery & Whitelist Card */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-500 text-sm font-medium">{t('cards.discovery.title')}</h3>
            <Shield className="w-5 h-5 text-green-500" />
          </div>
          <div className="space-y-1">
             <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">{t('cards.discovery.discovered')}</span>
                <span className="text-lg font-bold text-gray-900">{stats?.discovered_domains || 0}</span>
             </div>
             <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">{t('cards.discovery.whitelisted')}</span>
                <span className="text-lg font-bold text-gray-900">{stats?.whitelisted_domains || 0}</span>
             </div>
          </div>
        </div>

        {/* Contents Card */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-500 text-sm font-medium">{t('cards.contents.title')}</h3>
            <Database className="w-5 h-5 text-purple-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-3xl font-bold text-gray-900">{stats?.total_contents || 0}</span>
            <span className="ml-2 text-sm text-gray-500">{t('cards.contents.items')}</span>
          </div>
        </div>

        {/* Validation Quality Card */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-500 text-sm font-medium">{t('cards.quality.title')}</h3>
            <CheckCircle className="w-5 h-5 text-orange-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-3xl font-bold text-gray-900">{stats?.validation_pass_rate || 0}%</span>
            <span className="ml-2 text-sm text-gray-500">{t('cards.quality.passed')}</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100 h-96">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-medium text-gray-900">{t('charts.trend_title')}</h3>
                <TrendingUp className="w-5 h-5 text-gray-400" />
            </div>
            <div className="h-80 w-full">
                {trend && trend.trends.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%" minWidth={100} minHeight={100}>
                        <LineChart data={trend.trends}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                            <XAxis 
                                dataKey="date" 
                                tick={{fontSize: 12, fill: '#6b7280'}} 
                                axisLine={false}
                                tickLine={false}
                                tickFormatter={(value) => value.substring(5)}
                            />
                            <YAxis 
                                yAxisId="left"
                                tick={{fontSize: 12, fill: '#6b7280'}} 
                                axisLine={false}
                                tickLine={false}
                                domain={[0, 100]}
                                unit="%"
                            />
                            <YAxis 
                                yAxisId="right"
                                orientation="right"
                                tick={{fontSize: 12, fill: '#6b7280'}} 
                                axisLine={false}
                                tickLine={false}
                            />
                            <Tooltip 
                                contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}}
                            />
                            <Legend />
                            <Line 
                                yAxisId="left"
                                type="monotone" 
                                dataKey="pass_rate" 
                                name={t('charts.pass_rate')}
                                stroke="#f97316" 
                                strokeWidth={2}
                                dot={{r: 4, fill: '#f97316', strokeWidth: 2, stroke: '#fff'}}
                                activeDot={{r: 6}}
                            />
                            <Line 
                                yAxisId="right"
                                type="monotone" 
                                dataKey="total_validations" 
                                name={t('charts.validation_count')}
                                stroke="#3b82f6" 
                                strokeWidth={2}
                                dot={{r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff'}}
                                activeDot={{r: 6}}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-full flex items-center justify-center text-gray-400">
                        {t('charts.no_data')}
                    </div>
                )}
            </div>
        </div>
        
        {/* Activity or other chart placeholder */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100 h-96 flex items-center justify-center text-gray-400">
            {t('charts.more_developing')}
        </div>
      </div>
    </div>
  );
}
