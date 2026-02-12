'use client';

import ApprovalList from '@/components/approval/ApprovalList';

export default function ApprovalPage() {
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
      <ApprovalList />
    </div>
  );
}
