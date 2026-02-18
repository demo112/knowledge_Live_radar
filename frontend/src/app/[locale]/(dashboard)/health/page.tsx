"use client";

import React, { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { healthApi, hotspotApi, evolutionApi } from '@/lib/api';
import { HealthReport, HealthIssue, Hotspot } from '@/lib/types';
import { Activity, Zap, RefreshCw, AlertTriangle } from 'lucide-react';
import PyramidHealthCard from '@/components/health/PyramidHealthCard';
import SourceHealthSummary from '@/components/health/SourceHealthSummary';
import HotspotDistribution from '@/components/health/HotspotDistribution';
import CrawlStats from '@/components/health/CrawlStats';
import ApprovalBacklog from '@/components/health/ApprovalBacklog';

export default function HealthPage() {
  const t = useTranslations('Health');
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
          alert(t('optimize_triggered'));
      } catch (error) {
          console.error("Optimization failed", error);
          alert(t('optimize_failed'));
      }
  };

  if (loading && !report) return <div className="p-8">{t('loading')}</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-900 dark:text-white">
          <Activity className="w-6 h-6 text-blue-600" />
          {t('title')}
        </h1>
        <div className="flex gap-2">
            <button 
                onClick={handleOptimize} 
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-700"
            >
                <Zap className="w-4 h-4 mr-2" />
                {t('optimize_strategy')}
            </button>
            <button 
                onClick={handleDetect} 
                disabled={detecting}
                className="flex items-center px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
                <RefreshCw className={`w-4 h-4 mr-2 ${detecting ? 'animate-spin' : ''}`} />
                {detecting ? t('detecting') : t('detect_now')}
            </button>
        </div>
      </div>

      {/* Top Row: Overall + Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Overall Score */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">{t('overall_score')}</h3>
            <div className="mt-2 flex items-baseline">
                <span className="text-4xl font-bold text-gray-900 dark:text-white">{report?.overall_score || 0}</span>
                <span className="ml-2 text-sm text-gray-500">/ 100</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
                {t('last_check')}: {report?.created_at ? new Date(report.created_at).toLocaleString() : t('never')}
            </p>
        </div>
        
        {/* Source Health */}
        <SourceHealthSummary score={report?.source_health_score || 0} />

        {/* Approval Backlog */}
        <ApprovalBacklog backlog={report?.approval_backlog || {
            pending_count: 0,
            backlog_penalty: 0,
            oldest_pending_days: 0
        }} />

        {/* Crawl Stats */}
        <CrawlStats stats={report?.crawl_stats || {}} />
      </div>

      {/* Middle Row: Detailed Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pyramid Structure Health */}
        <PyramidHealthCard scores={report?.pyramid_scores || {}} />

        {/* Hotspots Distribution */}
        <HotspotDistribution 
            distribution={report?.hotspot_distribution || {}} 
            hotspots={hotspots}
        />
      </div>

      {/* Bottom Row: Issues */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                  {t('issues_title')}
              </h3>
          </div>
          <div className="p-4">
              <div className="space-y-3">
                  {(!report?.issues || report.issues.length === 0) ? (
                      <p className="text-sm text-gray-500">{t('no_issues')}</p>
                  ) : (
                      report.issues.map((issue: HealthIssue, idx: number) => (
                          <div key={idx} className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-100 dark:border-red-900/50">
                              <div className="flex justify-between">
                                  <span className="font-medium text-sm text-red-800 dark:text-red-300">
                                      [{t(`categories.${issue.category}`)}] {t(`types.${issue.type}`)}
                                  </span>
                                  <span className="text-xs bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200 px-1.5 py-0.5 rounded font-medium">
                                      -{issue.severity} {t('points')}
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
  );
}
