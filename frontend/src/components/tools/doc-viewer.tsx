import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Copy, ExternalLink, Video } from 'lucide-react';
import { DouyinConvertResponse } from '@/types';
import { useToast } from '@/hooks/use-toast';
import { useTranslations } from 'next-intl';

interface DocViewerProps {
  data: DouyinConvertResponse;
}

export function DocViewer({ data }: DocViewerProps) {
  const { toast } = useToast();
  const t = useTranslations('Tools.Douyin');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(data.markdown);
      toast({
        title: t('copy_success'),
        description: t('copy_desc'),
      });
    } catch (err) {
      toast({
        title: t('copy_failed'),
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <Card>
        <CardHeader>
          <div className="flex flex-col space-y-2">
            <CardTitle className="flex items-center gap-2 text-xl">
              <Video className="w-5 h-5 text-primary" />
              {data.video_info.title}
            </CardTitle>
            <CardDescription className="flex items-center gap-4 text-sm">
              <span>{t('author')}: {data.video_info.author}</span>
              <span>•</span>
              <span>{t('duration')}: {data.video_info.duration}s</span>
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
             <Button variant="outline" size="sm" onClick={() => window.open(data.video_info.url, '_blank', 'noopener,noreferrer')}>
               <ExternalLink className="w-4 h-4 mr-2" />
               {t('watch_original')}
             </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="border-primary/20 shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 border-b bg-muted/30">
          <CardTitle className="text-lg font-medium">{t('generated_doc')}</CardTitle>
          <Button variant="ghost" size="sm" onClick={handleCopy} className="hover:bg-background">
            <Copy className="mr-2 h-4 w-4" />
            {t('copy_markdown')}
          </Button>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="bg-card p-6 rounded-lg border border-border overflow-auto max-h-[600px] whitespace-pre-wrap font-mono text-sm leading-relaxed shadow-inner">
            {data.markdown}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
