'use client';

import {useLocale} from 'next-intl';
import {usePathname, useRouter} from '@/i18n/routing';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Globe } from 'lucide-react';
import { ChangeEvent } from 'react';

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleLocaleChange = (value: string) => {
    router.replace(pathname, {locale: value});
  };

  return (
    <div className="flex items-center gap-2 w-full">
      <Globe className="h-4 w-4 text-muted-foreground shrink-0" />
      <Select 
        value={locale} 
        onValueChange={handleLocaleChange}
      >
        <SelectTrigger className="h-8 text-xs py-1 w-full">
          <SelectValue placeholder="Language" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="zh">中文</SelectItem>
          <SelectItem value="en">English</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
