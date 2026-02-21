import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Settings2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

interface DouyinInputProps {
  onConvert: (url: string, cookies?: string) => Promise<void>;
  isLoading: boolean;
}

export function DouyinInput({ onConvert, isLoading }: DouyinInputProps) {
  const [url, setUrl] = useState('');
  const [cookies, setCookies] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const t = useTranslations('Tools.Douyin');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    await onConvert(url, cookies);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex gap-4 items-center">
        <Input
          type="text"
          placeholder={t('input_placeholder')}
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={isLoading}
          className="flex-1"
        />
        <Collapsible open={isOpen} onOpenChange={setIsOpen}>
          <CollapsibleTrigger asChild>
            <Button variant="outline" size="icon" type="button">
              <Settings2 className="h-4 w-4" />
            </Button>
          </CollapsibleTrigger>
        </Collapsible>
        <Button type="submit" disabled={isLoading || !url.trim()}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {t('convert_button')}
        </Button>
      </div>
      
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleContent>
          <div className="space-y-2">
            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
              Cookies (Optional)
            </label>
            <Textarea
              placeholder="Paste cookies here (Netscape format or header string)..."
              value={cookies}
              onChange={(e) => setCookies(e.target.value)}
              disabled={isLoading}
              className="min-h-[100px]"
            />
            <p className="text-xs text-muted-foreground">
              If download fails with authentication error, paste cookies here.
            </p>
          </div>
        </CollapsibleContent>
      </Collapsible>
    </form>
  );
}
