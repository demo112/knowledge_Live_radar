'use client';

import ApprovalList from '@/components/approval/ApprovalList';
import ApprovalHistory from '@/components/approval/ApprovalHistory';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

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

      <Tabs defaultValue="pending" className="w-full">
        <div className="mb-6 border-b border-border">
          <TabsList className="bg-transparent p-0 h-auto space-x-8">
            <TabsTrigger 
              value="pending"
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-primary py-4 px-1 font-medium"
            >
              待审批
            </TabsTrigger>
            <TabsTrigger 
              value="history"
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-primary py-4 px-1 font-medium"
            >
              审批历史
            </TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="pending" className="mt-0">
          <ApprovalList />
        </TabsContent>
        <TabsContent value="history" className="mt-0">
          <ApprovalHistory />
        </TabsContent>
      </Tabs>
    </div>
  );
}
