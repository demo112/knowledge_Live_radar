import React from 'react';
import {Link} from '@/i18n/routing';
import {useTranslations} from 'next-intl';
import { 
  LayoutDashboard,
  Layers, 
  Globe, 
  FileText, 
  Activity, 
  ClipboardCheck, 
  HeartPulse,
  History,
  Repeat,
  Settings,
  Wrench,
  Cpu,
  Hammer,
  Network
} from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const NAV_ITEMS = [
  { href: '/dashboard', labelKey: 'dashboard', icon: LayoutDashboard },
  { href: '/knowledge', labelKey: 'knowledge', icon: Network },
  { href: '/ai-monitor', labelKey: 'aiMonitor', icon: Cpu },
  { href: '/tools/douyin', labelKey: 'tools', icon: Hammer },
  { href: '/pyramid', labelKey: 'pyramid', icon: Layers },
  { href: '/sources', labelKey: 'sources', icon: Globe },
  { href: '/contents', labelKey: 'contents', icon: FileText },
  { href: '/feed', labelKey: 'feed', icon: Activity },
  { href: '/approval', labelKey: 'approval', icon: ClipboardCheck },
  { href: '/synonyms', labelKey: 'synonyms', icon: Repeat },
  { href: '/history', labelKey: 'history', icon: History },
  { href: '/health', labelKey: 'health', icon: HeartPulse },
  { href: '/maintenance/metabolism', labelKey: 'metabolism', icon: Wrench },
  { href: '/settings', labelKey: 'settings', icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const t = useTranslations('Navigation');

  return (
    <div className="flex h-screen bg-background text-foreground font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-border flex flex-col">
        <div className="p-6 border-b border-border">
          <h1 className="text-xl font-bold text-primary flex items-center gap-2">
            <Activity className="w-6 h-6" />
            {t('appName')}
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
              {t(item.labelKey)}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-border space-y-4">
          <LanguageSwitcher />
          <p className="text-xs text-muted-foreground text-center">
            {t('version')}
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
