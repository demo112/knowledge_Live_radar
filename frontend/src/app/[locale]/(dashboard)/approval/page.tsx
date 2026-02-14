'use client';

import { useState } from 'react';
import ApprovalList from '@/components/approval/ApprovalList';
import ApprovalHistory from '@/components/approval/ApprovalHistory';

export default function ApprovalPage() {
  const [activeTab, setActiveTab] = useState<'pending' | 'history'>('pending');

  return (
    <div className="max-w-7xl mx-auto">
      <div className="md:flex md:items-center md:justify-between mb-8">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-foreground sm:text-3xl sm:truncate">
            审批中心
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            审查并批准待处理的系统变更提案。
          </p>
        </div>
      </div>

      <div className="mb-6 border-b border-border">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('pending')}
            className={`
              whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
              ${activeTab === 'pending'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'}
            `}
          >
            待审批
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`
              whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
              ${activeTab === 'history'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'}
            `}
          >
            历史记录
          </button>
        </nav>
      </div>

      {activeTab === 'pending' ? <ApprovalList /> : <ApprovalHistory />}
    </div>
  );
}
