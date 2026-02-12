import React from 'react';

export default function HealthOverview() {
  return (
    <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
      <h3 className="text-lg font-medium text-gray-900 mb-4">系统健康概览</h3>
      <p className="text-gray-600">健康报告功能正在开发中。</p>
      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="p-4 bg-gray-50 rounded-md">
          <p className="text-sm font-medium text-gray-500">整体评分</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">--</p>
        </div>
        <div className="p-4 bg-gray-50 rounded-md">
          <p className="text-sm font-medium text-gray-500">金字塔健康度</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">--</p>
        </div>
        <div className="p-4 bg-gray-50 rounded-md">
          <p className="text-sm font-medium text-gray-500">信息源状态</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">--</p>
        </div>
      </div>
    </div>
  );
}
