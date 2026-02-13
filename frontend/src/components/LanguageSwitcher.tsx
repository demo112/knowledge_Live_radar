'use client';

import {useLocale} from 'next-intl';
import {usePathname, useRouter} from '@/i18n/routing';
import { Select } from "@/components/ui/select";
import { Globe } from 'lucide-react';
import { ChangeEvent } from 'react';

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleLocaleChange = (e: ChangeEvent<HTMLSelectElement>) => {
    router.replace(pathname, {locale: e.target.value});
  };

  return (
    <div className="flex items-center gap-2 w-full">
      <Globe className="h-4 w-4 text-muted-foreground shrink-0" />
      <Select 
        value={locale} 
        onChange={handleLocaleChange}
        className="h-8 text-xs py-1"
      >
        <option value="zh">中文</option>
        <option value="en">English</option>
      </Select>
    </div>
  );
}
