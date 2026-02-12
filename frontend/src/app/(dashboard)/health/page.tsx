"use client";

import React, { useEffect, useState } from 'react';
import { healthApi, hotspotApi, evolutionApi } from '@/lib/api';
import { HealthReport, Hotspot } from '@/lib/types';
import { Activity, Zap, RefreshCw, AlertTriangle, TrendingUp, Layers, Globe, FileText } from 'lucide-react';

export default function HealthPage() {
  const [report, setReport] = useState<HealthReport | null>(null);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [reportData, hotspotsData] = await Promise.all([
        healthApi.getReport().catch(() => null),
        hotspotApi.getAll().catch(() => [])
      ]);
      setReport(reportData);
      setHotspots(hotspotsData || []);
    } catch (error) {
      console.error("Failed to fetch health data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDetect = async () => {
    setDetecting(true);
    try {
      await healthApi.triggerDetection();
      await fetchData();
    } catch (error) {
      console.error("Detection failed", error);
    } finally {
      setDetecting(false);
    }
  };

  const handleOptimize = async () => {
      try {
          await evolutionApi.triggerOptimization();
          alert("Optimization triggered");
      } catch (error) {
          console.error("Optimization failed", error);
      }
  };

  if (loading && !report) return <div className="p-8">Loading health data...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-900 dark:text-white">
          <Activity className="w-6 h-6 text-blue-600" />
          系统健康与进化
        </h1>
        <div className="flex gap-2">
            <button 
                onClick={handleOptimize} 
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-700"
            >
                <Zap className="w-4 h-4 mr-2" />
                优化抓取策略
            </button>
            <button 
                onClick={handleDetect} 
                disabled={detecting}
                className="flex items-center px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
                <RefreshCw className={`w-4 h-4 mr-2 ${detecting ? 'animate-spin' : ''}`} />
                {detecting ? '检测中...' : '立即检测'}
            </button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">总体健康分</h3>
            <div className="mt-2 flex items-baseline">
                <span className="text-4xl font-bold text-gray-900 dark:text-white">{report?.overall_score || 0}</span>
                <span className="ml-2 text-sm text-gray-500">/ 100</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
                上次检测: {report?.created_at ? new Date(report.created_at).toLocaleString() : 'Never'}
            </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1">
                <Layers className="w-4 h-4" /> 金字塔结构
            </h3>
            <div className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
                {(Object.values(report?.pyramid_scores || {}).reduce((a: any, b: any) => a + b, 0) as number / (Object.values(report?.pyramid_scores || {}).length || 1) || 100).toFixed(1)}
            </div>
            <p className="text-xs text-gray-400 mt-1">平均分</p>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1">
                <Globe className="w-4 h-4" /> 信息源健康
            </h3>
            <div className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
                {report?.source_health_score || 0}
            </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1">
                <FileText className="w-4 h-4" /> 待处理审批
            </h3>
            <div className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
                {report?.approval_backlog?.total_pending || 0}
            </div>
            <p className="text-xs text-gray-400 mt-1">
                扣分: -{report?.approval_backlog?.backlog_penalty || 0}
            </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hotspots */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-purple-500" />
                    热点话题 (Hotspots)
                </h3>
            </div>
            <div className="p-4">
                <div className="space-y-4">
                    {hotspots.length === 0 ? (
                        <p className="text-sm text-gray-500">暂无热点数据</p>
                    ) : (
                        hotspots.map((h: any) => (
                            <div key={h.id} className="flex justify-between items-center border-b border-gray-100 dark:border-gray-700 pb-2 last:border-0 last:pb-0">
                                <div>
                                    <div className="font-medium text-gray-900 dark:text-white">{h.topic_name}</div>
                                    <div className="text-xs text-gray-500 flex gap-2 mt-1">
                                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                                            h.status === 'trending' ? 'bg-green-100 text-green-800' :
                                            h.status === 'emerging' ? 'bg-blue-100 text-blue-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                            {h.status ? h.status.toUpperCase() : 'UNKNOWN'}
                                        </span>
                                        <span>Growth: {h.growth_rate?.toFixed(1) || 0}%</span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="font-bold text-gray-900 dark:text-white">{h.recent_7d_count}</div>
                                    <div className="text-xs text-gray-500">Mentions (7d)</div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>

        {/* Issues */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                    系统问题 (Issues)
                </h3>
            </div>
            <div className="p-4">
                <div className="space-y-3">
                    {(!report?.issues || report.issues.length === 0) ? (
                        <p className="text-sm text-gray-500">系统运行良好，未发现问题。</p>
                    ) : (
                        report.issues.map((issue: any, idx: number) => (
                            <div key={idx} className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-100 dark:border-red-900/50">
                                <div className="flex justify-between">
                                    <span className="font-medium text-sm text-red-800 dark:text-red-300">
                                        [{issue.category}] {issue.type}
                                    </span>
                                    <span className="text-xs bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200 px-1.5 py-0.5 rounded font-medium">
                                        -{issue.severity} pts
                                    </span>
                                </div>
                                <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                                    {issue.description}
                                </p>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}
