'use client';

import React from 'react';
import { useTranslations } from 'next-intl';

export default function HealthOverview() {
  const t = useTranslations('Health.Overview');

  return (
    <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{t('title')}</h3>
      <p className="text-gray-600">{t('description')}</p>
      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="p-4 bg-gray-50 rounded-md">
          <p className="text-sm font-medium text-gray-500">{t('metrics.overall')}</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">--</p>
        </div>
        <div className="p-4 bg-gray-50 rounded-md">
          <p className="text-sm font-medium text-gray-500">{t('metrics.pyramid')}</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">--</p>
        </div>
        <div className="p-4 bg-gray-50 rounded-md">
          <p className="text-sm font-medium text-gray-500">{t('metrics.source')}</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">--</p>
        </div>
      </div>
    </div>
  );
}
