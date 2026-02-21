"use client"

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { DouyinInput } from '@/components/tools/douyin-input';
import { DocViewer } from '@/components/tools/doc-viewer';
import { toolsApi } from '@/lib/api';
import { DouyinConvertResponse } from '@/types';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

export default function DouyinToolPage() {
  const t = useTranslations('Tools.Douyin');
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('');
  const [result, setResult] = useState<DouyinConvertResponse | null>(null);
  const { toast } = useToast();

  const handleConvert = async (url: string, cookies?: string) => {
    setIsLoading(true);
    setResult(null);
    setProgress(0);
    setStage(t('start'));
    try {
      const data = await toolsApi.convertDouyinStream(url, (event) => {
        if (event.stage === 'error') {
           throw new Error(event.message);
        }
        if (event.progress) setProgress(event.progress);
        if (event.message) setStage(event.message);
      }, cookies);
      setResult(data);
    } catch (error: any) {
      console.error('Conversion failed:', error);
      setStage('error'); // Set stage to error to keep visibility if needed, or handle differently
      toast({
        title: t('error'),
        description: error.message || t('error_desc'),
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container max-w-4xl mx-auto py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
        <p className="text-muted-foreground">
          {t('description')}
        </p>
      </div>

      <div className="bg-card p-6 rounded-lg border shadow-sm">
        <DouyinInput onConvert={handleConvert} isLoading={isLoading} />
        
        {(isLoading || (stage && stage !== t('start'))) && (
          <div className="mt-6 space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span className={stage === 'error' ? "text-destructive" : ""}>
                {stage === 'error' ? t('error') : (stage || t('converting'))}
              </span>
              <span>{progress}%</span>
            </div>
            <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ease-in-out ${
                  stage === 'error' ? 'bg-destructive' : 'bg-primary'
                }`}
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {result && <DocViewer data={result} />}
    </div>
  );
}
