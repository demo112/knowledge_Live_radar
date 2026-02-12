'use client';

import { useEffect, useState } from 'react';
import { dashboardApi } from '@/lib/api';
import { Globe, Shield, CheckCircle, Database } from 'lucide-react';

interface DashboardStats {
  total_sources: number;
  active_sources: number;
  discovered_domains: number;
  whitelisted_domains: number;
  total_contents: number;
  validation_pass_rate: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await dashboardApi.getStats();
      setStats(response);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8">加载中...</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">系统概览</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Information Sources Card */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-500 text-sm font-medium">信息源</h3>
            <Globe className="w-5 h-5 text-blue-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-3xl font-bold text-gray-900">{stats?.active_sources}</span>
            <span className="ml-2 text-sm text-gray-500">/ {stats?.total_sources} 活跃</span>
          </div>
        </div>

        {/* Discovery & Whitelist Card */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-500 text-sm font-medium">发现 & 白名单</h3>
            <Shield className="w-5 h-5 text-green-500" />
          </div>
          <div className="space-y-1">
             <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">新发现域名</span>
                <span className="text-lg font-bold text-gray-900">{stats?.discovered_domains}</span>
             </div>
             <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">白名单域名</span>
                <span className="text-lg font-bold text-gray-900">{stats?.whitelisted_domains}</span>
             </div>
          </div>
        </div>

        {/* Contents Card */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-500 text-sm font-medium">已收录内容</h3>
            <Database className="w-5 h-5 text-purple-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-3xl font-bold text-gray-900">{stats?.total_contents}</span>
            <span className="ml-2 text-sm text-gray-500">条目</span>
          </div>
        </div>

        {/* Validation Quality Card */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-500 text-sm font-medium">内容合格率</h3>
            <CheckCircle className="w-5 h-5 text-orange-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-3xl font-bold text-gray-900">{stats?.validation_pass_rate}%</span>
            <span className="ml-2 text-sm text-gray-500">通过校验</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Placeholder for Charts or Lists */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100 h-64 flex items-center justify-center text-gray-400">
            趋势图表区域 (待实现)
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100 h-64 flex items-center justify-center text-gray-400">
            最近活动日志 (待实现)
        </div>
      </div>
    </div>
  );
}
