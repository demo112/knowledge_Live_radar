"use client";

import React, { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { healthApi, hotspotApi, evolutionApi } from '@/lib/api';
import { HealthReport, HealthIssue, Hotspot } from '@/lib/types';
import { Activity, Zap, RefreshCw, AlertTriangle, ArrowRight } from 'lucide-react';
import PyramidHealthCard from '@/components/health/PyramidHealthCard';
import SourceHealthSummary from '@/components/health/SourceHealthSummary';
import HotspotDistribution from '@/components/health/HotspotDistribution';
import CrawlStats from '@/components/health/CrawlStats';
import ApprovalBacklog from '@/components/health/ApprovalBacklog';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";

interface OptimizationChange {
  source_id: string;
  source_name: string;
  old_interval: number;
  new_interval: number;
  reason: string;
}

interface OptimizationResult {
  success: boolean;
  message: string;
  changes: OptimizationChange[];
}

export default function HealthPage() {
  const t = useTranslations('Health');
  const { toast } = useToast();
  const [report, setReport] = useState<HealthReport | null>(null);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [isOptimizationDialogOpen, setIsOptimizationDialogOpen] = useState(false);

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
    toast({
        title: "开始检测",
        description: "正在进行全系统健康检测...",
    });
    try {
      await healthApi.triggerDetection();
      await fetchData();
      toast({
        title: "检测完成",
        description: "系统健康报告已更新",
      });
    } catch (error) {
      console.error("Detection failed", error);
      toast({
        title: "检测失败",
        description: "无法完成健康检测，请稍后重试",
        variant: "destructive",
      });
    } finally {
      setDetecting(false);
    }
  };

  const handleOptimize = async () => {
      try {
          const result = await evolutionApi.triggerOptimization();
          setOptimizationResult(result);
          setIsOptimizationDialogOpen(true);
          toast({
            title: "优化完成",
            description: result.message || "策略优化已完成",
          });
      } catch (error) {
          console.error("Optimization failed", error);
          toast({
            title: "优化失败",
            description: "策略优化执行失败",
            variant: "destructive",
          });
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

      <Dialog open={isOptimizationDialogOpen} onOpenChange={setIsOptimizationDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>策略优化结果</DialogTitle>
            <DialogDescription>
              {optimizationResult?.message}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <h4 className="text-sm font-medium mb-3">调整详情 ({optimizationResult?.changes?.length || 0})</h4>
            <div className="space-y-3 max-h-[300px] overflow-y-auto">
              {optimizationResult?.changes && optimizationResult.changes.length > 0 ? (
                optimizationResult.changes.map((change, idx) => (
                  <div key={idx} className="flex flex-col p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 text-sm">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-medium text-gray-900 dark:text-gray-100">{change.source_name}</span>
                      <span className="text-xs text-gray-500">{change.reason}</span>
                    </div>
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <span>抓取间隔: {change.old_interval}m</span>
                      <ArrowRight className="w-3 h-3 mx-2" />
                      <span className="font-medium text-blue-600 dark:text-blue-400">{change.new_interval}m</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  本次优化无需调整任何策略
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
