'use client';

import React from 'react';
import HealthOverview from '@/components/health/HealthOverview';

export default function HealthPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="md:flex md:items-center md:justify-between mb-8">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            健康报告
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            查看系统整体健康状态、金字塔结构质量和信息源监控指标。
          </p>
        </div>
      </div>
      
      <div className="space-y-6">
        <HealthOverview />
      </div>
    </div>
  );
}
