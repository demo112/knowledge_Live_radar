import React from 'react';
import Link from 'next/link';
import { 
  LayoutDashboard,
  Layers, 
  Globe, 
  FileText, 
  Activity, 
  ClipboardCheck, 
  HeartPulse,
  History
} from 'lucide-react';

const NAV_ITEMS = [
  { href: '/dashboard', label: '仪表板', icon: LayoutDashboard },
  { href: '/pyramid', label: '知识金字塔', icon: Layers },
  { href: '/sources', label: '信息源', icon: Globe },
  { href: '/contents', label: '内容库', icon: FileText },
  { href: '/feed', label: '动态流', icon: Activity },
  { href: '/approval', label: '审批中心', icon: ClipboardCheck },
  { href: '/history', label: '变更历史', icon: History },
  { href: '/health', label: '健康报告', icon: HeartPulse },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-background text-foreground font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-border flex flex-col">
        <div className="p-6 border-b border-border">
          <h1 className="text-xl font-bold text-primary flex items-center gap-2">
            <Activity className="w-6 h-6" />
            AI 知识雷达
          </h1>
        </div>
        <nav className="flex-1 mt-6 px-3 space-y-1">
          {NAV_ITEMS.map((item) => (
            <Link 
              key={item.href}
              href={item.href} 
              className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-foreground hover:bg-primary/10 hover:text-primary transition-colors duration-200"
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-border">
          <p className="text-xs text-muted-foreground text-center">
            v0.4.0 Iteration 4
          </p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-background p-8">
        {children}
      </main>
    </div>
  );
}
